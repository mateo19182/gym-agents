from langchain_chroma import Chroma
from tools.retriever_tool import RetrieverTool
from db.rag_store import get_vector_store
import os
import dotenv

dotenv.load_dotenv()

def main():
    print("Starting test retriever...")
    
    # Check if environment variable is set
    hf_token = os.getenv("HF_TOKEN")
    print(f"HF_TOKEN present: {bool(hf_token)}")
    
    # Get existing vector store
    print("\nLoading existing vector store...")
    vector_store = get_vector_store()
    collection = vector_store._collection
    print(f"Vector store collection size: {collection.count()}")
    
    # Initialize the RetrieverTool
    print("\nInitializing RetrieverTool...")
    retriever_tool = RetrieverTool(vector_store=vector_store)
    
    # Test queries
    test_queries = [
        "gym hours",
        "membership price",
        "swimming pool"
    ]
    
    # Run tests
    print("\nRunning test queries...")
    for query in test_queries:
        print(f"\nTesting query: {query}")
        result = retriever_tool.forward(query)
        print(f"Result type: {type(result)}")
        print(f"Result content: {result}")

if __name__ == "__main__":
    main() 