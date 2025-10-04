import zmq
from gestor_almacenamiento.gestor_db import GestorBD

ctx = zmq.Context()
sub = ctx.socket(zmq.SUB)
sub.connect("tcp://localhost:5561")
sub.setsockopt_string(zmq.SUBSCRIBE, "Devolucion")

bd = GestorBD()
print("[Actor Devolución] Escuchando tópico 'Devolucion'...")

while True:
    msg = sub.recv_string()
    _, isbn, usuario = msg.split('|')
    print(f"Devolución recibida: {usuario} devuelve {isbn}")
    res = bd.devolver_libro(isbn, usuario)
    print(res)