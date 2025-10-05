import os
import json
import zmq
import time  # <- añadido para darle tiempo a los SUBs a conectarse

# Cargar configuración desde config.json
CFG = json.load(open(os.path.join(os.path.dirname(__file__), 'config.json'), 'r', encoding='utf-8'))

ZMQ_GC_REP = CFG["zmq"]["gc_rep"]              # Solicitudes del cliente/test
ZMQ_GC_PUB = CFG["zmq"]["gc_pub"]              # Canal para actores SUB (Renovacion / Devolucion)
ZMQ_ACTOR_PRESTAMO_REP = CFG["zmq"]["actor_prestamo_rep"]  # Comunicación directa con el actor préstamo

def main():
    ctx = zmq.Context()

    # REP → recibe solicitudes del cliente/test
    rep = ctx.socket(zmq.REP)
    rep.bind(ZMQ_GC_REP)

    # PUB → publica mensajes para los actores de renovación y devolución
    pub = ctx.socket(zmq.PUB)
    pub.bind(ZMQ_GC_PUB)

    # REQ → comunicación directa con el actor de préstamo
    req_actor = ctx.socket(zmq.REQ)
    req_actor.connect(ZMQ_ACTOR_PRESTAMO_REP)

    print(f"[GC] REP {ZMQ_GC_REP} | PUB->{ZMQ_GC_PUB} | REQ->{ZMQ_ACTOR_PRESTAMO_REP}")
    print("[GC] Esperando solicitudes...")

    while True:
        # Esperar solicitud JSON del cliente o test
        msg = rep.recv_json()
        op = msg.get("op", "").upper()
        print(f"[GC] Solicitud recibida: {msg}")

        # --- Operación: PRESTAR ---
        if op == "PRESTAR":
            # Enviar al actor préstamo y recibir respuesta
            req_actor.send_json(msg)
            res = req_actor.recv_json()

            # Responder al cliente
            rep.send_json(res)
            print(f"[GC] Respuesta enviada al cliente: {res}")

        # --- Operación: DEVOLUCION ---
        elif op == "DEVOLUCION":
            # Espera breve para asegurar conexión SUBs
            time.sleep(1)
            pub.send_multipart([b"Devolucion", json.dumps(msg).encode("utf-8")])

            rep.send_json({"ok": True, "msg": "Devolución publicada"})
            print("[GC] Publicada solicitud de devolución")

        # --- Operación: RENOVACION ---
        elif op == "RENOVACION":
            # Espera breve para asegurar conexión SUBs
            time.sleep(1)
            pub.send_multipart([b"Renovacion", json.dumps(msg).encode("utf-8")])

            rep.send_json({"ok": True, "msg": "Renovación publicada"})
            print("[GC] Publicada solicitud de renovación")

        # --- Operación inválida ---
        else:
            rep.send_json({"ok": False, "msg": "Operación inválida"})
            print("[GC] Operación inválida recibida")

if __name__ == "__main__":
    main()