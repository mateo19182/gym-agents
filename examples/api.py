from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from combined_agent import agent  # import the combined agent with both tools

app = FastAPI()

class QueryRequest(BaseModel):
    query: str  

@app.post("/query")
async def query_agent(request: QueryRequest):
    """
    Receives a natural language query in JSON, then runs the combined agent (which will choose the right tool),
    and returns the resulting data.
    """
    try:
        result = agent.run(request.query)
        return {"result": result}
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))

@app.get("/")
async def root():
    return {"message": "Welcome to the Agent API. Use /query to submit your queries."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
