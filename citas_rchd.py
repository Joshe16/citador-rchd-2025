import streamlit as st
from datetime import datetime
import io
import re

# =========================
# Utilidades de formato
# =========================

def versalitas(txt: str) -> str:
    return (txt or "").upper()

def span_versalitas(txt: str) -> str:
    if not txt:
        return ""
    return f"<span style='font-variant: small-caps'>{versalitas(txt)}</span>"

def italics(txt: str) -> str:
    return f"<i>{txt}</i>" if txt else ""

def smart_join(items, sep=", ", last_sep=" y "):
    items = [x for x in items if x]
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return sep.join(items[:-1]) + last_sep + items[-1]

def limpiar_html_a_texto(html_text: str) -> str:
    # Sencillo "stripping" de HTML para copiar como texto plano
    return re.sub(r"<[^>]+>", "", html_text or "").replace("&nbsp;", " ").strip()

# =========================
# Formato de autores
# =========================

def _autor_html(a):
    ap = versalitas(a.get("apellido1","").strip())
    ap2 = versalitas(a.get("apellido2","").strip())
    ap_full = ap if not ap2 else f"{ap} {ap2}"
    return f"{span_versalitas(ap_full)}, {a.get('nombre','').strip()}"

def _autor_txt(a):
    ap = versalitas(a.get("apellido1","").strip())
    ap2 = versalitas(a.get("apellido2","").strip())
    ap_full = ap if not ap2 else f"{ap} {ap2}"
    return f"{ap_full}, {a.get('nombre','').strip()}"

def format_authors_html(autores):
    n = len(autores)
    if n == 0:
        return ""
    if n == 1:
        return _autor_html(autores[0])
    elif 2 <= n <= 3:
        return smart_join([_autor_html(a) for a in autores])
    else:
        return f"{_autor_html(autores[0])} y otros"

def format_authors_txt(autores):
    n = len(autores)
    if n == 0:
        return ""
    if n == 1:
        return _autor_txt(autores[0])
    elif 2 <= n <= 3:
        return smart_join([_autor_txt(a) for a in autores])
    else:
        return f"{_autor_txt(autores[0])} y otros"

def format_solo_apellidos_html(autores):
    """Para abreviadas: solo apellido(s) del/los autores en versalitas."""
    n = len(autores)
    if n == 0:
        return ""
    if n == 1:
        ap = versalitas(autores[0].get("apellido1",""))
        return span_versalitas(ap)
    elif 2 <= n <= 3:
        aps = [span_versalitas(versalitas(a.get("apellido1",""))) for a in autores]
        return smart_join(aps)
    else:
        ap = versalitas(autores[0].get("apellido1",""))
        return f"{span_versalitas(ap)} y otros"

def format_solo_apellidos_txt(autores):
    n = len(autores)
    if n == 0:
        return ""
    if n == 1:
        return versalitas(autores[0].get("apellido1",""))
    elif 2 <= n <= 3:
        return smart_join([versalitas(a.get("apellido1","")) for a in autores])
    else:
        return f"{versalitas(autores[0].get('apellido1',''))} y otros"

# =========================
# Abreviadas (2.7)
# =========================

def cita_abreviada_obras(autores, año, paginas=None, tomo=None, letra=None, cap_sec=None, parrafo=None):
    """
    Regla general 2.7.1
    - Apellido(s) del autor (versalita), (año(+letra)), [Tomo I,] p./pp. X-Y
    - eBooks sin páginas: (capítulo/sección, párrafo)
    """
    yr = f"{año}{letra}" if letra else f"{año}"

    # eBook sin páginas (capítulo/sección/párrafo)
    if cap_sec or parrafo:
        base = f"{format_solo_apellidos_txt(autores)} ({yr})"
        partes = []
        if cap_sec:
            partes.append(str(cap_sec))
        if parrafo:
            # “párr. 2”
            partes.append(f"párr. {parrafo}")
        return f"{base} {', '.join(partes)}."

    # Con tomos y/o páginas
    t = f", Tomo {tomo}" if tomo else ""
    p = ""
    if paginas:
        # si tiene guion -> pp., si es única -> p.
        p = f", pp. {paginas}" if "-" in paginas or "–" in paginas or "y" in paginas else f", p. {paginas}"
    return f"{format_solo_apellidos_txt(autores)} ({yr}){t}{p}."

def cita_abreviada_normas(pais, nombre_o_num):
    # 2.7.2
    return f"{versalitas(pais)}, {nombre_o_num}."

def cita_abreviada_jurisprudencia(tribunal, nombre_caso=None, fecha=None, pinpoint=None):
    # 2.7.3
    # tribunal + (nombre caso o fecha) + pinpoint (cons./párr./pág.)
    base = f"{versalitas(tribunal)}"
    cuerpo = nombre_caso if nombre_caso else (fecha or "")
    if cuerpo:
        base += f", {cuerpo}"
    if pinpoint:
        base += f", {pinpoint}"
    base += "."
    return base

# =========================
# Esquema de campos por tipo
# =========================

# Cada tipo define:
#  - 'label'        : nombre en UI
#  - 'fields'       : lista de campos (name,label,optional,kind)
#  - 'render_html'  : función -> referencia completa (HTML)
#  - 'render_txt'   : función -> referencia completa (texto plano)
#  - 'short'        : función -> cita abreviada (texto)
#  - 'w_authors'    : bool, si usa autores del bloque principal
#  - 'w_editors'    : bool, si usa editores
#  - 'note'         : tips opcionales

# Helpers de entrada
def input_autores(key_prefix="", titulo="Autores", minimo=0):
    autores = []
    st.markdown(f"**{titulo}**")
    n = st.number_input(f"Número de {titulo.lower()}", min_value=minimo, max_value=10, value=minimo, key=f"{key_prefix}_n")
    for i in range(n):
        col1, col2, col3 = st.columns([1,1,1.2])
        with col1:
            a1 = st.text_input(f"Primer apellido {i+1}", key=f"{key_prefix}_a1_{i}")
        with col2:
            a2 = st.text_input(f"Segundo apellido {i+1} (opcional)", key=f"{key_prefix}_a2_{i}")
        with col3:
            nom = st.text_input(f"Nombre {i+1}", key=f"{key_prefix}_nom_{i}")
        autores.append({"apellido1": a1.strip(), "apellido2": a2.strip(), "nombre": nom.strip()})
    return autores

def input_field(field, key_prefix=""):
    kind = field.get("kind","text")
    opt = field.get("optional", False)
    label = field["label"] + (" (opcional)" if opt else "")
    key = f"{key_prefix}_{field['name']}"
    if kind == "text":
        return st.text_input(label, key=key)
    if kind == "textarea":
        return st.text_area(label, key=key, height=80)
    if kind == "date":
        s = st.text_input(label, key=key, placeholder="dd/mm/aaaa")
        return s
    if kind == "select":
        return st.selectbox(label, field.get("options",[]), key=key)
    return st.text_input(label, key=key)

# =========================
# Renderizadores por tipo
# =========================

def RCHD_libro_html(d):
    # a) Libro (1, 2-3, 4+ autores) y d) tomos
    autores = format_authors_html(d["autores"])
    t = italics(d["titulo"])
    tomo = f", {d['tomo']}" if d.get("tomo") else ""
    ed = f", {d['edicion']}" if d.get("edicion") else ""
    return f"{autores} ({d['anio']}): {t}{tomo} ({d['ciudad']}, {d['editorial']}{ed})."

def RCHD_libro_txt(d):
    autores = format_authors_txt(d["autores"])
    t = d["titulo"]
    tomo = f", {d['tomo']}" if d.get("tomo") else ""
    ed = f", {d['edicion']}" if d.get("edicion") else ""
    return f"{autores} ({d['anio']}): {t}{tomo} ({d['ciudad']}, {d['editorial']}{ed})."

def RCHD_traduccion_libro_html(d):
    autores = format_authors_html(d["autores"])
    t = italics(d["titulo"])
    return f"{autores} ([{d['anio_original']}] {d['anio']}): {t} (trad. {d['traductor']}, {d['ciudad']}, {d['editorial']})."

def RCHD_traduccion_libro_txt(d):
    autores = format_authors_txt(d["autores"])
    t = d["titulo"]
    return f"{autores} ([{d['anio_original']}] {d['anio']}): {t} (trad. {d['traductor']}, {d['ciudad']}, {d['editorial']})."

def RCHD_traduccion_articulo_html(d):
    # e) ii. Traducción de artículo
    autores = format_authors_html(d["autores"])
    t = f"“{d['titulo_articulo']}”"
    rev = d["revista"]
    vol = f", vol. {d['volumen']}" if d.get("volumen") else ""
    num = f", Nº {d['numero']}" if d.get("numero") else ""
    pgs = f": pp. {d['paginas']}" if d.get("paginas") else ""
    ttrad = f" (trad. {d['traductor']})" if d.get("traductor") else ""
    an = d["anio"]
    if d.get("anio_original"):
        an = f"[{d['anio_original']}] {d['anio']}"
    return f"{autores} ({an}): {t}, {rev}{vol}{num}{pgs}{ttrad}."

def RCHD_traduccion_articulo_txt(d):
    autores = format_authors_txt(d["autores"])
    t = f"“{d['titulo_articulo']}”"
    rev = d["revista"]
    vol = f", vol. {d['volumen']}" if d.get("volumen") else ""
    num = f", Nº {d['numero']}" if d.get("numero") else ""
    pgs = f": pp. {d['paginas']}" if d.get("paginas") else ""
    ttrad = f" (trad. {d['traductor']})" if d.get("traductor") else ""
    an = d["anio"]
    if d.get("anio_original"):
        an = f"[{d['anio_original']}] {d['anio']}"
    return f"{autores} ({an}): {t}, {rev}{vol}{num}{pgs}{ttrad}."

def RCHD_capitulo_editor_html(d):
    # f) editor (singular) / g) editores (plural) -> detectamos plural según cantidad
    autor_cap = format_authors_html(d["autores_cap"])
    editores = format_authors_html(d["editores"])
    etiqueta = "(edit.)" if len(d["editores"]) == 1 else "(edits.)"
    tcap = f"“{d['titulo_cap']}”"
    tlib = italics(d["titulo_libro"])
    return f"{autor_cap} ({d['anio']}): {tcap}, en {editores} {etiqueta}, {tlib} ({d['ciudad']}, {d['editorial']}) pp. {d['paginas']}."

def RCHD_capitulo_editor_txt(d):
    autor_cap = format_authors_txt(d["autores_cap"])
    editores = format_authors_txt(d["editores"])
    etiqueta = "(edit.)" if len(d["editores"]) == 1 else "(edits.)"
    tcap = f"“{d['titulo_cap']}”"
    tlib = d["titulo_libro"]
    return f"{autor_cap} ({d['anio']}): {tcap}, en {editores} {etiqueta}, {tlib} ({d['ciudad']}, {d['editorial']}) pp. {d['paginas']}."

def RCHD_articulo_revista_html(d):
    autores = format_authors_html(d["autores"])
    t = f"“{d['titulo_art']}”"
    rev = d["revista"]
    vol = f", vol. {d['volumen']}" if d.get("volumen") else ""
    num = f", N° {d['numero']}" if d.get("numero") else ""
    pgs = f": pp. {d['paginas']}" if d.get("paginas") else ""
    doi = f". DOI: {d['doi']}" if d.get("doi") else ""
    return f"{autores} ({d['anio']}): {t}, {rev}{vol}{num}{pgs}{doi}."

def RCHD_articulo_revista_txt(d):
    autores = format_authors_txt(d["autores"])
    t = f"“{d['titulo_art']}”"
    rev = d["revista"]
    vol = f", vol. {d['volumen']}" if d.get("volumen") else ""
    num = f", N° {d['numero']}" if d.get("numero") else ""
    pgs = f": pp. {d['paginas']}" if d.get("paginas") else ""
    doi = f". DOI: {d['doi']}" if d.get("doi") else ""
    return f"{autores} ({d['anio']}): {t}, {rev}{vol}{num}{pgs}{doi}."

def RCHD_articulo_sin_pags_html(d):
    # i) sin vol/núm o sin páginas -> usamos DOI o Vol con DOI
    autores = format_authors_html(d["autores"])
    t = f"“{d['titulo_art']}”"
    rev = d["revista"]
    trozos = [f"{autores} ({d['anio']}): {t}, {rev}"]
    if d.get("volumen"):
        trozos.append(f"Vol. {d['volumen']}")
    if d.get("doi"):
        trozos.append(d["doi"])
        cuerpo = ", ".join(trozos) + "."
    else:
        cuerpo = ", ".join(trozos) + "."
    return cuerpo

def RCHD_articulo_sin_pags_txt(d):
    autores = format_authors_txt(d["autores"])
    t = f"“{d['titulo_art']}”"
    rev = d["revista"]
    trozos = [f"{autores} ({d['anio']}): {t}, {rev}"]
    if d.get("volumen"):
        trozos.append(f"Vol. {d['volumen']}")
    if d.get("doi"):
        trozos.append(d["doi"])
        cuerpo = ", ".join(trozos) + "."
    else:
        cuerpo = ", ".join(trozos) + "."
    return cuerpo

def RCHD_no_latino_html(d):
    # j) Autor con nombre original + traducción título + revista/datos
    autor = f"{span_versalitas(versalitas(d['apellidos_latinos']))}, {d['nombres_latinos']} ({d['anio']})"
    titulo_ori = f"“{d['titulo_original']}”"
    titulo_trad = f"“{d['titulo_trad']}”" if d.get("titulo_trad") else ""
    revista_ori = d.get("revista_original","")
    if d.get("numero"):
        revista_ori += f", N° {d['numero']}"
    pgs = f": pp. {d['paginas']}" if d.get("paginas") else ""
    tit = f"{titulo_ori} ({titulo_trad})" if titulo_trad else titulo_ori
    return f"{autor}: {tit}, {revista_ori}{pgs}."

def RCHD_no_latino_txt(d):
    autor = f"{versalitas(d['apellidos_latinos'])}, {d['nombres_latinos']} ({d['anio']})"
    titulo_ori = f"“{d['titulo_original']}”"
    titulo_trad = f"“{d['titulo_trad']}”" if d.get("titulo_trad") else ""
    revista_ori = d.get("revista_original","")
    if d.get("numero"):
        revista_ori += f", N° {d['numero']}"
    pgs = f": pp. {d['paginas']}" if d.get("paginas") else ""
    tit = f"{titulo_ori} ({titulo_trad})" if titulo_trad else titulo_ori
    return f"{autor}: {tit}, {revista_ori}{pgs}."

def RCHD_ebook_html(d):
    # k) e-book sin páginas
    autores = format_authors_html(d["autores"])
    t = f"“{d['titulo_cap'] or d['titulo']}”" if d.get("titulo_cap") else italics(d["titulo"])
    ed = f": {d['edicion_plataforma']}" if d.get("edicion_plataforma") else ""
    loc = f", N° {d['ubicacion_num']}" if d.get("ubicacion_num") else ""
    return f"{autores} ({d['anio']}): {t}, {italics(d['cont_in']} {italics(d['cont_de']) if d.get('cont_de') else ''}){ed}{loc}."

def RCHD_ebook_txt(d):
    autores = format_authors_txt(d["autores"])
    t = f"“{d['titulo_cap'] or d['titulo']}”" if d.get("titulo_cap") else d["titulo"]
    ed = f": {d['edicion_plataforma']}" if d.get("edicion_plataforma") else ""
    loc = f", N° {d['ubicacion_num']}" if d.get("ubicacion_num") else ""
    # Contenedor (ej. en MAURER... Autonomous Driving ...)
    cont = f"en {d['cont_in']}" if d.get("cont_in") else ""
    if d.get("cont_de"):
        cont += f" {d['cont_de']}"
    return f"{autores} ({d['anio']}): {t}, {cont}{ed}{loc}."

def RCHD_manuscrito_html(d):
    # l) Fuente manuscrita
    ent = span_versalitas(d["entidad"])
    fondo = d["fondo"]
    desc = d["descripcion"]
    fecha = d["fecha"]
    return f"{ent} - {fondo}: {desc}, {fecha}."

def RCHD_manuscrito_txt(d):
    ent = versalitas(d["entidad"])
    fondo = d["fondo"]
    desc = d["descripcion"]
    fecha = d["fecha"]
    return f"{ent} - {fondo}: {desc}, {fecha}."

def RCHD_dogmatica_hist_html(d):
    # m) Obras dogmáticas con sistemas históricos (input libre)
    return d["cita_bruta"].strip().rstrip(".") + "."

def RCHD_dogmatica_hist_txt(d):
    return d["cita_bruta"].strip().rstrip(".") + "."

def RCHD_tesis_html(d):
    # n) Tesis/memoria
    autores = format_authors_html(d["autores"])
    t = italics(d["titulo"])
    return f"{autores} ({d['anio']}): {t}. {d['grado']}. {d['institucion']}."

def RCHD_tesis_txt(d):
    autores = format_authors_txt(d["autores"])
    t = d["titulo"]
    return f"{autores} ({d['anio']}): {t}. {d['grado']}. {d['institucion']}."

def RCHD_informe_html(d):
    # o) Informes institucionales
    org = f"{span_versalitas(d['org'])}"
    unidad = f", {span_versalitas(d['unidad'])}" if d.get("unidad") else ""
    t = f": “{d['titulo']}”"
    num = f", {d['numero']}" if d.get("numero") else ""
    extra = f", {d['extra']}" if d.get("extra") else ""
    sd = " (s.d.)" if d.get("sd") else ""
    return f"{org}{unidad}{t}{num}{extra}{sd}."

def RCHD_informe_txt(d):
    org = versalitas(d["org"])
    unidad = f", {versalitas(d['unidad'])}" if d.get("unidad") else ""
    t = f": “{d['titulo']}”"
    num = f", {d['numero']}" if d.get("numero") else ""
    extra = f", {d['extra']}" if d.get("extra") else ""
    sd = " (s.d.)" if d.get("sd") else ""
    return f"{org}{unidad}{t}{num}{extra}{sd}."

def RCHD_doc_web_html(d):
    # p) Documentos alojados en sitios web (no libros/artículos)
    encabezado = d["encabezado"]  # “Lo que corresponda según el tipo…”
    disp = f" Disponible en: {d['url']}."
    fcons = f" Fecha de consulta: {d['fecha_consulta']}." if d.get("fecha_consulta") else ""
    return f"{encabezado}{disp}{fcons}"

def RCHD_doc_web_txt(d):
    encabezado = d["encabezado"]
    disp = f" Disponible en: {d['url']}."
    fcons = f" Fecha de consulta: {d['fecha_consulta']}." if d.get("fecha_consulta") else ""
    return f"{encabezado}{disp}{fcons}"

def RCHD_diario_sin_autor_html(d):
    # q.a) Periódico sin autor
    per = d["periodico"]
    fecha = d["fecha"]
    tit = f"“{d['titulo']}”"
    pag = f", p. {d['pagina']}" if d.get("pagina") else ""
    return f"{versalitas(per)} ({fecha}): {tit}{pag}."

def RCHD_diario_sin_autor_txt(d):
    per = d["periodico"]
    fecha = d["fecha"]
    tit = f"“{d['titulo']}”"
    pag = f", p. {d['pagina']}" if d.get("pagina") else ""
    return f"{versalitas(per)} ({fecha}): {tit}{pag}."

def RCHD_diario_con_autor_html(d):
    # q.b) Periódico con autor
    autores = format_authors_html(d["autores"])
    fecha = d["fecha"]
    tit = f"“{d['titulo']}”"
    per = d["periodico"]
    pag = f", p. {d['pagina']}" if d.get("pagina") else ""
    return f"{autores} ({fecha}): {tit}, {per}{pag}."

def RCHD_diario_con_autor_txt(d):
    autores = format_authors_txt(d["autores"])
    fecha = d["fecha"]
    tit = f"“{d['titulo']}”"
    per = d["periodico"]
    pag = f", p. {d['pagina']}" if d.get("pagina") else ""
    return f"{autores} ({fecha}): {tit}, {per}{pag}."

def RCHD_noticias_web_html(d):
    # r) Noticias/columnas en sitios web
    autores = format_authors_html(d["autores"])
    tit = f"“{d['titulo']}”"
    medio = d["medio"]
    url = d["url"]
    fcons = d.get("fecha_consulta")
    base = f"{autores} ({d['anio']}): {tit}, {medio}. Disponible en: {url}."
    if fcons:
        base += f" Fecha de consulta: {fcons}."
    return base

def RCHD_noticias_web_txt(d):
    autores = format_authors_txt(d["autores"])
    tit = f"“{d['titulo']}”"
    medio = d["medio"]
    url = d["url"]
    fcons = d.get("fecha_consulta")
    base = f"{autores} ({d['anio']}): {tit}, {medio}. Disponible en: {url}."
    if fcons:
        base += f" Fecha de consulta: {fcons}."
    return base

def RCHD_sitio_web_html(d):
    # s) Página web / blog institucional
    ent = span_versalitas(d["entidad"])
    anio = d["anio"]
    titulo = d["titulo"]
    url = d["url"]
    fcons = d["fecha_consulta"]
    return f"{ent} (sitio web, {anio}): {titulo}. Disponible en: {url}. Fecha de consulta: {fcons}."

def RCHD_sitio_web_txt(d):
    ent = versalitas(d["entidad"])
    anio = d["anio"]
    titulo = d["titulo"]
    url = d["url"]
    fcons = d["fecha_consulta"]
    return f"{ent} (sitio web, {anio}): {titulo}. Disponible en: {url}. Fecha de consulta: {fcons}."

# -------- Normas (2.6.2)

def RCHD_constitucion_html(d):
    return f"{versalitas(d['pais'])}, {italics('Constitución Política de la República')} ({d['fecha']})."

def RCHD_constitucion_txt(d):
    return f"{versalitas(d['pais'])}, Constitución Política de la República ({d['fecha']})."

def RCHD_ley_no_cod_html(d):
    return f"{versalitas(d['pais'])}, Ley N° {d['numero']}. {italics(d['denominacion'])} ({d['fecha']})."

def RCHD_ley_no_cod_txt(d):
    return f"{versalitas(d['pais'])}, Ley N° {d['numero']}. {d['denominacion']} ({d['fecha']})."

def RCHD_codigo_html(d):
    fecha = f" ({d['fecha']})" if d.get("fecha") else " (s.d.)." if d.get("sd") else ""
    return f"{versalitas(d['pais'])}, {italics(d['nombre'])}{fecha if fecha else ''}"

def RCHD_codigo_txt(d):
    fecha = f" ({d['fecha']})" if d.get("fecha") else " (s.d.)." if d.get("sd") else ""
    return f"{versalitas(d['pais'])}, {d['nombre']}{fecha if fecha else ''}"

def RCHD_decreto_html(d):
    return f"{versalitas(d['pais'])}, {versalitas(d['organismo'])}, Decreto Supremo {d['numero']}, {d['denominacion']} ({d['fecha']})."

def RCHD_decreto_txt(d):
    return f"{versalitas(d['pais'])}, {versalitas(d['organismo'])}, Decreto Supremo {d['numero']}, {d['denominacion']} ({d['fecha']})."

def RCHD_oficio_html(d):
    return f"{versalitas(d['pais'])}, {versalitas(d['emisor'])}, Ord. {d['numero']}, {d['descripcion']} ({d['fecha']})."

def RCHD_oficio_txt(d):
    return f"{versalitas(d['pais'])}, {versalitas(d['emisor'])}, Ord. {d['numero']}, {d['descripcion']} ({d['fecha']})."

def RCHD_proyecto_ley_html(d):
    return f"{versalitas(d['pais'])}, {d['descripcion']} (boletín N° {d['boletin']})."

def RCHD_proyecto_ley_txt(d):
    return f"{versalitas(d['pais'])}, {d['descripcion']} (boletín N° {d['boletin']})."

def RCHD_historia_ley_html(d):
    return f"{versalitas(d['entidad'])} ({d['anio']}): {italics(d['titulo'])}, {d['instancia']}; {d['detalle']}. Disponible en: {d['url']}. Fecha de consulta: {d['fecha_consulta']}."
def RCHD_historia_ley_txt(d):
    return f"{versalitas(d['entidad'])} ({d['anio']}): {d['titulo']}, {d['instancia']}; {d['detalle']}. Disponible en: {d['url']}. Fecha de consulta: {d['fecha_consulta']}."

def RCHD_tratado_html(d):
    return f"{italics(d['nombre'])} ({d['fecha_adop']})."

def RCHD_tratado_txt(d):
    return f"{d['nombre']} ({d['fecha_adop']})."

def RCHD_congreso_intern_html(d):
    return f"{versalitas(d['evento'])}: “{d['titulo']}” ({d['lugar']}, {d['rango_fechas']})."

def RCHD_congreso_intern_txt(d):
    return f"{versalitas(d['evento'])}: “{d['titulo']}” ({d['lugar']}, {d['rango_fechas']})."

def RCHD_doc_onu_html(d):
    return f"{versalitas('NACIONES UNIDAS')}, {versalitas(d['organo'])}: “{d['titulo']}”, {d['signatura']} ({d['fecha']})."
def RCHD_doc_onu_txt(d):
    return f"{versalitas('NACIONES UNIDAS')}, {versalitas(d['organo'])}: “{d['titulo']}”, {d['signatura']} ({d['fecha']})."

def RCHD_ue_html(d):
    return f"{versalitas('UNIÓN EUROPEA')}, {d['tipo']} {d['numero']}, {d['fecha']}, {d['descripcion']}. Diario Oficial UE, {d['serie']} ({d['fecha_dou']})."
def RCHD_ue_txt(d):
    return f"{versalitas('UNIÓN EUROPEA')}, {d['tipo']} {d['numero']}, {d['fecha']}, {d['descripcion']}. Diario Oficial UE, {d['serie']} ({d['fecha_dou']})."

# -------- Jurisprudencia (2.6.3)

def RCHD_tc_html(d):
    return f"Tribunal Constitucional, {d['fecha']}, rol {d['rol']}, {d['procedimiento']} ({d['nombre']})."
def RCHD_tc_txt(d):
    return f"Tribunal Constitucional, {d['fecha']}, rol {d['rol']}, {d['procedimiento']} ({d['nombre']})."

def RCHD_cs_pj_html(d):
    base = f"Corte Suprema, {d['fecha']}, rol {d['rol']}"
    if d.get("procedimiento"):
        base += f", {d['procedimiento']}"
    return base + "."
def RCHD_cs_pj_txt(d):
    base = f"Corte Suprema, {d['fecha']}, rol {d['rol']}"
    if d.get("procedimiento"):
        base += f", {d['procedimiento']}"
    return base + "."

def RCHD_penal_html(d):
    return f"{d['tribunal']}, RUC {d['ruc']}, RIT {d['rit']}, {d['tipo']}"
def RCHD_penal_txt(d):
    return f"{d['tribunal']}, RUC {d['ruc']}, RIT {d['rit']}, {d['tipo']}"

def RCHD_no_pj_html(d):
    return f"Corte Suprema, {d['fecha']}, {d['procedimiento']}, {d['fuente']}, {d['detalle']} ({d['nombre']})."
def RCHD_no_pj_txt(d):
    return f"Corte Suprema, {d['fecha']}, {d['procedimiento']}, {d['fuente']}, {d['detalle']} ({d['nombre']})."

def RCHD_base_datos_html(d):
    return f"{d['tribunal']}, {d['fecha']}, rol {d['rol']}, {d['procedimiento']} ({d['nombre']}) {d['bd']}, cita online {d['cita_online']}. Fecha de consulta: {d['fecha_consulta']}."
def RCHD_base_datos_txt(d):
    return f"{d['tribunal']}, {d['fecha']}, rol {d['rol']}, {d['procedimiento']} ({d['nombre']}) {d['bd']}, cita online {d['cita_online']}. Fecha de consulta: {d['fecha_consulta']}."

def RCHD_extranjera_html(d):
    return f"{versalitas(d['pais'])}, {d['tribunal']}, {d['cita']}."
def RCHD_extranjera_txt(d):
    return f"{versalitas(d['pais'])}, {d['tribunal']}, {d['cita']}."

def RCHD_internacional_html(d):
    return f"{d['tribunal']}, {d['cita']}."
def RCHD_internacional_txt(d):
    return f"{d['tribunal']}, {d['cita']}."

# =========================
# ESQUEMA DE TIPOS
# =========================

TIPOS = {
    # 2.6.1 a, d
    "Libro": {
        "label": "Libro (incluye 1, 2–3 o 4+ autores y/o tomos)",
        "w_authors": True,
        "fields": [
            {"name":"anio","label":"Año de publicación"},
            {"name":"titulo","label":"Título del libro"},
            {"name":"tomo","label":"Tomo/Volumen (ej. Tomo I)","optional":True},
            {"name":"ciudad","label":"Ciudad"},
            {"name":"editorial","label":"Editorial"},
            {"name":"edicion","label":"Número de edición","optional":True},
            {"name":"pags_corta","label":"Páginas para abreviada (p. o pp.)","optional":True},
        ],
        "render_html": RCHD_libro_html,
        "render_txt": RCHD_libro_txt,
        "short": lambda d: cita_abreviada_obras(d["autores"], d["anio"], paginas=d.get("pags_corta"), tomo=d.get("tomo"))
    },
    # 2.6.1 e.i
    "Traducción de libro": {
        "label": "Traducción de libro",
        "w_authors": True,
        "fields":[
            {"name":"anio_original","label":"Año de publicación original"},
            {"name":"anio","label":"Año de edición consultada"},
            {"name":"titulo","label":"Título"},
            {"name":"traductor","label":"Traductor"},
            {"name":"ciudad","label":"Ciudad"},
            {"name":"editorial","label":"Editorial"},
            {"name":"pags_corta","label":"Páginas para abreviada","optional":True},
        ],
        "render_html": RCHD_traduccion_libro_html,
        "render_txt": RCHD_traduccion_libro_txt,
        "short": lambda d: cita_abreviada_obras(d["autores"], d["anio"], paginas=d.get("pags_corta"))
    },
    # 2.6.1 e.ii
    "Traducción de artículo": {
        "label": "Traducción de artículo",
        "w_authors": True,
        "fields":[
            {"name":"anio_original","label":"Año original (opcional)","optional":True},
            {"name":"anio","label":"Año de publicación"},
            {"name":"titulo_articulo","label":"Título del artículo"},
            {"name":"revista","label":"Revista"},
            {"name":"volumen","label":"Volumen","optional":True},
            {"name":"numero","label":"Número","optional":True},
            {"name":"paginas","label":"Páginas","optional":True},
            {"name":"traductor","label":"Traductor"},
            {"name":"pags_corta","label":"Páginas para abreviada","optional":True},
        ],
        "render_html": RCHD_traduccion_articulo_html,
        "render_txt": RCHD_traduccion_articulo_txt,
        "short": lambda d: cita_abreviada_obras(d["autores"], d["anio"], paginas=d.get("pags_corta"))
    },
    # 2.6.1 f,g
    "Capítulo de libro (con editor/es)": {
        "label": "Capítulo de libro con editor(es)",
        "w_authors": False,
        "w_editors": True,
        "fields":[
            {"name":"anio","label":"Año"},
            {"name":"titulo_cap","label":"Título del capítulo"},
            {"name":"titulo_libro","label":"Título del libro"},
            {"name":"ciudad","label":"Ciudad"},
            {"name":"editorial","label":"Editorial"},
            {"name":"paginas","label":"Páginas (pp. inicio-fin)"},
            {"name":"pags_corta","label":"Páginas para abreviada","optional":True},
        ],
        "render_html": RCHD_capitulo_editor_html,
        "render_txt": RCHD_capitulo_editor_txt,
        "short": lambda d: cita_abreviada_obras(d["autores_cap"], d["anio"], paginas=d.get("pags_corta"))
    },
    # 2.6.1 h
    "Artículo de revista": {
        "label": "Artículo de revista (con volumen/número/páginas/DOI)",
        "w_authors": True,
        "fields":[
            {"name":"anio","label":"Año"},
            {"name":"titulo_art","label":"Título del artículo"},
            {"name":"revista","label":"Revista"},
            {"name":"volumen","label":"Volumen","optional":True},
            {"name":"numero","label":"Número","optional":True},
            {"name":"paginas","label":"Páginas (pp. inicio-fin)","optional":True},
            {"name":"doi","label":"DOI (opcional)","optional":True},
            {"name":"pags_corta","label":"Páginas para abreviada","optional":True},
        ],
        "render_html": RCHD_articulo_revista_html,
        "render_txt": RCHD_articulo_revista_txt,
        "short": lambda d: cita_abreviada_obras(d["autores"], d["anio"], paginas=d.get("pags_corta"))
    },
    # 2.6.1 i
    "Artículo de revista (sin vol/n°/páginas)": {
        "label": "Artículo de revista sin vol/num o páginas (con DOI)",
        "w_authors": True,
        "fields":[
            {"name":"anio","label":"Año"},
            {"name":"titulo_art","label":"Título del artículo"},
            {"name":"revista","label":"Revista"},
            {"name":"volumen","label":"Volumen (opcional)","optional":True},
            {"name":"doi","label":"DOI"},
            {"name":"pags_corta","label":"Páginas para abreviada (si aplica)","optional":True},
        ],
        "render_html": RCHD_articulo_sin_pags_html,
        "render_txt": RCHD_articulo_sin_pags_txt,
        "short": lambda d: cita_abreviada_obras(d["autores"], d["anio"], paginas=d.get("pags_corta"))
    },
    # 2.6.1 j
    "Trabajo no latino": {
        "label": "Trabajo en alfabeto no latino",
        "w_authors": False,
        "fields":[
            {"name":"apellidos_latinos","label":"Apellidos (transliteración)"},
            {"name":"nombres_latinos","label":"Nombres (transliteración)"},
            {"name":"anio","label":"Año"},
            {"name":"titulo_original","label":"Título original"},
            {"name":"titulo_trad","label":"Título traducido (opcional)","optional":True},
            {"name":"revista_original","label":"Revista/Editorial"},
            {"name":"numero","label":"Número (opcional)","optional":True},
            {"name":"paginas","label":"Páginas (opcional)","optional":True},
            {"name":"pags_corta","label":"Páginas para abreviada","optional":True},
        ],
        "render_html": RCHD_no_latino_html,
        "render_txt": RCHD_no_latino_txt,
        "short": lambda d: f"{versalitas(d['apellidos_latinos'])} ({d['anio']}){', p. '+d['pags_corta'] if d.get('pags_corta') else ''}."
    },
    # 2.6.1 k
    "E-book sin páginas": {
        "label": "E-book sin números de página",
        "w_authors": True,
        "fields":[
            {"name":"anio","label":"Año"},
            {"name":"titulo","label":"Título del libro o capítulo"},
            {"name":"titulo_cap","label":"Título del capítulo (si corresponde)","optional":True},
            {"name":"cont_in","label":"Contenedor (ej. en MAURER, Markus y otros (edits.), Autonomous Driving...)"},
            {"name":"cont_de","label":"Detalle del contenedor (opcional)","optional":True},
            {"name":"edicion_plataforma","label":"Edición/Plataforma (ej. Kindle Edition)"},
            {"name":"ubicacion_num","label":"Número de ubicación/capítulo/sección (ej. N° 4)","optional":True},
            {"name":"cap_sec_abrev","label":"Capítulo/Sección para ABREVIADA (ej. 4.1.1.)","optional":True},
            {"name":"parrafo_abrev","label":"Párrafo para ABREVIADA (ej. 2)","optional":True},
        ],
        "render_html": RCHD_ebook_html,
        "render_txt": RCHD_ebook_txt,
        "short": lambda d: cita_abreviada_obras(d["autores"], d["anio"], cap_sec=d.get("cap_sec_abrev"), parrafo=d.get("parrafo_abrev"))
    },
    # 2.6.1 l
    "Fuente manuscrita": {
        "label": "Fuente manuscrita",
        "w_authors": False,
        "fields":[
            {"name":"entidad","label":"Entidad (ej. ARCHIVO NACIONAL)"},
            {"name":"fondo","label":"Fondo"},
            {"name":"descripcion","label":"Descripción del documento"},
            {"name":"fecha","label":"Fecha (dd/mm/aaaa)"},
        ],
        "render_html": RCHD_manuscrito_html,
        "render_txt": RCHD_manuscrito_txt,
        "short": lambda d: d["entidad"]
    },
    # 2.6.1 m
    "Obra dogmática (histórica)": {
        "label": "Obras dogmáticas (sistemas históricos de citación)",
        "w_authors": False,
        "fields":[
            {"name":"cita_bruta","label":"Cita (ej. D. 42,1,56.)","textarea":True,"kind":"text"},
        ],
        "render_html": RCHD_dogmatica_hist_html,
        "render_txt": RCHD_dogmatica_hist_txt,
        "short": lambda d: d["cita_bruta"]
    },
    # 2.6.1 n
    "Tesis": {
        "label": "Tesis",
        "w_authors": True,
        "fields":[
            {"name":"anio","label":"Año"},
            {"name":"titulo","label":"Título"},
            {"name":"grado","label":"Grado académico"},
            {"name":"institucion","label":"Institución"},
            {"name":"pags_corta","label":"Páginas para abreviada (si aplica)","optional":True},
        ],
        "render_html": RCHD_tesis_html,
        "render_txt": RCHD_tesis_txt,
        "short": lambda d: cita_abreviada_obras(d["autores"], d["anio"], paginas=d.get("pags_corta"))
    },
    # 2.6.1 o
    "Informe": {
        "label": "Informe",
        "w_authors": False,
        "fields":[
            {"name":"org","label":"Organismo (ej. GENDARMERÍA DE CHILE)"},
            {"name":"unidad","label":"Unidad (opcional)","optional":True},
            {"name":"titulo","label":"Título del informe"},
            {"name":"numero","label":"Número (ej. sin N°) (opcional)","optional":True},
            {"name":"extra","label":"Notas adicionales (opcional)","optional":True},
            {"name":"sd","label":"¿Sin fecha? Escribe 's.d.' si corresponde (opcional)","optional":True},
        ],
        "render_html": RCHD_informe_html,
        "render_txt": RCHD_informe_txt,
        "short": lambda d: d["org"]
    },
    # 2.6.1 p
    "Documento en sitio web": {
        "label": "Documento alojado en sitio web (no libro/artículo)",
        "w_authors": False,
        "fields":[
            {"name":"encabezado","label":"Encabezado (lo que corresponda)"},
            {"name":"url","label":"URL"},
            {"name":"fecha_consulta","label":"Fecha de consulta (dd/mm/aaaa)","optional":True},
        ],
        "render_html": RCHD_doc_web_html,
        "render_txt": RCHD_doc_web_txt,
        "short": lambda d: d["encabezado"]
    },
    # 2.6.1 q.a
    "Periódico (sin autor)": {
        "label": "Diario/Periódico impreso (sin autor)",
        "w_authors": False,
        "fields":[
            {"name":"periodico","label":"Nombre del periódico"},
            {"name":"fecha","label":"Fecha (dd/mm/aaaa)"},
            {"name":"titulo","label":"Título de la nota"},
            {"name":"pagina","label":"Página (opcional)","optional":True},
        ],
        "render_html": RCHD_diario_sin_autor_html,
        "render_txt": RCHD_diario_sin_autor_txt,
        "short": lambda d: f"{versalitas(d['periodico'])} ({d['fecha']})."
    },
    # 2.6.1 q.b
    "Periódico (con autor)": {
        "label": "Diario/Periódico impreso (con autor)",
        "w_authors": True,
        "fields":[
            {"name":"fecha","label":"Fecha (dd/mm/aaaa)"},
            {"name":"titulo","label":"Título de la nota"},
            {"name":"periodico","label":"Nombre del periódico"},
            {"name":"pagina","label":"Página (opcional)","optional":True},
        ],
        "render_html": RCHD_diario_con_autor_html,
        "render_txt": RCHD_diario_con_autor_txt,
        "short": lambda d: cita_abreviada_obras(d["autores"], d["fecha"].split("/")[-1], paginas=d.get("pagina"))
    },
    # 2.6.1 r
    "Noticias/columnas web": {
        "label": "Noticias y columnas en sitios web",
        "w_authors": True,
        "fields":[
            {"name":"anio","label":"Año"},
            {"name":"titulo","label":"Título"},
            {"name":"medio","label":"Medio"},
            {"name":"url","label":"URL"},
            {"name":"fecha_consulta","label":"Fecha de consulta (dd/mm/aaaa)","optional":True},
        ],
        "render_html": RCHD_noticias_web_html,
        "render_txt": RCHD_noticias_web_txt,
        "short": lambda d: f"{format_solo_apellidos_txt(d['autores'])} ({d['anio']})."
    },
    # 2.6.1 s
    "Sitio web / blog": {
        "label": "Página web o blog institucional",
        "w_authors": False,
        "fields":[
            {"name":"entidad","label":"Entidad"},
            {"name":"anio","label":"Año"},
            {"name":"titulo","label":"Título de la página"},
            {"name":"url","label":"URL"},
            {"name":"fecha_consulta","label":"Fecha de consulta (dd/mm/aaaa)"},
        ],
        "render_html": RCHD_sitio_web_html,
        "render_txt": RCHD_sitio_web_txt,
        "short": lambda d: f"{versalitas(d['entidad'])} ({d['anio']})."
    },

    # 2.6.2 NORMAS
    "Constitución": {
        "label": "Constitución",
        "w_authors": False,
        "fields":[
            {"name":"pais","label":"País"},
            {"name":"fecha","label":"Fecha de publicación (dd/mm/aaaa)"},
        ],
        "render_html": RCHD_constitucion_html,
        "render_txt": RCHD_constitucion_txt,
        "short": lambda d: cita_abreviada_normas(d["pais"], "Constitución Política de la República")
    },
    "Ley no codificada": {
        "label": "Ley no codificada",
        "w_authors": False,
        "fields":[
            {"name":"pais","label":"País"},
            {"name":"numero","label":"Número de ley"},
            {"name":"denominacion","label":"Denominación legal (si la tiene)"},
            {"name":"fecha","label":"Fecha (dd/mm/aaaa)"},
        ],
        "render_html": RCHD_ley_no_cod_html,
        "render_txt": RCHD_ley_no_cod_txt,
        "short": lambda d: cita_abreviada_normas(d["pais"], f"Ley N° {d['numero']}")
    },
    "Código": {
        "label": "Código (con o sin fecha)",
        "w_authors": False,
        "fields":[
            {"name":"pais","label":"País"},
            {"name":"nombre","label":"Nombre del Código (ej. Código Civil)"},
            {"name":"fecha","label":"Fecha (dd/mm/aaaa) (opcional)","optional":True},
            {"name":"sd","label":"¿Sin fecha? escribir 's.d.' (opcional)","optional":True},
        ],
        "render_html": RCHD_codigo_html,
        "render_txt": RCHD_codigo_txt,
        "short": lambda d: cita_abreviada_normas(d["pais"], d["nombre"])
    },
    "Decreto": {
        "label": "Decreto Supremo",
        "w_authors": False,
        "fields":[
            {"name":"pais","label":"País"},
            {"name":"organismo","label":"Ministerio/Organismo"},
            {"name":"numero","label":"Número"},
            {"name":"denominacion","label":"Denominación"},
            {"name":"fecha","label":"Fecha (dd/mm/aaaa)"},
        ],
        "render_html": RCHD_decreto_html,
        "render_txt": RCHD_decreto_txt,
        "short": lambda d: cita_abreviada_normas(d["pais"], f"Decreto Supremo {d['numero']}")
    },
    "Oficio": {
        "label": "Oficio",
        "w_authors": False,
        "fields":[
            {"name":"pais","label":"País"},
            {"name":"emisor","label":"Emisor (con mayúsculas)"},
            {"name":"numero","label":"Número"},
            {"name":"descripcion","label":"Descripción"},
            {"name":"fecha","label":"Fecha (dd/mm/aaaa)"},
        ],
        "render_html": RCHD_oficio_html,
        "render_txt": RCHD_oficio_txt,
        "short": lambda d: cita_abreviada_normas(d["pais"], f"Ord. {d['numero']}")
    },
    "Proyecto de ley": {
        "label": "Proyecto de ley",
        "w_authors": False,
        "fields":[
            {"name":"pais","label":"País"},
            {"name":"descripcion","label":"Descripción (ej. Mensaje de S.E...)"},
            {"name":"boletin","label":"Número de boletín"},
        ],
        "render_html": RCHD_proyecto_ley_html,
        "render_txt": RCHD_proyecto_ley_txt,
        "short": lambda d: cita_abreviada_normas(d["pais"], "Proyecto de ley")
    },
    "Historia de la ley (BCN)": {
        "label": "Historia de la ley (BCN)",
        "w_authors": False,
        "fields":[
            {"name":"entidad","label":"Entidad (ej. BIBLIOTECA DEL CONGRESO NACIONAL DE CHILE)"},
            {"name":"anio","label":"Año"},
            {"name":"titulo","label":"Título"},
            {"name":"instancia","label":"Instancia (ej. Primer Trámite...)"},
            {"name":"detalle","label":"Detalle (ej. Segundo Informe..., p. 106)"},
            {"name":"url","label":"URL"},
            {"name":"fecha_consulta","label":"Fecha de consulta (dd/mm/aaaa)"},
        ],
        "render_html": RCHD_historia_ley_html,
        "render_txt": RCHD_historia_ley_txt,
        "short": lambda d: d["entidad"]
    },
    "Tratado internacional": {
        "label": "Tratado internacional",
        "w_authors": False,
        "fields":[
            {"name":"nombre","label":"Nombre del tratado (en versales/cursiva)"},
            {"name":"fecha_adop","label":"Fecha de adopción (dd/mm/aaaa)"},
        ],
        "render_html": RCHD_tratado_html,
        "render_txt": RCHD_tratado_txt,
        "short": lambda d: d["nombre"]
    },
    "Instrumento de congreso/conf.": {
        "label": "Instrumento de congreso o conferencia gubernamental",
        "w_authors": False,
        "fields":[
            {"name":"evento","label":"Nombre del evento (todo en mayúsculas)"},
            {"name":"titulo","label":"Título del instrumento"},
            {"name":"lugar","label":"Lugar"},
            {"name":"rango_fechas","label":"Rango de fechas (dd/mm/aaaa - dd/mm/aaaa)"},
        ],
        "render_html": RCHD_congreso_intern_html,
        "render_txt": RCHD_congreso_intern_txt,
        "short": lambda d: d["evento"]
    },
    "Documento de la ONU": {
        "label": "Documento oficial de organismo internacional (ONU)",
        "w_authors": False,
        "fields":[
            {"name":"organo","label":"Órgano (ASAMBLEA GENERAL, etc.)"},
            {"name":"titulo","label":"Título del documento"},
            {"name":"signatura","label":"Signatura (ej. A/63/332)"},
            {"name":"fecha","label":"Fecha (dd/mm/aaaa)"},
        ],
        "render_html": RCHD_doc_onu_html,
        "render_txt": RCHD_doc_onu_txt,
        "short": lambda d: f"NACIONES UNIDAS, {d['organo']}"
    },
    "Instrumento de la UE": {
        "label": "Instrumento de la Unión Europea",
        "w_authors": False,
        "fields":[
            {"name":"tipo","label":"Tipo (Directiva, Reglamento, etc.)"},
            {"name":"numero","label":"Número (ej. 2015/2376)"},
            {"name":"fecha","label":"Fecha (dd/mm/aaaa)"},
            {"name":"descripcion","label":"Descripción breve"},
            {"name":"serie","label":"Serie DOUE (ej. L 332)"},
            {"name":"fecha_dou","label":"Fecha del DOUE (dd/mm/aaaa)"},
        ],
        "render_html": RCHD_ue_html,
        "render_txt": RCHD_ue_txt,
        "short": lambda d: "UNIÓN EUROPEA"
    },

    # 2.6.3 Jurisprudencia
    "TC con nombre del caso": {
        "label": "Sentencia del Tribunal Constitucional (con nombre de caso)",
        "w_authors": False,
        "fields":[
            {"name":"fecha","label":"Fecha (dd/mm/aaaa)"},
            {"name":"rol","label":"Rol"},
            {"name":"procedimiento","label":"Procedimiento (ej. inconstitucionalidad)"},
            {"name":"nombre","label":"Nombre del caso"},
            {"name":"pinpoint","label":"Pinpoint (cons. / párr. / pág.) para abreviada (opcional)","optional":True},
        ],
        "render_html": RCHD_tc_html,
        "render_txt": RCHD_tc_txt,
        "short": lambda d: cita_abreviada_jurisprudencia("Tribunal Constitucional", nombre_caso=d["nombre"], pinpoint=d.get("pinpoint"))
    },
    "CS (Poder Judicial)": {
        "label": "Corte Suprema (disponible en sitio del Poder Judicial)",
        "w_authors": False,
        "fields":[
            {"name":"fecha","label":"Fecha (dd/mm/aaaa)"},
            {"name":"rol","label":"Rol"},
            {"name":"procedimiento","label":"Procedimiento (opcional)","optional":True},
            {"name":"pinpoint","label":"Pinpoint para abreviada (opcional)","optional":True},
        ],
        "render_html": RCHD_cs_pj_html,
        "render_txt": RCHD_cs_pj_txt,
        "short": lambda d: cita_abreviada_jurisprudencia("Corte Suprema", fecha=d["fecha"], pinpoint=d.get("pinpoint"))
    },
    "Penal (RUC/RIT)": {
        "label": "Sentencia penal con RUC/RIT",
        "w_authors": False,
        "fields":[
            {"name":"tribunal","label":"Tribunal"},
            {"name":"ruc","label":"RUC"},
            {"name":"rit","label":"RIT"},
            {"name":"tipo","label":"Tipo de procedimiento (juicio oral, etc.)"},
            {"name":"pinpoint","label":"Pinpoint para abreviada (opcional)","optional":True},
        ],
        "render_html": RCHD_penal_html,
        "render_txt": RCHD_penal_txt,
        "short": lambda d: cita_abreviada_jurisprudencia(d["tribunal"], fecha=None, pinpoint=d.get("pinpoint"))
    },
    "Sentencia no disponible en PJ": {
        "label": "Sentencia (no disponible en PJ) con fuente",
        "w_authors": False,
        "fields":[
            {"name":"fecha","label":"Fecha (dd/mm/aaaa)"},
            {"name":"procedimiento","label":"Procedimiento (apelación, etc.)"},
            {"name":"fuente","label":"Fuente (colección/base)"},
            {"name":"detalle","label":"Detalle (tomo/parte/sección/páginas)"},
            {"name":"nombre","label":"Nombre del caso (fantasía o intervinientes)"},
            {"name":"pinpoint","label":"Pinpoint para abreviada (opcional)","optional":True},
        ],
        "render_html": RCHD_no_pj_html,
        "render_txt": RCHD_no_pj_txt,
        "short": lambda d: cita_abreviada_jurisprudencia("Corte Suprema", nombre_caso=d["nombre"], pinpoint=d.get("pinpoint"))
    },
    "Sentencia en base de datos": {
        "label": "Sentencia en base de datos (con cita online)",
        "w_authors": False,
        "fields":[
            {"name":"tribunal","label":"Tribunal"},
            {"name":"fecha","label":"Fecha (dd/mm/aaaa)"},
            {"name":"rol","label":"Rol"},
            {"name":"procedimiento","label":"Procedimiento"},
            {"name":"nombre","label":"Nombre del caso"},
            {"name":"bd","label":"Base de datos (Westlaw, etc.)"},
            {"name":"cita_online","label":"Cita online (ej. CL/JUR/226/1996)"},
            {"name":"fecha_consulta","label":"Fecha de consulta (dd/mm/aaaa)"},
            {"name":"pinpoint","label":"Pinpoint para abreviada (opcional)","optional":True},
        ],
        "render_html": RCHD_base_datos_html,
        "render_txt": RCHD_base_datos_txt,
        "short": lambda d: cita_abreviada_jurisprudencia(d["tribunal"], nombre_caso=d["nombre"], pinpoint=d.get("pinpoint"))
    },
    "Jurisprudencia extranjera": {
        "label": "Jurisprudencia extranjera",
        "w_authors": False,
        "fields":[
            {"name":"pais","label":"País"},
            {"name":"tribunal","label":"Tribunal"},
            {"name":"cita","label":"Cita oficial (ej. BROWN V. BOARD..., 347 U.S. 483 (1954))"},
            {"name":"pinpoint","label":"Pinpoint para abreviada (opcional)","optional":True},
        ],
        "render_html": RCHD_extranjera_html,
        "render_txt": RCHD_extranjera_txt,
        "short": lambda d: cita_abreviada_jurisprudencia(d["tribunal"], nombre_caso=d["cita"].split(",")[0], pinpoint=d.get("pinpoint"))
    },
    "Jurisprudencia internacional": {
        "label": "Jurisprudencia internacional (CIJ, TEDH, Corte IDH, etc.)",
        "w_authors": False,
        "fields":[
            {"name":"tribunal","label":"Tribunal (Corte Internacional de Justicia, Tribunal Europeo de DD.HH., Corte Interamericana de DD.HH., etc.)"},
            {"name":"cita","label":"Cita completa (serie, número, año, etc.)"},
            {"name":"pinpoint","label":"Pinpoint para abreviada (opcional)","optional":True},
        ],
        "render_html": RCHD_internacional_html,
        "render_txt": RCHD_internacional_txt,
        "short": lambda d: cita_abreviada_jurisprudencia(d["tribunal"], nombre_caso=d["cita"].split(",")[0], pinpoint=d.get("pinpoint"))
    },
}

# =========================
# Descargas (HTML / RTF)
# =========================

def to_html_block(s: str) -> bytes:
    html = f"""<!doctype html>
<html><head><meta charset="utf-8">
<style>body{{font-family: "Times New Roman", serif; font-size: 12pt; line-height: 1.2}}</style>
</head><body>{s}</body></html>"""
    return html.encode("utf-8")

def to_rtf(s: str) -> bytes:
    # RTF mínimo (Times New Roman por defecto en muchos lectores)
    # Conversión básica: cursivas <i>...</i> -> \i ... \i0 ; small-caps -> \scaps ... \scaps0 (no estándar en todos, usaremos uppercase simple)
    plain = limpiar_html_a_texto(s)
    rtf = r"{\rtf1\ansi\deff0{\fonttbl{\f0 Times New Roman;}}\fs24 " + plain.replace("\n", r"\line ") + "}"
    return rtf.encode("utf-8")

# =========================
# APP
# =========================

st.set_page_config(page_title="Citador RChD", page_icon="📚", layout="wide")
st.title("📚 Citador – Revista Chilena de Derecho (RChD)")

# Estado
if "historial" not in st.session_state:
    st.session_state["historial"] = []

# Selección de tipo
tipo = st.selectbox("Tipo de fuente", list(TIPOS.keys()))
cfg = TIPOS[tipo]

colL, colR = st.columns([1.15, 1])

with colL:
    st.markdown("### Datos de la fuente")
    data = {}

    # Autores (si corresponde)
    if cfg.get("w_authors"):
        data["autores"] = input_autores("aut", titulo="Autores", minimo=1)

    # Autores capítulo y editores (para capítulos)
    if tipo == "Capítulo de libro (con editor/es)":
        data["autores_cap"] = input_autores("cap_aut", titulo="Autores del capítulo", minimo=1)
        data["editores"] = input_autores("cap_edt", titulo="Editores", minimo=1)

    # Campos declarados
    for f in cfg["fields"]:
        val = input_field(f, key_prefix=f"{tipo}_{f['name']}")
        data[f["name"]] = val.strip() if isinstance(val, str) else val

    # Presentador visual
    st.markdown("---")
    generar = st.button("Generar cita", type="primary", use_container_width=True)

with colR:
    st.markdown("### Vista previa y copia")

    placeholder_preview = st.empty()
    placeholder_text = st.empty()
    placeholder_short = st.empty()
    placeholder_dl1 = st.empty()
    placeholder_dl2 = st.empty()

if generar:
    # Normalizar algunos campos vacíos como None
    for k,v in list(data.items()):
        if isinstance(v, str) and v.strip() == "":
            data[k] = None

    # Render completo
    ref_html = cfg["render_html"](data)
    ref_txt = cfg["render_txt"](data)
    # Abreviada
    ref_short = cfg["short"](data)

    # Mostrar
    with colR:
        st.markdown("**Referencia completa (con formato):**")
        st.markdown(
            f"""
<div style="border:1px solid #ddd; padding:14px; border-radius:12px; background:#fafafa; font-size:16px">
{ref_html}
</div>
""",
            unsafe_allow_html=True
        )
        st.markdown("**Copiar referencia completa (texto plano):**")
        st.text_area("Referencia completa (texto)", value=limpiar_html_a_texto(ref_html), height=80, key="txt_full")

        st.markdown("**Cita abreviada (nota al pie):**")
        st.text_area("Cita abreviada", value=ref_short, height=60, key="txt_short")

        # Descargas
        fname_base = f"cita_rchd_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        st.download_button("Descargar como HTML (mantiene versalitas y cursivas)",
                           data=to_html_block(ref_html), file_name=f"{fname_base}.html", mime="text/html", use_container_width=True)
        st.download_button("Descargar como RTF (para pegar en Word)",
                           data=to_rtf(ref_html), file_name=f"{fname_base}.rtf", mime="application/rtf", use_container_width=True)

        # Guardar en historial
        st.session_state["historial"].append({"tipo": tipo, "full_html": ref_html, "full_txt": ref_txt, "short": ref_short})

st.markdown("---")
st.subheader("Historial")
if st.session_state["historial"]:
    for i, it in enumerate(reversed(st.session_state["historial"]), start=1):
        with st.expander(f"{i}. {it['tipo']}"):
            st.markdown("**Referencia completa (formato):**")
            st.markdown(it["full_html"], unsafe_allow_html=True)
            st.markdown("**Referencia completa (texto):**")
            st.code(limpiar_html_a_texto(it["full_html"]))
            st.markdown("**Cita abreviada:**")
            st.code(it["short"])
else:
    st.info("Aún no has generado citas.")

# Tips de uso
with st.expander("Ayuda rápida"):
    st.markdown(
        """
- **Versalitas**: los apellidos se muestran en versalitas (small-caps) en la vista previa y en los HTML descargables.
- **Copiar con formato**: usa la descarga **HTML** o **RTF** y pégalo en tu procesador (Word/Docs).
- **Abreviadas**: agrega páginas/tomo/capítulo/párrafo según el tipo; la app construye la abreviada conforme a 2.7.
- **Editores**: en capítulos, la etiqueta cambia automáticamente a **(edit.)** o **(edits.)** según el número de editores.
- **Autores 4+**: se mostrará “y otros” conforme a la norma.
"""
    )
```

