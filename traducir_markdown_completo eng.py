from deep_translator import GoogleTranslator
import re
from tqdm import tqdm
import os


def explorar_directorio(ruta_actual):
    while True:
        print(f"\n📁 Carpeta actual: {ruta_actual}\n")

        # Listar carpetas y archivos .md
        elementos = os.listdir(ruta_actual)
        carpetas = [e for e in elementos if os.path.isdir(os.path.join(ruta_actual, e))]
        archivos_md = [e for e in elementos if e.lower().endswith(".md")]

        opciones = []

        print("📂 Carpetas:")
        for i, carpeta in enumerate(carpetas, 1):
            print(f"{i}. [DIR] {carpeta}")
            opciones.append(("carpeta", carpeta))

        print("\n📄 Archivos Markdown:")
        for i, archivo in enumerate(archivos_md, len(opciones) + 1):
            print(f"{i}. {archivo}")
            opciones.append(("archivo", archivo))

        print("\n0. ⬅️  Subir un nivel")
        print("99. ❌ Cancelar")

        try:
            opcion = int(input("\nSeleccione una opción: "))

            if opcion == 99:
                return None

            if opcion == 0:
                # Subir un nivel
                nueva_ruta = os.path.dirname(ruta_actual)
                if nueva_ruta == ruta_actual:
                    print("Ya estás en la carpeta raíz.")
                else:
                    ruta_actual = nueva_ruta
                continue

            if 1 <= opcion <= len(opciones):
                tipo, nombre = opciones[opcion - 1]
                ruta_seleccionada = os.path.join(ruta_actual, nombre)

                if tipo == "carpeta":
                    ruta_actual = ruta_seleccionada
                else:
                    return ruta_seleccionada

            else:
                print("Número fuera de rango.")

        except ValueError:
            print("Entrada inválida. Escriba un número.")
            
translator = GoogleTranslator(source='auto', target='en')

def traducir_texto(texto):
    try:
        traducido = translator.translate(texto)
        return traducido if traducido else texto
    except:
        return texto

def es_bloque_codigo(linea):
    return linea.strip().startswith("```")

def es_html(linea):
    # Detecta cualquier etiqueta HTML en la línea
    return bool(re.search(r"<[^>]+>", linea))

def es_url(linea):
    return "http://" in linea or "https://" in linea

def traducir_tabla(linea):
    partes = linea.split("|")
    nuevas = []
    for p in partes:
        contenido = p.strip()
        if contenido and "---" not in contenido:
            nuevas.append(" " + traducir_texto(contenido) + " ")
        else:
            nuevas.append(p)
    return "|".join(nuevas)

def traducir_linea(linea):
    # No traducir HTML ni URLs
    if es_url(linea) or es_html(linea):
        return linea

    # ❗ NO traducir encabezados Markdown (#)
    if linea.lstrip().startswith("#"):
        return linea

    # Tablas
    if "|" in linea and not linea.strip().startswith("```"):
        return traducir_tabla(linea)

    # Listas Markdown (-, *, +, >)
    if linea.strip().startswith(("-", "*", "+", ">")):
        espacios = len(linea) - len(linea.lstrip())
        simbolo = linea[:espacios]
        contenido = linea.lstrip()
        return simbolo + traducir_texto(contenido)

    # Texto normal
    return traducir_texto(linea)

def traducir_markdown(entrada, salida):
    with open(entrada, "r", encoding="utf-8") as f:
        lineas = f.readlines()

    dentro_codigo = False

    # Abrimos el archivo de salida una sola vez
    with open(salida, "w", encoding="utf-8") as f_out:

        for linea in tqdm(lineas, desc="Traduciendo", unit="líneas"):

            if es_bloque_codigo(linea):
                dentro_codigo = not dentro_codigo
                f_out.write(linea)
                continue

            if dentro_codigo:
                f_out.write(linea)
                f_out.flush()
                os.fsync(f_out.fileno())
            else:
                nueva = traducir_linea(linea)
                if not nueva.endswith("\n"):
                    nueva += "\n"
                f_out.write(nueva)
                f_out.flush()
                os.fsync(f_out.fileno())

    print(f"\nArchivo traducido guardado como: {salida}")



# Ejecutar
ruta_inicial = os.getcwd()
archivo_entrada = explorar_directorio(ruta_inicial)

if archivo_entrada:
    archivo_salida = archivo_entrada.replace(".md", " - Traduccion Completa.md")
    traducir_markdown(archivo_entrada, archivo_salida)