import zmq, os, json
CFG = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'gestor_carga', 'config.json'), 'r', encoding='utf-8'))

GA_REP = CFG["zmq"]["ga_rep"]
ACTOR_REP = CFG["zmq"]["actor_prestamo_rep"]

def main():
    ctx = zmq.Context()
    rep = ctx.socket(zmq.REP)
    rep.bind(ACTOR_REP)

    req = ctx.socket(zmq.REQ)
    req.connect(GA_REP)

    print(f"[Actor Préstamo] Esperando solicitudes en {ACTOR_REP} ...")

    while True:
        msg = rep.recv_json()
        print(f"Solicitud recibida: {msg}")
        isbn = msg["isbn"]
        user = msg["user"]

        data = {"op": "PRESTAR", "isbn": isbn, "user": user}
        req.send_string(json.dumps(data))
        res = req.recv_json()

        print(f"Resultado: {res['msg']}")
        rep.send_json(res)

if __name__ == "__main__":
    main()