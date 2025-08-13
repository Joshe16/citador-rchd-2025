import streamlit as st
import re

# ------------------ UTILIDADES DE FORMATO ------------------
def versalitas(texto):
    return texto.upper() if texto else ""

def italics(texto):
    return f"<i>{texto}</i>" if texto else ""

def limpiar_html_a_texto(html):
    text = re.sub(r'<.*?>', '', html)
    return text.strip()

def formatear_autores_html(autores):
    """Devuelve string HTML para la referencia completa"""
    n = len(autores)
    if n == 0:
        return ""
    def formato(a):
        ap = versalitas(a['apellido1'])
        if a['apellido2']:
            ap += f" {versalitas(a['apellido2'])}"
        return f"{ap}, {a['nombre']}"
    if n == 1:
        return formato(autores[0])
    elif 2 <= n <= 3:
        return " y ".join(formato(a) for a in autores)
    else:
        return f"{formato(autores[0])} y otros"

def cita_abreviada(autores, año, paginas=None):
    """Devuelve la cita abreviada según número de autores"""
    n = len(autores)
    if n == 0:
        return f"({año})"
    elif n == 1:
        return f"{versalitas(autores[0]['apellido1'])} ({año})" + (f", p. {paginas}" if paginas else "")
    elif 2 <= n <= 3:
        aps = " y ".join([versalitas(a['apellido1']) for a in autores])
        return f"{aps} ({año})" + (f", p. {paginas}" if paginas else "")
    else:
        return f"{versalitas(autores[0]['apellido1'])} y otros ({año})" + (f", p. {paginas}" if paginas else "")

# ------------------ PLANTILLAS ------------------
PLANTILLAS = {
    "Libro": "{autor} ({año}): {titulo} ({lugar}, {editorial}{edicion}).",
    "Traducción de libro": "{autor} ([{año_original}] {año}): {titulo} (trad. {traductor}, {lugar}, {editorial}).",
    "Capítulo de libro": "{autor} ({año}): {titulo_cap}, en {editor} (edit.), {titulo_libro} ({lugar}, {editorial}) pp. {paginas}.",
    "Artículo de revista": "{autor} ({año}): {titulo_art}, {revista}, vol. {volumen}, Nº {numero}: pp. {paginas}.",
    "Norma": "{pais}, {tipo_norma} {nombre_norma}{fecha}.",
    "Jurisprudencia": "{tribunal}, {fecha}{rol}{nombre_caso}{info_extra}.",
    "Página web o blog": "{autor} ({año}): {titulo}. Disponible en: {url}. Fecha de consulta: {fecha}.",
    "Tesis": "{autor} ({año}): {titulo}. {grado}. {institucion}."
}

# ------------------ CAMPOS POR TIPO ------------------
CAMPOS = {
    "Libro": ["titulo", "año", "lugar", "editorial", "edicion"],
    "Traducción de libro": ["titulo", "año_original", "año", "traductor", "lugar", "editorial"],
    "Capítulo de libro": ["titulo_cap", "año", "editor", "titulo_libro", "lugar", "editorial", "paginas"],
    "Artículo de revista": ["titulo_art", "año", "revista", "volumen", "numero", "paginas"],
    "Norma": ["pais", "tipo_norma", "nombre_norma", "fecha"],
    "Jurisprudencia": ["tribunal", "fecha", "rol", "nombre_caso", "info_extra"],
    "Página web o blog": ["titulo", "año", "url", "fecha"],
    "Tesis": ["titulo", "año", "grado", "institucion"]
}

# ------------------ APP STREAMLIT ------------------
st.title("📚 Citador - Revista Chilena de Derecho")

tipo = st.selectbox("Selecciona el tipo de cita", list(PLANTILLAS.keys()))

# Autores
st.subheader("Autores")
num_autores = st.number_input("Número de autores", min_value=0, max_value=10, value=1)
autores = []
for i in range(num_autores):
    st.markdown(f"**Autor {i+1}**")
    apellido1 = st.text_input(f"Primer apellido", key=f"ape1_{i}")
    apellido2 = st.text_input(f"Segundo apellido (opcional)", key=f"ape2_{i}")
    nombre = st.text_input(f"Nombre", key=f"nom_{i}")
    autores.append({'apellido1': apellido1.strip(), 'apellido2': apellido2.strip(), 'nombre': nombre.strip()})

# Otros campos
st.subheader("Datos de la referencia")
datos = {}
for campo in CAMPOS[tipo]:
    datos[campo] = st.text_input(campo.capitalize())

paginas_cita = st.text_input("Número de página para cita abreviada (opcional)")

if st.button("Generar cita"):
    plantilla = PLANTILLAS[tipo]

    # Autor en HTML
    autor_html = formatear_autores_html(autores)

    # Aplicar italics a títulos y revistas
    datos_formateados = {k: italics(v) if "titulo" in k or "revista" in k else v for k,v in datos.items()}
    datos_formateados['autor'] = autor_html

    cita_html = plantilla.format(**datos_formateados)
    cita_texto = limpiar_html_a_texto(cita_html)

    # Cita abreviada
    cita_abrev = cita_abreviada(autores, datos.get("año",""), paginas=paginas_cita if paginas_cita else None)

    st.markdown("### Vista previa (con formato)")
    st.markdown(cita_html, unsafe_allow_html=True)

    st.markdown("### Cita abreviada")
    st.write(cita_abrev)

    # Historial
    if "historial" not in st.session_state:
        st.session_state.historial = []
    st.session_state.historial.append((cita_html, cita_abrev))

# Mostrar historial
if "historial" in st.session_state and st.session_state.historial:
    st.subheader("Historial de citas")
    for idx, (cita_full, cita_abrev) in enumerate(reversed(st.session_state.historial)):
        st.markdown(f"**{len(st.session_state.historial)-idx}. Cita completa:**")
        st.markdown(cita_full, unsafe_allow_html=True)
        st.markdown(f"**Cita abreviada:** {cita_abrev}")


