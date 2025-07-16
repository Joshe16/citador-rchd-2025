# citador_streamlit.py
import streamlit as st

st.set_page_config(page_title="Generador de Citas Jurídicas RChD 2025", page_icon="⚖️")

def versalitas(texto):
    return texto.upper()

def dividir_nombre(autor):
    if ' ' in autor:
        partes = autor.strip().rsplit(' ', 1)
        return partes[0], partes[1]
    else:
        return autor, ""

st.title("⚖️ Generador de Citas Jurídicas - RChD 2025")
st.subheader("Consejería Académica Derecho UC")

tipo = st.selectbox("Selecciona el tipo de fuente:", [
    "Libro", "Artículo de revista", "Capítulo de libro", "Ley o norma jurídica",
    "Sentencia o jurisprudencia", "Tesis o memoria", "Sitio web / noticia digital", "Tratado internacional"
])

if tipo == "Libro":
    autor = st.text_input("Autor(es)")
    año = st.text_input("Año")
    titulo = st.text_input("Título del libro")
    ciudad = st.text_input("Ciudad")
    editorial = st.text_input("Editorial")
    edicion = st.text_input("Edición (dejar vacío si es la primera)")
    if st.button("Generar cita"):
        apellidos, nombre = dividir_nombre(autor)
        cita = f"{versalitas(apellidos)}, {nombre} ({año}): *{titulo}* ({ciudad}, {editorial}"
        if edicion:
            cita += f", {edicion} edición"
        cita += ")."
        st.success("📌 Cita generada:")
        st.code(cita)

elif tipo == "Artículo de revista":
    autor = st.text_input("Autor(es)")
    año = st.text_input("Año")
    titulo = st.text_input("Título del artículo")
    revista = st.text_input("Nombre de la revista")
    volumen = st.text_input("Volumen")
    numero = st.text_input("Número")
    paginas = st.text_input("Páginas (ej: 93-107)")
    if st.button("Generar cita"):
        apellidos, nombre = dividir_nombre(autor)
        cita = f"{versalitas(apellidos)}, {nombre} ({año}): \"{titulo}\", *{revista}*"
        if volumen:
            cita += f", vol. {volumen}"
        if numero:
            cita += f", N° {numero}"
        if paginas:
            cita += f": pp. {paginas}"
        cita += "."
        st.success("📌 Cita generada:")
        st.code(cita)

elif tipo == "Capítulo de libro":
    autor = st.text_input("Autor del capítulo")
    año = st.text_input("Año")
    titulo = st.text_input("Título del capítulo")
    editor = st.text_input("Editor del libro")
    libro = st.text_input("Título del libro")
    ciudad = st.text_input("Ciudad")
    editorial = st.text_input("Editorial")
    paginas = st.text_input("Páginas")
    if st.button("Generar cita"):
        apellidos, nombre = dividir_nombre(autor)
        cita = f"{versalitas(apellidos)}, {nombre} ({año}): \"{titulo}\", en {editor} (edit.), *{libro}* ({ciudad}, {editorial}) pp. {paginas}."
        st.success("📌 Cita generada:")
        st.code(cita)

elif tipo == "Ley o norma jurídica":
    pais = st.text_input("País")
    tipo_norma = st.text_input("Tipo (Ley, Código, DS...)")
    numero = st.text_input("Número o nombre")
    fecha = st.text_input("Fecha (dd/mm/aaaa)")
    nombre = st.text_input("Nombre oficial (opcional)")
    if st.button("Generar cita"):
        cita = f"{versalitas(pais)}, {tipo_norma} {numero} ({fecha})"
        if nombre:
            cita += f". *{nombre}*"
        cita += "."
        st.success("📌 Cita generada:")
        st.code(cita)

elif tipo == "Sentencia o jurisprudencia":
    tribunal = st.text_input("Tribunal")
    fecha = st.text_input("Fecha")
    rol = st.text_input("Rol o RUC/RIT")
    tipo_proc = st.text_input("Tipo procedimiento")
    nombre_fantasia = st.text_input("Nombre del caso (opcional)")
    if st.button("Generar cita"):
        cita = f"{tribunal}, {fecha}, rol {rol}, {tipo_proc}"
        if nombre_fantasia:
            cita += f" ({nombre_fantasia})"
        cita += "."
        st.success("📌 Cita generada:")
        st.code(cita)

elif tipo == "Tesis o memoria":
    autor = st.text_input("Autor")
    año = st.text_input("Año")
    titulo = st.text_input("Título")
    universidad = st.text_input("Universidad")
    grado = st.text_input("Grado académico")
    if st.button("Generar cita"):
        apellidos, nombre = dividir_nombre(autor)
        cita = f"{versalitas(apellidos)}, {nombre} ({año}): *{titulo}*. Memoria para optar al grado de {grado}, {universidad}."
        st.success("📌 Cita generada:")
        st.code(cita)

elif tipo == "Sitio web / noticia digital":
    autor = st.text_input("Autor")
    año = st.text_input("Año")
    titulo = st.text_input("Título")
    medio = st.text_input("Nombre del sitio o medio")
    url = st.text_input("URL")
    fecha_consulta = st.text_input("Fecha de consulta (dd/mm/aaaa)")
    if st.button("Generar cita"):
        apellidos, nombre = dividir_nombre(autor)
        cita = f"{versalitas(apellidos)}, {nombre} ({año}): \"{titulo}\", {medio}. Disponible en: {url}. Fecha de consulta: {fecha_consulta}."
        st.success("📌 Cita generada:")
        st.code(cita)

elif tipo == "Tratado internacional":
    nombre = st.text_input("Nombre del tratado")
    fecha = st.text_input("Fecha de adopción (dd/mm/aaaa)")
    fuente = st.text_input("Fuente (opcional)")
    if st.button("Generar cita"):
        cita = f"{versalitas(nombre)} ({fecha})"
        if fuente:
            cita += f". {fuente}"
        cita += "."
        st.success("📌 Cita generada:")
        st.code(cita)
