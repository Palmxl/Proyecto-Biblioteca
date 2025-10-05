import zmq, json, os

# Cargar configuración
CFG = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'gestor_carga', 'config.json'), 'r', encoding='utf-8'))
GA_REP = CFG["zmq"]["ga_rep"]
GC_PUB = CFG["zmq"]["gc_pub"]

def main():
    ctx = zmq.Context()
    sub = ctx.socket(zmq.SUB)
    sub.connect(GC_PUB)
    sub.setsockopt_string(zmq.SUBSCRIBE, "Devolucion")

    req = ctx.socket(zmq.REQ)
    req.connect(GA_REP)

    print("[Actor Devolución] Escuchando tópico 'Devolucion'...")

    while True:
        topic, msg_json = sub.recv_string().split(" ", 1)
        msg = json.loads(msg_json)
        print(f"Devolución recibida: {msg}")
        isbn = msg["isbn"]
        user = msg["user"]

        data = {"op": "DEVOLVER", "isbn": isbn, "user": user}
        req.send_string(json.dumps(data))
        res = req.recv_json()
        print(f"Resultado: {res['msg']}")

if __name__ == "__main__":
    main()
