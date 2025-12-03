import zmq
import time
import json

ctx = zmq.Context()
req = ctx.socket(zmq.REQ)
req.connect("tcp://127.0.0.1:5555")

print("Iniciando pruebas del flujo completo del sistema distribuido...")

# Datos de prueba
isbn = "456"
usuario = "carlos"

# --- PRÉSTAMO ---
print("\n--- PRUEBA 1: PRÉSTAMO ---")
data_prestamo = {"op": "PRESTAR", "isbn": isbn, "user": usuario}
req.send_string(json.dumps(data_prestamo))
print(f"Enviado: {data_prestamo}")
respuesta = req.recv_json()
print(f"Respuesta: {respuesta}")

time.sleep(2)

# --- RENOVACIÓN ---
print("\n--- PRUEBA 2: RENOVACIÓN ---")
data_renovacion = {"op": "RENOVACION", "isbn": isbn, "user": usuario}
req.send_string(json.dumps(data_renovacion))
print(f"Enviado: {data_renovacion}")
respuesta = req.recv_json()
print(f"Respuesta: {respuesta}")

time.sleep(2)

# --- DEVOLUCIÓN ---
print("\n--- PRUEBA 3: DEVOLUCIÓN ---")
data_devolucion = {"op": "DEVOLUCION", "isbn": isbn, "user": usuario}
req.send_string(json.dumps(data_devolucion))
print(f"Enviado: {data_devolucion}")
respuesta = req.recv_json()
print(f"Respuesta: {respuesta}")

print("\nFlujo completo finalizado correctamente.")