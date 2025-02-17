import os
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, insert, text

# Ensure the data directory exists
os.makedirs("data", exist_ok=True)

db_path = "data/gym_clases.db"
engine = create_engine(f"sqlite:///{db_path}")
metadata_obj = MetaData()

gym_classes = Table(
    "gym_clases",
    metadata_obj,
    Column("clase_id", Integer, primary_key=True),
    Column("nombre_monitor", String(32), primary_key=True),
    Column("nombre_clase", String(32)),
    Column("hora_comienzo", String(5)),  # Format: "HH:MM"
    Column("duracion_minutos", Integer),
)

metadata_obj.create_all(engine)

# Insert initial rows if the table is empty.
initial_rows = [
    {
        "clase_id": 1,
        "nombre_monitor": "Sara Jiménez",
        "nombre_clase": "Yoga Flow",
        "hora_comienzo": "09:00",
        "duracion_minutos": 60,
    },
    {
        "clase_id": 2,
        "nombre_monitor": "Miguel Pérez",
        "nombre_clase": "HIIT",
        "hora_comienzo": "10:30",
        "duracion_minutos": 45,
    },
    {
        "clase_id": 3,
        "nombre_monitor": "Emma Díaz",
        "nombre_clase": "Spinning",
        "hora_comienzo": "17:00",
        "duracion_minutos": 45,
    },
    {
        "clase_id": 4,
        "nombre_monitor": "Jaime Wilson",
        "nombre_clase": "Pilates",
        "hora_comienzo": "18:30",
        "duracion_minutos": 60,
    },
]

with engine.connect() as connection:
    count = connection.execute(text("SELECT COUNT(*) FROM gym_clases")).scalar()
    if count == 0:
        for row in initial_rows:
            stmt = insert(gym_classes).values(**row)
            with engine.begin() as transaction:
                transaction.execute(stmt) 