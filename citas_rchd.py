import streamlit as st
import re

# ---------- Funciones de formato ----------
def versalitas(texto):
    return texto.upper() if texto else ""

def formatear_autores(autores, html=False, libro=False):
    n = len(autores)
    if n == 0:
        return ""
    
    def formato(a):
        ap = versalitas(a['apellido1'])
        if a.get('apellido2'):
            ap += f" {versalitas(a['apellido2'])}"
        return f"{ap}, {a['nombre']}" if not html else f"<span style='font-variant: small-caps'>{ap}</span>, {a['nombre']}"
    
    # Si es libro y hay 3 o más autores, mostrar solo el primero + "y otros"
    if libro and n >= 3:
        return f"{formato(autores[0])} y otros"
    
    # Si no es libro, mantener la lógica normal
    if n == 1:
        return formato(autores[0])
    elif 2 <= n <= 3:
        return " y ".join([formato(a) for a in autores])
    else:
        return f"{formato(autores[0])} y otros"

def formatear_titulo(titulo):
    return f"<i>{titulo}</i>"

def cita_abreviada(autores, año, paginas=None, tomo=None, libro=False):
    n = len(autores)
    tomo_str = f", tomo {tomo}" if tomo else ""
    paginas_str = f", p. {paginas}" if paginas else ""
    
    if libro and n >= 3:
        return f"{versalitas(autores[0]['apellido1'])} y otros ({año}){tomo_str}{paginas_str}"
    
    if n == 0:
        return ""
    elif n == 1:
        return f"{versalitas(autores[0]['apellido1'])} ({año}){tomo_str}{paginas_str}"
    elif 2 <= n <= 3:
        return f"{' y '.join([versalitas(a['apellido1']) for a in autores])} ({año}){paginas_str}"
    else:
        return f"{versalitas(autores[0]['apellido1'])} y otros ({año}){paginas_str}"

def limpiar_html(html_text):
    return re.sub('<.*?>', '', html_text)

def agregar_autores(num, prefix=""):
    autores = []
    for i in range(num):
        st.markdown(f"**Autor {i+1}**")
        apellido1 = st.text_input(f"Primer apellido", key=f"{prefix}ape1_{i}")
        apellido2 = st.text_input(f"Segundo apellido (opcional)", key=f"{prefix}ape2_{i}")
        nombre = st.text_input(f"Nombre", key=f"{prefix}nom_{i}")
        autores.append({'apellido1': apellido1.strip(), 'apellido2': apellido2.strip(), 'nombre': nombre.strip()})
    return autores

# ---------- Funciones generadoras ----------
def libro(datos):
    autores_html = formatear_autores(datos['autores'], libro=True)
    titulo_html = formatear_titulo(datos['titulo'])
    ciudad = datos.get('ciudad')
    editorial = datos.get('editorial')
    edicion = datos.get('edicion')
    tomo = datos.get('tomo')
    ed_str = f", {edicion}" if edicion and edicion != "1" else ""
    tomo_str = f", {tomo}" if tomo else ""
    ciudad_str = f" ({ciudad}, {editorial}{ed_str})" if ciudad or editorial else ""
    return f"{autores_html} ({datos['año']}): {titulo_html}{tomo_str}{ciudad_str}."

def traduccion_libro(datos):
    autores_html = formatear_autores(datos['autores'], html=True)
    titulo_html = formatear_titulo(datos['titulo'])
    return f"{autores_html} ([{datos['año_original']}] {datos['año']}): {titulo_html} (trad. {datos['traductor']}, {datos['ciudad']}, {datos['editorial']})."

def capitulo_libro(datos):
    autor_html = formatear_autores(datos['autor_capitulo'], html=True)
    editores_html = formatear_autores(datos['editores'], html=True)
    titulo_cap_html = formatear_titulo(datos['titulo_capitulo'])
    titulo_libro_html = formatear_titulo(datos['titulo_libro'])
    return f"{autor_html} ({datos['año']}): “{titulo_cap_html}”, en {editores_html} (edit.), {titulo_libro_html} ({datos['ciudad']}, {datos['editorial']}) pp. {datos['paginas']}."

def articulo_revista(datos):
    autores_html = formatear_autores(datos['autores'], html=True)
    titulo_html = formatear_titulo(datos['titulo'])
    ref = f"{autores_html} ({datos['año']}): “{titulo_html}”, {datos['revista']}"
    if datos.get('volumen'):
        ref += f", vol. {datos['volumen']}"
    if datos.get('numero'):
        ref += f", Nº {datos['numero']}"
    if datos.get('paginas'):
        ref += f": pp. {datos['paginas']}"
    if datos.get('doi'):
        ref += f". DOI: {datos['doi']}"
    return ref + "."

def norma(datos):
    pais = versalitas(datos['pais'])
    fecha = f" ({datos['fecha']})" if datos.get('fecha') else ""
    return f"{pais}, {datos['tipo_norma']} {datos['nombre_norma']}{fecha}."

def jurisprudencia(datos):
    tribunal = versalitas(datos['tribunal'])
    ref = f"{tribunal}, {datos['fecha']}"
    if datos.get('rol'):
        ref += f", rol {datos['rol']}"
    if datos.get('nombre_caso'):
        ref += f" ({datos['nombre_caso']})"
    if datos.get('info_extra'):
        ref += f", {datos['info_extra']}"
    return ref + "."

def web(datos):
    autor = formatear_autores(datos.get('autores', [])) if datos.get('autores') else datos.get('autor_sin_autor', '')
    ref = f"{autor} ({datos.get('año')}): {datos['titulo']}, Disponible en: {datos['url']}."
    if datos.get('fecha_consulta'):
        ref += f" Fecha de consulta: {datos['fecha_consulta']}."
    return ref

def tesis(datos):
    autor = formatear_autores(datos['autores'], html=True)
    titulo_html = formatear_titulo(datos['titulo'])
    return f"{autor} ({datos['año']}): {titulo_html}. {datos['grado']}. {datos['institucion']}."

# ---------- Diccionario ----------
TIPOS = {
    "Libro": libro,
    "Traducción de libro": traduccion_libro,
    "Capítulo de libro": capitulo_libro,
    "Artículo de revista": articulo_revista,
    "Norma": norma,
    "Jurisprudencia": jurisprudencia,
    "Página web o blog": web,
    "Tesis": tesis
}

# ---------- Streamlit ----------
st.title("Citador RChD Compacto")

tipo = st.selectbox("Tipo de fuente", list(TIPOS.keys()))
num_autores = st.number_input("Número de autores", min_value=0, max_value=10, value=1)

# Historial de citas en sesión
if "historial_citas" not in st.session_state:
    st.session_state["historial_citas"] = []

# Ajuste para libros con ≥3 autores
libro_y_otros = False
if tipo == "Libro" and num_autores >= 3:
    st.info("Se detectaron 3 o más autores: solo se pedirá el primer autor y se agregará 'y otros'.")
    autores = agregar_autores(1)
    libro_y_otros = True
else:
    autores = agregar_autores(num_autores) if num_autores > 0 else []

# ---------- Inputs dinámicos ----------
datos = {'autores': autores}

if tipo == "Libro":
    datos.update({
        'año': st.text_input("Año de publicación"),
        'titulo': st.text_input("Título del libro"),
        'ciudad': st.text_input("Ciudad de publicación (opcional)"),
        'editorial': st.text_input("Editorial (ej: Editorial LexisNexis)"),
        'edicion': st.text_input("Número de edición (opcional)"),
        'tomo': st.text_input("Tomo o volumen (opcional)"),
        'paginas': st.text_input("Páginas (opcional para cita abreviada)")
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
    datos['autor_capitulo'] = agregar_autores(num_aut_cap)
    num_editores = st.number_input("Número de editores", 1, 10, 1)
    datos['editores'] = agregar_autores(num_editores, prefix="edit_")
    datos.update({
        'año': st.text_input("Año"),
        'titulo_capitulo': st.text_input("Título del capítulo"),
        'titulo_libro': st.text_input("Título del libro"),
        'ciudad': st.text_input("Ciudad"),
        'editorial': st.text_input("Editorial (ej: Editorial LexisNexis)"),
        'paginas': st.text_input("Páginas")
    })
elif tipo == "Artículo de revista":
    datos.update({
        'año': st.text_input("Año"),
        'titulo': st.text_input("Título"),
        'revista': st.text_input("Revista"),
        'volumen': st.text_input("Volumen (opcional)"),
        'numero': st.text_input("Número (opcional)"),
        'paginas': st.text_input("Páginas (opcional)"),
        'doi': st.text_input("DOI (opcional)")
    })
elif tipo == "Norma":
    datos.update({
        'pais': st.text_input("País"),
        'tipo_norma': st.text_input("Tipo de norma"),
        'nombre_norma': st.text_input("Nombre/numero"),
        'fecha': st.text_input("Fecha (opcional)")
    })
elif tipo == "Jurisprudencia":
    datos.update({
        'tribunal': st.text_input("Tribunal"),
        'fecha': st.text_input("Fecha"),
        'rol': st.text_input("Rol (opcional)"),
        'nombre_caso': st.text_input("Nombre caso (opcional)"),
        'info_extra': st.text_input("Info extra (opcional)")
    })
elif tipo == "Página web o blog":
    if num_autores == 0:
        datos['autor_sin_autor'] = st.text_input("Autor o entidad (si no hay autores)")
    datos.update({
        'año': st.text_input("Año"),
        'titulo': st.text_input("Título"),
        'url': st.text_input("URL"),
        'fecha_consulta': st.text_input("Fecha de consulta (opcional)")
    })
elif tipo == "Tesis":
    datos.update({
        'año': st.text_input("Año"),
        'titulo': st.text_input("Título"),
        'grado': st.text_input("Grado"),
        'institucion': st.text_input("Institución")
    })

# ---------- Generación ----------
if st.button("Generar cita"):
    ref_html = TIPOS[tipo](datos)
    cita_texto = cita_abreviada(
        autores,
        datos.get('año'),
        paginas=datos.get('paginas'),
        tomo=datos.get('tomo'),
        libro=libro_y_otros
    ) if tipo in ["Libro", "Traducción de libro", "Capítulo de libro", "Artículo de revista", "Tesis"] else limpiar_html(ref_html)
    ref_texto = limpiar_html(ref_html)

    # Guardar en historial
    st.session_state.historial_citas.append({
        "tipo": tipo,
        "referencia": ref_texto,
        "cita": cita_texto
    })

    st.subheader("Referencia completa:")
    st.markdown(ref_html, unsafe_allow_html=True)
    st.text_area("Copiar referencia completa:", value=ref_texto, height=80)

    st.subheader("Cita abreviada:")
    st.write(cita_texto)
    st.text_area("Copiar cita abreviada:", value=cita_texto, height=40)

# ---------- Mostrar historial ----------
if st.session_state.historial_citas:
    st.subheader("Historial de citas generadas:")
    for i, item in enumerate(reversed(st.session_state.historial_citas), 1):
        st.markdown(f"**{i}. {item['tipo']}**")
        st.text_area("Referencia:", value=item['referencia'], height=60, key=f"hist_ref_{i}")
        st.text_area("Cita abreviada:", value=item['cita'], height=40, key=f"hist_cit_{i}")



