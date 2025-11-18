from flask import Flask, request, jsonify
import zmq, json

app = Flask(__name__)

# Contexto global, sockets por request
context = zmq.Context()
GC_ENDPOINT = "tcp://10.43.103.200:5555"  # REP del GC que quieras probar


@app.route("/")
def home():
    return jsonify({"msg": "🚀 Gateway Biblioteca Distribuida activo"})


def call_gc(payload: dict):
    """Helper: abre un REQ, manda al GC y devuelve la respuesta."""
    socket = context.socket(zmq.REQ)
    socket.connect(GC_ENDPOINT)

    try:
        socket.send_json(payload)
        reply = socket.recv_json()
        return reply
    except Exception as e:
        print(f"[Gateway] Error hablando con GC: {e}")
        return {"ok": False, "msg": "Error interno en gateway"}
    finally:
        socket.close()


@app.route("/prestamo", methods=["POST"])
def prestar():
    data = request.get_json(force=True)
    data["operacion"] = "PRESTAR"
    reply = call_gc(data)
    return jsonify(reply)


@app.route("/devolucion", methods=["POST"])
def devolver():
    data = request.get_json(force=True)
    data["operacion"] = "DEVOLVER"
    reply = call_gc(data)
    return jsonify(reply)


@app.route("/renovacion", methods=["POST"])
def renovar():
    data = request.get_json(force=True)
    data["operacion"] = "RENOVAR"
    reply = call_gc(data)
    return jsonify(reply)


if __name__ == "__main__":
    # host 0.0.0.0 para que Locust desde otra máquina pueda pegarle
    app.run(host="0.0.0.0", port=8080)
