import os
import json

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
