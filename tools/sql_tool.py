from smolagents import tool
import json
from sqlalchemy import create_engine, text

@tool
def sql_engine(query: str) -> str:
    """
    Ejecuta consultas SQL en la tabla gym_clases.
    La tabla tiene las siguientes columnas:
      - clase_id: INTEGER
      - nombre_monitor: VARCHAR(32)
      - nombre_clase: VARCHAR(32)
      - hora_comienzo: VARCHAR(5)
      - duracion_minutos: INTEGER

    Args:
        query: Una consulta SQL válida que se ejecutará.
    Returns:
        Un string en formato JSON con los resultados de la consulta.
    """
    engine_local = create_engine("sqlite:///data/gym_clases.db")
    results = []
    with engine_local.connect() as con:
        result_set = con.execute(text(query))
        for row in result_set:
            results.append(dict(row._mapping))
    return json.dumps(results, indent=2) 