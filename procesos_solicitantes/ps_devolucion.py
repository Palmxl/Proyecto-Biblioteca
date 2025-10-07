import zmq, time, json, sys

def main(archivo):
    ctx = zmq.Context()
    socket = ctx.socket(zmq.REQ)
    socket.connect("tcp://127.0.0.1:5555")

    with open(archivo, "r") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or not linea.startswith("DEVOLVER"):
                continue
            _, isbn = linea.split(",")
            solicitud = {"tipo": "DEVOLVER", "isbn": isbn}

            print(f"[PS] Enviando devolución de {isbn}")
            socket.send_json(solicitud)
            respuesta = socket.recv_json()
            print(f"[PS] Respuesta: {respuesta}")
            time.sleep(0.3)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python -m procesos_solicitantes.ps_devolver archivo.txt")
    else:
        main(sys.argv[1])
