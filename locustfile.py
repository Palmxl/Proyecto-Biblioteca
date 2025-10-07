from locust import HttpUser, task, between
import json, random

class BibliotecaUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def prestar_libro(self):
        for _ in range(3):  # hace 3 operaciones antes de pausar
            data = {
                "op": "PRESTAR",
                "isbn": f"{random.randint(100, 999)}",
                "user": f"usuario{random.randint(1, 200)}"
            }
            self.client.post("/", data=json.dumps(data))

    @task(2)
    def renovar_libro(self):
        data = {
            "op": "RENOVAR",
            "isbn": f"{random.randint(100, 999)}",
            "user": f"usuario{random.randint(1, 200)}"
        }
        self.client.post("/", data=json.dumps(data))

    @task(1)
    def devolver_libro(self):
        data = {
            "op": "DEVOLVER",
            "isbn": f"{random.randint(100, 999)}",
            "user": f"usuario{random.randint(1, 200)}"
        }
        self.client.post("/", data=json.dumps(data))
