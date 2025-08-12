import streamlit as st

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

def cita_abreviada_autores(autores, año, paginas=None, tomo=None, letra=None):
    n = len(autores)
    if letra:
        año = f"{año}{letra}"
    if n == 0:
        return ""
    if n == 1:
        ap = versalitas(autores[0]['apellido1'])
        tomo_str = f" Tomo {tomo}," if tomo else ""
        paginas_str = f" p. {paginas}" if paginas else ""
        return f"{ap} ({año}){tomo_str}{paginas_str}"
    elif 2 <= n <= 3:
        aps = [versalitas(a['apellido1']) for a in autores]
        ap_str = " y ".join(aps)
        paginas_str = f" p. {paginas}" if paginas else ""
        return f"{ap_str} ({año}){paginas_str}"
    else:
        ap = versalitas(autores[0]['apellido1'])
        paginas_str = f" p. {paginas}" if paginas else ""
        return f"{ap} y otros ({año}){paginas_str}"

def agregar_autores(num):
    autores = []
    for i in range(num):
        st.markdown(f"**Autor {i+1}**")
        apellido1 = st.text_input(f"Primer apellido autor {i+1}", key=f"ape1_{i}")
        apellido2 = st.text_input(f"Segundo apellido autor {i+1} (opcional)", key=f"ape2_{i}")
        nombre = st.text_input(f"Nombre autor {i+1}", key=f"nom_{i}")
        autores.append({'apellido1': apellido1.strip(), 'apellido2': apellido2.strip(), 'nombre': nombre.strip()})
    return autores

def generar_referencia_libro(datos):
    autores = formatear_autores_revista(datos['autores'])
    año = datos['año']
    titulo = datos['titulo']
    ciudad = datos['ciudad']
    editorial = datos['editorial']
    edicion = datos.get('edicion')
    tomo = datos.get('tomo')
    ed_str = f", {edicion}" if edicion else ""
    tomo_str = f", {tomo}" if tomo else ""
    return f"{autores} ({año}): {titulo}{tomo_str} ({ciudad}, {editorial}{ed_str})."

def generar_referencia_traduccion_libro(datos):
    autores = formatear_autores_revista(datos['autores'])
    año_original = datos['año_original']
    año = datos['año']
    titulo = datos['titulo']
    traductor = datos['traductor']
    ciudad = datos['ciudad']
    editorial = datos['editorial']
    return f"{autores} ([{año_original}] {año}): {titulo} (trad. {traductor}, {ciudad}, {editorial})."

def generar_referencia_capitulo_libro(datos):
    autor_capitulo = formatear_autores_revista(datos['autor_capitulo'])
    año = datos['año']
    titulo_cap = datos['titulo_capitulo']
    editor = formatear_autores_revista(datos['editores'])
    titulo_libro = datos['titulo_libro']
    ciudad = datos['ciudad']
    editorial = datos['editorial']
    paginas = datos['paginas']
    return f"{autor_capitulo} ({año}): “{titulo_cap}”, en {editor} (edit.), {titulo_libro} ({ciudad}, {editorial}) pp. {paginas}."

def generar_referencia_articulo_revista(datos):
    autores = formatear_autores_revista(datos['autores'])
    año = datos['año']
    titulo_articulo = datos['titulo']
    revista = datos['revista']
    volumen = datos.get('volumen')
    numero = datos.get('numero')
    paginas = datos.get('paginas')
    doi = datos.get('doi')
    ref = f"{autores} ({año}): “{titulo_articulo}”, {revista}"
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
    tribunal = datos['tribunal']
    fecha = datos['fecha']
    rol = datos.get('rol')
    nombre_caso = datos.get('nombre_caso')
    info_extra = datos.get('info_extra')
    ref = f"{versalitas(tribunal)}, {fecha}"
    if rol:
        ref += f", rol {rol}"
    if nombre_caso:
        ref += f" ({nombre_caso})"
    if info_extra:
        ref += f", {info_extra}"
    ref += "."
    return ref

def generar_referencia_web(datos):
    autor = formatear_autores_revista(datos.get('autores', [])) if datos.get('autores') else datos.get('autor_sin_autor')
    año = datos.get('año')
    titulo = datos.get('titulo')
    url = datos.get('url')
    fecha_consulta = datos.get('fecha_consulta')
    ref = f"{autor} ({año}): {titulo}, Disponible en: {url}."
    if fecha_consulta:
        ref += f" Fecha de consulta: {fecha_consulta}."
    return ref

def generar_referencia_tesis(datos):
    autor = formatear_autores_revista(datos['autores'])
    año = datos['año']
    titulo = datos['titulo']
    grado = datos['grado']
    institucion = datos['institucion']
    return f"{autor} ({año}): {titulo}. {grado}. {institucion}."

# Guarda citas en la sesión
if "historial" not in st.session_state:
    st.session_state.historial = []

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
        ref = generar_referencia_libro(datos)
        cita = cita_abreviada_autores(autores, año, tomo=tomo)
        st.subheader("Referencia completa:")
        st.write(ref)
        st.subheader("Cita abreviada:")
        st.write(cita)
        st.session_state.historial.append((ref, cita))

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
        ref = generar_referencia_traduccion_libro(datos)
        cita = cita_abreviada_autores(autores, año)
        st.subheader("Referencia completa:")
        st.write(ref)
        st.subheader("Cita abreviada:")
        st.write(cita)
        st.session_state.historial.append((ref, cita))

elif tipo == "Capítulo de libro":
    num_autores_cap = st.number_input("Número de autores del capítulo", min_value=1, max_value=10, value=1, key="cap_num_autores")
    autor_capitulo = []
    if num_autores_cap > 0:
        autor_capitulo = []
        for i in range(num_autores_cap):
            st.markdown(f"**Autor capítulo {i+1}**")
            apellido1 = st.text_input(f"Primer apellido autor capítulo {i+1}", key=f"cap_ape1_{i}")
            apellido2 = st.text_input(f"Segundo apellido autor capítulo {i+1} (opcional)", key=f"cap_ape2_{i}")
            nombre = st.text_input(f"Nombre autor capítulo {i+1}", key=f"cap_nom_{i}")
            autor_capitulo.append({'apellido1': apellido1.strip(), 'apellido2': apellido2.strip(), 'nombre': nombre.strip()})
    año = st.text_input("Año de publicación")
    titulo_capitulo = st.text_input("Título del capítulo")
    num_editores = st.number_input("Número de editores", min_value=1, max_value=10, value=1, key="cap_num_edit")
    editores = []
    if num_editores > 0:
        for i in range(num_editores):
            st.markdown(f"**Editor {i+1}**")
            apellido1 = st.text_input(f"Primer apellido editor {i+1}", key=f"edit_ape1_{i}")
            apellido2 = st.text_input(f"Segundo apellido editor {i+1} (opcional)", key=f"edit_ape2_{i}")
            nombre = st.text_input(f"Nombre editor {i+1}", key=f"edit_nom_{i}")
            editores.append({'apellido1': apellido1.strip(), 'apellido2': apellido2.strip(), 'nombre': nombre.strip()})
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
        ref = generar_referencia_capitulo_libro(datos)
        cita = cita_abreviada_autores(autor_capitulo, año, paginas=paginas)
        st.subheader("Referencia completa:")
        st.write(ref)
        st.subheader("Cita abreviada:")
        st.write(cita)
        st.session_state.historial.append((ref, cita))

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
        ref = generar_referencia_articulo_revista(datos)
        cita = cita_abreviada_autores(autores, año, paginas=paginas)
        st.subheader("Referencia completa:")
        st.write(ref)
        st.subheader("Cita abreviada:")
        st.write(cita)
        st.session_state.historial.append((ref, cita))

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
        ref = generar_referencia_norma(datos)
        cita = f"{versalitas(pais)}, {tipo_norma} {nombre_norma}."
        st.subheader("Referencia completa:")
        st.write(ref)
        st.subheader("Cita abreviada:")
        st.write(cita)
        st.session_state.historial.append((ref, cita))

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
        ref = generar_referencia_jurisprudencia(datos)
        # Para cita abreviada igual que referencia pero más corta, aquí simplificamos
        cita = ref
        st.subheader("Referencia completa:")
        st.write(ref)
        st.subheader("Cita abreviada:")
        st.write(cita)
        st.session_state.historial.append((ref, cita))

elif tipo == "Página web o blog":
    autor_sin_autor = None
    if num_autores == 0:
        autor_sin_autor = st.text_input("Autor o entidad responsable (si no hay autores)")

    año = st.text_input("Año (puede ser aproximado)")
    titulo = st.text_input("Título de la página o artículo")
    url = st.text_input("URL completa")
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
        ref = generar_referencia_web(datos)
        cita = ref  # Se usa igual referencia para cita abreviada en web
        st.subheader("Referencia completa:")
        st.write(ref)
        st.subheader("Cita abreviada:")
        st.write(cita)
        st.session_state.historial.append((ref, cita))

elif tipo == "Tesis":
    año = st.text_input("Año")
    titulo = st.text_input("Título de la tesis")
    grado = st.text_input("Grado académico (ej. Licenciatura, Magíster)")
    institucion = st.text_input("Institución académica")

    if st.button("Generar cita"):
        datos = {
            'autores': autores,
            'año': año,
            'titulo': titulo,
            'grado': grado,
            'institucion': institucion
        }
        ref = generar_referencia_tesis(datos)
        cita = cita_abreviada_autores(autores, año)
        st.subheader("Referencia completa:")
        st.write(ref)
        st.subheader("Cita abreviada:")
        st.write(cita)
        st.session_state.historial.append((ref, cita))

# Mostrar historial
if st.session_state.historial:
    st.markdown("---")
    st.subheader("Historial de citas generadas")
    for i, (ref, cita) in enumerate(st.session_state.historial[::-1]):
        st.markdown(f"**{len(st.session_state.historial)-i}. Referencia completa:** {ref}")
        st.markdown(f"**Cita abreviada:** {cita}")
        st.markdown("")



