# gestor_almacenamiento/replica_manager.py
import json, os
import mysql.connector as mysql

CFG = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'gestor_carga', 'config.json'), 'r', encoding='utf-8'))
PRIMARY = CFG["mysql"]["primary"]
SECONDARY = CFG["mysql"]["secondary"]

def connect(cfg):
    return mysql.connect(
        host=cfg["host"], port=cfg["port"],
        user=cfg["user"], password=cfg["password"],
        database=cfg["database"], autocommit=True
    )

class ReplicaManager:
    def __init__(self):
        self.active = "PRIMARY"
        self.primary = connect(PRIMARY)
        self.secondary = connect(SECONDARY)

    def _conn(self):
        """Devuelve la conexión activa (primaria o secundaria)."""
        return self.primary if self.active == "PRIMARY" else self.secondary

    def switch(self):
        """Alterna entre la base primaria y secundaria en caso de fallo."""
        self.active = "SECONDARY" if self.active == "PRIMARY" else "PRIMARY"
        print(f"Conmutación realizada. Nueva BD activa: {self.active}")