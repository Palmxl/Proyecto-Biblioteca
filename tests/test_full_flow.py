import zmq
import time

# ------------------------------
# CONFIGURACIÓN
# ------------------------------
PORT_REQ_REP = 5560     # Puerto del actor_prestamo
PORT_PUB_SUB = 5561     # Puerto compartido para devolucion/renovacion
isbn = "456"
usuario = "sebas"

# ------------------------------
# FUNCIÓN 1: PRÉSTAMO
# ------------------------------
def realizar_prestamo():
    print("\n--- PRUEBA 1: PRÉSTAMO ---")
    ctx = zmq.Context()
    req = ctx.socket(zmq.REQ)
    req.connect(f"tcp://localhost:{PORT_REQ_REP}")
    msg = f"{isbn}|{usuario}"
    print(f"Enviado: {msg}")
    req.send_string(msg)
    resp = req.recv_string()
    print(f"Respuesta del Actor de Préstamo:\n   {resp}\n")
    req.close()
    time.sleep(2)

# ------------------------------
# FUNCIÓN 2: RENOVACIÓN
# ------------------------------
def realizar_renovacion():
    print("\n--- PRUEBA 2: RENOVACIÓN ---")
    ctx = zmq.Context()
    pub = ctx.socket(zmq.PUB)
    pub.bind(f"tcp://*:{PORT_PUB_SUB}")
    time.sleep(1)
    msg = f"Renovacion|{isbn}|{usuario}"
    print(f"Publicado: {msg}")
    pub.send_string(msg)
    time.sleep(2)
    pub.close()

# ------------------------------
# FUNCIÓN 3: DEVOLUCIÓN
# ------------------------------
def realizar_devolucion():
    print("\n--- PRUEBA 3: DEVOLUCIÓN ---")
    ctx = zmq.Context()
    pub = ctx.socket(zmq.PUB)
    pub.bind(f"tcp://*:{PORT_PUB_SUB}")
    time.sleep(1)
    msg = f"Devolucion|{isbn}|{usuario}"
    print(f"Publicado: {msg}")
    pub.send_string(msg)
    time.sleep(2)
    pub.close()

# ------------------------------
# EJECUCIÓN PRINCIPAL
# ------------------------------
if __name__ == "__main__":
    print("Iniciando pruebas del flujo completo...")
    realizar_prestamo()
    realizar_renovacion()
    realizar_devolucion()
    print("\nFlujo completo finalizado.")