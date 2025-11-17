import zmq, os, json

CFG = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'gestor_carga', 'config.json'), 'r', encoding='utf-8'))

GA_REP = CFG["zmq"]["ga_rep"]
ACTOR_REP = CFG["zmq"]["actor_prestamo_rep"]

def main():
    ctx = zmq.Context()

    # REP: recibe solicitudes del Gestor de Carga
    rep = ctx.socket(zmq.REP)
    rep.bind(ACTOR_REP)

    # REQ: habla con el Gestor de Almacenamiento (GA)
    req = ctx.socket(zmq.REQ)
    req.connect(GA_REP)

    print(f"[Actor Préstamo] Esperando solicitudes en {ACTOR_REP} ...")

    while True:
        msg = rep.recv_json()
        print(f"[Actor Préstamo] Solicitud recibida: {msg}")

        isbn = msg.get("isbn")
        user = msg.get("user")

        if not isbn or not user:
            print("[Actor Préstamo] Mensaje sin isbn/user, se ignora.")
            rep.send_json({"ok": False, "msg": "Solicitud inválida"})
            continue

        data = {"op": "PRESTAR", "isbn": isbn, "user": user}

        # Pedir al GA que intente el préstamo
        req.send_json(data)
        res = req.recv_json()

        print(f"[Actor Préstamo] Resultado GA: {res.get('msg', res)}")
        # Devolver la respuesta al GC (que luego la envía al PS)
        rep.send_json(res)

if __name__ == "__main__":
    main()
