import streamlit as st
import re

# Funciones de formato
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
        return " y ".join([formato(a) for a in autores])
    else:
        return f"{formato(autores[0])} y otros"

def formatear_autores_html(autores):
    n = len(autores)
    if n == 0:
        return ""
    def formato(a):
        ap = versalitas(a['apellido1'])
        if a['apellido2']:
            ap += f" {versalitas(a['apellido2'])}"
        return f"<span style='font-variant: small-caps'>{ap}</span>, {a['nombre']}"
    if n == 1:
        return formato(autores[0])
    elif 2 <= n <= 3:
        return " y ".join(formato(a) for a in autores)
    else:
        return f"{formato(autores[0])} y otros"

def formatear_titulo_html(titulo):
    return f"<i>{titulo}</i>"

def cita_abreviada_autores(autores, año, paginas=None, tomo=None, letra=None):
    n = len(autores)
    if letra:
        año = f"{año}{letra}"
    tomo_str = f", tomo {tomo}" if tomo else ""
    paginas_str = f", p. {paginas}" if paginas else ""
    if n == 0:
        return ""
    elif n == 1:
        ap = versalitas(autores[0]['apellido1'])
        return f"{ap} ({año}){tomo_str}{paginas_str}"
    elif n in [2,3]:
        aps = [versalitas(a['apellido1']) for a in autores]
        ap_str = " y ".join(aps)
        return f"{ap_str} ({año}){paginas_str}"
    else:
        ap = versalitas(autores[0]['apellido1'])
        return f"{ap} y otros ({año}){paginas_str}"

def generar_referencia_libro(datos):
    autores_html = formatear_autores_libro(datos['autores'])
    año = datos['año']
    titulo_html = formatear_titulo_html(datos['titulo'])
    ciudad = datos['ciudad']
    editorial = datos.get('editorial', 'Editorial LexisNexis')
    edicion = datos.get('edicion')
    tomo = datos.get('tomo')
    ed_str = f", {edicion}" if edicion and edicion != "1" else ""
    tomo_str = f", {tomo}" if tomo else ""
    ciudad_str = f" ({ciudad}, {editorial}{ed_str})" if ciudad or editorial else ""
    return f"{autores_html} ({año}): {titulo_html}{tomo_str}{ciudad_str}."

def generar_referencia_traduccion_libro(datos):
    autores_html = formatear_autores_html(datos['autores'])
    año_original = datos['año_original']
    año = datos['año']
    titulo_html = formatear_titulo_html(datos['titulo'])
    traductor = datos['traductor']
    ciudad = datos['ciudad']
    editorial = datos['editorial']
    return f"{autores_html} ([{año_original}] {año}): {titulo_html} (trad. {traductor}, {ciudad}, {editorial})."

def generar_referencia_capitulo_libro(datos):
    autor_capitulo_html = formatear_autores_html(datos['autor_capitulo'])
    año = datos['año']
    titulo_cap_html = formatear_titulo_html(datos['titulo_capitulo'])
    editor_html = formatear_autores_html(datos['editores'])
    titulo_libro_html = formatear_titulo_html(datos['titulo_libro'])
    ciudad = datos['ciudad']
    editorial = datos['editorial']
    paginas = datos['paginas']
    return f"{autor_capitulo_html} ({año}): “{titulo_cap_html}”, en {editor_html} (edit.), {titulo_libro_html} ({ciudad}, {editorial}) pp. {paginas}."

def generar_referencia_articulo_revista(datos):
    autores_html = formatear_autores_html(datos['autores'])
    año = datos['año']
    titulo_articulo_html = formatear_titulo_html(datos['titulo'])
    revista = datos['revista']
    volumen = datos.get('volumen')
    numero = datos.get('numero')
    paginas = datos.get('paginas')
    doi = datos.get('doi')
    ref = f"{autores_html} ({año}): “{titulo_articulo_html}”, {revista}"
    if volumen:
        ref += f", vol. {volumen}"
    if numero:
        ref += f", Nº {numero}"
    if paginas:
        ref += f": pp. {paginas}"
    if doi:
        ref += f". DOI: {doi}"
    ref += "."
    return ref

def generar_referencia_norma(datos):
    pais = versalitas(datos['pais'])
    tipo = datos['tipo_norma']
    nombre = datos['nombre_norma']
    fecha = datos.get('fecha', '')
    if fecha:
        fecha = f" ({fecha})"
    return f"{pais}, {tipo} {nombre}{fecha}."

def generar_referencia_jurisprudencia(datos):
    tribunal = versalitas(datos['tribunal'])
    fecha = datos['fecha']
    rol = datos.get('rol')
    nombre_caso = datos.get('nombre_caso')
    info_extra = datos.get('info_extra')
    ref = f"{tribunal}, {fecha}"
    if rol:
        ref += f", rol {rol}"
    if nombre_caso:
        ref += f" ({nombre_caso})"
    if info_extra:
        ref += f", {info_extra}"
    ref += "."
    return ref

def generar_referencia_web(datos):
    autor = formatear_autores_libro(datos.get('autores', [])) if datos.get('autores') else datos.get('autor_sin_autor', '')
    año = datos.get('año')
    titulo = datos.get('titulo')
    url = datos.get('url')
    fecha_consulta = datos.get('fecha_consulta')
    ref = f"{autor} ({año}): {titulo}, Disponible en: {url}."
    if fecha_consulta:
        ref += f" Fecha de consulta: {fecha_consulta}."
    return ref

def generar_referencia_tesis(datos):
    autor = formatear_autores_html(datos['autores'])
    año = datos['año']
    titulo_html = formatear_titulo_html(datos['titulo'])
    grado = datos['grado']
    institucion = datos['institucion']
    return f"{autor} ({año}): {titulo_html}. {grado}. {institucion}."

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
    # Eliminar tags HTML simples
    clean = re.sub('<.*?>', '', html_text)
    return clean

# Streamlit app
st.title("Citador estilo Revista Chilena de Derecho")

tipo = st.selectbox("Tipo de fuente", [
    "Libro",
    "Traducción de libro",
    "Capítulo de libro",
    "Artículo de revista",
    "Norma",
    "Jurisprudencia",
    "Página web o blog",
    "Tesis"
])

num_autores = st.number_input("Número de autores", min_value=0, max_value=10, value=1)
autores = agregar_autores(num_autores) if num_autores > 0 else []

# --- Generación según tipo ---
if tipo == "Libro":
    año = st.text_input("Año de publicación")
    titulo = st.text_input("Título del libro")
    ciudad = st.text_input("Ciudad de publicación")
    editorial = st.text_input("Editorial (por defecto: LexisNexis)")
    edicion = st.text_input("Número de edición (opcional)")
    tomo = st.text_input("Tomo o volumen (opcional)")
    paginas = st.text_input("Páginas (opcional, para cita abreviada)")

    if st.button("Generar cita"):
        datos = {
            'autores': autores,
            'año': año,
            'titulo': titulo,
            'ciudad': ciudad,
            'editorial': editorial or 'Editorial LexisNexis',
            'edicion': edicion,
            'tomo': tomo
        }
        ref_html = generar_referencia_libro(datos)
        cita_texto = cita_abreviada_autores(autores, año, paginas=paginas if paginas else None, tomo=tomo if tomo else None)
        ref_texto = limpiar_html_a_texto(ref_html)

        st.subheader("Referencia completa:")
        st.markdown(ref_html, unsafe_allow_html=True)
        st.text_area("Copiar referencia completa:", value=ref_texto, height=80)
        st.subheader("Cita abreviada:")
        st.write(cita_texto)
        st.text_area("Copiar cita abreviada:", value=cita_texto, height=40)

# --- Aquí irían los bloques para los otros tipos: traducción, capítulo, artículo, norma, jurisprudencia, web y tesis
# Puedes usar la misma estructura que arriba, cambiando la función de generación correspondiente


