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
        try:
            # Esperar solicitud JSON del cliente o test
            msg = rep.recv_json()
            print(f"[GC] Solicitud recibida: {msg}")

            # 🔧 Compatibilidad de campo ('op', 'operacion', 'tipo')
            op = (msg.get("op") or msg.get("operacion") or msg.get("tipo") or "").upper()
            isbn = msg.get("isbn")

            # --- Operación: PRESTAR ---
            if op == "PRESTAR":
                req_actor.send_json(msg)
                res = req_actor.recv_json()

                rep.send_json(res)
                print(f"[GC] Respuesta enviada al cliente: {res}")

            # --- Operación: DEVOLVER / DEVOLUCION ---
            elif op in ["DEVOLVER", "DEVOLUCION"]:
                time.sleep(0.5)
                pub.send_multipart([b"Devolucion", json.dumps(msg).encode("utf-8")])

                rep.send_json({"ok": True, "msg": "Devolución publicada"})
                print(f"[GC] Publicada solicitud de devolución ({isbn})")

            # --- Operación: RENOVAR / RENOVACION ---
            elif op in ["RENOVAR", "RENOVACION"]:
                time.sleep(0.5)
                pub.send_multipart([b"Renovacion", json.dumps(msg).encode("utf-8")])

                rep.send_json({"ok": True, "msg": "Renovación publicada"})
                print(f"[GC] Publicada solicitud de renovación ({isbn})")

            # --- Operación inválida ---
            else:
                rep.send_json({"ok": False, "msg": f"Operación inválida: {op}"})
                print(f"[GC] Operación inválida recibida: {op}")

        except Exception as e:
            print(f"[GC] Error procesando solicitud: {e}")
            rep.send_json({"ok": False, "msg": "Error interno en Gestor de Carga"})


if __name__ == "__main__":
    main()
