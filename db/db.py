import os
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, insert, text

# Ensure the data directory exists
os.makedirs("data", exist_ok=True)

db_path = "data/gym_classes.db"
engine = create_engine(f"sqlite:///{db_path}")
metadata_obj = MetaData()

gym_classes = Table(
    "gym_classes",
    metadata_obj,
    Column("class_id", Integer, primary_key=True),
    Column("instructor_name", String(32), primary_key=True),
    Column("class_name", String(32)),
    Column("start_time", String(5)),  # Format: "HH:MM"
    Column("duration_mins", Integer),
)

metadata_obj.create_all(engine)

# Insert initial rows if the table is empty.
initial_rows = [
    {
        "class_id": 1,
        "instructor_name": "Sarah Johnson",
        "class_name": "Yoga Flow",
        "start_time": "09:00",
        "duration_mins": 60,
    },
    {
        "class_id": 2,
        "instructor_name": "Mike Peters",
        "class_name": "HIIT",
        "start_time": "10:30",
        "duration_mins": 45,
    },
    {
        "class_id": 3,
        "instructor_name": "Emma Davis",
        "class_name": "Spin Class",
        "start_time": "17:00",
        "duration_mins": 45,
    },
    {
        "class_id": 4,
        "instructor_name": "James Wilson",
        "class_name": "Pilates",
        "start_time": "18:30",
        "duration_mins": 60,
    },
]

with engine.connect() as connection:
    count = connection.execute(text("SELECT COUNT(*) FROM gym_classes")).scalar()
    if count == 0:
        for row in initial_rows:
            stmt = insert(gym_classes).values(**row)
            with engine.begin() as transaction:
                transaction.execute(stmt) 