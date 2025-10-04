# actores/actor_renovacion.py
import os, json, zmq
CFG = json.load(open(os.path.join(os.path.dirname(__file__),'..','gestor_carga','config.json'),'r',encoding='utf-8'))
GC_PUB = CFG["zmq"]["gc_pub"]
GA_REP = CFG["zmq"]["ga_rep"]

def main():
    ctx = zmq.Context()
    sub = ctx.socket(zmq.SUB); sub.connect(GC_PUB)
    sub.setsockopt_string(zmq.SUBSCRIBE, "renovacion")
    ga = ctx.socket(zmq.REQ); ga.connect(GA_REP)
    print(f"[Actor-Renovacion] SUB {GC_PUB} -> GA {GA_REP}")

    while True:
        topic, payload = sub.recv_multipart()
        msg = json.loads(payload.decode())
        days = int(msg.get("days",7))
        ga.send_string(json.dumps({"op":"RENOVAR","user":msg["user"],"isbn":msg["isbn"],"days":days}))
        _ = ga.recv_json()

if __name__ == "__main__":
    main()
