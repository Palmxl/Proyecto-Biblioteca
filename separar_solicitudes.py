import os

# Archivo de entrada (tu archivo original con las 1000 operaciones)
archivo_entrada = "solicitudes.txt"

# Carpeta donde se guardarán los archivos separados
carpeta_salida = "solicitudes"

# Crear la carpeta si no existe
os.makedirs(carpeta_salida, exist_ok=True)

# Rutas completas de los archivos de salida
path_prestar = os.path.join(carpeta_salida, "solicitudes_prestar.txt")
path_renovar = os.path.join(carpeta_salida, "solicitudes_renovar.txt")
path_devolver = os.path.join(carpeta_salida, "solicitudes_devolver.txt")

# Abrir los tres archivos de salida
out_prestar = open(path_prestar, "w", encoding="utf-8")
out_renovar = open(path_renovar, "w", encoding="utf-8")
out_devolver = open(path_devolver, "w", encoding="utf-8")

# Contadores de líneas
count_prestar = count_renovar = count_devolver = 0

# Leer línea por línea y clasificar
with open(archivo_entrada, "r", encoding="utf-8") as f:
    for linea in f:
        linea = linea.strip()
        if not linea:
            continue

        if linea.startswith("PRESTAR,"):
            out_prestar.write(linea + "\n")
            count_prestar += 1
        elif linea.startswith("RENOVAR,"):
            out_renovar.write(linea + "\n")
            count_renovar += 1
        elif linea.startswith("DEVOLVER,"):
            out_devolver.write(linea + "\n")
            count_devolver += 1

# Cerrar los archivos
out_prestar.close()
out_renovar.close()
out_devolver.close()

# Mostrar resumen final
total = count_prestar + count_renovar + count_devolver
print("✅ Archivos generados en la carpeta 'solicitudes':")
print(f" - solicitudes_prestar.txt  ({count_prestar} líneas)")
print(f" - solicitudes_renovar.txt  ({count_renovar} líneas)")
print(f" - solicitudes_devolver.txt ({count_devolver} líneas)")
print(f"Total procesado: {total} operaciones")
