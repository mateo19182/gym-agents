import os
import dotenv
from smolagents import CodeAgent, HfApiModel
from tools.retriever_tool import RetrieverTool
from tools.sql_tool import sql_engine
from db.rag_store import vector_store

dotenv.load_dotenv()

# Initialize the retriever tool with our vector store
retriever_tool = RetrieverTool(vector_store)

# Initialize the model and agent
model = HfApiModel(token=os.getenv("HF_TOKEN"))

agent = CodeAgent(
    tools=[retriever_tool, sql_engine],
    model=model,
    max_steps=4,
    verbosity_level=2,
) 