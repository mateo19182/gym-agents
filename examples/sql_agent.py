from sqlalchemy import (
    Column,
    Float,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    insert,
    inspect,
    text,
)
import os
import dotenv
from smolagents import GradioUI
import json

dotenv.load_dotenv()

# Change the engine creation to use a file-based database
engine = create_engine("sqlite:///data/gym_classes.db")
metadata_obj = MetaData()

# create gym classes SQL table
table_name = "gym_classes"
gym_classes = Table(
    table_name,
    metadata_obj,
    Column("class_id", Integer, primary_key=True),
    Column("instructor_name", String(32), primary_key=True),
    Column("class_name", String(32)),
    Column("start_time", String(5)),  # Format: "HH:MM"
    Column("duration_mins", Integer),
)
metadata_obj.create_all(engine)

rows = [
    {"class_id": 1, "instructor_name": "Sarah Johnson", "class_name": "Yoga Flow", "start_time": "09:00", "duration_mins": 60},
    {"class_id": 2, "instructor_name": "Mike Peters", "class_name": "HIIT", "start_time": "10:30", "duration_mins": 45},
    {"class_id": 3, "instructor_name": "Emma Davis", "class_name": "Spin Class", "start_time": "17:00", "duration_mins": 45},
    {"class_id": 4, "instructor_name": "James Wilson", "class_name": "Pilates", "start_time": "18:30", "duration_mins": 60},
]

# Check if data exists before inserting
with engine.connect() as connection:
    result = connection.execute(text("SELECT COUNT(*) FROM gym_classes")).scalar()
    if result == 0:  # Only insert if table is empty
        for row in rows:
            stmt = insert(gym_classes).values(**row)
            with engine.begin() as connection:
                cursor = connection.execute(stmt)

inspector = inspect(engine)
columns_info = [(col["name"], col["type"]) for col in inspector.get_columns("gym_classes")]
table_description = "Columns:\n" + "\n".join([f"  - {name}: {col_type}" for name, col_type in columns_info])

from smolagents import tool


@tool
def sql_engine(query: str) -> str:
    """
    Allows you to perform SQL queries on the table. Returns a string representation of the result.
    The table is named 'gym_classes'. Its description is as follows:
        Columns:
        - class_id: INTEGER
        - instructor_name: VARCHAR(32)
        - class_name: VARCHAR(32)
        - start_time: VARCHAR(5)
        - duration_mins: INTEGER

    Args:
        query: The query to perform. This should be correct SQL.
    """
    # Create a new engine connection for each query
    engine = create_engine("sqlite:///data/gym_classes.db")
    results = []
    with engine.connect() as con:
        result_set = con.execute(text(query))
        for row in result_set:
            # Convert the row to a dict using the _mapping attribute
            results.append(dict(row._mapping))
    # Return a nicely formatted JSON string
    return json.dumps(results, indent=2)


from smolagents import CodeAgent, HfApiModel


agent = CodeAgent(
    tools=[sql_engine],
    model=HfApiModel( token=os.getenv("HF_TOKEN")),
)

if __name__ == "__main__":
    # This block runs only when the script is executed directly.
    input_query = input("Enter a query: ")
    agent.run(input_query)

# GradioUI(agent).launch()