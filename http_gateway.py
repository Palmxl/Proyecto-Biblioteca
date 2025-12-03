from flask import Flask, request, jsonify
import zmq, json

app = Flask(__name__)

# Configuración del socket ZMQ para comunicarse con el Gestor de Carga (GC)
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://10.195.89.122:5555")  # puerto REP del GC

@app.route("/")
def home():
    return jsonify({"msg": "🚀 Gateway Biblioteca Distribuida activo"})

# -----------------------
#   ENDPOINTS REST
# -----------------------

@app.route("/prestamo", methods=["POST"])
def prestar():
    data = request.get_json(force=True)
    data["operacion"] = "PRESTAR"
    socket.send_json(data)
    reply = socket.recv_json()
    return jsonify(reply)

@app.route("/devolucion", methods=["POST"])
def devolver():
    data = request.get_json(force=True)
    data["operacion"] = "DEVOLVER"
    socket.send_json(data)
    reply = socket.recv_json()
    return jsonify(reply)

@app.route("/renovacion", methods=["POST"])
def renovar():
    data = request.get_json(force=True)
    data["operacion"] = "RENOVAR"
    socket.send_json(data)
    reply = socket.recv_json()
    return jsonify(reply)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
