# gestor_almacenamiento/replica_manager.py
import json
import os
import mysql.connector as mysql
from mysql.connector import Error

# Cargar config.json (ruta relativa al proyecto)
CFG = json.load(
    open(
        os.path.join(os.path.dirname(__file__), '..', 'gestor_carga', 'config.json'),
        'r',
        encoding='utf-8'
    )
)

PRIMARY = CFG["mysql"]["primary"]
SECONDARY = CFG["mysql"]["secondary"]


def connect(cfg):
    return mysql.connect(
        host=cfg["host"],
        port=cfg["port"],
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        autocommit=False  # commit lo maneja el GA
    )


class ReplicaManager:
    def __init__(self):
        # Siempre intentamos conectar a la primaria
        self.primary = connect(PRIMARY)
        print(f"[ReplicaManager] PRIMARY OK -> {PRIMARY['host']}:{PRIMARY['port']} / {PRIMARY['database']}")

        # La secundaria es opcional: si falla, seguimos con None
        self.secondary = None
        try:
            self.secondary = connect(SECONDARY)
            print(f"[ReplicaManager] SECONDARY OK -> {SECONDARY['host']}:{SECONDARY['port']} / {SECONDARY['database']}")
        except Error as e:
            print(f"[ReplicaManager] WARN: no se pudo conectar a SECONDARY ({SECONDARY['host']}:{SECONDARY['port']}): {e}")
            self.secondary = None

        # Empezamos trabajando con la primaria
        self.active = "PRIMARY"

    def _conn(self):
        """Devuelve la conexión activa (primaria o secundaria)."""
        if self.active == "PRIMARY":
            return self.primary
        else:
            # Si queremos usar secundaria pero no existe, devolvemos primaria
            return self.secondary if self.secondary is not None else self.primary

    def switch(self):
        """Alterna entre la base primaria y secundaria en caso de fallo."""
        if self.active == "PRIMARY" and self.secondary is not None:
            self.active = "SECONDARY"
            print("[ReplicaManager] FAILOVER: PRIMARY -> SECONDARY")
        elif self.active == "SECONDARY":
            print("[ReplicaManager] FAILOVER ignorado: ya estamos en SECONDARY")
        else:
            print("[ReplicaManager] FAILOVER ignorado: no hay SECONDARY disponible")