from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from agent.agent import agent
from api.utils.conversation import load_conversation_memory, save_conversation_memory
import os

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    query: str
    conversation_id: str = None
    api_key: str = Field(..., description="API key for authentication")

@router.post("/", response_model=dict, status_code=status.HTTP_200_OK)
def chat_agent(request: ChatRequest):
    """
    Chat Agent endpoint that accepts a query and an optional conversation_id.
    Requires API key authentication.
    """
    # Check API key
    if request.api_key != os.getenv("API_KEY"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )

    conversation_id = request.conversation_id

    if conversation_id:
        conversation_memory = load_conversation_memory(conversation_id)
        history_prompt = ""
        for msg in conversation_memory:
            history_prompt += f"{msg['role']}: {msg['content']}\n"
        prompt = history_prompt + f"User: {request.query}\n"
    else:
        prompt = request.query

    try:
        response = agent.run(prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if conversation_id:
        conversation_memory = load_conversation_memory(conversation_id)
        conversation_memory.append({"role": "User", "content": request.query})
        conversation_memory.append({"role": "Assistant", "content": response})
        save_conversation_memory(conversation_id, conversation_memory)

    return {"conversation_id": conversation_id, "response": response}
