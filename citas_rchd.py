# Generador de citas en formato jurídico tradicional chileno (RChD 2025)
# Desarrollado para la Consejería Académica de Derecho UC

import textwrap

def versalitas(texto):
    return texto.upper()

def dividir_nombre(autor):
    if ' ' in autor:
        partes = autor.strip().rsplit(' ', 1)
        return partes[0], partes[1]
    else:
        return autor, ""

# --------------------------- FORMATOS DE CITA ---------------------------

def formatear_cita_libro():
    print("\n📘 Libro")
    autor = input("Autor(es): ")
    año = input("Año: ")
    titulo = input("Título del libro: ")
    ciudad = input("Ciudad: ")
    editorial = input("Editorial: ")
    edicion = input("Edición (dejar vacío si es la primera): ")
    apellidos, nombre = dividir_nombre(autor)
    cita = f"{versalitas(apellidos)}"
    if nombre: cita += f", {nombre}"
    cita += f" ({año}): *{titulo}* ({ciudad}, {editorial}"
    if edicion: cita += f", {edicion}"
    cita += ")."
    return cita

def formatear_cita_articulo():
    print("\n📰 Artículo de revista")
    autor = input("Autor(es): ")
    año = input("Año: ")
    titulo = input("Título del artículo: ")
    revista = input("Nombre de la revista: ")
    volumen = input("Volumen: ")
    numero = input("Número: ")
    paginas = input("Páginas (ej: 93-107): ")
    apellidos, nombre = dividir_nombre(autor)
    cita = f"{versalitas(apellidos)}"
    if nombre: cita += f", {nombre}"
    cita += f" ({año}): \"{titulo}\", *{revista}*"
    if volumen: cita += f", vol. {volumen}"
    if numero: cita += f", N° {numero}"
    if paginas: cita += f": pp. {paginas}"
    cita += "."
    return cita

def formatear_cita_capitulo():
    print("\n📚 Capítulo de libro")
    autor = input("Autor del capítulo: ")
    año = input("Año: ")
    titulo = input("Título del capítulo: ")
    editor = input("Editor del libro: ")
    libro = input("Título del libro: ")
    ciudad = input("Ciudad: ")
    editorial = input("Editorial: ")
    paginas = input("Páginas: ")
    apellidos, nombre = dividir_nombre(autor)
    cita = f"{versalitas(apellidos)}"
    if nombre: cita += f", {nombre}"
    cita += f" ({año}): \"{titulo}\", en {editor} (edit.), *{libro}* ({ciudad}, {editorial}) pp. {paginas}."
    return cita

def formatear_cita_ley():
    print("\n⚖️ Ley o norma jurídica")
    pais = input("País: ")
    tipo = input("Tipo (Ley, Código, DS...): ")
    numero = input("Número o nombre: ")
    fecha = input("Fecha (dd/mm/aaaa): ")
    nombre = input("Nombre oficial (opcional): ")
    cita = f"{versalitas(pais)}, {tipo} {numero} ({fecha})"
    if nombre: cita += f". *{nombre}*"
    cita += "."
    return cita

def formatear_cita_sentencia():
    print("\n📄 Sentencia o jurisprudencia")
    tribunal = input("Tribunal: ")
    fecha = input("Fecha: ")
    rol = input("Rol o RUC/RIT: ")
    tipo_proc = input("Tipo procedimiento: ")
    nombre_fantasia = input("Nombre del caso (opcional): ")
    cita = f"{tribunal}, {fecha}, rol {rol}, {tipo_proc}"
    if nombre_fantasia: cita += f" ({nombre_fantasia})"
    cita += "."
    return cita

def formatear_cita_tesis():
    print("\n🎓 Tesis o memoria académica")
    autor = input("Autor: ")
    año = input("Año: ")
    titulo = input("Título: ")
    universidad = input("Universidad: ")
    grado = input("Grado académico: ")
    apellidos, nombre = dividir_nombre(autor)
    cita = f"{versalitas(apellidos)}"
    if nombre: cita += f", {nombre}"
    cita += f" ({año}): *{titulo}*. Memoria para optar al grado de {grado}, {universidad}."
    return cita

def formatear_cita_web():
    print("\n🌐 Sitio web o columna digital")
    autor = input("Autor: ")
    año = input("Año: ")
    titulo = input("Título: ")
    medio = input("Nombre del sitio o medio: ")
    url = input("URL: ")
    fecha_consulta = input("Fecha de consulta (dd/mm/aaaa): ")
    apellidos, nombre = dividir_nombre(autor)
    cita = f"{versalitas(apellidos)}"
    if nombre: cita += f", {nombre}"
    cita += f" ({año}): \"{titulo}\", {medio}. Disponible en: {url}. Fecha de consulta: {fecha_consulta}."
    return cita

def formatear_cita_tratado():
    print("\n🌍 Tratado internacional")
    nombre = input("Nombre del tratado: ")
    fecha = input("Fecha de adopción (dd/mm/aaaa): ")
    fuente = input("Fuente (opcional): ")
    cita = f"{versalitas(nombre)} ({fecha})"
    if fuente: cita += f". {fuente}"
    cita += "."
    return cita

# --------------------------- INTERFAZ PRINCIPAL ---------------------------

def menu():
    print(textwrap.dedent("""
    ------------------------------------------
    GENERADOR DE CITAS RChD 2025
    Consejería Académica Derecho UC
    ------------------------------------------
    1. Libro
    2. Artículo de revista
    3. Capítulo de libro
    4. Ley o norma
    5. Sentencia o jurisprudencia
    6. Tesis o memoria
    7. Sitio web / noticia digital
    8. Tratado internacional
    9. Salir
    """))

def main():
    while True:
        menu()
        opcion = input("👉 Opción (1-9): ")

        if opcion == "1": cita = formatear_cita_libro()
        elif opcion == "2": cita = formatear_cita_articulo()
        elif opcion == "3": cita = formatear_cita_capitulo()
        elif opcion == "4": cita = formatear_cita_ley()
        elif opcion == "5": cita = formatear_cita_sentencia()
        elif opcion == "6": cita = formatear_cita_tesis()
        elif opcion == "7": cita = formatear_cita_web()
        elif opcion == "8": cita = formatear_cita_tratado()
        elif opcion == "9":
            print("\n👋 ¡Gracias por usar el generador!")
            break
        else:
            print("❌ Opción inválida. Intenta de nuevo.\n")
            continue

        print("\n📌 Cita generada:")
        print("------------------------------------------")
        print(cita)
        print("------------------------------------------\n")

if __name__ == "__main__":
    main()
