import zmq

ctx = zmq.Context()
req = ctx.socket(zmq.REQ)
req.connect("tcp://localhost:5560")  # puerto del actor_prestamo

isbn = "123"
usuario = "juan"
req.send_string(f"{isbn}|{usuario}")
print(f"Enviado préstamo: {isbn} | {usuario}")

respuesta = req.recv_string()
print("Respuesta:", respuesta)
