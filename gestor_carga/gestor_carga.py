import os, json, zmq
CFG = json.load(open(os.path.join(os.path.dirname(__file__),'config.json'),'r',encoding='utf-8'))
ZMQ_GC_REP = CFG["zmq"]["gc_rep"]
ZMQ_GC_PUB = CFG["zmq"]["gc_pub"]
ZMQ_ACTOR_PRESTAMO_REP = CFG["zmq"]["actor_prestamo_rep"]

def main():
    ctx = zmq.Context()
    rep = ctx.socket(zmq.REP); rep.bind(ZMQ_GC_REP)
    pub = ctx.socket(zmq.PUB); pub.connect(ZMQ_GC_PUB)
    req_actor = ctx.socket(zmq.REQ); req_actor.connect(ZMQ_ACTOR_PRESTAMO_REP)
    print(f"[GC] REP {ZMQ_GC_REP} | PUB->{ZMQ_GC_PUB} | REQ->{ZMQ_ACTOR_PRESTAMO_REP}")

    while True:
        msg = rep.recv_json()
        op = msg.get("op","").upper()
        if op == "PRESTAR":
            req_actor.send_json(msg)
            res = req_actor.recv_json()
            rep.send_json(res)
        elif op == "DEVOLVER":
            pub.send_multipart([b"devolucion", json.dumps(msg).encode("utf-8")])
            rep.send_json({"ok": True, "msg": "Devolución aceptada"})
        elif op == "RENOVAR":
            pub.send_multipart([b"renovacion", json.dumps(msg).encode("utf-8")])
            rep.send_json({"ok": True, "msg": "Renovación aceptada"})
        else:
            rep.send_json({"ok": False, "msg": "op inválida"})

if __name__ == "__main__":
    main()
