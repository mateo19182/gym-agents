from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as api_router

app = FastAPI(
    title="Gym Agent API",
    description="""
    An API that combines RAG (Retrieval Augmented Generation) and SQL capabilities to:
    - Answer questions about gym policies and rules using uploaded documents
    - Manage gym class schedules using a SQL database
    - Process natural language queries about both documents and class schedules
    """,
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Gym Agent API",
        "docs_url": "/docs",
        "endpoints": {
            "Query Agent": "/api/v1/query",
            "Upload Document": "/api/v1/upload_document",
            "Manage Classes": "/api/v1/classes"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True) 