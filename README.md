# 📚 Biblioteca Distribuida 2025  
**Proyecto académico de Sistemas Distribuidos — Pontificia Universidad Javeriana**

---

## 🧠 Descripción general
El sistema **Biblioteca Distribuida** implementa un entorno **cliente-servidor distribuido** para la gestión de operaciones de biblioteca:  
- 📖 *Préstamo*  
- ♻️ *Renovación*  
- 🔁 *Devolución*  

El proyecto utiliza **ZeroMQ** como middleware para comunicación distribuida, con soporte para:
- Patrones **REQ/REP** (operaciones síncronas),
- Patrones **PUB/SUB** (difusión de eventos),
- Replicación de datos entre sedes mediante un **Gestor de Almacenamiento (GA) primario/secundario**,  
- Mecanismos de failover automatizados,
- Un **gateway HTTP** para integrar pruebas de carga con **Locust**.

---

## 🏗️ Arquitectura del sistema

```
                ┌──────────────────────────┐
                │  Procesos Solicitantes   │
                │ (Usuarios / PS / Locust) │
                └────────────┬─────────────┘
                             │  REQ/REP (ZMQ)
                             ▼
                ┌──────────────────────────┐
                │     Gestor de Carga (GC) │
                │  REP ← PS | PUB → Actores│
                │  REQ → Actor Préstamo    │
                └──────┬──────────┬────────┘
                       │          │
           PUB/SUB ↓   │          │  REQ/REP ↓
 ┌──────────────────┐  │  ┌──────────────────┐
 │ Actor Renovación │  │  │  Actor Préstamo  │
 │  SUB "Renovacion"│  │  │  REQ → GA        │
 └──────────────────┘  │  └──────────────────┘
           PUB/SUB ↓   │
 ┌──────────────────┐  │
 │ Actor Devolución │  │
 │  SUB "Devolucion"│  │
 └──────────────────┘  │
                       ▼
                ┌──────────────────────────┐
                │ Gestor de Almacenamiento │
                │ (GA - Base de Datos)     │
                └──────────────────────────┘
```

---

## 📦 Estructura del proyecto

```
Proyecto-Biblioteca/
│
├── actores/
│   ├── actor_prestamo.py
│   ├── actor_devolucion.py
│   ├── actor_renovacion.py
│
├── gestor_carga/
│   ├── gestor_carga.py
│   ├── config.json
│
├── gestor_almacenamiento/
│   ├── gestor_db.py
│   ├── replica_manager.py
│
├── procesos_solicitantes/
│   ├── ps_mixto.py
│
├── solicitudes/
│   ├── solicitudes_mixto1.txt
│   └── solicitudes_mixto2.txt
│
├── requirements.txt
├── http_gateway.py
├── locustfile.py
└── README.md
```

---

# 🐍 Instalación del entorno virtual (Python 3.10+)

### 1️⃣ Crear entorno
```bash
python3 -m venv venv
```

### 2️⃣ Activar entorno

**Linux / Ubuntu:**
```bash
source venv/bin/activate
```

**Windows (PowerShell):**
```bash
venv\Scripts\activate
```

### 3️⃣ Instalar dependencias
```bash
pip install -r requirements.txt
```

Si no existe, instala manualmente:
```bash
pip install pyzmq mysql-connector-python flask locust
```

---

# 📘 Ejecución del Sistema Distribuido (3 Máquinas)

Estas instrucciones describen **únicamente** cómo ejecutar cada componente en las tres máquinas del sistema distribuido.

---

# 🖥️ MÁQUINA 1 – Sede 1 (VM 10.43.103.174)

### ▶️ Gestor de Carga (GC – Sede 1)
```bash
python3 -m gestor_carga.gestor_carga
```

### ▶️ Actores de Sede 1
```bash
python3 -m actores.actor_prestamo
python3 -m actores.actor_devolucion
python3 -m actores.actor_renovacion
```

### ▶️ Proceso Solicitante (PS mixto)
```bash
python3 procesos_solicitantes/ps_mixto.py solicitudes/solicitudes_mixto1.txt
```

---

# 🖥️ MÁQUINA 2 – Sede 1 (192.168.0.3)

### ▶️ Gestor de Almacenamiento — BD primaria
```bash
python3 -m gestor_almacenamiento.gestor_db
```

**Requisitos de la BD primaria:**
- MySQL activo en `127.0.0.1:3306`
- BD `biblioteca_sede1`

---

# 🖥️ MÁQUINA 3 – Sede 2 (192.168.1.65)

### ▶️ Gestor de Almacenamiento — BD secundaria
```bash
python3 -m gestor_almacenamiento.gestor_db
```

### ▶️ Actores de Sede 2
```bash
python3 -m actores.actor_prestamo
python3 -m actores.actor_devolucion
python3 -m actores.actor_renovacion
```

### ▶️ (Opcional) Segundo Gestor de Carga
```bash
python3 -m gestor_carga.gestor_carga
```

---

# 🌐 Gateway HTTP + Locust (Pruebas de carga)

### 1️⃣ Iniciar gateway HTTP → GC
```bash
python3 http_gateway.py
```

### 2️⃣ Ejecutar Locust
```bash
locust -f locustfile.py
```

Panel de control:
```
http://localhost:8089
```

---

# 🧠 Créditos

**Autores:** Juan Martín Sánchez – Juan Sebastián Téllez  
**Proyecto:** Biblioteca Distribuida — Sistemas Distribuidos  
**Profesor:** M. Curiel — Pontificia Universidad Javeriana  
**Tecnologías:** Python 3.10, ZeroMQ, MySQL, Flask, Locust  
