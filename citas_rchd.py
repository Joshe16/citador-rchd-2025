import streamlit as st
from bs4 import BeautifulSoup

# Funciones de formato

def versalitas(texto):
    return texto.upper() if texto else ""

def formatear_autores_revista(autores):
    n = len(autores)
    if n == 0:
        return ""
    if n == 1:
        a = autores[0]
        apellidos = f"{versalitas(a['apellido1'])}"
        if a['apellido2']:
            apellidos += f" {versalitas(a['apellido2'])}"
        return f"{apellidos}, {a['nombre']}"
    elif 2 <= n <= 3:
        autores_form = []
        for a in autores:
            apellidos = f"{versalitas(a['apellido1'])}"
            if a['apellido2']:
                apellidos += f" {versalitas(a['apellido2'])}"
            autores_form.append(f"{apellidos}, {a['nombre']}")
        return " y ".join(autores_form)
    else:
        a = autores[0]
        apellidos = f"{versalitas(a['apellido1'])}"
        if a['apellido2']:
            apellidos += f" {versalitas(a['apellido2'])}"
        return f"{apellidos}, {a['nombre']} y otros"

def formatear_autores_html(autores):
    """Devuelve string con versalitas y nombre normal en HTML para markdown."""
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
    if n == 0:
        return ""
    tomo_str = f", tomo {tomo}" if tomo else ""
    paginas_str = f", p. {paginas}" if paginas else ""
    if n == 1:
        ap = versalitas(autores[0]['apellido1'])
        return f"{ap} ({año}){tomo_str}{paginas_str}"
    elif 2 <= n <= 3:
        aps = [versalitas(a['apellido1']) for a in autores]
        ap_str = " y ".join(aps)
        return f"{ap_str} ({año}){paginas_str}"
    else:
        ap = versalitas(autores[0]['apellido1'])
        return f"{ap} y otros ({año}){paginas_str}"

def generar_referencia_libro(datos):
    autores_html = formatear_autores_html(datos['autores'])
    año = datos['año']
    titulo_html = formatear_titulo_html(datos['titulo'])
    ciudad = datos['ciudad']
    editorial = datos['editorial']
    edicion = datos.get('edicion')
    tomo = datos.get('tomo')
    ed_str = f", {edicion}" if edicion else ""
    tomo_str = f", {tomo}" if tomo else ""
    return f"{autores_html} ({año}): {titulo_html}{tomo_str} ({ciudad}, {editorial}{ed_str})."

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
    autor = formatear_autores_revista(datos.get('autores', [])) if datos.get('autores') else datos.get('autor_sin_autor', '')
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
    soup = BeautifulSoup(html_text, "html.parser")
    return soup.get_text()

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

autores = []
if num_autores > 0:
    autores = agregar_autores(num_autores)

if tipo == "Libro":
    año = st.text_input("Año de publicación")
    titulo = st.text_input("Título del libro")
    ciudad = st.text_input("Ciudad de publicación")
    editorial = st.text_input("Editorial")
    edicion = st.text_input("Número de edición (opcional)")
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
        cita_texto = cita_abreviada_autores(autores, año, paginas=paginas if paginas else None, tomo=tomo if tomo else None)

        ref_texto = limpiar_html_a_texto(ref_html)

        st.subheader("Referencia completa:")
        st.markdown(ref_html, unsafe_allow_html=True)
        st.text_area("Copiar referencia completa:", value=ref_texto, height=80)

        st.subheader("Cita abreviada:")
        st.write(cita_texto)
        st.text_area("Copiar cita abreviada:", value=cita_texto, height=40)

        st.session_state.setdefault("historial", []).append((ref_html, cita_texto))


elif tipo == "Traducción de libro":
    año_original = st.text_input("Año de publicación original")
    año = st.text_input("Año de publicación")
    titulo = st.text_input("Título del libro")
    traductor = st.text_input("Traductor (nombre completo)")
    ciudad = st.text_input("Ciudad de publicación")
    editorial = st.text_input("Editorial")

    if st.button("Generar cita"):
        datos = {
            'autores': autores,
            'año_original': año_original,
            'año': año,
            'titulo': titulo,
            'traductor': traductor,
            'ciudad': ciudad,
            'editorial': editorial
        }
        ref_html = generar_referencia_traduccion_libro(datos)
        cita_texto = cita_abreviada_autores(autores, año)

        ref_texto = limpiar_html_a_texto(ref_html)

        st.subheader("Referencia completa:")
        st.markdown(ref_html, unsafe_allow_html=True)
        st.text_area("Copiar referencia completa:", value=ref_texto, height=80)

        st.subheader("Cita abreviada:")
        st.write(cita_texto)
        st.text_area("Copiar cita abreviada:", value=cita_texto, height=40)

        st.session_state.setdefault("historial", []).append((ref_html, cita_texto))


elif tipo == "Capítulo de libro":
    num_autores_cap = st.number_input("Número de autores del capítulo", min_value=1, max_value=10, value=1, key="cap_num_autores")
    autor_capitulo = []
    if num_autores_cap > 0:
        autor_capitulo = agregar_autores(num_autores_cap, prefix="cap_")

    año = st.text_input("Año de publicación")
    titulo_capitulo = st.text_input("Título del capítulo")
    num_editores = st.number_input("Número de editores", min_value=1, max_value=10, value=1, key="cap_num_edit")
    editores = []
    if num_editores > 0:
        editores = agregar_autores(num_editores, prefix="edit_")

    titulo_libro = st.text_input("Título del libro")
    ciudad = st.text_input("Ciudad de publicación")
    editorial = st.text_input("Editorial")
    paginas = st.text_input("Páginas (ejemplo: 55-73)")

    if st.button("Generar cita"):
        datos = {
            'autor_capitulo': autor_capitulo,
            'año': año,
            'titulo_capitulo': titulo_capitulo,
            'editores': editores,
            'titulo_libro': titulo_libro,
            'ciudad': ciudad,
            'editorial': editorial,
            'paginas': paginas
        }
        ref_html = generar_referencia_capitulo_libro(datos)
        cita_texto = cita_abreviada_autores(autor_capitulo, año, paginas=paginas)

        ref_texto = limpiar_html_a_texto(ref_html)

        st.subheader("Referencia completa:")
        st.markdown(ref_html, unsafe_allow_html=True)
        st.text_area("Copiar referencia completa:", value=ref_texto, height=80)

        st.subheader("Cita abreviada:")
        st.write(cita_texto)
        st.text_area("Copiar cita abreviada:", value=cita_texto, height=40)

        st.session_state.setdefault("historial", []).append((ref_html, cita_texto))


elif tipo == "Artículo de revista":
    año = st.text_input("Año de publicación")
    titulo_articulo = st.text_input("Título del artículo")
    revista = st.text_input("Nombre de la revista")
    volumen = st.text_input("Volumen (opcional)")
    numero = st.text_input("Número (opcional)")
    paginas = st.text_input("Páginas (ejemplo: 23-45)")
    doi = st.text_input("DOI (opcional)")

    if st.button("Generar cita"):
        datos = {
            'autores': autores,
            'año': año,
            'titulo': titulo_articulo,
            'revista': revista,
            'volumen': volumen,
            'numero': numero,
            'paginas': paginas,
            'doi': doi
        }
        ref_html = generar_referencia_articulo_revista(datos)
        cita_texto = cita_abreviada_autores(autores, año, paginas=paginas)

        ref_texto = limpiar_html_a_texto(ref_html)

        st.subheader("Referencia completa:")
        st.markdown(ref_html, unsafe_allow_html=True)
        st.text_area("Copiar referencia completa:", value=ref_texto, height=80)

        st.subheader("Cita abreviada:")
        st.write(cita_texto)
        st.text_area("Copiar cita abreviada:", value=cita_texto, height=40)

        st.session_state.setdefault("historial", []).append((ref_html, cita_texto))


elif tipo == "Norma":
    pais = st.text_input("País (ejemplo: CHILE)")
    tipo_norma = st.text_input("Tipo de norma (ejemplo: Ley N°)")
    nombre_norma = st.text_input("Nombre o número de la norma")
    fecha = st.text_input("Fecha de publicación (dd/mm/aaaa) (opcional)")

    if st.button("Generar cita"):
        datos = {
            'pais': pais,
            'tipo_norma': tipo_norma,
            'nombre_norma': nombre_norma,
            'fecha': fecha
        }
        ref_texto = generar_referencia_norma(datos)
        cita_texto = f"{versalitas(pais)}, {tipo_norma} {nombre_norma}."

        st.subheader("Referencia completa:")
        st.write(ref_texto)
        st.text_area("Copiar referencia completa:", value=ref_texto, height=80)

        st.subheader("Cita abreviada:")
        st.write(cita_texto)
        st.text_area("Copiar cita abreviada:", value=cita_texto, height=40)

        st.session_state.setdefault("historial", []).append((ref_texto, cita_texto))


elif tipo == "Jurisprudencia":
    tribunal = st.text_input("Tribunal")
    fecha = st.text_input("Fecha (dd/mm/aaaa)")
    rol = st.text_input("Rol (opcional)")
    nombre_caso = st.text_input("Nombre del caso (opcional)")
    info_extra = st.text_input("Información extra (opcional)")

    if st.button("Generar cita"):
        datos = {
            'tribunal': tribunal,
            'fecha': fecha,
            'rol': rol,
            'nombre_caso': nombre_caso,
            'info_extra': info_extra
        }
        ref_texto = generar_referencia_jurisprudencia(datos)
        cita_texto = ref_texto  # Igual que referencia

        st.subheader("Referencia completa:")
        st.write(ref_texto)
        st.text_area("Copiar referencia completa:", value=ref_texto, height=80)

        st.subheader("Cita abreviada:")
        st.write(cita_texto)
        st.text_area("Copiar cita abreviada:", value=cita_texto, height=40)

        st.session_state.setdefault("historial", []).append((ref_texto, cita_texto))


elif tipo == "Página web o blog":
    autor_sin_autor = None
    if num_autores == 0:
        autor_sin_autor = st.text_input("Autor o entidad responsable (si no hay autores)")

    año = st.text_input("Año (puede ser aproximado)")
    titulo = st.text_input("Título del documento o entrada")
    url = st.text_input("URL")
    fecha_consulta = st.text_input("Fecha de consulta (dd/mm/aaaa) (opcional)")

    if st.button("Generar cita"):
        datos = {
            'autores': autores if autores else None,
            'autor_sin_autor': autor_sin_autor,
            'año': año,
            'titulo': titulo,
            'url': url,
            'fecha_consulta': fecha_consulta
        }
        ref_texto = generar_referencia_web(datos)
        cita_texto = f"{formatear_autores_revista(autores) if autores else autor_sin_autor} ({año})"

        st.subheader("Referencia completa:")
        st.write(ref_texto)
        st.text_area("Copiar referencia completa:", value=ref_texto, height=80)

        st.subheader("Cita abreviada:")
        st.write(cita_texto)
        st.text_area("Copiar cita abreviada:", value=cita_texto, height=40)

        st.session_state.setdefault("historial", []).append((ref_texto, cita_texto))


elif tipo == "Tesis":
    año = st.text_input("Año de publicación")
    titulo = st.text_input("Título de la tesis")
    grado = st.text_input("Grado académico (ejemplo: Tesis para optar al título de Ingeniero Civil)")
    institucion = st.text_input("Institución")

    if st.button("Generar cita"):
        datos = {
            'autores': autores,
            'año': año,
            'titulo': titulo,
            'grado': grado,
            'institucion': institucion
        }
        ref_html = generar_referencia_tesis(datos)
        cita_texto = cita_abreviada_autores(autores, año)

        ref_texto = limpiar_html_a_texto(ref_html)

        st.subheader("Referencia completa:")
        st.markdown(ref_html, unsafe_allow_html=True)
        st.text_area("Copiar referencia completa:", value=ref_texto, height=80)

        st.subheader("Cita abreviada:")
        st.write(cita_texto)
        st.text_area("Copiar cita abreviada:", value=cita_texto, height=40)

        st.session_state.setdefault("historial", []).append((ref_html, cita_texto))


# Historial de citas generadas
if "historial" in st.session_state and st.session_state["historial"]:
    st.markdown("---")
    st.subheader("Historial de citas generadas")
    for i, (ref, cita) in enumerate(reversed(st.session_state["historial"])):
        st.markdown(f"**{len(st.session_state['historial']) - i}. Referencia completa:**")
        if "<span" in ref or "<i>" in ref:
            st.markdown(ref, unsafe_allow_html=True)
        else:
            st.write(ref)
        st.markdown(f"**Cita abreviada:** {cita}")
        st.markdown("")


