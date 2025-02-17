import os
import yaml
import dotenv
from smolagents import ToolCallingAgent, OpenAIServerModel
from tools.retriever_tool import RetrieverTool
from tools.sql_tool import sql_engine
from db.rag_store import vector_store
import datetime

dotenv.load_dotenv()

# Load Spanish prompt templates
with open("agent/agent_prompts_es.yaml", "r") as f:
    spanish_prompt_templates = yaml.safe_load(f)

# Get the current date and time
current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Replace the placeholder in the Spanish prompt templates
for key in spanish_prompt_templates:
    spanish_prompt_templates[key] = spanish_prompt_templates[key].replace("{{ current_datetime }}", current_datetime)

# Initialize retriever tool
retriever_tool = RetrieverTool(vector_store)

# Initialize the model and Spanish agent
model = OpenAIServerModel(
    model_id="google/gemini-2.0-flash-001",
    api_base="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

agent_es = ToolCallingAgent(
    tools=[
        retriever_tool,
        sql_engine,
    ],
    model=model,
    max_steps=4,
    verbosity_level=4,
    prompt_templates=spanish_prompt_templates
) 