# 📚 Biblioteca Distribuida 2025  
**Proyecto académico de Sistemas Distribuidos — Pontificia Universidad Javeriana**

---

## 🧠 Descripción general
El sistema **Biblioteca Distribuida** implementa un entorno **cliente-servidor distribuido** para gestionar operaciones de biblioteca (📖 *préstamo*, ♻️ *renovación*, 🔁 *devolución*), comunicándose mediante **ZeroMQ** con un **Gestor de Carga (GC)**, **Gestores de Almacenamiento (GA)** y **Actores especializados**.  

Incluye:
- Comunicación asíncrona entre componentes (REQ/REP, PUB/SUB).  
- Replicación de base de datos entre sedes.  
- Integración con **Locust + Flask Gateway** para pruebas de carga HTTP.  

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
│   ├── biblioteca.db / conexión MySQL
│
├── procesos_solicitantes/
│   ├── ps_prestar.py
│   ├── ps_devolver.py
│   ├── ps_renovar.py
│
├── solicitudes/
│   ├── solicitudes_ps1.txt
│   ├── solicitudes_ps2.txt
│   └── solicitudes_ps3.txt
│
├── gateway/
│   ├── http_gateway.py
│   ├── locustfile.py
│
├── generar_solicitudes.py
├── requirements.txt
└── README.md
```

---

## 🐍 Instalación del entorno virtual (Python 3.10+)

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

Si no tienes el archivo `requirements.txt`, puedes instalar manualmente:
```bash
pip install pyzmq flask locust
```

---

## ⚙️ Ejecución del sistema distribuido

Abre 6 terminales y ejecuta en orden:

### 🧱 1. Gestor de Almacenamiento (GA)
```bash
python3 -m gestor_almacenamiento.gestor_db
```

### ⚙️ 2. Gestor de Carga (GC)
```bash
python3 -m gestor_carga.gestor_carga
```

### 🎭 3. Actores
```bash
python3 -m actores.actor_prestamo
python3 -m actores.actor_devolucion
python3 -m actores.actor_renovacion
```

### 👥 4. Procesos Solicitantes (PS)
```bash
python3 -m procesos_solicitantes.ps_prestar solicitudes/solicitudes_ps1.txt
python3 -m procesos_solicitantes.ps_devolver solicitudes/solicitudes_ps2.txt
python3 -m procesos_solicitantes.ps_renovar solicitudes/solicitudes_ps3.txt
```

---

## 🌐 Gateway HTTP + Locust (pruebas de carga)

### 🧩 1. Iniciar el gateway
```bash
python3 gateway/http_gateway.py
```

### ⚡ 2. Iniciar Locust
```bash
locust -f gateway/locustfile.py --host http://127.0.0.1:8080
```

Abre el panel en tu navegador:
```
http://localhost:8089
```

---

## 📊 Métricas sugeridas

| Prueba | Usuarios | Operaciones | Tiempo medio (ms) | Éxito (%) |
|---------|-----------|--------------|------------------|------------|
| Funcional (manual) | 1 | 10 | <100 | 100 |
| Carga moderada | 10 | 100 | <200 | 100 |
| Alta concurrencia | 50 | 1000 | <300 | 95 |
| Réplica entre sedes | 10/10 | 500 | <400 | 98 |

---

## 🧪 Consultas MySQL útiles
```sql
SELECT isbn, titulo, usuario FROM libros WHERE usuario IS NULL;
SELECT isbn, usuario FROM libros WHERE usuario IS NOT NULL;
SELECT COUNT(*) FROM libros;
```

---

## 🧠 Créditos
**Autores:** Juan Martín Sánchez - Juan Sebastian Tellez
**Proyecto:** Biblioteca Sistemas Distribuidos  
**Profesor:** M. Curiel — Pontificia Universidad Javeriana  
**Tecnologías:** Python 3.10, ZeroMQ, Flask, Locust, MySQL  
