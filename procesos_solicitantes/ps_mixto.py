import zmq, time, json, sys, os

# Carga la ruta del archivo de configuración del Gestor de Carga
CONFIG_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "gestor_carga",
    "config.json"
)

# Lee la configuración del sistema (IP/puerto del GC)
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CFG = json.load(f)

# Dirección del socket REP del Gestor de Carga (GC)
GC_ENDPOINT = CFG["zmq"]["gc_rep"]


def main(archivo):
    # Crea un contexto ZMQ y socket REQ para enviar solicitudes al GC
    ctx = zmq.Context()
    socket = ctx.socket(zmq.REQ)
    socket.connect(GC_ENDPOINT)

    # Lee el archivo de solicitudes línea por línea
    with open(archivo, "r") as f:
        for linea in f:
            linea = linea.strip()

            # Omite líneas vacías
            if not linea:
                continue

            # Cada línea debe tener: OPERACIÓN,ISBN,USUARIO
            partes = linea.split(",")
            if len(partes) < 3:
                continue

            operacion, isbn, user = partes
            operacion = operacion.upper()

            # Verifica que la operación sea válida
            if operacion not in ["PRESTAR", "DEVOLVER", "RENOVAR"]:
                print(f"[PS] Operación desconocida '{operacion}', se ignora.")
                continue

            # Construye la solicitud para el GC
            solicitud = {
                "operacion": operacion,
                "isbn": isbn,
                "user": user
            }

            # Envía solicitud al Gestor de Carga
            print(f"[PS] ({user}) Enviando {operacion} para libro {isbn}")
            socket.send_json(solicitud)

            # Espera la respuesta del GC (bloqueante)
            respuesta = socket.recv_json()
            print(f"[PS] Respuesta: {respuesta}\n")

            # Pausa breve para evitar saturar el GC
            time.sleep(0.3)


if __name__ == "__main__":
    # Usa el archivo de solicitudes recibido por argumentos
    if len(sys.argv) < 2:
        print("Uso: python ps_mixto.py archivo_solicitudes.txt")
    else:
        main(sys.argv[1])
