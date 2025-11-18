from locust import HttpUser, task, between
import random

class BibliotecaUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def prestar_libro(self):
        data = {
            "isbn": f"ISBN{random.randint(1,15):05d}",
            "user": f"usuario{random.randint(1,200)}"
        }
        self.client.post("/prestamo", json=data)

    @task(2)
    def renovar_libro(self):
        data = {
            "isbn": f"ISBN{random.randint(1,15):05d}",
            "user": f"usuario{random.randint(1,200)}"
        }
        self.client.post("/renovacion", json=data)

    @task(1)
    def devolver_libro(self):
        data = {
            "isbn": f"ISBN{random.randint(1,15):05d}",
            "user": f"usuario{random.randint(1,200)}"
        }
        self.client.post("/devolucion", json=data)
