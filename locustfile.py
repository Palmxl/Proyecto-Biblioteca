from locust import HttpUser, task, between
import random, json

class BibliotecaUser(HttpUser):
    wait_time = between(1, 3)  # tiempo de espera entre tareas

    # --- Simular préstamo ---
    @task(3)
    def prestar_libro(self):
        data = {
            "isbn": f"ISBN{random.randint(1,15):05d}",  # tus ISBN reales (1 a 15)
            "user": f"usuario{random.randint(1, 200)}"
        }
        self.client.post("/prestamo", json=data)

    # --- Simular renovación ---
    @task(2)
    def renovar_libro(self):
        data = {
            "isbn": f"ISBN{random.randint(1,15):05d}",
            "user": f"usuario{random.randint(1, 200)}"
        }
        self.client.post("/renovacion", json=data)

    # --- Simular devolución ---
    @task(1)
    def devolver_libro(self):
        data = {
            "isbn": f"ISBN{random.randint(1,15):05d}",
            "user": f"usuario{random.randint(1, 200)}"
        }
        self.client.post("/devolucion", json=data)
