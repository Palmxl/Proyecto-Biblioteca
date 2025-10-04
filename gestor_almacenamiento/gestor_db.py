import mysql.connector
from datetime import datetime, timedelta
import threading

class GestorBD:
    def __init__(self, host='localhost', user='root', password='password',
                 database='biblioteca', replica_host=None):
        self.cnx = mysql.connector.connect(
            host=host, user=user, password=password, database=database
        )
        self.cursor = self.cnx.cursor(dictionary=True)
        self.replica_host = replica_host
        self.user = user
        self.password = password
        self.database = database

    # -------- Operaciones --------
    def prestar_libro(self, isbn, usuario):
        self.cursor.execute("SELECT * FROM libros WHERE isbn=%s", (isbn,))
        libro = self.cursor.fetchone()

        if not libro:
            return "Libro no encontrado."
        if libro['ejemplares_disponibles'] <= 0:
            return "No hay ejemplares disponibles."

        fecha_prestamo = datetime.now()
        fecha_dev = fecha_prestamo + timedelta(weeks=2)

        self.cursor.execute("""
            INSERT INTO prestamos (isbn, usuario, fecha_prestamo, fecha_devolucion)
            VALUES (%s, %s, %s, %s)
        """, (isbn, usuario, fecha_prestamo, fecha_dev))
        self.cursor.execute("""
            UPDATE libros SET ejemplares_disponibles = ejemplares_disponibles - 1
            WHERE isbn=%s
        """, (isbn,))
        self.cnx.commit()

        self._replicar_async(f"UPDATE libros SET ejemplares_disponibles = ejemplares_disponibles - 1 WHERE isbn='{isbn}'")
        return f"Préstamo exitoso. Devolver antes de {fecha_dev.date()}"

    def devolver_libro(self, isbn, usuario):
        self.cursor.execute("""
            UPDATE prestamos SET estado='devuelto'
            WHERE isbn=%s AND usuario=%s AND estado='activo'
        """, (isbn, usuario))
        self.cursor.execute("""
            UPDATE libros SET ejemplares_disponibles = ejemplares_disponibles + 1
            WHERE isbn=%s
        """, (isbn,))
        self.cnx.commit()

        self._replicar_async(f"UPDATE libros SET ejemplares_disponibles = ejemplares_disponibles + 1 WHERE isbn='{isbn}'")
        return "Libro devuelto."

    def renovar_libro(self, isbn, usuario):
        self.cursor.execute("""
            SELECT * FROM prestamos
            WHERE isbn=%s AND usuario=%s AND estado='activo'
        """, (isbn, usuario))
        prestamo = self.cursor.fetchone()

        if not prestamo:
            return "No existe préstamo activo."
        if prestamo['renovaciones'] >= 2:
            return "Límite de renovaciones alcanzado."

        # Sumar una semana a la fecha actual de devolución
        fecha_dev = prestamo['fecha_devolucion']
        if isinstance(fecha_dev, datetime):
            nueva_fecha = fecha_dev + timedelta(weeks=1)
        else:
            # Si es un objeto date, convertirlo a datetime antes de sumar
            nueva_fecha = datetime.combine(fecha_dev, datetime.min.time()) + timedelta(weeks=1)
            nueva_fecha = nueva_fecha.date()  # dejarlo como date final

        self.cursor.execute("""
            UPDATE prestamos
            SET fecha_devolucion=%s, renovaciones=renovaciones+1
            WHERE id=%s
        """, (nueva_fecha, prestamo['id']))
        self.cnx.commit()

        self._replicar_async(f"UPDATE prestamos SET fecha_devolucion='{nueva_fecha}', renovaciones=renovaciones+1 WHERE id={prestamo['id']}")
        return f"Renovado. Nueva fecha de devolución: {nueva_fecha}"

    # -------- Réplica --------
    def _replicar_async(self, query):
        if not self.replica_host:
            return
        def _replicar():
            try:
                cnx2 = mysql.connector.connect(
                    host=self.replica_host, user=self.user,
                    password=self.password, database=self.database
                )
                c2 = cnx2.cursor()
                c2.execute(query)
                cnx2.commit()
                c2.close()
                cnx2.close()
                print(f"[Replica] Ejecutado: {query}")
            except Exception as e:
                print(f"[Replica Error] {e}")

        threading.Thread(target=_replicar).start()

    def close(self):
        self.cursor.close()
        self.cnx.close()