import os
import json
import zmq
import time

# Cargar configuración desde config.json
BASE_DIR = os.path.dirname(__file__)
CFG_PATH = os.path.join(BASE_DIR, "config.json")

with open(CFG_PATH, "r", encoding="utf-8") as f:
    CFG = json.load(f)

ZMQ_GC_REP = CFG["zmq"]["gc_rep"]                  # Solicitudes de PS / gateway
ZMQ_GC_PUB = CFG["zmq"]["gc_pub"]                  # Canal para actores SUB (Renovacion / Devolucion)
ZMQ_ACTOR_PRESTAMO_REP = CFG["zmq"]["actor_prestamo_rep"]  # Comunicación directa con actor préstamo


def main():
    ctx = zmq.Context.instance()

    # REP → recibe solicitudes de los PS / gateway HTTP
    rep = ctx.socket(zmq.REP)
    rep.bind(ZMQ_GC_REP)

    # PUB → publica mensajes para los actores de renovación y devolución
    pub = ctx.socket(zmq.PUB)
    pub.bind(ZMQ_GC_PUB)

    # REQ → comunicación directa con el actor de préstamo
    req_actor = ctx.socket(zmq.REQ)
    req_actor.connect(ZMQ_ACTOR_PRESTAMO_REP)

    # Timeouts para no colgarnos si el actor no responde
    req_actor.RCVTIMEO = 5000   # 5 segundos
    req_actor.SNDTIMEO = 5000   # 5 segundos

    # Pequeña pausa para que los SUBs alcancen a suscribirse
    time.sleep(0.5)

    print(f"[GC] REP  -> {ZMQ_GC_REP}")
    print(f"[GC] PUB  -> {ZMQ_GC_PUB}")
    print(f"[GC] REQ  -> {ZMQ_ACTOR_PRESTAMO_REP}")
    print("[GC] Esperando solicitudes...")

    while True:
        try:
            # Esperar solicitud JSON del PS / gateway
            msg = rep.recv_json()
            print(f"[GC] Solicitud recibida: {msg}")

            # Normalizar operación
            op = (msg.get("op") or msg.get("operacion") or msg.get("tipo") or "").upper()
            isbn = msg.get("isbn")
            user = msg.get("user") or msg.get("usuario")

            # --- PRESTAR (síncrono con actor_prestamo) ---
            if op == "PRESTAR":
                try:
                    print(f"[GC] Enviando solicitud de PRESTAR a actor_prestamo: {isbn} - {user}")
                    req_actor.send_json(msg)
                    res = req_actor.recv_json()
                    print(f"[GC] Respuesta de actor_prestamo: {res}")
                    rep.send_json(res)
                except zmq.error.Again:
                    # No respondió el actor en el timeout
                    err = {"ok": False, "msg": "Actor de préstamo no responde (timeout)"}
                    print(f"[GC] {err}")
                    rep.send_json(err)

            # --- DEVOLVER / DEVOLUCION (asíncrono via PUB/SUB) ---
            elif op in ("DEVOLVER", "DEVOLUCION"):
                payload = json.dumps(msg).encode("utf-8")
                pub.send_multipart([b"Devolucion", payload])
                print(f"[GC] Publicada solicitud de DEVOLUCION para {isbn} - {user}")
                rep.send_json({"ok": True, "msg": "Devolución publicada al tópico 'Devolucion'"})

            # --- RENOVAR / RENOVACION (asíncrono via PUB/SUB) ---
            elif op in ("RENOVAR", "RENOVACION"):
                payload = json.dumps(msg).encode("utf-8")
                pub.send_multipart([b"Renovacion", payload])
                print(f"[GC] Publicada solicitud de RENOVACION para {isbn} - {user}")
                rep.send_json({"ok": True, "msg": "Renovación publicada al tópico 'Renovacion'"})

            # --- Operación inválida ---
            else:
                msg_err = f"Operación inválida o no soportada: '{op}'"
                print(f"[GC] {msg_err}")
                rep.send_json({"ok": False, "msg": msg_err})

        except Exception as e:
            print(f"[GC] Error procesando solicitud: {e}")
            try:
                rep.send_json({"ok": False, "msg": "Error interno en Gestor de Carga"})
            except Exception:
                # Si el REP ya quedó desincronizado, igual seguimos el loop
                pass


if __name__ == "__main__":
    main()
