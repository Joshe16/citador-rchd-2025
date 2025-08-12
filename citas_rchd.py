import streamlit as st
import re

st.set_page_config(page_title="Generador de Citas Jurídicas RChD 2025", page_icon="⚖️")

st.title("⚖️ Generador de Citas Jurídicas - RChD 2025")
st.subheader("Consejería Académica Derecho UC")

def versalitas(texto):
    return texto.upper()

def strip_tags(texto):
    return re.sub('<[^<]+?>', '', texto)

def formatear_autores(autores):
    n = len(autores)
    if n == 1:
        a = autores[0]
        return f"{versalitas(a['apellido'])}, {a['nombre']}"
    elif 2 <= n <= 3:
        autores_fmt = [f"{versalitas(a['apellido'])}, {a['nombre']}" for a in autores]
        return ' y '.join(autores_fmt)
    else:
        a = autores[0]
        return f"{versalitas(a['apellido'])}, {a['nombre']} y otros"

def input_autores(max_autores=10):
    n_autores = st.number_input("Número de autores", min_value=1, max_value=max_autores, value=1, step=1)
    autores = []
    for i in range(n_autores):
        st.markdown(f"### Autor {i+1}")
        apellido = st.text_input(f"Apellido(s)", key=f"apellido_{i}")
        nombre = st.text_input(f"Nombre(s)", key=f"nombre_{i}")
        autores.append({"apellido": apellido.strip(), "nombre": nombre.strip()})
    return autores

def libro_cita(autores, año, titulo, ciudad, editorial, edicion, tomo, traduccion, traductor, año_original):
    autores_fmt = formatear_autores(autores)
    if traduccion and año_original:
        año_str = f"[{año_original}] {año}"
    else:
        año_str = año

    edicion_str = ''
    if edicion and edicion != "1":
        edicion_str = f", {edicion} edición"

    tomo_str = ''
    if tomo:
        tomo_str = f", {tomo}"

    traductor_str = ''
    if traduccion and traductor:
        traductor_str = f" (trad. {traductor})"

    cita = f"{autores_fmt} ({año_str}): {titulo}{tomo_str}{traductor_str} ({ciudad}, {editorial}{edicion_str})."
    return cita

def libro_cita_corta(autores, año, pagina_o_articulo):
    # Formato simple para cita corta: Apellido autor principal + año + página/artículo
    if not autores:
        return ""
    a = autores[0]
    autor_fmt = versalitas(a['apellido'])
    if pagina_o_articulo:
        return f"({autor_fmt} {año}, p. {pagina_o_articulo})"
    else:
        return f"({autor_fmt} {año})"

def validar_campos_requeridos(campos):
    return all(campos.values()) and all(str(v).strip() != '' for v in campos.values())

# Inicializa el historial de citas en session_state si no existe
if "historial_citas" not in st.session_state:
    st.session_state.historial_citas = []

tipo = st.selectbox("Selecciona el tipo de fuente:", [
    "Libro", "Capítulo de libro", "Artículo de revista", "Ley o norma jurídica",
    "Sentencia o jurisprudencia", "Tesis o memoria", "Sitio web / noticia digital", "Tratado internacional"
])

with st.form("form_cita"):
    if tipo == "Libro":
        st.markdown("### Datos del libro")
        autores = input_autores(5)
        año = st.text_input("Año")
        año_original = st.text_input("Año original (si es traducción, opcional)")
        titulo = st.text_input("Título del libro")
        ciudad = st.text_input("Ciudad")
        editorial = st.text_input("Editorial")
        edicion = st.text_input("Edición (dejar vacío o 1 si es primera edición)")
        tomo = st.text_input("Tomo / volumen (opcional)")
        traduccion = st.checkbox("¿Es una traducción?")
        traductor = ''
        if traduccion:
            traductor = st.text_input("Nombre del traductor")
        pagina_o_articulo = st.text_input("Página o artículo para cita corta (opcional)")

    elif tipo == "Capítulo de libro":
        st.markdown("### Datos del capítulo")
        autor_cap = {}
        autor_cap["apellido"] = st.text_input("Apellido(s) autor del capítulo")
        autor_cap["nombre"] = st.text_input("Nombre(s) autor del capítulo")




