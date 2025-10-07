# http_gateway.py
from flask import Flask, request, jsonify
import zmq, json

app = Flask(__name__)

# Configuración del socket ZMQ para hablar con el Gestor de Carga
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://127.0.0.1:5555")  # puerto REP del GC (ajusta si cambió)

@app.route("/")
def home():
    return jsonify({"msg": "Gateway Biblioteca Distribuida activo 🚀"})

# -----------------------
#   ENDPOINTS REST
# -----------------------

@app.route("/prestamo", methods=["POST"])
def prestar():
    data = request.get_json()
    data["op"] = "PRESTAR"
    socket.send_string(json.dumps(data))
    reply = socket.recv_string()
    return jsonify({"response": reply})

@app.route("/devolucion", methods=["POST"])
def devolver():
    data = request.get_json()
    data["op"] = "DEVOLVER"
    socket.send_string(json.dumps(data))
    reply = socket.recv_string()
    return jsonify({"response": reply})

@app.route("/renovacion", methods=["POST"])
def renovar():
    data = request.get_json()
    data["op"] = "RENOVAR"
    socket.send_string(json.dumps(data))
    reply = socket.recv_string()
    return jsonify({"response": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)