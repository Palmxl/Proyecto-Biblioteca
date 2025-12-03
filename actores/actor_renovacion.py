import zmq, json, os

# Cargar configuración
CFG = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'gestor_carga', 'config.json'), 'r', encoding='utf-8'))
GA_REP = CFG["zmq"]["ga_rep"]
GC_PUB = CFG["zmq"]["gc_pub"]

def main():
    ctx = zmq.Context()

    # SUB para escuchar al Gestor de Carga
    sub = ctx.socket(zmq.SUB)
    sub.connect(GC_PUB)
    sub.setsockopt_string(zmq.SUBSCRIBE, "Renovacion")

    # REQ hacia el Gestor de Almacenamiento
    req = ctx.socket(zmq.REQ)
    req.connect(GA_REP)

    print("[Actor Renovación] Escuchando tópico 'Renovacion'...")

    while True:
        # Recibir MULTIPART: [topic, payload_json]
        topic, payload = sub.recv_multipart()

        try:
            data_recv = json.loads(payload.decode("utf-8"))
        except Exception as e:
            print(f"[Actor Renovación][WARN] Payload malformado: {payload} ({e})")
            continue

        print(f"[Actor Renovación] Mensaje recibido: {data_recv}")

        isbn = data_recv.get("isbn")
        user = data_recv.get("user")

        if not isbn or not user:
            print("[Actor Renovación][WARN] Mensaje sin isbn/user, se ignora.")
            continue

        # Enviar solicitud de RENOVAR al GA
        data = {"op": "RENOVAR", "isbn": isbn, "user": user}
        req.send_json(data)
        res = req.recv_json()

        print(f"[Actor Renovación] Resultado GA: {res.get('msg', res)}")

if __name__ == "__main__":
    main()
