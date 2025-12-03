import zmq, time, json, sys, os

# Cargar config del GC
CONFIG_PATH = os.path.join(
    os.path.dirname(__file__), 
    "..", 
    "gestor_carga", 
    "config.json"
)

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CFG = json.load(f)

GC_ENDPOINT = CFG["zmq"]["gc_rep"]   # tcp://10.43.103.174:5555

def main(archivo):
    ctx = zmq.Context()
    socket = ctx.socket(zmq.REQ)
    socket.connect(GC_ENDPOINT)

    with open(archivo, "r") as f:
        for linea in f:
            linea = linea.strip()
            if not linea:
                continue

            partes = linea.split(",")
            if len(partes) < 3:
                continue

            operacion, isbn, user = partes
            operacion = operacion.upper()

            if operacion not in ["PRESTAR", "DEVOLVER", "RENOVAR"]:
                print(f"[PS] Operación desconocida '{operacion}', se ignora.")
                continue

            solicitud = {
                "operacion": operacion,
                "isbn": isbn,
                "user": user
            }

            print(f"[PS] ({user}) Enviando {operacion} para libro {isbn}")
            socket.send_json(solicitud)

            respuesta = socket.recv_json()
            print(f"[PS] Respuesta: {respuesta}\n")

            time.sleep(0.3)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python ps_mixto.py archivo_solicitudes.txt")
    else:
        main(sys.argv[1])
