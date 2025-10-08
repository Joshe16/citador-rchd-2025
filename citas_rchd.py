# app_citador_rchd.py
import streamlit as st
import re
from datetime import datetime

# ---------------- Helpers ----------------
def versalitas(texto):
    return texto.upper() if texto else ""

def smallcaps_html(texto):
    return f"<span style='font-variant: small-caps'>{versalitas(texto)}</span>"

def limpiar_html(html_text):
    return re.sub('<.*?>', '', html_text)

def to_roman(num):
    try:
        n = int(num)
        if n <= 0:
            return str(num)
        val = [
            1000, 900, 500, 400,
            100, 90, 50, 40,
            10, 9, 5, 4, 1
        ]
        syms = [
            "M", "CM", "D", "CD",
            "C", "XC", "L", "XL",
            "X", "IX", "V", "IV", "I"
        ]
        roman_num = ''
        i = 0
        while n > 0:
            for _ in range(n // val[i]):
                roman_num += syms[i]
                n -= val[i]
            i += 1
        return roman_num
    except Exception:
        return str(num)

_ORDINAL_ES = {
    2: "segunda",
    3: "tercera",
    4: "cuarta",
    5: "quinta",
    6: "sexta",
    7: "séptima",
    8: "octava",
    9: "novena",
    10: "décima"
}
def edicion_spanish(ed):
    if not ed:
        return ""
    ed_clean = str(ed).strip()
    try:
        n = int(ed_clean)
        if n == 1:
            return ""
        return f"{_ORDINAL_ES.get(n, str(n) + 'ª')} edición"
    except Exception:
        ed_lower = ed_clean.lower()
        if "ed" in ed_lower or "edición" in ed_lower or "ª" in ed_lower:
            return ed_clean
        return f"{ed_clean} edición"

def pages_prefix(pags):
    if not pags:
        return ""
    pags = pags.strip()
    if "-" in pags or "–" in pags:
        return f"pp. {pags}"
    else:
        return f"p. {pags}"

def normalize_date(date_str):
    """
    Intenta normalizar varias representaciones de fecha a dd/mm/YYYY.
    Si no puede, devuelve el string original.
    Nota: el formulario ahora pedirá solo AÑO en la mayoría de campos.
    """
    if not date_str:
        return ""
    d = date_str.strip()
    formats_try = [
        "%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d %B %Y",
        "%d de %B de %Y", "%d/%m/%y", "%d-%m-%y"
    ]
    for fmt in formats_try:
        try:
            dt = datetime.strptime(d, fmt)
            return dt.strftime("%d/%m/%Y")
        except Exception:
            continue
    if re.fullmatch(r"\d{8}", d):
        try:
            dt = datetime.strptime(d, "%d%m%Y")
            return dt.strftime("%d/%m/%Y")
        except Exception:
            pass
    return d

# ---------------- Autor formatting ----------------
def formatear_autor(a, html=False):
    ape1 = a.get('apellido1', '').strip()
    ape2 = a.get('apellido2', '').strip()
    nom = a.get('nombre', '').strip()
    apellidos = versalitas(ape1)
    if ape2:
        apellidos += f" {versalitas(ape2)}"
    if html:
        apellidos_html = smallcaps_html(apellidos)
        return f"{apellidos_html}, {nom}"
    else:
        return f"{apellidos}, {nom}"

def formatear_autores(autores, html=False, y_otros_threshold=4):
    autores_validos = [a for a in autores if (a.get('apellido1') or a.get('nombre'))]
    n = len(autores_validos)
    if n == 0:
        return ""
    def formato(a):
        return formatear_autor(a, html=html)
    if n >= y_otros_threshold:
        return f"{formato(autores_validos[0])} y otros"
    if n == 1:
        return formato(autores_validos[0])
    elif 2 <= n <= 3:
        parts = [formato(a) for a in autores_validos]
        return " y ".join(parts)
    else:
        return f"{formato(autores_validos[0])} y otros"

# ---------------- Cita abreviada ----------------
def cita_abreviada(autores, año, paginas=None, tomo=None, tipo=None, libro_y_otros=False, y_otros_threshold=4):
    autores_validos = [a for a in autores if (a.get('apellido1') or a.get('nombre'))]
    n = len(autores_validos)
    tomo_part = f" Tomo {to_roman(tomo)}" if tomo and str(tomo).isdigit() else (f" {tomo}" if tomo else "")
    pag_part = ""
    if paginas:
        pag_part = f", {pages_prefix(paginas)}"
    if tipo == "Norma" or tipo == "Jurisprudencia":
        return ""
    if n == 0:
        return ""
    if libro_y_otros or (n >= y_otros_threshold):
        apellido = versalitas(autores_validos[0].get('apellido1',''))
        return f"{apellido} y otros ({año}){tomo_part}{pag_part}"
    if n == 1:
        apellido = versalitas(autores_validos[0].get('apellido1',''))
        return f"{apellido} ({año}){tomo_part}{pag_part}"
    elif 2 <= n <= 3:
        apellidos = " y ".join([versalitas(a.get('apellido1','')) for a in autores_validos])
        return f"{apellidos} ({año}){pag_part}"
    else:
        apellido = versalitas(autores_validos[0].get('apellido1',''))
        return f"{apellido} y otros ({año}){pag_part}"

# ---------------- Generadores por tipo ----------------
def libro(datos, y_otros_threshold=4):
    autores_html = formatear_autores(datos.get('autores', []), html=True, y_otros_threshold=y_otros_threshold)
    titulo_html = f"<i>{datos.get('titulo','')}</i>" if datos.get('titulo') else ""
    año = datos.get('año','').strip()
    tomo = datos.get('tomo','').strip()
    edicion = datos.get('edicion','').strip()
    ciudad = datos.get('ciudad','').strip()
    editorial = datos.get('editorial','').strip()

    tomo_str = f", Tomo {to_roman(tomo)}" if tomo and tomo.isdigit() else (f", {tomo}" if tomo else "")
    ed_str = ""
    if edicion:
        if edicion.isdigit():
            e = edicion_spanish(edicion)
            if e:
                ed_str = f", {e}"
        else:
            ed_str = f", {edicion}" if "ed" in edicion.lower() or "edición" in edicion.lower() else f", {edicion} edición"

    parent_parts = [p for p in [ciudad, editorial, ed_str.lstrip(', ').strip() if ed_str else ""] if p]
    ciudad_str = f" ({', '.join(parent_parts)})" if parent_parts else ""
    return f"{autores_html} ({año}): {titulo_html}{tomo_str}{ciudad_str}."

def traduccion_libro(datos, y_otros_threshold=4):
    autores_html = formatear_autores(datos.get('autores', []), html=True, y_otros_threshold=y_otros_threshold)
    titulo_html = f"<i>{datos.get('titulo','')}</i>"
    año_original = datos.get('año_original','').strip()
    año = datos.get('año','').strip()
    traductor = datos.get('traductor','').strip()
    ciudad = datos.get('ciudad','').strip()
    editorial = datos.get('editorial','').strip()
    anos = f"[{año_original}] {año}" if año_original else año
    return f"{autores_html} ({anos}): {titulo_html} (trad. {traductor}, {ciudad}, {editorial})."

def capitulo_libro(datos, y_otros_threshold=4):
    autor_html = formatear_autores(datos.get('autor_capitulo', []), html=True, y_otros_threshold=y_otros_threshold)
    editores_html = formatear_autores(datos.get('editores', []), html=True, y_otros_threshold=y_otros_threshold)
    titulo_cap = datos.get('titulo_capitulo','').strip()
    titulo_libro_html = f"<i>{datos.get('titulo_libro','')}</i>"
    año = datos.get('año','').strip()
    ciudad = datos.get('ciudad','').strip()
    editorial = datos.get('editorial','').strip()
    paginas = datos.get('paginas','').strip()
    paginas_part = f" pp. {paginas}" if paginas else ""
    return f"{autor_html} ({año}): \"{titulo_cap}\", en {editores_html} (edit.), {titulo_libro_html} ({ciudad}, {editorial}){paginas_part}."

def articulo_revista(datos, y_otros_threshold=4):
    autores_html = formatear_autores(datos.get('autores', []), html=True, y_otros_threshold=y_otros_threshold)
    titulo_art = datos.get('titulo','').strip()
    revista_html = f"<i>{datos.get('revista','')}</i>" if datos.get('revista') else ""
    año = datos.get('año','').strip()
    volumen = datos.get('volumen','').strip()
    numero = datos.get('numero','').strip()
    paginas = datos.get('paginas','').strip()
    doi = datos.get('doi','').strip()
    url = datos.get('url','').strip()

    ref = f"{autores_html} ({año}): \"{titulo_art}\", {revista_html}"
    if volumen:
        ref += f", vol. {volumen}"
    if numero:
        ref += f", N° {numero}"
    if paginas:
        ref += f": pp. {paginas}"
    if doi:
        ref += f". DOI: {doi}"
    if url:
        ref += f". Disponible en: {url}"
    return ref + "."

def norma(datos):
    pais = versalitas(datos.get('pais','CHILE'))
    tipo_norma = datos.get('tipo_norma','').strip()
    nombre = datos.get('nombre_norma','').strip()
    numero = datos.get('numero','').strip()
    organismo = datos.get('organismo','').strip()
    año = datos.get('año','').strip()

    # Constitución
    if "constit" in tipo_norma.lower() or "constitución" in nombre.lower():
        ref = f"{pais}, <i>{nombre or tipo_norma}</i>"
        ref += f" ({año})" if año else ""
        return ref + ".", f"{pais}, {nombre or tipo_norma}"

    # Ley
    if "ley" in tipo_norma.lower():
        num_part = f"Ley N° {numero}" if numero else "Ley"
        ref = f"{pais}, {num_part}"
        if nombre:
            ref += f". <i>{nombre}</i>"
        ref += f" ({año})" if año else ""
        abreviada = f"{pais}, {num_part}"
        return ref + ".", abreviada

    # Código
    if "código" in tipo_norma.lower() or "codigo" in tipo_norma.lower():
        ref = f"{pais}, <i>{nombre or tipo_norma}</i>"
        ref += f" ({año})" if año else " (s.d.)"
        abreviada = f"{pais}, {nombre or tipo_norma}"
        return ref + ".", abreviada

    # Decreto Supremo / Reglamento / Decreto / Oficio / Circular
    if any(k in tipo_norma.lower() for k in ["decreto", "reglamento", "oficio", "circular"]) or tipo_norma:
        org_part = f", {versalitas(organismo)}" if organismo else ""
        num_part = f" {numero}" if numero else ""
        ref = f"{pais}{org_part}, {tipo_norma}{num_part}"
        if nombre:
            ref += f", <i>{nombre}</i>"
        ref += f" ({año})" if año else ""
        abreviada = f"{pais}, {tipo_norma}{num_part}"
        return ref + ".", abreviada

    # Tratado internacional o convención
    if "tratado" in tipo_norma.lower() or "convención" in tipo_norma.lower():
        ref = f"<i>{nombre or tipo_norma}</i>"
        ref += f" ({año})" if año else ""
        return ref + ".", f"{nombre or tipo_norma}"

    # Instrumento UE
    if any(k in tipo_norma.lower() for k in ["directiva", "reglamento", "decisión"]):
        ref = f"UNIÓN EUROPEA, <i>{nombre or tipo_norma}</i>"
        ref += f", de {año}" if año else ""
        return ref + ".", f"UNIÓN EUROPEA, {nombre or tipo_norma}"

    # fallback
    ref = f"{pais}, {tipo_norma or nombre}"
    if numero:
        ref += f" {numero}"
    if nombre and tipo_norma:
        ref += f". <i>{nombre}</i>"
    ref += f" ({año})" if año else ""
    abreviada = f"{pais}, {tipo_norma or nombre}"
    return ref + ".", abreviada

def jurisprudencia(datos):
    estado = datos.get('estado','').strip()
    tribunal = datos.get('tribunal','').strip()
    año = datos.get('año','').strip()
    fecha = datos.get('fecha','').strip()  # keep if they prefer full date
    fecha_norm = normalize_date(fecha) if fecha else ""
    rol = datos.get('rol','').strip()
    nombre_caso = datos.get('nombre_caso','').strip()
    info_extra = datos.get('info_extra','').strip()
    fuente = datos.get('fuente','').strip()

    inicio = f"{versalitas(estado)}, " if estado else ""
    inicio += f"{tribunal}" if tribunal else ""
    ref = inicio
    if año:
        ref += f", {año}"
    elif fecha_norm:
        ref += f", {fecha_norm}"
    if rol:
        ref += f", rol {rol}"
    if nombre_caso:
        ref += f" ({nombre_caso})"
    if info_extra:
        ref += f", {info_extra}"
    if fuente:
        ref += f". Fuente: {fuente}"
    abre = f"{tribunal}, {año or fecha_norm}" if tribunal and (año or fecha_norm) else tribunal or (año or fecha_norm)
    return ref + ".", abre

def jurisprudencia_internacional(datos):
    tribunal = versalitas(datos.get('tribunal','')).strip()
    nombre_caso = datos.get('nombre_caso','').strip()
    fecha = datos.get('fecha','').strip()
    serie = datos.get('serie','').strip()

    ref = f"{tribunal}, <i>{nombre_caso}</i>"
    if fecha:
        ref += f", Sentencia de {fecha}"
    if serie:
        ref += f" ({serie})"
    abre = f"{tribunal}, {nombre_caso} ({fecha})" if fecha else f"{tribunal}, {nombre_caso}"
    return ref + ".", abre

def decreto_oficio(datos):
    pais = versalitas(datos.get('pais', 'CHILE'))
    organismo = datos.get('organismo', '').strip()
    tipo = datos.get('tipo', '').strip()
    numero = datos.get('numero', '').strip()
    titulo = datos.get('titulo', '').strip()
    año = datos.get('año','').strip()

    org_part = f", {versalitas(organismo)}" if organismo else ""
    num_part = f" {numero}" if numero else ""
    ref = f"{pais}{org_part}, {tipo}{num_part}"
    if titulo:
        ref += f", <i>{titulo}</i>"
    if año:
        ref += f" ({año})"
    abreviada = f"{pais}, {tipo}{num_part}"
    return ref + ".", abreviada

def proyecto_ley(datos):
    pais = versalitas(datos.get('pais', 'CHILE'))
    nombre = datos.get('nombre', '').strip()
    boletin = datos.get('boletin', '').strip()
    año = datos.get('año','').strip()

    ref = f"{pais}, <i>{nombre}</i>" if nombre else f"{pais}, Proyecto de ley"
    if boletin:
        ref += f" (Boletín N° {boletin}"
        if año:
            ref += f", {año})"
        else:
            ref += ")"
    elif año:
        ref += f" ({año})"
    abreviada = f"{pais}, Proyecto de ley {boletin or ''}".strip()
    return ref + ".", abreviada

def historia_ley(datos):
    pais = versalitas(datos.get('pais', 'CHILE'))
    numero = datos.get('numero', '').strip()
    titulo = datos.get('titulo', '').strip()
    año = datos.get('año','').strip()

    ref = f"{pais}, <i>Historia de la Ley N° {numero}"
    if titulo:
        ref += f", {titulo}</i>"
    else:
        ref += "</i>"
    if año:
        ref += f" ({año})"
    abreviada = f"{pais}, Historia de la Ley N° {numero}"
    return ref + ".", abreviada

def documento_internacional(datos):
    organismo = versalitas(datos.get('organismo', '')).strip()
    titulo = datos.get('titulo', '').strip()
    año = datos.get('año','').strip()

    ref = f"{organismo}, <i>{titulo}</i>" if organismo else f"<i>{titulo}</i>"
    if año:
        ref += f" ({año})"
    abreviada = f"{organismo}, {titulo}" if organismo else titulo
    return ref + ".", abreviada

def instrumento_conferencia(datos):
    nombre = datos.get('nombre', '').strip()
    conferencia = datos.get('conferencia', '').strip()
    año = datos.get('año','').strip()

    ref = f"<i>{nombre}</i>" if nombre else ""
    if conferencia:
        ref += f", {conferencia}"
    if año:
        ref += f" ({año})"
    abreviada = nombre
    return ref + ".", abreviada

def web(datos):
    autores = datos.get('autores', [])
    autor_sin = datos.get('autor_sin_autor','').strip()
    año = datos.get('año','').strip()
    titulo = datos.get('titulo','').strip()
    url = datos.get('url','').strip()
    fecha_consulta = datos.get('fecha_consulta','').strip()

    autor_text = formatear_autores(autores, html=False) if autores else autor_sin
    ref = f"{autor_text} ({año}): {titulo}, Disponible en: {url}." if autor_text or titulo else f"{url}"
    if fecha_consulta:
        ref += f" Fecha de consulta: {fecha_consulta}."
    abre = f"{versalitas(autor_text)} ({año})" if autor_text and año else versalitas(autor_text) or autor_sin
    return ref, abre

def tesis(datos, y_otros_threshold=4):
    autor = formatear_autores(datos.get('autores', []), html=True, y_otros_threshold=y_otros_threshold)
    titulo_html = f"<i>{datos.get('titulo','')}</i>"
    año = datos.get('año','').strip()
    grado = datos.get('grado','').strip()
    institucion = datos.get('institucion','').strip()
    paginas = datos.get('paginas','').strip()
    ref = f"{autor} ({año}): {titulo_html}. Memoria para optar al grado de {grado} en la {institucion}."
    return ref

# ---------------- TIPOS mapping ----------------
TIPOS = {
    "Libro": lambda d, config: libro(d, y_otros_threshold=config['y_otros_threshold']),
    "Traducción de libro": lambda d, config: traduccion_libro(d, y_otros_threshold=config['y_otros_threshold']),
    "Capítulo de libro": lambda d, config: capitulo_libro(d, y_otros_threshold=config['y_otros_threshold']),
    "Artículo de revista": lambda d, config: articulo_revista(d, y_otros_threshold=config['y_otros_threshold']),
    "Norma": lambda d, config: norma(d),
    "Decreto / Oficio / Reglamento": lambda d, config: decreto_oficio(d),
    "Proyecto de ley": lambda d, config: proyecto_ley(d),
    "Historia de la ley": lambda d, config: historia_ley(d),
    "Documento internacional (ONU, OEA, etc.)": lambda d, config: documento_internacional(d),
    "Instrumento emanado de congreso / conferencia": lambda d, config: instrumento_conferencia(d),
    "Jurisprudencia": lambda d, config: jurisprudencia(d),
    "Jurisprudencia internacional": lambda d, config: jurisprudencia_internacional(d),
    "Página web o blog": lambda d, config: web(d),
    "Tesis": lambda d, config: tesis(d, y_otros_threshold=config['y_otros_threshold'])
}

# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="Citador RChD Consejeria Academica Derecho UC x >> Avanzar", layout="wide")
st.title("Citador RChD Consejería Académica Derecho UC x >> Avanzar (RChD 2025)")
st.warning("⚠️ Recuerda que las versalitas y las cursivas pueden no copiarse correctamente en algunos navegadores o procesadores de texto. Verifica siempre la cita final manualmente.")

with st.sidebar:
    st.header("Ajustes")
    y_otros_threshold = st.selectbox("Umbral para 'y otros' (mostrar 'y otros' desde N autores)", options=[3,4], index=1,
                                    help="Normas RChD indican 4+, algunas adaptaciones usan 3+. Elige según tu necesidad.")
    show_help = st.checkbox("Mostrar ayudas/hints en formularios", value=True)

config = {"y_otros_threshold": y_otros_threshold}

tipo = st.selectbox("Tipo de fuente", list(TIPOS.keys()))

# número de autores
num_autores = st.number_input("Número de autores (rellenar 0 si no aplica)", min_value=0, max_value=10, value=1)

# historial en sesión
if "historial_citas" not in st.session_state:
    st.session_state["historial_citas"] = []

def agregar_autores_ui(num, prefix="", show_help=True):
    autores = []
    for i in range(num):
        st.markdown(f"**Autor {i+1}**")
        apellido1 = st.text_input(f"Primer apellido", key=f"{prefix}ape1_{i}", placeholder=("Primer apellido o nombre del sitio para webs" if show_help else ""))
        apellido2 = st.text_input(f"Segundo apellido (opcional)", key=f"{prefix}ape2_{i}")
        nombre = st.text_input(f"Nombre", key=f"{prefix}nom_{i}", placeholder=("Si es persona: Nombre(s). Si es entidad: dejar vacío y usar campo 'Autor/Entidad' en webs" if show_help else ""))
        autores.append({'apellido1': apellido1.strip(), 'apellido2': apellido2.strip(), 'nombre': nombre.strip()})
    return autores

libro_y_otros = False
autores = []
if tipo == "Libro" and num_autores >= config['y_otros_threshold']:
    st.info(f"Se detectaron {num_autores} autores (umbral {config['y_otros_threshold']}): solo se pedirá el primer autor y se agregará 'y otros' en la referencia.")
    autores = agregar_autores_ui(1, show_help=show_help)
    libro_y_otros = True
else:
    autores = agregar_autores_ui(num_autores, show_help=show_help) if num_autores > 0 else []

datos = {'autores': autores}

# Inputs dinámicos por tipo (Año en la mayoría)
if tipo == "Libro":
    datos.update({
        'año': st.text_input("Año de publicación"),
        'titulo': st.text_input("Título del libro"),
        'ciudad': st.text_input("Ciudad de publicación (opcional)"),
        'editorial': st.text_input("Editorial (ej: Editorial LexisNexis)"),
        'edicion': st.text_input("Número de edición (opcional, p.ej. Segunda)"),
        'tomo': st.text_input("Tomo o volumen (opcional, p.ej. '1' o 'Tomo I')"),
        'paginas': st.text_input("Páginas (opcional para cita abreviada, ej. 45-47)")
    })
elif tipo == "Traducción de libro":
    datos.update({
        'año_original': st.text_input("Año original"),
        'año': st.text_input("Año de publicación"),
        'titulo': st.text_input("Título"),
        'traductor': st.text_input("Traductor"),
        'ciudad': st.text_input("Ciudad"),
        'editorial': st.text_input("Editorial (ej: Editorial LexisNexis)")
    })
elif tipo == "Capítulo de libro":
    num_aut_cap = st.number_input("Número de autores del capítulo", 1, 10, 1)
    datos['autor_capitulo'] = agregar_autores_ui(num_aut_cap, prefix="cap_", show_help=show_help)
    num_editores = st.number_input("Número de editores", 1, 10, 1)
    datos['editores'] = agregar_autores_ui(num_editores, prefix="edit_", show_help=show_help)
    datos.update({
        'año': st.text_input("Año"),
        'titulo_capitulo': st.text_input("Título del capítulo"),
        'titulo_libro': st.text_input("Título del libro"),
        'ciudad': st.text_input("Ciudad"),
        'editorial': st.text_input("Editorial (ej: Editorial LexisNexis)"),
        'paginas': st.text_input("Páginas (ej. 101-146)")
    })
elif tipo == "Artículo de revista":
    datos.update({
        'año': st.text_input("Año"),
        'titulo': st.text_input("Título del artículo (sin cursivas)"),
        'revista': st.text_input("Nombre de la revista (saldrá en cursiva)"),
        'volumen': st.text_input("Volumen (opcional)"),
        'numero': st.text_input("Número (opcional)"),
        'paginas': st.text_input("Páginas (opcional)"),
        'doi': st.text_input("DOI (opcional)"),
        'url': st.text_input("URL (si es versión web)")
    })
elif tipo == "Norma":
    datos.update({
        'pais': st.text_input("País (ej: Chile)", value="Chile"),
        'tipo_norma': st.text_input("Tipo de norma (ej: Constitución Política de la República / Ley / Código / Decreto Supremo)"),
        'numero': st.text_input("Número (ej: 18.575, 21.171) — dejar vacío si no aplica"),
        'nombre_norma': st.text_input("Nombre o denominación legal (si aplica)"),
        'organismo': st.text_input("Ministerio u órgano (opcional, ej: Ministerio de Salud)"),
        'año': st.text_input("Año (opcional)")
    })
elif tipo == "Decreto / Oficio / Reglamento":
    datos.update({
        'pais': st.text_input("País (ej: Chile)", value="Chile"),
        'organismo': st.text_input("Ministerio u organismo (opcional, ej: Ministerio del Interior)"),
        'tipo': st.text_input("Tipo (ej: Decreto, Reglamento, Oficio, Circular)"),
        'numero': st.text_input("Número (ej: 1.234)"),
        'titulo': st.text_input("Título o descripción (en cursiva)"),
        'año': st.text_input("Año (opcional)")
    })
elif tipo == "Proyecto de ley":
    datos.update({
        'pais': st.text_input("País (ej: Chile)", value="Chile"),
        'nombre': st.text_input("Nombre del proyecto (en cursiva)"),
        'boletin': st.text_input("Boletín N° (ej: 12.345-04)"),
        'año': st.text_input("Año (opcional)")
    })
elif tipo == "Historia de la ley":
    datos.update({
        'pais': st.text_input("País (ej: Chile)", value="Chile"),
        'numero': st.text_input("Número de ley (ej: 21.400)"),
        'titulo': st.text_input("Título o descripción (opcional, en cursiva)"),
        'año': st.text_input("Año (opcional)")
    })
elif tipo == "Documento internacional (ONU, OEA, etc.)":
    datos.update({
        'organismo': st.text_input("Organismo internacional (ej: Organización de las Naciones Unidas)"),
        'titulo': st.text_input("Título del documento (en cursiva)"),
        'año': st.text_input("Año (opcional)")
    })
elif tipo == "Instrumento emanado de congreso / conferencia":
    datos.update({
        'nombre': st.text_input("Nombre del instrumento (en cursiva, ej: Declaración de Río sobre Medio Ambiente y Desarrollo)"),
        'conferencia': st.text_input("Congreso o conferencia (opcional, ej: Conferencia de las Naciones Unidas sobre Medio Ambiente y Desarrollo)"),
        'año': st.text_input("Año (opcional)")
    })
elif tipo == "Jurisprudencia":
    datos.update({
        'estado': st.text_input("Estado / País (opcional, ej: Chile)"),
        'tribunal': st.text_input("Tribunal (ej: Corte Suprema)"),
        'año': st.text_input("Año (opcional)"),
        'fecha': st.text_input("Fecha completa (opcional)"),
        'rol': st.text_input("Rol / RIT / RUC (opcional)"),
        'nombre_caso': st.text_input("Nombre del caso (opcional)"),
        'info_extra': st.text_input("Info extra (ej: 'protección', tomo, revista)"),
        'fuente': st.text_input("Fuente / base de datos / URL (opcional)")
    })
elif tipo == "Jurisprudencia internacional":
    datos.update({
        'tribunal': st.text_input("Tribunal internacional (ej: Corte Interamericana de DD.HH.)"),
        'nombre_caso': st.text_input("Nombre del caso (ej: Velásquez Rodríguez vs. Honduras)"),
        'fecha': st.text_input("Fecha (opcional)"),
        'serie': st.text_input("Serie / número (opcional)")
    })
elif tipo == "Página web o blog":
    if num_autores == 0:
        datos['autor_sin_autor'] = st.text_input("Autor o entidad (si no hay autores) — ej: TRIBUNAL CONSTITUCIONAL")
    datos.update({
        'año': st.text_input("Año (o año del sitio, si aplica)"),
        'titulo': st.text_input("Título de la página / entrada"),
        'url': st.text_input("URL"),
        'fecha_consulta': st.text_input("Fecha de consulta (opcional)")
    })
elif tipo == "Documento internacional (ONU, OEA, etc.)":
    pass  # ya cubierto arriba
elif tipo == "Instrumento emanado de congreso / conferencia":
    pass
elif tipo == "Tesis":
    datos.update({
        'año': st.text_input("Año"),
        'titulo': st.text_input("Título"),
        'grado': st.text_input("Grado (ej: Licenciado)"),
        'institucion': st.text_input("Institución (ej: Facultad de Leyes y Ciencias Políticas de la Universidad de Chile)"),
        'paginas': st.text_input("Páginas (opcional para abreviada)")
    })

# ---------------- Generación ----------------
if st.button("Generar cita"):
    gen = TIPOS[tipo](datos, config)
    ref_html = ""
    cita_texto = ""
    ref_texto = ""
    # Algunas funciones devuelven (ref, abreviada)
    if tipo in ["Norma", "Decreto / Oficio / Reglamento", "Proyecto de ley", "Historia de la ley",
                "Documento internacional (ONU, OEA, etc.)", "Instrumento emanado de congreso / conferencia",
                "Jurisprudencia", "Jurisprudencia internacional", "Página web o blog"]:
        # TIPOS devuelve una tupla (ref, abre)
        ref_html, abre = gen
        cita_texto = abre
        ref_texto = limpiar_html(ref_html)
    else:
        ref_html = gen
        cita_texto = cita_abreviada(
            autores,
            datos.get('año',''),
            paginas=datos.get('paginas', ''),
            tomo=datos.get('tomo',''),
            tipo=tipo,
            libro_y_otros=libro_y_otros,
            y_otros_threshold=config['y_otros_threshold']
        )
        if not cita_texto and tipo in ["Tesis", "Artículo de revista", "Capítulo de libro", "Libro", "Traducción de libro"]:
            cita_texto = cita_abreviada(autores, datos.get('año',''), paginas=datos.get('paginas',''),
                                        tomo=datos.get('tomo',''), tipo=tipo,
                                        libro_y_otros=libro_y_otros, y_otros_threshold=config['y_otros_threshold'])
        ref_texto = limpiar_html(ref_html)

    st.session_state.historial_citas.append({
        "tipo": tipo,
        "referencia": ref_texto,
        "cita": cita_texto
    })

    st.subheader("Referencia completa:")
    st.markdown(ref_html, unsafe_allow_html=True)
    st.text_area("Copiar referencia completa:", value=ref_texto, height=120)

    st.subheader("Cita abreviada (para nota al pie):")
    st.write(cita_texto)
    st.text_area("Copiar cita abreviada:", value=cita_texto, height=60)

# ---------------- Mostrar historial (corregido y estable) ----------------
if "historial_citas" in st.session_state and len(st.session_state.historial_citas) > 0:
    st.subheader("Historial de citas generadas:")

    # Asignamos un ID único a cada cita para evitar que los widgets se confundan
    for idx, item in enumerate(reversed(st.session_state.historial_citas)):
        unique_id = f"{idx}_{hash(item['referencia']) % 10000}"

        with st.expander(f"{len(st.session_state.historial_citas) - idx}. {item['tipo']}"):
            st.markdown("**Referencia completa:**")
            st.text_area(
                "Referencia",
                value=item['referencia'],
                height=80,
                key=f"hist_ref_{unique_id}",
                label_visibility="collapsed"
            )

            st.markdown("**Cita abreviada:**")
            st.text_area(
                "Cita abreviada",
                value=item['cita'],
                height=50,
                key=f"hist_cit_{unique_id}",
                label_visibility="collapsed"
            )

if st.button("🧹 Limpiar historial"):
    st.session_state.historial_citas.clear()
    st.experimental_rerun()

