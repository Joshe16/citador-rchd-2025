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

# ------------------ PLANTILLAS DE CITA ------------------
PLANTILLAS = {
    "Libro con un autor": "{autor} ({anio}): {titulo} ({lugar}, {editorial}{edicion}).",
    "Libro con dos o tres autores": "{autor1} y {autor2}{autor3} ({anio}): {titulo} ({lugar}, {editorial}).",
    "Libro con más de tres autores": "{autor} y otros ({anio}): {titulo} ({lugar}, {editorial}).",
    "Libros divididos en tomos o volúmenes": "{autor} ({anio}): {titulo}, Tomo {tomo} ({lugar}, {editorial}).",
    "Traducción de libro": "{autor} ([{anio_original}] {anio}): {titulo} (trad. {traductor}, {lugar}, {editorial}).",
    "Traducción de artículo": "{autor} ([{anio_original}] {anio}): {titulo_articulo}, {revista}, vol. {volumen}, Nº {numero}: pp. {paginas} (trad. {traductor}).",
    "Capítulo de libro con editor": "{autor} ({anio}): {titulo_cap}, en {editor} (edit.), {titulo_libro} ({lugar}, {editorial}) pp. {paginas}.",
    "Capítulo de libro con editores": "{autor} ({anio}): {titulo_cap}, en {editor1}, {editor2} y {editor3} (edits.), {titulo_libro} ({lugar}, {editorial}) pp. {paginas}.",
    "Artículo de revista": "{autor} ({anio}): {titulo_art}, {revista}, vol. {volumen}, N° {numero}: pp. {paginas}.",
    "Artículo de revista sin volumen/número/páginas": "{autor} ({anio}): {titulo_art}, {revista}. {doi}",
    "Trabajo escrito en alfabeto no latino": "{autor_rom} ({autor_orig}) ({anio}): {titulo_rom} ({titulo_orig}), {revista}, N° {numero}: pp. {paginas}.",
    "E-book sin páginas": "{autor} ({anio}): {titulo}, en {editor} (edit.), {titulo_libro} ({lugar}, {editorial}): Kindle Edition, N° {numero}.",
    "Fuente manuscrita": "{archivo}: {descripcion}, {fecha}.",
    "Obra dogmática con sistema histórico": "{referencia}.",
    "Tesis": "{autor} ({anio}): {titulo}. {descripcion}.",
    "Informe": "{institucion}: {titulo}, sin N° (s.d.).",
    "Documento en sitio web": "{descripcion}. Disponible en: {url}. Fecha de consulta: {fecha}.",
    "Diario o periódico sin autor": "{medio} ({fecha}): {titulo}, p. {pagina}.",
    "Diario o periódico con autor": "{autor} ({fecha}): {titulo}, {medio}, p. {pagina}.",
    "Noticia o columna en sitio web": "{autor} ({anio}): {titulo}, {medio}. Disponible en: {url}. Fecha de consulta: {fecha}.",
    "Página web o blog": "{autor} (sitio web, {anio}): {titulo}. Disponible en: {url}. Fecha de consulta: {fecha}."
}

# ------------------ CAMPOS POR TIPO ------------------
CAMPOS = {
    "Libro con un autor": ["autor", "anio", "titulo", "lugar", "editorial", "edicion"],
    "Libro con dos o tres autores": ["autor1", "autor2", "autor3", "anio", "titulo", "lugar", "editorial"],
    "Libro con más de tres autores": ["autor", "anio", "titulo", "lugar", "editorial"],
    "Libros divididos en tomos o volúmenes": ["autor", "anio", "titulo", "tomo", "lugar", "editorial"],
    "Traducción de libro": ["autor", "anio_original", "anio", "titulo", "traductor", "lugar", "editorial"],
    "Traducción de artículo": ["autor", "anio_original", "anio", "titulo_articulo", "revista", "volumen", "numero", "paginas", "traductor"],
    "Capítulo de libro con editor": ["autor", "anio", "titulo_cap", "editor", "titulo_libro", "lugar", "editorial", "paginas"],
    "Capítulo de libro con editores": ["autor", "anio", "titulo_cap", "editor1", "editor2", "editor3", "titulo_libro", "lugar", "editorial", "paginas"],
    "Artículo de revista": ["autor", "anio", "titulo_art", "revista", "volumen", "numero", "paginas"],
    "Artículo de revista sin volumen/número/páginas": ["autor", "anio", "titulo_art", "revista", "doi"],
    "Trabajo escrito en alfabeto no latino": ["autor_rom", "autor_orig", "anio", "titulo_rom", "titulo_orig", "revista", "numero", "paginas"],
    "E-book sin páginas": ["autor", "anio", "titulo", "editor", "titulo_libro", "lugar", "editorial", "numero"],
    "Fuente manuscrita": ["archivo", "descripcion", "fecha"],
    "Obra dogmática con sistema histórico": ["referencia"],
    "Tesis": ["autor", "anio", "titulo", "descripcion"],
    "Informe": ["institucion", "titulo"],
    "Documento en sitio web": ["descripcion", "url", "fecha"],
    "Diario o periódico sin autor": ["medio", "fecha", "titulo", "pagina"],
    "Diario o periódico con autor": ["autor", "fecha", "titulo", "medio", "pagina"],
    "Noticia o columna en sitio web": ["autor", "anio", "titulo", "medio", "url", "fecha"],
    "Página web o blog": ["autor", "anio", "titulo", "url", "fecha"]
}

# ------------------ APP STREAMLIT ------------------
st.title("📚 Citador - Revista Chilena de Derecho")

tipo = st.selectbox("Selecciona el tipo de cita", list(PLANTILLAS.keys()))
datos = {}

st.subheader("Completa los datos")
for campo in CAMPOS[tipo]:
    datos[campo] = st.text_input(campo.capitalize())

if st.button("Generar cita"):
    plantilla = PLANTILLAS[tipo]
    cita_html = plantilla.format(**{k: italics(v) if "titulo" in k or "revista" in k else v for k,v in datos.items()})
    cita_texto = limpiar_html_a_texto(cita_html)

    st.markdown("### Vista previa (con formato)")
    st.markdown(cita_html, unsafe_allow_html=True)

    # Botones de copiar usando JavaScript
    st.markdown(
        f"""
        <button onclick="navigator.clipboard.writeText(`{cita_html}`)">📋 Copiar con formato</button>
        <button onclick="navigator.clipboard.writeText(`{cita_texto}`)">📋 Copiar texto plano</button>
        """,
        unsafe_allow_html=True
    )

    if "historial" not in st.session_state:
        st.session_state.historial = []
    st.session_state.historial.append(cita_html)

if "historial" in st.session_state and st.session_state.historial:
    st.subheader("Historial de citas")
    for cita in st.session_state.historial:
        st.markdown(cita, unsafe_allow_html=True)


