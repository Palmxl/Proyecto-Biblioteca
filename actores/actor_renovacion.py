import zmq
from gestor_almacenamiento.gestor_db import GestorBD

ctx = zmq.Context()
sub = ctx.socket(zmq.SUB)
sub.connect("tcp://localhost:5561")
sub.setsockopt_string(zmq.SUBSCRIBE, "Renovacion")

bd = GestorBD()
print("[Actor Renovación] Escuchando tópico 'Renovacion'...")

while True:
    msg = sub.recv_string()
    _, isbn, usuario = msg.split('|')
    print(f"Renovación recibida: {usuario} renueva {isbn}")
    res = bd.renovar_libro(isbn, usuario)
    print(res)