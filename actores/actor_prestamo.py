import zmq
from gestor_almacenamiento.gestor_db import GestorBD

ctx = zmq.Context()
socket = ctx.socket(zmq.REP)
socket.bind("tcp://*:5560")

bd = GestorBD()

print("[Actor Préstamo] Esperando solicitudes...")

while True:
    msg = socket.recv_string()
    isbn, usuario = msg.split('|')
    print(f"Solicitud de préstamo: {usuario} pide {isbn}")
    respuesta = bd.prestar_libro(isbn, usuario)
    socket.send_string(respuesta)
