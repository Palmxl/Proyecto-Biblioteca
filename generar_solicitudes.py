import random
import os

# Carpeta donde se guardarán los archivos
CARPETA = "solicitudes"
os.makedirs(CARPETA, exist_ok=True)

# Tipos de operaciones posibles
OPERACIONES = ["PRESTAR", "RENOVAR", "DEVOLVER"]

# 🔹 ISBN reales extraídos de tu base de datos
ISBN_LISTA = [
    "ISBN00001", "ISBN00002", "ISBN00003", "ISBN00004", "ISBN00005",
    "ISBN00006", "ISBN00007", "ISBN00008", "ISBN00009", "ISBN00010",
    "ISBN00011", "ISBN00012", "ISBN00013", "ISBN00014", "ISBN00015"
]

# Usuarios simulados
USUARIOS = [f"usuario{i}" for i in range(1, 11)]  # usuario1 ... usuario10

def generar_archivo(nombre_archivo, n_lineas=20):
    """
    Genera un archivo de solicitudes con operaciones aleatorias
    y usuarios aleatorios, usando los ISBN reales.
    """
    with open(nombre_archivo, "w") as f:
        for _ in range(n_lineas):
            operacion = random.choice(OPERACIONES)
            isbn = random.choice(ISBN_LISTA)
            user = random.choice(USUARIOS)
            f.write(f"{operacion},{isbn},{user}\n")
    print(f"✅ Generado: {nombre_archivo}")

def main():
    print("📚 Generando archivos de solicitudes con ISBN reales y usuarios aleatorios...")
    for i in range(1, 6):  # Genera 5 archivos
        archivo = os.path.join(CARPETA, f"solicitudes_ps{i}.txt")
        generar_archivo(archivo)
    print("\n🎉 Archivos generados correctamente en /solicitudes")

if __name__ == "__main__":
    main()
