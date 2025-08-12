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
    # autores es lista de dicts {'apellido': str, 'nombre': str}
    n = len(autores)
    if n == 1:
        a = autores[0]
        return f"{versalitas(a['apellido'])}, {a['nombre']}"
    elif 2 <= n <= 3:
        autores_fmt = [f"{versalitas(a['apellido'])}, {a['nombre']}" for a in autores]
        return ' y '.join(autores_fmt)
    else:
        # Más de 3 autores: primer autor + "y otros"
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
    # Ejemplos:
    # a) Libro con un autor:
    # GUZMÁN BRITO, Alejandro (2005): De las donaciones entre vivos. Conceptos y tipos (Santiago, Editorial LexisNexis, segunda edición).
    #
    # d) Libros divididos en tomos o volúmenes:
    # SILVA BASCUÑÁN, Alejandro (1997): Tratado de Derecho constitucional, Tomo I (Santiago, Editorial Jurídica de Chile).
    #
    # e.i) Traducciones de libros:
    # LE TOURNEAU, Philippe ([1982] 2004): La responsabilidad civil (trad. Javier Tamayo Jaramillo, Bogotá, Editorial Legis).

    # Autor
    autores_fmt = formatear_autores(autores)

    # Año con posible original entre corchetes si hay traducción
    if traduccion and año_original:
        año_str = f"[{año_original}] {año}"
    else:
        año_str = año

    # Edición
    edicion_str = ''
    if edicion and edicion != "1":
        edicion_str = f", {edicion} edición"

    # Tomo o volumen
    tomo_str = ''
    if tomo:
        tomo_str = f", {tomo}"

    # Traducción
    traductor_str = ''
    if traduccion and traductor:
        traductor_str = f" (trad. {traductor})"

    cita = f"{autores_fmt} ({año_str}): {titulo}{tomo_str}{traductor_str} ({ciudad}, {editorial}{edicion_str})."
    return cita

def capitulo_libro_cita(autor_cap, año, titulo_cap, editores, libro, ciudad, editorial, paginas):
    # Ejemplo f) Capítulo de libro con editor:
    # HÜBNER GUZMÁN, Ana María (1998): “Los bienes familiares en la legislación chilena”, en CORRAL TALCIANI, Hernán (edit.), Los regímenes matrimoniales en Chile (Santiago, Universidad de los Andes) pp. 101-146.

    autor_fmt = formatear_autores([autor_cap]) if isinstance(autor_cap, dict) else autor_cap
    editores_fmt = ''
    if editores:
        editores_fmt = f"en {editores} (edit.), "

    cita = f"{autor_fmt} ({año}): “{titulo_cap}”, {editores_fmt}<em>{libro}</em> ({ciudad}, {editorial}) pp. {paginas}."
    return cita

def validar_campos_requeridos(campos):
    return all(campos.values()) and all(str(v).strip() != '' for v in campos.values())

tipo = st.selectbox("Selecciona el tipo de fuente:", [
    "Libro", "Capítulo de libro", "Artículo de revista", "Ley o norma jurídica",
    "Sentencia o jurisprudencia", "Tesis o memoria", "Sitio web / noticia digital", "Tratado internacional"
])

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

    if st.button("Generar cita"):
        # Validación básica de autores
        autores_validos = all(a["apellido"] and a["nombre"] for a in autores)
        if not autores_validos:
            st.error("Completa apellido y nombre de todos los autores.")
        elif not validar_campos_requeridos({
            "Año": año,
            "Título": titulo,
            "Ciudad": ciudad,
            "Editorial": editorial
        }):
            st.error("Completa todos los campos obligatorios.")
        else:
            cita = libro_cita(autores, año, titulo, ciudad, editorial, edicion, tomo, traduccion, traductor, año_original)
            st.markdown("### Cita generada con formato visual:")
            st.markdown(cita, unsafe_allow_html=True)
            st.text("📋 Cita para copiar y pegar:")
            st.code(strip_tags(cita))

elif tipo == "Capítulo de libro":
    st.markdown("### Datos del capítulo")
    autor_cap = {}
    autor_cap["apellido"] = st.text_input("Apellido(s) autor del capítulo")
    autor_cap["nombre"] = st.text_input("Nombre(s) autor del capítulo")
    año = st.text_input("Año")
    titulo_cap = st.text_input("Título del capítulo")
    editores = st.text_input("Editor(es) del libro (Ej: 'CORRAL TALCIANI, Hernán')")
    libro = st.text_input("Título del libro")
    ciudad = st.text_input("Ciudad")
    editorial = st.text_input("Editorial")
    paginas = st.text_input("Páginas (ej: 101-146)")

    if st.button("Generar cita"):
        if not autor_cap["apellido"] or not autor_cap["nombre"]:
            st.error("Completa apellido y nombre del autor del capítulo.")
        elif not validar_campos_requeridos({
            "Año": año,
            "Título del capítulo": titulo_cap,
            "Editor(es)": editores,
            "Título libro": libro,
            "Ciudad": ciudad,
            "Editorial": editorial,
            "Páginas": paginas
        }):
            st.error("Completa todos los campos obligatorios.")
        else:
            cita = capitulo_libro_cita(autor_cap, año, titulo_cap, editores, libro, ciudad, editorial, paginas)
            st.markdown("### Cita generada con formato visual:")
            st.markdown(cita, unsafe_allow_html=True)
            st.text("📋 Cita para copiar y pegar:")
            st.code(strip_tags(cita))

# -- Aquí podrías agregar bloques elif para otros tipos --
# Ejemplo rápido para Artículo de revista:

elif tipo == "Artículo de revista":
    st.markdown("### Datos del artículo de revista")
    autores = input_autores(5)
    año = st.text_input("Año")
    titulo_art = st.text_input("Título del artículo")
    revista = st.text_input("Nombre de la revista")
    volumen = st.text_input("Volumen (opcional)")
    numero = st.text_input("Número (opcional)")
    paginas = st.text_input("Páginas (ej: 93-107, opcional)")
    traduccion = st.checkbox("¿Es una traducción?")
    traductor = ''
    if traduccion:
        traductor = st.text_input("Nombre del traductor")

    if st.button("Generar cita"):
        autores_validos = all(a["apellido"] and a["nombre"] for a in autores)
        if not autores_validos:
            st.error("Completa apellido y nombre de todos los autores.")
        elif not validar_campos_requeridos({
            "Año": año,
            "Título": titulo_art,
            "Revista": revista
        }):
            st.error("Completa los campos obligatorios.")
        else:
            autores_fmt = formatear_autores(autores)
            año_str = año
            if traduccion and año_original:
                año_str = f"[{año_original}] {año}"
            cita = f"{autores_fmt} ({año_str}): “{titulo_art}”"
            cita += f", <em>{revista}</em>"
            if volumen:
                cita += f", vol. {volumen}"
            if numero:
                cita += f", N° {numero}"
            if paginas:
                cita += f": pp. {paginas}"
            if traduccion and traductor:
                cita += f" (trad. {traductor})"
            cita += "."
            st.markdown("### Cita generada con formato visual:")
            st.markdown(cita, unsafe_allow_html=True)
            st.text("📋 Cita para copiar y pegar:")
            st.code(strip_tags(cita))

else:
    st.info("Próximamente agregaremos más tipos de cita.")

# Aquí podrías ampliar para todos los demás tipos con lógica específica que quieras.



