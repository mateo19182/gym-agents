from fastapi import FastAPI
from api.routes import router as api_router

app = FastAPI(title="Gym Agent API")
app.include_router(api_router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Gym Agent API. Use /query to submit queries, /upload_document to add RAG docs, and /add_class to update gym class data."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 