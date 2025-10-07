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
        msg = sub.recv_string()

        # Ignora mensajes vacíos o sin contenido JSON
        if "{" not in msg or "}" not in msg:
            continue

        # Extrae solo la parte JSON del mensaje recibido
        try:
            json_part = msg[msg.index("{") : msg.rindex("}") + 1]
            data_recv = json.loads(json_part)
        except Exception as e:
            print(f"[WARN] Mensaje malformado recibido: {msg} ({e})")
            continue

        print(f"Devolución recibida: {data_recv}")
        isbn = data_recv["isbn"]
        user = data_recv["user"]

        # Envía solicitud al gestor de almacenamiento
        data = {"op": "RENOVAR", "isbn": isbn, "user": user}
        req.send_string(json.dumps(data))
        res = req.recv_json()
        print(f"Resultado: {res['msg']}")

if __name__ == "__main__":
    main()
