import os
import yaml
import dotenv
from smolagents import ToolCallingAgent, HfApiModel
from tools.retriever_tool import RetrieverTool
from tools.sql_tool import sql_engine
from db.rag_store import vector_store
from smolagents.default_tools import PythonInterpreterTool

dotenv.load_dotenv()

# Load prompt templates
with open("agent/agent_prompts.yaml", "r") as f:
    prompt_templates = yaml.safe_load(f)

# Initialize the retriever tool with our vector store
retriever_tool = RetrieverTool(vector_store)

# Initialize the model and agent
model = HfApiModel(token=os.getenv("HF_TOKEN"))

# ToolCalling seems to work much better than CodeAgent
agent = ToolCallingAgent(
    tools=[
        retriever_tool, 
        sql_engine,
    ],
    model=model,
    max_steps=4,
    verbosity_level=2,
    prompt_templates=prompt_templates
) 