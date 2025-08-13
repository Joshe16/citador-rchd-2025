import streamlit as st
import re

# ------------------ UTILIDADES DE FORMATO ------------------
def versalitas(text):
    return f"<span style='font-variant: small-caps;'>{text.upper()}</span>"

def italics(text):
    return f"<i>{text}</i>"

def quotes(text):
    return f"“{text}”"

def limpiar_html_a_texto(html):
    text = re.sub(r'<.*?>', '', html)
    return text.strip()

def cita_abreviada(autores, año, paginas=None):
    if not autores:
        return f"({año})"
    n = len(autores)
    if n == 1:
        ap = autores[0].upper()
        return f"{ap} ({año})" + (f", p. {paginas}" if paginas else "")
    elif 2 <= n <= 3:
        aps = " y ".join([a.upper() for a in autores])
        return f"{aps} ({año})" + (f", p. {paginas}" if paginas else "")
    else:
        ap = autores[0].upper()
        return f"{ap} y otros ({año})" + (f", p. {paginas}" if paginas else "")

# ------------------ PLANTILLAS DE CITA ------------------
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
    "Libro": ["autor", "año", "titulo", "lugar", "editorial", "edicion"],
    "Traducción de libro": ["autor", "año_original", "año", "titulo", "traductor", "lugar", "editorial"],
    "Capítulo de libro": ["autor", "año", "titulo_cap", "editor", "titulo_libro", "lugar", "editorial", "paginas"],
    "Artículo de revista": ["autor", "año", "titulo_art", "revista", "volumen", "numero", "paginas"],
    "Norma": ["pais", "tipo_norma", "nombre_norma", "fecha"],
    "Jurisprudencia": ["tribunal", "fecha", "rol", "nombre_caso", "info_extra"],
    "Página web o blog": ["autor", "año", "titulo", "url", "fecha"],
    "Tesis": ["autor", "año", "titulo", "grado", "institucion"]
}

# ------------------ APP STREAMLIT ------------------
st.title("📚 Citador - Revista Chilena de Derecho")

tipo = st.selectbox("Selecciona el tipo de cita", list(PLANTILLAS.keys()))
datos = {}

st.subheader("Completa los datos")
for campo in CAMPOS[tipo]:
    datos[campo] = st.text_input(campo.capitalize())

paginas_cita = st.text_input("Número de página para cita abreviada (opcional)")

# Para la cita abreviada, pedimos lista de autores separados por coma
autores_corta = st.text_input("Autores para cita abreviada (apellidos, separados por coma)")

if st.button("Generar cita"):
    plantilla = PLANTILLAS[tipo]
    # Aplicar italics a títulos y revistas
    cita_html = plantilla.format(**{k: italics(v) if "titulo" in k or "revista" in k else v for k,v in datos.items()})
    cita_texto = limpiar_html_a_texto(cita_html)

    # Cita abreviada
    autores_lista = [a.strip() for a in autores_corta.split(",")] if autores_corta else []
    cita_abrev = cita_abreviada(autores_lista, datos.get("año", ""), paginas=paginas_cita if paginas_cita else None)

    st.markdown("### Vista previa (con formato)")
    st.markdown(cita_html, unsafe_allow_html=True)

    st.markdown("### Cita abreviada")
    st.write(cita_abrev)

    # Botones de copiar usando JavaScript
    st.markdown(
        f"""
        <button onclick="navigator.clipboard.writeText(`{cita_html}`)">📋 Copiar cita completa con formato</button>
        <button onclick="navigator.clipboard.writeText(`{cita_texto}`)">📋 Copiar cita completa texto plano</button>
        <button onclick="navigator.clipboard.writeText(`{cita_abrev}`)">📋 Copiar cita abreviada</button>
        """,
        unsafe_allow_html=True
    )

    # Historial
    if "historial" not in st.session_state:
        st.session_state.historial = []
    st.session_state.historial.append((cita_html, cita_abrev))

if "historial" in st.session_state and st.session_state.historial:
    st.subheader("Historial de citas")
    for idx, (cita_full, cita_abrev) in enumerate(reversed(st.session_state.historial)):
        st.markdown(f"**{len(st.session_state.historial)-idx}. Cita completa:**")
        st.markdown(cita_full, unsafe_allow_html=True)
        st.markdown(f"**Cita abreviada:** {cita_abrev}")


