import os
import json
import uuid
from fastapi import APIRouter, HTTPException, UploadFile, File, status
from pydantic import BaseModel, Field
from sqlalchemy import insert, text
from typing import List
from smolagents import CodeAgent, HfApiModel

from agent.agent import agent
from db import engine, gym_classes, add_document

router = APIRouter()

# Directory to store conversation memory files.
CONVERSATION_DIR = "data/conversations"
os.makedirs(CONVERSATION_DIR, exist_ok=True)

def memory_file_path(conversation_id: str) -> str:
    """Returns the file path for the conversation memory JSON file."""
    return os.path.join(CONVERSATION_DIR, f"{conversation_id}.json")

def load_conversation_memory(conversation_id: str) -> list:
    """
    Loads the conversation memory from a JSON file.
    Returns a list of dicts with keys "role" and "content". If the file does not exist,
    returns an empty history list.
    """
    path = memory_file_path(conversation_id)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []  # No history yet

def save_conversation_memory(conversation_id: str, memory: list) -> None:
    """Stores the conversation memory (a list of messages) into a JSON file."""
    path = memory_file_path(conversation_id)
    with open(path, "w") as f:
        json.dump(memory, f, indent=2)

class QueryRequest(BaseModel):
    query: str = Field(..., description="The natural language query to process")

class GymClass(BaseModel):
    class_id: int = Field(..., description="Unique identifier for the class")
    instructor_name: str = Field(..., description="Name of the instructor", max_length=32)
    class_name: str = Field(..., description="Name of the class", max_length=32)
    start_time: str = Field(..., description="Start time in HH:MM format", pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    duration_mins: int = Field(..., description="Duration in minutes", gt=0, le=180)

    class Config:
        json_schema_extra = {
            "example": {
                "class_id": 5,
                "instructor_name": "John Smith",
                "class_name": "CrossFit",
                "start_time": "14:30",
                "duration_mins": 60
            }
        }

class ChatRequest(BaseModel):
    query: str
    conversation_id: str = None  # Optional: if provided, we persist conversation history

@router.post("/upload_document", status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document (PDF or TXT) to be processed by the RAG system.
    The document will be saved to the data directory and added to the vector store.
    """
    allowed_extensions = {".pdf", ".txt"}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    try:
        # Save file to data directory
        file_path = os.path.join("data", file.filename)
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Process the document
        num_chunks = add_document(file_path)
        return {
            "message": f"Document processed successfully",
            "filename": file.filename,
            "chunks_added": num_chunks
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing document: {str(e)}"
        )

@router.post("/classes", status_code=status.HTTP_201_CREATED)
async def add_gym_class(gym_class: GymClass):
    """
    Add a new gym class to the database.
    """
    try:
        with engine.connect() as connection:
            stmt = insert(gym_classes).values(**gym_class.dict())
            with connection.begin() as transaction:
                transaction.execute(stmt)
        return {
            "message": "Gym class added successfully",
            "class": gym_class.dict()
        }
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error)
        )

@router.get("/classes", response_model=dict)
async def get_classes():
    """
    Retrieve all gym classes from the database.
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT * FROM gym_classes ORDER BY start_time"))
            classes = [dict(row._mapping) for row in result]
        return {"classes": classes}
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error)
        )

@router.post("/chat", response_model=dict, status_code=status.HTTP_200_OK)
def chat_agent(request: ChatRequest):
    """
    Chat Agent endpoint that accepts a query and an optional conversation_id.
    When a conversation_id is provided, the conversation history is loaded and saved in a JSON file.
    If no conversation_id is provided, the agent operates statelessly.
    """
    conversation_id = request.conversation_id

    # Build the prompt using conversation memory if a conversation_id is provided.
    if conversation_id:
        conversation_memory = load_conversation_memory(conversation_id)
        # Build history text (e.g., "User: ...\nAssistant: ...\n")
        history_prompt = ""
        for msg in conversation_memory:
            history_prompt += f"{msg['role']}: {msg['content']}\n"
        prompt = history_prompt + f"User: {request.query}\n"
    else:
        prompt = request.query

    try:
        # Use the shared agent (as defined in agent/agent.py) for running the query.
        response = agent.run(prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # If conversation memory is used, update the saved conversation.
    if conversation_id:
        conversation_memory = load_conversation_memory(conversation_id)
        conversation_memory.append({"role": "User", "content": request.query})
        conversation_memory.append({"role": "Assistant", "content": response})
        save_conversation_memory(conversation_id, conversation_memory)

    return {"conversation_id": conversation_id, "response": response}