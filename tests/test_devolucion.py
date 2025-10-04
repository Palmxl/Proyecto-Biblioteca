import zmq, time

ctx = zmq.Context()
pub = ctx.socket(zmq.PUB)
pub.bind("tcp://*:5561")  # mismo puerto de los actores de devolucion/renovacion

time.sleep(1)  # espera para que se conecten los suscriptores

isbn = "123"
usuario = "juan"
pub.send_string(f"Devolucion|{isbn}|{usuario}")
print(f"Enviada devolución: {isbn} | {usuario}")