import os, json, time, zmq
CFG = json.load(open(os.path.join(os.path.dirname(__file__),'config.json'),'r',encoding='utf-8'))
ZMQ_GC_PUB = CFG["zmq"]["gc_pub"]

def main():
    ctx = zmq.Context()
    pub = ctx.socket(zmq.PUB)
    pub.bind(ZMQ_GC_PUB)
    print(f"[GC-PUB] Activo en {ZMQ_GC_PUB}")
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt: pass

if __name__ == "__main__":
    main()
