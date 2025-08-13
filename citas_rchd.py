import streamlit as st
import re

# --------- Funciones generales ------------
def versalitas(texto):
    return texto.upper() if texto else ""

def formatear_autores_libro(autores):
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
    elif n in [2, 3]:
        return " y ".join(formato(a) for a in autores)
    else:
        return f"{formato(autores[0])} y otros"

def cita_abreviada_libro(autores, año, paginas=None):
    n = len(autores)
    if n == 0:
        return f"({año})"
    if n == 1:
        base = f"{versalitas(autores[0]['apellido1'])} ({año})"
    elif n in [2,3]:
        aps = " y ".join([versalitas(a['apellido1']) for a in autores])
        base = f"{aps} ({año})"
    else:
        base = f"{versalitas(autores[0]['apellido1'])} y otros ({año})"
    if paginas:
        base += f", p. {paginas}"
    return base

def formatear_titulo_html(titulo):
    return f"<i>{titulo}</i>"

def agregar_autores(num, prefix=""):
    autores = []
    for i in range(num):
        st.markdown(f"**Autor {i+1}**")
        apellido1 = st.text_input(f"Primer apellido autor {i+1}", key=f"{prefix}ape1_{i}")
        apellido2 = st.text_input(f"Segundo apellido autor {i+1} (opcional)", key=f"{prefix}ape2_{i}")
        nombre = st.text_input(f"Nombre autor {i+1}", key=f"{prefix}nom_{i}")
        autores.append({'apellido1': apellido1.strip(), 'apellido2': apellido2.strip(), 'nombre': nombre.strip()})
    return autores

def limpiar_html_a_texto(html_text):
    # eliminar tags HTML simples
    clean = re.sub('<.*?>', '', html_text)
    return clean

# --------- Generación de referencias ------------
def generar_referencia_libro(datos):
    autores_html = formatear_autores_libro(datos['autores'])
    año = datos['año']
    titulo_html = formatear_titulo_html(datos['titulo'])
    ciudad = datos['ciudad']
    editorial = datos['editorial']
    edicion = datos.get('edicion')
    tomo = datos.get('tomo')
    ed_str = f", {edicion}" if edicion and edicion != "1" else ""
    tomo_str = f", {tomo}" if tomo else ""
    ciudad_str = f" ({ciudad}, {editorial}{ed_str})" if ciudad or editorial else ""
    return f"{autores_html} ({año}): {titulo_html}{tomo_str}{ciudad_str}."

# --------- Streamlit interfaz ------------

st.title("Citador estilo Revista Chilena de Derecho")

tipo = st.selectbox("Tipo de fuente", ["Libro"])

num_autores = st.number_input("Número de autores", min_value=0, max_value=10, value=1)
autores = []
if num_autores > 0:
    autores = agregar_autores(num_autores)

# --- Libro ---
if tipo == "Libro":
    año = st.text_input("Año de publicación")
    titulo = st.text_input("Título del libro")
    ciudad = st.text_input("Ciudad de publicación")
    editorial = st.text_input("Editorial (ej. Editorial LexisNexis)")
    edicion = st.text_input("Número de edición (opcional, primera se omite)")
    tomo = st.text_input("Tomo o volumen (opcional)")
    paginas = st.text_input("Páginas (opcional, para cita abreviada)")

    if st.button("Generar cita"):
        datos = {
            'autores': autores,
            'año': año,
            'titulo': titulo,
            'ciudad': ciudad,
            'editorial': editorial,
            'edicion': edicion,
            'tomo': tomo
        }

        ref_html = generar_referencia_libro(datos)
        cita_texto = cita_abreviada_libro(autores, año, paginas=paginas if paginas else None)
        ref_texto = limpiar_html_a_texto(ref_html)

        st.subheader("Referencia completa:")
        st.markdown(ref_html, unsafe_allow_html=True)
        st.text_area("Copiar referencia completa:", value=ref_texto, height=80)

        st.subheader("Cita abreviada:")
        st.write(cita_texto)
        st.text_area("Copiar cita abreviada:", value=cita_texto, height=40)

        st.session_state.setdefault("historial", []).append((ref_html, cita_texto))

# --- Historial ---
if "historial" in st.session_state and st.session_state["historial"]:
    st.markdown("---")
    st.subheader("Historial de citas generadas")
    for i, (ref, cita) in enumerate(reversed(st.session_state["historial"])):
        st.markdown(f"**{len(st.session_state['historial']) - i}. Referencia completa:**")
        st.markdown(ref, unsafe_allow_html=True)
        st.markdown(f"**Cita abreviada:** {cita}")
        st.markdown("")

