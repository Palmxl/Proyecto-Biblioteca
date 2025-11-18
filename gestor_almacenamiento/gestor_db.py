import os, json
import zmq
from mysql.connector import Error
from .replica_manager import ReplicaManager

# Carga la configuración del sistema (direcciones ZMQ, BD, etc.)
CFG = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'gestor_carga', 'config.json'), 'r', encoding='utf-8'))
GA_REP = CFG["zmq"]["ga_rep"]

# Respuestas estándar
def ok(msg):   return {"ok": True, "msg": msg}
def nok(msg):  return {"ok": False, "msg": msg}

def main():
    # Inicializa el gestor de réplicas (primaria/secundaria)
    rm = ReplicaManager()

    # Crea socket REP para atender solicitudes desde los actores
    ctx = zmq.Context()
    rep = ctx.socket(zmq.REP)
    rep.bind(GA_REP)

    print(f"[GA] REP en {GA_REP} | BD activa: {rm.active}")

    # Ciclo principal del Gestor de Almacenamiento
    while True:
        # Recibe solicitud en formato JSON
        req = json.loads(rep.recv_string())
        op = req.get("op", "").upper()

        try:
            conn = rm._conn()          # Selecciona la BD activa (primaria o secundaria)
            cur = conn.cursor()        # Crea cursor para ejecutar consultas SQL

            # --------------------------------------------------------
            # OPERACIÓN: PRESTAR
            # --------------------------------------------------------
            if op == "PRESTAR":
                isbn = req["isbn"]
                user = req["user"]
                days = int(req.get("days", 14))

                # Verifica disponibilidad del libro
                cur.execute("SELECT ejemplares_total, ejemplares_disponibles FROM libros WHERE isbn=%s FOR UPDATE", (isbn,))
                row = cur.fetchone()

                if not row:
                    cur.close()
                    rep.send_json(nok("Libro no existe"))
                    continue

                total, disp = row
                if disp <= 0:
                    cur.close()
                    rep.send_json(nok("Sin ejemplares disponibles"))
                    continue

                # Actualiza inventario y registra préstamo
                cur.execute("UPDATE libros SET ejemplares_disponibles = ejemplares_disponibles - 1 WHERE isbn=%s", (isbn,))
                cur.execute("""
                    INSERT INTO prestamos(isbn, usuario, fecha_prestamo, fecha_devolucion, renovaciones, estado)
                    VALUES (%s, %s, CURDATE(), DATE_ADD(CURDATE(), INTERVAL %s DAY), 0, 'activo')
                """, (isbn, user, days))
                conn.commit()
                cur.close()

                rep.send_json(ok("Prestado"))

                # Replica el cambio si se está usando la BD primaria
                if rm.active == "PRIMARY":
                    try:
                        cur2 = rm.secondary.cursor()
                        cur2.execute("UPDATE libros SET ejemplares_disponibles = ejemplares_disponibles - 1 WHERE isbn=%s", (isbn,))
                        cur2.execute("""
                            INSERT INTO prestamos(isbn, usuario, fecha_prestamo, fecha_devolucion, renovaciones, estado)
                            VALUES (%s, %s, CURDATE(), DATE_ADD(CURDATE(), INTERVAL %s DAY), 0, 'activo')
                        """, (isbn, user, days))
                        rm.secondary.commit()
                        cur2.close()
                    except Exception as e:
                        print(f"[GA] Error replicando PRESTAR en secundaria: {e}")

            # --------------------------------------------------------
            # OPERACIÓN: DEVOLVER
            # --------------------------------------------------------
            elif op == "DEVOLVER":
                isbn = req["isbn"]
                user = req["user"]

                # Marca el préstamo como devuelto
                cur.execute("""
                    UPDATE prestamos
                    SET estado='devuelto', fecha_devolucion=CURDATE()
                    WHERE isbn=%s AND usuario=%s AND estado='activo'
                    ORDER BY id DESC LIMIT 1
                """, (isbn, user))

                # Aumenta ejemplares disponibles sin superar el total
                cur.execute("""
                    UPDATE libros
                    SET ejemplares_disponibles = LEAST(ejemplares_total, ejemplares_disponibles + 1)
                    WHERE isbn=%s
                """, (isbn,))

                conn.commit()
                cur.close()

                rep.send_json(ok("Devolución aplicada"))

                # Replica si corresponde
                if rm.active == "PRIMARY":
                    try:
                        cur2 = rm.secondary.cursor()
                        cur2.execute("""
                            UPDATE prestamos
                            SET estado='devuelto', fecha_devolucion=CURDATE()
                            WHERE isbn=%s AND usuario=%s AND estado='activo'
                            ORDER BY id DESC LIMIT 1
                        """, (isbn, user))
                        cur2.execute("""
                            UPDATE libros
                            SET ejemplares_disponibles = LEAST(ejemplares_total, ejemplares_disponibles + 1)
                            WHERE isbn=%s
                        """, (isbn,))
                        rm.secondary.commit()
                        cur2.close()
                    except Exception as e:
                        print(f"[GA] Error replicando DEVOLVER en secundaria: {e}")

            # --------------------------------------------------------
            # OPERACIÓN: RENOVAR
            # --------------------------------------------------------
            elif op == "RENOVAR":
                isbn = req["isbn"]
                user = req["user"]
                days = int(req.get("days", 7))

                # Selecciona préstamo activo
                cur.execute("""
                    SELECT id, renovaciones FROM prestamos
                    WHERE isbn=%s AND usuario=%s AND estado='activo'
                    ORDER BY id DESC LIMIT 1
                """, (isbn, user))
                row = cur.fetchone()

                if not row:
                    cur.close()
                    rep.send_json(nok("No hay préstamo activo"))
                    continue

                pid, ren = row

                # Límite de renovaciones permitidas
                if ren >= 2:
                    cur.close()
                    rep.send_json(nok("Límite de 2 renovaciones alcanzado"))
                    continue

                # Actualiza fechas y contador
                cur.execute("""
                    UPDATE prestamos
                    SET fecha_devolucion = DATE_ADD(fecha_devolucion, INTERVAL %s DAY),
                        renovaciones = renovaciones + 1
                    WHERE id=%s
                """, (days, pid))
                conn.commit()
                cur.close()

                rep.send_json(ok("Renovación aplicada"))

                # Replica cambio si aplica
                if rm.active == "PRIMARY":
                    try:
                        cur2 = rm.secondary.cursor()
                        cur2.execute("""
                            UPDATE prestamos
                            SET fecha_devolucion = DATE_ADD(fecha_devolucion, INTERVAL %s DAY),
                                renovaciones = renovaciones + 1
                            WHERE isbn=%s AND usuario=%s AND estado='activo'
                            ORDER BY id DESC LIMIT 1
                        """, (days, isbn, user))
                        rm.secondary.commit()
                        cur2.close()
                    except Exception as e:
                        print(f"[GA] Error replicando RENOVAR en secundaria: {e}")

            # --------------------------------------------------------
            # OPERACIÓN NO VÁLIDA
            # --------------------------------------------------------
            else:
                cur.close()
                rep.send_json(nok("Operación inválida"))

        # Cambia a BD secundaria si ocurre un error en la primaria
        except Error as e:
            rm.switch()
            rep.send_json(nok(f"Failover activado: {e}"))

if __name__ == "__main__":
    main()
