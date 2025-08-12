import streamlit as st
import re

st.set_page_config(page_title="Generador de Citas Jurídicas RChD 2025", page_icon="⚖️", layout="wide")

# ----- Funciones útiles -----
def versalitas(texto):
    return texto.upper()

def procesar_autores(autores_str):
    autores = [a.strip() for a in autores_str.split(";") if a.strip()]
    autores_format = []
    for autor in autores:
        partes = autor.split()
        if len(partes) == 0:
            continue
        elif len(partes) == 1:
            autores_format.append(versalitas(partes[0]))
        else:
            apellido = partes[-1]
            nombre = " ".join(partes[:-1])
            autores_format.append(f"<b>{versalitas(apellido)}</b>, {nombre}")
    return "; ".join(autores_format)

def strip_tags(texto):
    return re.sub('<[^<]+?>', '', texto)

def validar_campos(campos):
    faltantes = [nombre for nombre, val in campos.items() if not val.strip()]
    if faltantes:
        st.error(f"❌ Faltan campos obligatorios: {', '.join(faltantes)}")
        return False
    return True

def mostrar_cita(cita):
    st.markdown("### 📌 Cita generada con formato visual:")
    st.markdown(cita, unsafe_allow_html=True)
    st.markdown("### 📋 Cita para copiar y pegar (sin formato HTML):")
    st.code(strip_tags(cita))


# ----- Datos para cita abreviada -----
ABREVIATION_LABELS = {
    "Libro": "Página",
    "Artículo de revista": "Página",
    "Capítulo de libro": "Página",
    "Ley o norma jurídica": "Artículo",
    "Sentencia o jurisprudencia": "Considerando",
    "Tesis o memoria": "Página",
    "Sitio web / noticia digital": None,
    "Tratado internacional": None
}

# ----- Historial simple en sesión -----
if "historial" not in st.session_state:
    st.session_state.historial = []

# ----- UI -----
st.title("⚖️ Generador de Citas Jurídicas - RChD 2025")
st.subheader("Consejería Académica Derecho UC")

tipo = st.selectbox("Selecciona el tipo de fuente:", [
    "Libro", "Artículo de revista", "Capítulo de libro", "Ley o norma jurídica",
    "Sentencia o jurisprudencia", "Tesis o memoria", "Sitio web / noticia digital", "Tratado internacional"
])

# Inputs dinámicos por tipo
with st.form(key="form_cita"):
    if tipo == "Libro":
        autor = st.text_input("Autor(es) (separar con ';' si hay más de uno)")
        año = st.text_input("Año")
        titulo = st.text_input("Título del libro")
        ciudad = st.text_input("Ciudad")
        editorial = st.text_input("Editorial")
        edicion = st.text_input("Edición (dejar vacío si es la primera)")
        campos = {"Autor": autor, "Año": año, "Título": titulo, "Ciudad": ciudad, "Editorial": editorial}

    elif tipo == "Artículo de revista":
        autor = st.text_input("Autor(es) (separar con ';')")
        año = st.text_input("Año")
        titulo = st.text_input("Título del artículo")
        revista = st.text_input("Nombre de la revista")
        volumen = st.text_input("Volumen")
        numero = st.text_input("Número")
        paginas = st.text_input("Páginas (ej: 93-107)")
        campos = {"Autor": autor, "Año": año, "Título": titulo, "Revista": revista}

    elif tipo == "Capítulo de libro":
        autor = st.text_input("Autor(es) del capítulo (separar con ';')")
        año = st.text_input("Año")
        titulo = st.text_input("Título del capítulo")
        editor = st.text_input("Editor del libro")
        libro = st.text_input("Título del libro")
        ciudad = st.text_input("Ciudad")
        editorial = st.text_input("Editorial")
        paginas = st.text_input("Páginas")
        campos = {"Autor": autor, "Año": año, "Título": titulo, "Editor": editor, "Título libro": libro, "Ciudad": ciudad, "Editorial": editorial}

    elif tipo == "Ley o norma jurídica":
        pais = st.text_input("País")
        tipo_norma = st.text_input("Tipo (Ley, Código, DS...)")
        numero = st.text_input("Número o nombre")
        fecha = st.text_input("Fecha (dd/mm/aaaa)")
        nombre = st.text_input("Nombre oficial (opcional)")
        campos = {"País": pais, "Tipo": tipo_norma, "Número": numero, "Fecha": fecha}

    elif tipo == "Sentencia o jurisprudencia":
        tribunal = st.text_input("Tribunal")
        fecha = st.text_input("Fecha")
        rol = st.text_input("Rol o RUC/RIT")
        tipo_proc = st.text_input("Tipo procedimiento")
        nombre_fantasia = st.text_input("Nombre del caso (opcional)")
        campos = {"Tribunal": tribunal, "Fecha": fecha, "Rol": rol, "Tipo procedimiento": tipo_proc}

    elif tipo == "Tesis o memoria":
        autor = st.text_input("Autor(es) (separar con ';')")
        año = st.text_input("Año")
        titulo = st.text_input("Título")
        universidad = st.text_input("Universidad")
        grado = st.text_input("Grado académico")
        campos = {"Autor": autor, "Año": año, "Título": titulo, "Universidad": universidad, "Grado": grado}

    elif tipo == "Sitio web / noticia digital":
        autor = st.text_input("Autor(es) (separar con ';')")
        año = st.text_input("Año")
        titulo = st.text_input("Título")
        medio = st.text_input("Nombre del sitio o medio")
        url = st.text_input("URL")
        fecha_consulta = st.text_input("Fecha de consulta (dd/mm/aaaa)")
        campos = {"Autor": autor, "Año": año, "Título": titulo, "Medio": medio, "URL": url, "Fecha consulta": fecha_consulta}

    elif tipo == "Tratado internacional":
        nombre_tratado = st.text_input("Nombre del tratado")
        fecha = st.text_input("Fecha de adopción (dd/mm/aaaa)")
        fuente = st.text_input("Fuente (opcional)")
        campos = {"Nombre tratado": nombre_tratado, "Fecha": fecha}

    submit = st.form_submit_button("Generar cita")

if submit:
    if validar_campos(campos):
        # Generar cita según tipo
        if tipo == "Libro":
            autores_fmt = procesar_autores(autor)
            cita = f"{autores_fmt} ({año}): <em>{titulo}</em> ({ciudad}, {editorial}"
            if edicion:
                cita += f", {edicion} edición"
            cita += ")."

        elif tipo == "Artículo de revista":
            autores_fmt = procesar_autores(autor)
            cita = f"{autores_fmt} ({año}): \"{titulo}\", <em>{revista}</em>"
            if volumen:
                cita += f", vol. {volumen}"
            if numero:
                cita += f", N° {numero}"
            if paginas:
                cita += f": pp. {paginas}"
            cita += "."

        elif tipo == "Capítulo de libro":
            autores_fmt = procesar_autores(autor)
            cita = (f"{autores_fmt} ({año}): \"{titulo}\", en {editor} (ed.), <em>{libro}</em> "
                    f"({ciudad}, {editorial}) pp. {paginas}.")

        elif tipo == "Ley o norma jurídica":
            cita = f"<b>{versalitas(pais)}</b>, {tipo_norma} {numero} ({fecha})"
            if nombre:
                cita += f". <em>{nombre}</em>"
            cita += "."

        elif tipo == "Sentencia o jurisprudencia":
            cita = f"{tribunal}, {fecha}, rol {rol}, {tipo_proc}"
            if nombre_fantasia:
                cita += f" ({nombre_fantasia})"
            cita += "."

        elif tipo == "Tesis o memoria":
            autores_fmt = procesar_autores(autor)
            cita = (f"{autores_fmt} ({año}): <em>{titulo}</em>. Memoria para optar al grado de {grado}, {universidad}.")

        elif tipo == "Sitio web / noticia digital":
            autores_fmt = procesar_autores(autor)
            cita = (f"{autores_fmt} ({año}): \"{titulo}\", {medio}. Disponible en: {url}. "
                    f"Fecha de consulta: {fecha_consulta}.")

        elif tipo == "Tratado internacional":
            cita = f"<b>{versalitas(nombre_tratado)}</b> ({fecha})"
            if fuente:
                cita += f". {fuente}"
            cita += "."

        else:
            cita = "Tipo de cita no soportado."

        # Guardar cita en historial
        st.session_state.historial.append(cita)
        mostrar_cita(cita)

        # Cita abreviada
        label_abrev = ABREVIATION_LABELS.get(tipo)
        if label_abrev:
            st.markdown("---")
            st.markdown(f"### Generar cita abreviada ({label_abrev})")
            abrev = st.text_input(f"Ingrese {label_abrev} para cita abreviada", key="abrev_input")
            if st.button("Generar cita abreviada"):
                if abrev.strip() == "":
                    st.error("Por favor ingresa el valor para la cita abreviada.")
                else:
                    cita_abrev = cita.rstrip(".") + f", {label_abrev} {abrev}."
                    st.markdown("#### Cita abreviada generada:")
                    st.code(strip_tags(cita_abrev))

# Mostrar historial
if st.session_state.historial:
    st.markdown("---")
    st.markdown("## 📚 Historial de citas generadas")
    for i, c in enumerate(st.session_state.historial[::-1], 1):
        st.markdown(f"**{len(st.session_state.historial) - i + 1}.** {c}", unsafe_allow_html=True)
    if st.button("Borrar historial"):
        st.session_state.historial.clear()
        st.experimental_rerun()
