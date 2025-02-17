import os
import dotenv
dotenv.load_dotenv()

# -------------------------------
# Imports for RAG / Retrieval Agent
# -------------------------------
import os
from tqdm import tqdm
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from transformers import AutoTokenizer

# -------------------------------
# Imports for SQL Agent
# -------------------------------
from sqlalchemy import (
    Column,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    insert,
    inspect,
    text,
)
import json

# -------------------------------
# Imports for Agent and Tools from smolagents
# -------------------------------
from smolagents import CodeAgent, HfApiModel, Tool, tool

# =====================================================
# SQL DATABASE INITIALIZATION & SQL TOOL DEFINITION
# =====================================================

# Create a file-based SQLite engine for gym classes.
engine = create_engine("sqlite:///data/gym_classes.db")
metadata_obj = MetaData()

# Define the gym classes table.
table_name = "gym_classes"
gym_classes = Table(
    table_name,
    metadata_obj,
    Column("class_id", Integer, primary_key=True),
    Column("instructor_name", String(32), primary_key=True),
    Column("class_name", String(32)),
    Column("start_time", String(5)),  # Format: "HH:MM"
    Column("duration_mins", Integer),
)
metadata_obj.create_all(engine)

# Create initial rows.
rows = [
    {
        "class_id": 1,
        "instructor_name": "Sarah Johnson",
        "class_name": "Yoga Flow",
        "start_time": "09:00",
        "duration_mins": 60,
    },
    {
        "class_id": 2,
        "instructor_name": "Mike Peters",
        "class_name": "HIIT",
        "start_time": "10:30",
        "duration_mins": 45,
    },
    {
        "class_id": 3,
        "instructor_name": "Emma Davis",
        "class_name": "Spin Class",
        "start_time": "17:00",
        "duration_mins": 45,
    },
    {
        "class_id": 4,
        "instructor_name": "James Wilson",
        "class_name": "Pilates",
        "start_time": "18:30",
        "duration_mins": 60,
    },
]

# Insert the rows only if the table is empty.
with engine.connect() as connection:
    count = connection.execute(text("SELECT COUNT(*) FROM gym_classes")).scalar()
    if count == 0:
        for row in rows:
            stmt = insert(gym_classes).values(**row)
            with engine.begin() as inner_connection:
                inner_connection.execute(stmt)

# Optionally, you can inspect the table (for documentation purposes)
inspector = inspect(engine)
columns_info = [(col["name"], col["type"]) for col in inspector.get_columns("gym_classes")]
table_description = "Columns:\n" + "\n".join(
    [f"  - {name}: {col_type}" for name, col_type in columns_info]
)

# Define the SQL tool using the @tool decorator.
@tool
def sql_engine(query: str) -> str:
    """
    Executes SQL queries on the gym_classes table.
    The table is named 'gym_classes' and has the following columns:
      - class_id: INTEGER
      - instructor_name: VARCHAR(32)
      - class_name: VARCHAR(32)
      - start_time: VARCHAR(5)
      - duration_mins: INTEGER

    Args:
        query: A valid SQL query to execute.
    Returns:
        A JSON-formatted string of the query results.
    """
    # Create a new engine connection for each query.
    engine_local = create_engine("sqlite:///data/gym_classes.db")
    results = []
    with engine_local.connect() as con:
        result_set = con.execute(text(query))
        for row in result_set:
            results.append(dict(row._mapping))
    return json.dumps(results, indent=2)

# =====================================================
# RAG / DOCUMENT RETRIEVAL TOOL INITIALIZATION
# =====================================================

data_directory = "data"
documents = []
print("Loading documents for RAG agent...")

# Process only PDF and TXT files (skip over the DB file and others).
for file in tqdm(os.listdir(data_directory)):
    file_path = os.path.join(data_directory, file)
    if file.lower().endswith(".pdf"):
        loader = PyPDFLoader(file_path)
        documents.extend(loader.load())
    elif file.lower().endswith(".txt"):
        loader = TextLoader(file_path)
        documents.extend(loader.load())

source_docs = documents

# Initialize the text splitter using the Hugging Face tokenizer.
text_splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
    AutoTokenizer.from_pretrained("thenlper/gte-small"),
    chunk_size=200,
    chunk_overlap=20,
    add_start_index=True,
    strip_whitespace=True,
    separators=["\n\n", "\n", ".", " ", ""],
)

print("Splitting documents...")
docs_processed = []
unique_texts = {}
for doc in tqdm(source_docs):
    new_docs = text_splitter.split_documents([doc])
    for new_doc in new_docs:
        if new_doc.page_content not in unique_texts:
            unique_texts[new_doc.page_content] = True
            docs_processed.append(new_doc)

print("Embedding documents... This may take a while.")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_store = Chroma.from_documents(docs_processed, embeddings, persist_directory="./chroma_db")

# Define the Retriever tool.
class RetrieverTool(Tool):
    name = "retriever"
    description = (
        "Uses semantic search to retrieve parts of documentation that could be most relevant to. It contains documents related to policies and rules for the gym, as well as membership and amenities information."
    )
    inputs = {
        "query": {
            "type": "string",
            "description": (
                "The query to perform. This should be semantically close to your target documents. "
                "Use the affirmative form rather than a question."
            ),
        }
    }
    output_type = "string"

    def __init__(self, vector_store, **kwargs):
        super().__init__(**kwargs)
        self.vector_store = vector_store

    def forward(self, query: str) -> str:
        assert isinstance(query, str), "Your search query must be a string"
        docs = self.vector_store.similarity_search(query, k=3)
        return "\nRetrieved documents:\n" + "".join(
            [f"\n\n===== Document {i} =====\n{doc.page_content}" for i, doc in enumerate(docs)]
        )

# Initialize an instance of the retriever.
retriever_tool = RetrieverTool(vector_store)

# =====================================================
# CREATE THE COMBINED AGENT
# =====================================================

# Initialize the LLM engine using the Hugging Face API model.
model = HfApiModel(token=os.getenv("HF_TOKEN"))

# Create the CodeAgent with both the SQL and Retriever tools.
agent = CodeAgent(
    tools=[retriever_tool, sql_engine],
    model=model,
    max_steps=4,
    verbosity_level=2,
)

if __name__ == "__main__":
    # For quick testing from the command line.
    query_input = input("Enter your query: ")
    print("Agent is processing your query...")
    output = agent.run(query_input)
    print("Final output:")
    print(output) 