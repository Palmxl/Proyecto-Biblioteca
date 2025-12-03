import zmq, time

ctx = zmq.Context()
pub = ctx.socket(zmq.PUB)
pub.bind("tcp://*:5561")

time.sleep(1)

isbn = "123"
usuario = "juan"
pub.send_string(f"Renovacion|{isbn}|{usuario}")
print(f"Enviada renovación: {isbn} | {usuario}")
