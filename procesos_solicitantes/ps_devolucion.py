import zmq, time, json, sys

def main(archivo):
    ctx = zmq.Context()
    socket = ctx.socket(zmq.REQ)
    socket.connect("tcp://127.0.0.1:5555")

    with open(archivo, "r") as f:
        for linea in f:
            linea = linea.strip()
            if not linea:
                continue

            partes = linea.split(",")
            if len(partes) < 3:
                continue

            operacion, isbn, user = partes
            if operacion.upper() != "DEVOLVER":
                continue

            solicitud = {"operacion": "DEVOLVER", "isbn": isbn, "user": user}

            print(f"[PS] ({user}) Devolviendo libro {isbn}")
            socket.send_json(solicitud)
            respuesta = socket.recv_json()
            print(f"[PS] Respuesta: {respuesta}")
            time.sleep(0.3)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python -m procesos_solicitantes.ps_devolver archivo.txt")
    else:
        main(sys.argv[1])
