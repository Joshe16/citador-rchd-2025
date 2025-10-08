# app_citador_rchd.py
import streamlit as st
import re
from datetime import datetime

# ---------------- Helpers ----------------
def versalitas(texto):
    return texto.upper() if texto else ""

def smallcaps_html(texto):
    # preferible: mostrar en small-caps para HTML; el texto ya será uppercase
    return f"<span style='font-variant: small-caps'>{versalitas(texto)}</span>"

def limpiar_html(html_text):
    return re.sub('<.*?>', '', html_text)

def to_roman(num):
    # conv entero (1-3999) a romano, si falla devuelve original
    try:
        n = int(num)
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
        return r(num)

# ordinal (es) para ediciones simples
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
    try:
        n = int(ed)
        if n == 1:
            return ""  # no escribir "1 edición"
        return f"{_ORDINAL_ES.get(n, r(n)+'ª')} edición"
    except Exception:
        # si el usuario escribió "segunda" o "2ª", intentar normalizar
        ed_lower = ed.rip().lower()
        if "ed" in ed_lower or "edición" in ed_lower or "ª" in ed_lower:
            return ed.rip()
        return f"{ed.strip()} edición"

def pages_prefix(pags):
    if not pags:
        return ""
    pags = pags.strip()
    # determinar si es rango
    if "-" in pags or "–" in pags:
        return f"pp. {pags}"
    else:
        return f"p. {pags}"

def normalize_date(date_str):
    if not date_str:
        return ""
    d = date_str.strip()
    # try several formats
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
    # if numeric-only and 8 chars like 11081980 -> try ddmmyyyy
    if re.fullmatch(r"\d{8}", d):
        try:
            dt = datetime.strptime(d, "%d%m%Y")
            return dt.strftime("%d/%m/%Y")
        except Exception:
            pass
    # fallback: return original but warn later
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
        apellidos_html = f"{smallcaps_html(apellidos)}"
        return f"{apellidos_html}, {nom}"
    else:
        return f"{apellidos}, {nom}"

def formatear_autores(autores, html=False, y_otros_threshold=4):
    # autores: lista de dicts {'apellido1','apellido2','nombre'}
    autores = [a for a in autores if (a.get('apellido1') or a.get('nombre'))]
    n = len(autores)
    if n == 0:
        return ""
    def formato(a):
        return formatear_autor(a, html=html)
    # Norma RChD: si 4 o más autores -> primer autor y otros
    if n >= y_otros_threshold:
        return f"{formato(autores[0])} y otros" if not html else f"{formato(autores[0])} y otros"
    if n == 1:
        return formato(autores[0])
    elif 2 <= n <= 3:
        # separar por "y" para el último
        parts = [formato(a) for a in autores]
        return " y ".join(parts)
    else:
        return f"{formato(autores[0])} y otros"

# ---------------- Cita abreviada ----------------
def cita_abreviada(autores, año, paginas=None, tomo=None, tipo=None, libro_y_otros=False, y_otros_threshold=4):
    autores = [a for a in autores if (a.get('apellido1') or a.get('nombre'))]
    n = len(autores)
    tomo_part = f" Tomo {to_roman(tomo)}" if tomo and tomo.isdigit() else (f" {tomo}" if tomo else "")
    pag_part = ""
    if paginas:
        pag_part = f", {pages_prefix(paginas)}"
    if tipo == "Norma":
        # abreviada: CHILE, Ley 18.575; o CHILE, Constitución Política de la República
        # This is handled elsewhere; return empty to be filled by norma-specific routine
        return ""
    if tipo == "Jurisprudencia":
        # show tribunal and date or case name — handled in jurisprudencia-specific routine
        return ""
    if n == 0:
        return ""
    # libros, teses, articulos
    if libro_y_otros or (n >= y_otros_threshold):
        apellido = versalitas(autores[0].get('apellido1',''))
        return f"{apellido} y otros ({año}){tomo_part}{pag_part}"
    if n == 1:
        apellido = versalitas(autores[0].get('apellido1',''))
        return f"{apellido} ({año}){tomo_part}{pag_part}"
    elif 2 <= n <= 3:
        apellidos = " y ".join([versalitas(a.get('apellido1','')) for a in autores])
        return f"{apellidos} ({año}){pag_part}"
    else:
        apellido = versalitas(autores[0].get('apellido1',''))
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

    tomo_str = ""
    if tomo:
        tomo_str = f", Tomo {to_roman(tomo)}" if tomo.isdigit() else f", {tomo}"

    ed_str = ""
    if edicion:
        if edicion.isdigit():
            e = edicion_spanish(edicion)
            if e:
                ed_str = f", {e}"
        else:
            ed_str = f", {edicion}" if "ed" in edicion.lower() or "edición" in edicion.lower() else f", {edicion} edición"

    parent_parts = []
    if ciudad:
        parent_parts.append(ciudad)
    if editorial:
        parent_parts.append(editorial)
    if ed_str:
        # ed_str includes leading comma, strip it
        parent_parts.append(ed_str.lstrip(', ').strip())

    ciudad_str = f" ({', '.join(parent_parts)})" if parent_parts else ""
    ref = f"{autores_html} ({año}): {titulo_html}{tomo_str}{ciudad_str}."
    return ref

def traduccion_libro(datos, y_otros_threshold=4):
    autores_html = formatear_autores(datos.get('autores', []), html=True, y_otros_threshold=y_otros_threshold)
    titulo_html = f"<i>{datos.get('titulo','')}</i>"
    año_original = datos.get('año_original','').strip()
    año = datos.get('año','').strip()
    traductor = datos.get('traductor','').strip()
    ciudad = datos.get('ciudad','').strip()
    editorial = datos.get('editorial','').strip()
    anos = ""
    if año_original:
        anos = f"[{año_original}] {año}"
    else:
        anos = año
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
    # ejemplo RChD: AUTOR (1998): “Título del capítulo”, en EDITOR (edit.), TÍTULO LIBRO (Ciudad, Editorial) pp. 101-146.
    ref = f"{autor_html} ({año}): \"{titulo_cap}\", en {editores_html} (edit.), {titulo_libro_html} ({ciudad}, {editorial}){paginas_part}."
    return ref

def articulo_revista(datos, y_otros_threshold=4):
    autores_html = formatear_autores(datos.get('autores', []), html=True, y_otros_threshold=y_otros_threshold)
    titulo_art = datos.get('titulo','').strip()  # article title NOT italic
    revista_html = f"<i>{datos.get('revista','')}</i>" if datos.get('revista') else ""
    año = datos.get('año','').strip()
    volumen = datos.get('volumen','').strip()
    numero = datos.get('numero','').strip()
    paginas = datos.get('paginas','').strip()
    doi = datos.get('doi','').strip()
    ref = f"{autores_html} ({año}): \"{titulo_art}\", {revista_html}"
    if volumen:
        ref += f", vol. {volumen}"
    if numero:
        ref += f", N° {numero}"
    if paginas:
        ref += f": pp. {paginas}"
    if doi:
        ref += f". DOI: {doi}"
    return ref + "."

def norma(datos):
    pais = versalitas(datos.get('pais','CHILE'))
    tipo_norma = datos.get('tipo_norma','').strip()
    nombre = datos.get('nombre_norma','').strip()
    numero = datos.get('numero','').strip()
    organismo = datos.get('organismo','').strip()
    fecha_raw = datos.get('fecha','').strip()
    fecha = normalize_date(fecha_raw) if fecha_raw else ""
    # construir referencia completa y abreviada (abreviada sin fecha)
    if "constit" in tipo_norma.lower() or "constitución" in nombre.lower() or "constitución" in tipo_norma.lower():
        # Constitución
        referencia = f"{pais}, <i>{nombre if nombre else 'Constitución Política de la República'}</i>"
        referencia += f" ({fecha})" if fecha else ""
        abreviada = f"{pais}, {nombre if nombre else 'Constitución Política de la República'}"
        return referencia + ".", abreviada
    if "ley" in tipo_norma.lower() or tipo_norma.lower().startswith("ley") or (numero and numero.isdigit()):
        # Ley: CHILE, Ley N° 21.171. Nombre en cursiva (si existe). (dd/mm/yyyy)
        num_part = f"Ley N° {numero}" if numero else "Ley"
        referencia = f"{pais}, {num_part}"
        if nombre:
            referencia += f". <i>{nombre}</i>"
        referencia += f" ({fecha})" if fecha else ""
        abreviada = f"{pais}, {num_part}"
        return referencia + ".", abreviada
    # Decretos Supremos: permitir organismo
    if "decreto" in tipo_norma.lower() and "supremo" in tipo_norma.lower() or "decreto supremo" in tipo_norma.lower():
        organismo_part = f", {versalitas(organismo)}" if organismo else ""
        num_part = f"Decreto Supremo {numero}" if numero else "Decreto Supremo"
        referencia = f"{pais}{organismo_part}, {num_part}"
        if nombre:
            referencia += f", <i>{nombre}</i>"
        referencia += f" ({fecha})" if fecha else ""
        abreviada = f"{pais}, {num_part}"
        return referencia + ".", abreviada
    # Código
    if "código" in tipo_norma.lower() or "código" in nombre.lower():
        referencia = f"{pais}, <i>{nombre if nombre else tipo_norma}</i>"
        referencia += f" ({fecha})" if fecha else " (s.d.)"
        abreviada = f"{pais}, {nombre if nombre else tipo_norma}"
        return referencia + ".", abreviada
    # fallback general
    referencia = f"{pais}, {tipo_norma if tipo_norma else nombre}"
    if numero:
        referencia += f" {numero}"
    if nombre and tipo_norma:
        referencia += f". <i>{nombre}</i>"
    referencia += f" ({fecha})" if fecha else ""
    abreviada = f"{pais}, {tipo_norma if tipo_norma else nombre}"
    return referencia + ".", abreviada

def jurisprudencia(datos):
    estado = datos.get('estado','').strip()
    tribunal = datos.get('tribunal','').strip()
    fecha_raw = datos.get('fecha','').strip()
    fecha = normalize_date(fecha_raw) if fecha_raw else ""
    rol = datos.get('rol','').strip()
    nombre_caso = datos.get('nombre_caso','').strip()
    info_extra = datos.get('info_extra','').strip()
    fuente = datos.get('fuente','').strip()

    inicio = f"{versalitas(estado)}, " if estado else ""
    inicio += f"{tribunal}" if tribunal else ""
    ref = inicio
    if fecha:
        if ref:
            ref += f", {fecha}"
        else:
            ref = fecha
    if rol:
        ref += f", rol {rol}"
    if nombre_caso:
        ref += f" ({nombre_caso})"
    if info_extra:
        ref += f", {info_extra}"
    if fuente:
        ref += f". Fuente: {fuente}"
    # abreviada: tribunal, fecha (sin rol ni tipo)
    abre = f"{tribunal}, {fecha}" if tribunal and fecha else (tribunal or fecha)
    return ref + ".", abre

def web(datos):
    autores = datos.get('autores', [])
    autor_sin = datos.get('autor_sin_autor','').strip()
    año = datos.get('año','').strip()
    titulo = datos.get('titulo','').strip()
    url = datos.get('url','').strip()
    fecha_consulta_raw = datos.get('fecha_consulta','').strip()
    fecha_consulta = normalize_date(fecha_consulta_raw) if fecha_consulta_raw else ""
    if autores:
        autor_text = formatear_autores(autores, html=False)
    else:
        autor_text = autor_sin if autor_sin else ""
    ref = f"{autor_text} ({año}): {titulo}, Disponible en: {url}."
    if fecha_consulta:
        ref += f" Fecha de consulta: {fecha_consulta}."
    # abreviada: AUTOR (AÑO) o SITIO (AÑO)
    abre = f"{versalitas(autor_text) if autor_text else autor_sin} ({año})" if año else (versalitas(autor_text) or autor_sin)
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
    "Jurisprudencia": lambda d, config: jurisprudencia(d),
    "Página web o blog": lambda d, config: web(d),
    "Tesis": lambda d, config: tesis(d, y_otros_threshold=config['y_otros_threshold'])
}

# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="Citador RChD Consejeria Academica Derecho UC x >> Avanzar", layout="wide")
st.title("Citador RChD Consejeria Academica Derecho UC x >> Avanzar (RChD 2025)")
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

# Helper to add authors with keys unique
def agregar_autores_ui(num, prefix="", show_help=True):
    autores = []
    for i in range(num):
        st.markdown(f"**Autor {i+1}**")
        apellido1 = st.text_input(f"Primer apellido", key=f"{prefix}ape1_{i}", placeholder=("Primer apellido o nombre del sitio para webs" if show_help else ""))
        apellido2 = st.text_input(f"Segundo apellido (opcional)", key=f"{prefix}ape2_{i}")
        nombre = st.text_input(f"Nombre", key=f"{prefix}nom_{i}", placeholder=("Si es persona: Nombre(s). Si es entidad: dejar vacío y usar campo 'Autor/Entidad' en webs" if show_help else ""))
        autores.append({'apellido1': apellido1.strip(), 'apellido2': apellido2.strip(), 'nombre': nombre.strip()})
    return autores

# Ajuste para libros con N autores -> solo pedir 1 si umbral se alcanza
libro_y_otros = False
autores = []
if tipo == "Libro" and num_autores >= config['y_otros_threshold']:
    st.info(f"Se detectaron {num_autores} autores (umbral {config['y_otros_threshold']}): solo se pedirá el primer autor y se agregará 'y otros' en la referencia.")
    autores = agregar_autores_ui(1, show_help=show_help)
    libro_y_otros = True
else:
    autores = agregar_autores_ui(num_autores, show_help=show_help) if num_autores > 0 else []

datos = {'autores': autores}

# Inputs dinámicos por tipo
if tipo == "Libro":
    datos.update({
        'año': st.text_input("Año de publicación"),
        'titulo': st.text_input("Título del libro"),
        'ciudad': st.text_input("Ciudad de publicación (opcional)"),
        'editorial': st.text_input("Editorial (ej: Editorial LexisNexis)"),
        'edicion': st.text_input("Número de edición (opcional, p.ej. 2)"),
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
        'fecha': st.text_input("Fecha (opcional) - formato recomendado dd/mm/aaaa")
    })
elif tipo == "Jurisprudencia":
    datos.update({
        'estado': st.text_input("Estado / País (opcional, ej: Chile)"),
        'tribunal': st.text_input("Tribunal (ej: Corte Suprema)"),
        'fecha': st.text_input("Fecha (ej: 23/03/2021)"),
        'rol': st.text_input("Rol / RIT / RUC (opcional)"),
        'nombre_caso': st.text_input("Nombre del caso (opcional)"),
        'info_extra': st.text_input("Info extra (ej: 'protección', tomo, revista)"),
        'fuente': st.text_input("Fuente / base de datos / URL (opcional)")
    })
elif tipo == "Página web o blog":
    if num_autores == 0:
        datos['autor_sin_autor'] = st.text_input("Autor o entidad (si no hay autores) — ej: TRIBUNAL CONSTITUCIONAL")
    datos.update({
        'año': st.text_input("Año (o año del sitio, si aplica)"),
        'titulo': st.text_input("Título de la página / entrada"),
        'url': st.text_input("URL"),
        'fecha_consulta': st.text_input("Fecha de consulta (opcional) - dd/mm/aaaa")
    })
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
    # generar referencia HTML (para mostrar con cursivas/versalitas) y versión texto limpia
    gen = TIPOS[tipo](datos, config)
    # algunas funciones (norma, web, jurisprudencia) devuelven tuplas (referencia, abreviada)
    ref_html = ""
    cita_texto = ""
    ref_texto = ""
    if tipo == "Norma":
        ref_html, abre = gen
        # abre viene sin HTML
        cita_texto = abre
        ref_texto = limpiar_html(ref_html)
    elif tipo == "Página web o blog":
        ref, abre = gen
        ref_html = ref
        cita_texto = abre
        ref_texto = limpiar_html(ref_html)
    elif tipo == "Jurisprudencia":
        ref, abre = gen
        ref_html = ref
        cita_texto = abre
        ref_texto = limpiar_html(ref_html)
    else:
        ref_html = gen
        # crear cita abreviada para tipos bibliográficos
        cita_texto = cita_abreviada(
            autores,
            datos.get('año',''),
            paginas=datos.get('paginas', ''),
            tomo=datos.get('tomo',''),
            tipo=tipo,
            libro_y_otros=libro_y_otros,
            y_otros_threshold=config['y_otros_threshold']
        )
        # En caso de que cita_abreviada no haya devuelto nada (p.ej. web/norma) genera basado en reglas simples
        if not cita_texto and tipo in ["Tesis", "Artículo de revista", "Capítulo de libro", "Libro", "Traducción de libro"]:
            cita_texto = cita_abreviada(autores, datos.get('año',''), paginas=datos.get('paginas',''),
                                        tomo=datos.get('tomo',''), tipo=tipo,
                                        libro_y_otros=libro_y_otros, y_otros_threshold=config['y_otros_threshold'])
        ref_texto = limpiar_html(ref_html)

    # guardar en historial
    st.session_state.historial_citas.append({
        "tipo": tipo,
        "referencia": ref_texto,
        "cita": cita_texto
    })

    # Mostrar resultados
    st.subheader("Referencia completa:")
    st.markdown(ref_html, unsafe_allow_html=True)
    st.text_area("Copiar referencia completa:", value=ref_texto, height=120)

    st.subheader("Cita abreviada (para nota al pie):")
    st.write(cita_texto)
    st.text_area("Copiar cita abreviada:", value=cita_texto, height=60)

# ---------------- Mostrar historial ----------------
if st.session_state.historial_citas:
    st.subheader("Historial de citas generadas:")
    for i, item in enumerate(reversed(st.session_state.historial_citas), 1):
        st.markdown(f"**{i}. {item['tipo']}**")
        st.text_area("Referencia:", value=item['referencia'], height=60, key=f"hist_ref_{i}")
        st.text_area("Cita abreviada:", value=item['cita'], height=40, key=f"hist_cit_{i}")



