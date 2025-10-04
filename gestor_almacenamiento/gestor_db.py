# gestor_almacenamiento/gestor_bd.py
import os, json
import zmq
from mysql.connector import Error
from .replica_manager import ReplicaManager

CFG = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'gestor_carga', 'config.json'), 'r', encoding='utf-8'))
GA_REP = CFG["zmq"]["ga_rep"]

def ok(msg):   return {"ok": True,  "msg": msg}
def nok(msg):  return {"ok": False, "msg": msg}

def main():
    rm = ReplicaManager()
    ctx = zmq.Context()
    rep = ctx.socket(zmq.REP)
    rep.bind(GA_REP)
    print(f"[GA] REP en {GA_REP} | BD activa: {rm.active}")

    while True:
        req = json.loads(rep.recv_string())
        op = req.get("op", "").upper()
        try:
            conn = rm._conn()
            cur = conn.cursor()

            if op == "PRESTAR":
                # Datos de entrada
                isbn = req["isbn"]
                user = req["user"]
                days = int(req.get("days", 14))  # periodo de préstamo

                # 1) disponibilidad
                cur.execute("SELECT ejemplares_total, ejemplares_disponibles FROM libros WHERE isbn=%s FOR UPDATE", (isbn,))
                row = cur.fetchone()
                if not row:
                    cur.close(); rep.send_json(nok("Libro no existe")); continue
                total, disp = row
                if disp <= 0:
                    cur.close(); rep.send_json(nok("Sin ejemplares disponibles")); continue

                # 2) aplicar préstamo
                cur.execute("UPDATE libros SET ejemplares_disponibles = ejemplares_disponibles - 1 WHERE isbn=%s", (isbn,))
                cur.execute("""
                    INSERT INTO prestamos(isbn, usuario, fecha_prestamo, fecha_devolucion, renovaciones, estado)
                    VALUES (%s, %s, CURDATE(), DATE_ADD(CURDATE(), INTERVAL %s DAY), 0, 'activo')
                """, (isbn, user, days))
                conn.commit()
                cur.close()
                rep.send_json(ok("Prestado"))

            elif op == "DEVOLVER":
                isbn = req["isbn"]
                user = req["user"]

                # 1) cerrar préstamo activo
                cur.execute("""
                    UPDATE prestamos
                    SET estado='devuelto', fecha_devolucion=CURDATE()
                    WHERE isbn=%s AND usuario=%s AND estado='activo'
                    ORDER BY id DESC LIMIT 1
                """, (isbn, user))
                # 2) devolver al inventario
                cur.execute("""
                    UPDATE libros
                    SET ejemplares_disponibles = LEAST(ejemplares_total, ejemplares_disponibles + 1)
                    WHERE isbn=%s
                """, (isbn,))
                conn.commit()
                cur.close()
                rep.send_json(ok("Devolución aplicada"))

            elif op == "RENOVAR":
                isbn = req["isbn"]
                user = req["user"]
                days = int(req.get("days", 7))

                # 1) validar límite de renovaciones
                cur.execute("""
                    SELECT id, renovaciones FROM prestamos
                    WHERE isbn=%s AND usuario=%s AND estado='activo'
                    ORDER BY id DESC LIMIT 1
                """, (isbn, user))
                row = cur.fetchone()
                if not row:
                    cur.close(); rep.send_json(nok("No hay préstamo activo")); continue
                pid, ren = row
                if ren >= 2:
                    cur.close(); rep.send_json(nok("Límite de 2 renovaciones alcanzado")); continue

                # 2) aplicar renovación
                cur.execute("""
                    UPDATE prestamos
                    SET fecha_devolucion = DATE_ADD(fecha_devolucion, INTERVAL %s DAY),
                        renovaciones = renovaciones + 1
                    WHERE id=%s
                """, (days, pid))
                conn.commit()
                cur.close()
                rep.send_json(ok("Renovación aplicada"))

            else:
                cur.close()
                rep.send_json(nok("Operación inválida"))

        except Error as e:
            rm.switch()
            rep.send_json(nok(f"Failover activado: {e}"))

if __name__ == "__main__":
    main()