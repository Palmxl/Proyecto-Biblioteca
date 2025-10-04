# actores/actor_prestamo.py
import os, json, zmq
CFG = json.load(open(os.path.join(os.path.dirname(__file__),'..','gestor_carga','config.json'),'r',encoding='utf-8'))
ZMQ_ACTOR_PRESTAMO_REP = CFG["zmq"]["actor_prestamo_rep"]
ZMQ_GA_REP = CFG["zmq"]["ga_rep"]

def main():
    ctx = zmq.Context()
    rep = ctx.socket(zmq.REP); rep.bind(ZMQ_ACTOR_PRESTAMO_REP)
    ga  = ctx.socket(zmq.REQ); ga.connect(ZMQ_GA_REP)
    print(f"[Actor-Prestamo] REP {ZMQ_ACTOR_PRESTAMO_REP} -> GA {ZMQ_GA_REP}")

    while True:
        msg = rep.recv_json()
        if msg.get("op") == "PRESTAR":
            payload = {"op":"PRESTAR","user":msg["user"],"isbn":msg["isbn"],"days":14}
            ga.send_string(json.dumps(payload))
            res = ga.recv_json()
            rep.send_json(res)
        else:
            rep.send_json({"ok":False,"msg":"op inválida"})

if __name__ == "__main__":
    main()
