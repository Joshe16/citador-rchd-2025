import streamlit as st
import re

st.set_page_config(page_title="Generador de Citas Jurídicas RChD 2025", page_icon="⚖️", layout="wide")

# CSS para versalitas simuladas con small caps
st.markdown("""
    <style>
    .small-caps {
        font-variant: small-caps;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# ----- Funciones -----
def format_autores(autores):
    # autores: lista de dicts con {"apellido":..., "nombre":...}
    partes = []
    for a in autores:
        # apellido con small caps (versalitas)
        partes.append(f'<span class="small-caps">{a["apellido"]}</span>, {a["nombre"]}')
    return "; ".join(partes)

def strip_tags(texto):
    return re.sub('<[^<]+?>', '', texto)

def validar_campos(campos):
    faltantes = [nombre for nombre, val in campos.items() if not val.strip()]
    if faltantes:
        st.error(f"❌ Faltan campos obligatorios: {', '.join(faltantes)}")
        return False
    return True

# Abreviaturas según tipo
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

# Estado para historial y autores temporal
if "historial" not in st.session_state:
    st.session_state.historial = []

if "autores" not in st.session_state:
    st.session_state.autores = []

st.title("⚖️ Generador de Citas Jurídicas - RChD 2025")
st.subheader("Consejería Académica Derecho UC")

tipo = st.selectbox("Selecciona el tipo de fuente:", [
    "Libro", "Artículo de revista", "Capítulo de libro", "Ley o norma jurídica",
    "Sentencia o jurisprudencia", "Tesis o memoria", "Sitio web / noticia digital", "Tratado internacional"
])

# --- Manejo autores ---

def input_autores():
    n_autores = st.number_input("Cantidad de autores", min_value=1, max_value=10, step=1, value=1)
    autores = []
    for i in range(n_autores):
        with st.expander(f"Autor {i+1}"):
            apellido = st.text_input(f"Apellido {i+1}", key=f"apellido_{i}")
            nombre = st.text_input(f"Nombre(s) {i+1}", key=f"nombre_{i}")
            autores.append({"apellido": apellido.strip(), "nombre": nombre.strip()})
    return autores

# Inputs dinámicos con autores en formulario
with st.form(key="form_cita"):
    if tipo in ["Libro", "Artículo de revista", "Capítulo de libro", "Tesis o memoria", "Sitio web / noticia digital"]:
        st.markdown("### Datos del Autor(es)")
        autores = input_autores()
    else:
        autores = []

    if tipo == "Libro":
        año = st.text_input("Año")
        titulo = st.text_input("Título del libro")
        ciudad = st.text_input("Ciudad")
        editorial = st.text_input("Editorial")
        edicion = st.text_input("Edición (dejar vacío si es la primera)")
        campos = {"Año": año, "Título": titulo, "Ciudad": ciudad, "Editorial": editorial}

    elif tipo == "Artículo de revista":
        año = st.text_input("Año")
        titulo = st.text_input("Título del artículo")
        revista = st.text_input("Nombre de la revista")
        volumen = st.text_input("Volumen")
        numero = st.text_input("Número")
        paginas = st.text_input("Páginas (ej: 93-107)")
        campos = {"Año": año, "Título": titulo, "Revista": revista}

    elif tipo == "Capítulo de libro":
        año = st.text_input("Año")
        titulo = st.text_input("Título del capítulo")
        editor = st.text_input("Editor del libro")
        libro = st.text_input("Título del libro")
        ciudad = st.text_input("Ciudad")
        editorial = st.text_input("Editorial")
        paginas = st.text_input("Páginas")
        campos = {"Año": año, "Título": titulo, "Editor": editor, "Título libro": libro, "Ciudad": ciudad, "Editorial": editorial}

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
        año = st.text_input("Año")
        titulo = st.text_input("Título")
        universidad = st.text_input("Universidad")
        grado = st.text_input("Grado académico")
        campos = {"Año": año, "Título": titulo, "Universidad": universidad, "Grado": grado}

    elif tipo == "Sitio web / noticia digital":
        año = st.text_input("Año")
        titulo = st.text_input("Título")
        medio = st.text_input("Nombre del sitio o medio")
        url = st.text_input("URL")
        fecha_consulta = st.text_input("Fecha de consulta (dd/mm/aaaa)")
        campos = {"Año": año, "Título": titulo, "Medio": medio, "URL": url, "Fecha consulta": fecha_consulta}

    elif tipo == "Tratado internacional":
        nombre_tratado = st.text_input("Nombre del tratado")
        fecha = st.text_input("Fecha de adopción (dd/mm/aaaa)")
        fuente = st.text_input("Fuente (opcional)")
        campos = {"Nombre tratado": nombre_tratado, "Fecha": fecha}

    submit = st.form_submit_button("Generar cita")

if submit:
    # Validamos campos obligatorios
    if validar_campos(campos):
        if tipo in ["Libro", "Artículo de revista", "Capítulo de libro", "Tesis o memoria", "Sitio web / noticia digital"]:
            # Solo procesamos autores si están presentes
            if any(not a["apellido"] or not a["nombre"] for a in autores):
                st.error("Por favor ingresa apellido y nombre para todos los autores.")
            else:
                autores_fmt = format_autores(autores)

                # Construcción cita
                if tipo == "Libro":
                    cita = f"{autores_fmt} ({campos['Año']}): <em>{campos['Título']}</em> ({campos['Ciudad']}, {campos['Editorial']}"
                    edicion = locals().get('edicion', '')
                    if edicion:
                        cita += f", {edicion} edición"
                    cita += ")."

                elif tipo == "Artículo de revista":
                    cita = f"{autores_fmt} ({campos['Año']}): \"{campos['Título']}\", <em>{campos['Revista']}</em>"
                    volumen = locals().get('volumen', '')
                    if volumen:
                        cita += f", vol. {volumen}"
                    numero = locals().get('numero', '')
                    if numero:
                        cita += f", N° {numero}"
                    paginas = locals().get('paginas', '')
                    if paginas:
                        cita += f": pp. {paginas}"
                    cita += "."

                elif tipo == "Capítulo de libro":
                    cita = (f"{autores_fmt} ({campos['Año']}): \"{campos['Título']}\", en {locals().get('editor', '')} (ed.), "
                            f"<em>{locals().get('libro', '')}</em> ({locals().get('ciudad', '')}, {locals().get('editorial', '')}) pp. {locals().get('paginas', '')}.")

                elif tipo == "Tesis o memoria":
                    cita = (f"{autores_fmt} ({campos['Año']}): <em>{campos['Título']}</em>. Memoria para optar al grado de {locals().get('grado', '')}, {campos['Universidad']}.")

                elif tipo == "Sitio web / noticia digital":
                    cita = (f"{autores_fmt} ({campos['Año']}): \"{campos['Título']}\", {locals().get('medio', '')}. Disponible en: {locals().get('url', '')}. "
                            f"Fecha de consulta: {locals().get('fecha_consulta', '')}.")

                else:
                    cita = "Tipo de cita no soportado."

                st.session_state.historial.append(cita)
                st.markdown("### Cita generada:")
                st.markdown(cita, unsafe_allow_html=True)

        else:
            # Otros tipos sin autores
            if tipo == "Ley o norma jurídica":
                cita = f"<span class='small-caps'>{campos['País']}</span>, {campos['Tipo']} {campos['Número']} ({campos['Fecha']})"
                nombre = locals().get("nombre", "")
                if nombre:
                    cita += f". <em>{nombre}</em>"
                cita += "."

            elif tipo == "Sentencia o jurisprudencia":
                cita = f"{campos['Tribunal']}, {campos['Fecha']}, rol {campos['Rol']}, {campos['Tipo procedimiento']}"
                nombre_fantasia = locals().get("nombre_fantasia", "")
                if nombre_fantasia:
                    cita += f" ({nombre_fantasia})"
                cita += "."

            elif tipo == "Tratado internacional":
                cita = f"<span class='small-caps'>{campos['Nombre tratado']}</span> ({campos['Fecha']})"
                fuente = locals().get("fuente", "")
                if fuente:
                    cita += f". {fuente}"
                cita += "."

            else:
                cita = "Tipo de cita no soportado."
            
            st.session_state.historial.append(cita)
            st.markdown("### Cita generada:")
            st.markdown(cita, unsafe_allow_html=True)

        # --- Cita abreviada ---
        label_abrev = ABREVIATION_LABELS.get(tipo)
        if label_abrev:
            st.markdown("---")
            st.markdown(f"### Generar cita abreviada ({label_abrev})")
            abrev = st.text_input(f"Ingrese {label_abrev} para cita abreviada", key="abrev_input")
            if st.button("Generar cita abreviada", key="btn_abrev"):
                if not abrev.strip():
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
