from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from agent.agent_es import agent_es
from api.utils.conversation import load_conversation_memory, save_conversation_memory

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    query: str
    conversation_id: str = None

@router.post("/", response_model=dict, status_code=status.HTTP_200_OK)
def chat_agent(request: ChatRequest):
    """
    Chat Agent endpoint that accepts a query and an optional conversation_id.
    When a conversation_id is provided, the conversation history is loaded and saved in a JSON file.
    If no conversation_id is provided, the agent operates statelessly.
    """
    conversation_id = request.conversation_id

    # Build the prompt using conversation memory if available
    if conversation_id:
        conversation_memory = load_conversation_memory(conversation_id)
        history_prompt = ""
        for msg in conversation_memory:
            history_prompt += f"{msg['role']}: {msg['content']}\n"
        # Use different role labels based on the language
        role_prefix = "User"
        prompt = history_prompt + f"{role_prefix}: {request.query}\n"
    else:
        prompt = request.query
    try:
        response = agent_es.run(prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # If conversation memory is used, update the conversation accordingly using language-specific role labels
    if conversation_id:
        conversation_memory = load_conversation_memory(conversation_id)
        conversation_memory.append({"role": "User", "content": request.query})
        conversation_memory.append({"role": "Assistant", "content": response})
        save_conversation_memory(conversation_id, conversation_memory)

    return {"conversation_id": conversation_id, "response": response}