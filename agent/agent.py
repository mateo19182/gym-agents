import os
import yaml
import dotenv
from smolagents import ToolCallingAgent, OpenAIServerModel, HfApiModel
from tools.retriever_tool import RetrieverTool
from tools.sql_tool import sql_engine
from db.rag_store import vector_store
from smolagents.default_tools import PythonInterpreterTool
import datetime

dotenv.load_dotenv()

# Load prompt templates
with open("agent/agent_prompts.yaml", "r") as f:
    prompt_templates = yaml.safe_load(f)

# Get the current date and time
current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Replace the placeholder in the prompt templates
for key in prompt_templates:
    prompt_templates[key] = prompt_templates[key].replace("{{ current_datetime }}", current_datetime)

# print(prompt_templates)

# Initialize the retriever tool with our vector store
retriever_tool = RetrieverTool(vector_store)

# Initialize the model and agent
# model = HfApiModel(token=os.getenv("HF_TOKEN"))
model = OpenAIServerModel(
    model_id="google/gemini-2.0-flash-001",
    # api_base=os.getenv("OPENROUTER_BASE_URL"),
    api_base="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# ToolCalling seems to work much better than CodeAgent
agent = ToolCallingAgent(
    tools=[
        retriever_tool, 
        sql_engine,
    ],
    model=model,
    max_steps=4,
    verbosity_level=4,
    prompt_templates=prompt_templates
) 