from smolagents import tool
import json
from sqlalchemy import create_engine, text

@tool
def sql_engine(query: str) -> str:
    """
    Executes SQL queries on the gym_classes table.
    The table has the following columns:
      - class_id: INTEGER
      - instructor_name: VARCHAR(32)
      - class_name: VARCHAR(32)
      - start_time: VARCHAR(5)
      - duration_mins: INTEGER

    Args:
        query: A valid SQL query to execute.
    Returns:
        A JSON-formatted string of the query results.
    """
    engine_local = create_engine("sqlite:///data/gym_classes.db")
    results = []
    with engine_local.connect() as con:
        result_set = con.execute(text(query))
        for row in result_set:
            results.append(dict(row._mapping))
    return json.dumps(results, indent=2) 