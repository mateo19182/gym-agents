import os
from dotenv import load_dotenv

# Load environment variables before any other imports
load_dotenv()

from fastapi import FastAPI
from api.routes import router as api_router

app = FastAPI(title="Gym Agent API")
app.include_router(api_router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Gym Agent API. Use /docs to see available endpoints."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 