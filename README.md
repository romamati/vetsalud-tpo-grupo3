# VetSalud S.A. — Sistema de Gestión de Clínica Veterinaria

**Trabajo Práctico Obligatorio — Bases de Datos II | 1er Cuatrimestre 2026**

| Campo | Detalle |
|---|---|
| Grupo | 3 |
| Integrantes | Franco Ghigliani, Román Berruti, Matías Romanto |
| Materia | Bases de Datos II |
| Entrega | Viernes 12/06/2026 hasta las 23:59 hs |

---

## Arquitectura de Persistencia Políglota

Este sistema implementa una arquitectura **políglota** combinando dos motores NoSQL de paradigmas distintos:

| Motor | Paradigma | Entidades | Justificación |
|---|---|---|---|
| **MongoDB** | Documental | Stock farmacéutico | Documentos con atributos variables, operaciones de inventario, actualizaciones masivas |
| **Neo4j** | Grafos | Pacientes, Propietarios, Veterinarios, Consultas, Vacunaciones | Relaciones complejas entre entidades, traversal eficiente, consultas de tipo JOIN profundo |

### ¿Por qué Neo4j y no una BD relacional?
Las entidades del sistema forman una red natural de relaciones: un paciente pertenece a un propietario, es atendido por veterinarios, recibe vacunas administradas por veterinarios, y esas consultas se realizan en sucursales. Consultas como *"historial completo de un paciente"* o *"todos los pacientes de una sucursal a través del veterinario"* son traversías de grafo que Neo4j resuelve de forma nativa y eficiente mediante Cypher, evitando múltiples JOINs costosos.

### ¿Por qué MongoDB para el stock?
El inventario farmacéutico tiene atributos que pueden variar por categoría de producto, es independiente del grafo de relaciones clínicas, y requiere operaciones de actualización masiva (ej: decrementar unidades tras una consulta). El modelo documental de MongoDB es ideal para este caso.

---

## Tecnologías utilizadas

- **Python 3.12+**
- **pymongo** — driver oficial de MongoDB para Python
- **neo4j** — driver oficial de Neo4j para Python
- **pandas** — carga y procesamiento de CSVs

---

## Instalación y configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/romamati/vetsalud-tpo-grupo3.git
cd vetsalud-tpo-grupo3
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Crear un archivo `.env` en la raíz del proyecto basándose en `.env.example`:

```bash
cp .env.example .env
```

Editar `.env` con las credenciales de cada base de datos:

```
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=vetsalud

NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=tu_password
```

### 4. Cargar los datos iniciales

```bash
python mongodb/load_data.py
python neo4j/load_data.py
```

### 5. Ejecutar el sistema

```bash
python main.py
```

---

## Estructura del proyecto

```
vetsalud-tpo/
├── data/                        # CSVs con datasets provistos + registros propios
│   ├── pacientes.csv
│   ├── propietarios.csv
│   ├── veterinarios.csv
│   ├── consultas.csv
│   ├── vacunaciones.csv
│   └── stock_farmaceutico.csv
├── mongodb/
│   ├── connection.py            # Conexión a MongoDB
│   └── load_data.py             # Carga de datos desde CSV
├── neo4j/
│   ├── connection.py            # Conexión a Neo4j
│   └── load_data.py             # Carga de nodos y relaciones desde CSV
├── queries/
│   ├── mongodb_queries.py       # Consultas Q7, Q8, Q9, Q11, Q15
│   └── neo4j_queries.py         # Consultas Q1–Q6, Q10, Q12–Q14
├── main.py                      # Menú principal integrador
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Consultas implementadas

| # | Descripción | Motor |
|---|---|---|
| 1 | Pacientes activos con todos sus datos de propietario | Neo4j |
| 2 | Consultas médicas en estado 'Seguimiento' con veterinario y costo | Neo4j |
| 3 | Historial completo de un paciente (consultas + vacunas por fecha) | Neo4j |
| 4 | Propietarios con más de un paciente registrado | Neo4j |
| 5 | Veterinarios activos y cantidad de consultas en los últimos 60 días | Neo4j |
| 6 | Pacientes con vacunas vencidas | Neo4j |
| 7 | Top 5 diagnósticos más frecuentes | Neo4j |
| 8 | Stock con menos de 50 unidades y su proveedor | MongoDB |
| 9 | Consultas de tipo 'Control' con costo menor a $5.000 | Neo4j |
| 10 | Todos los pacientes de una sucursal determinada | Neo4j |
| 11 | Ingresos totales por veterinario en el mes actual | Neo4j |
| 12 | Propietarios sin consultas en el último año | Neo4j |
| 13 | ABM completo de propietarios | Neo4j |
| 14 | Registro de nueva consulta médica con validación | Neo4j |
| 15 | Actualización masiva del stock tras una consulta | MongoDB |
