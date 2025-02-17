import os
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings

# Initialize paths and create directories
data_directory = "data"
chroma_directory = "chroma_db"
os.makedirs(data_directory, exist_ok=True)
os.makedirs(chroma_directory, exist_ok=True)

# Initialize text splitter with simpler configuration
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", ".", " ", ""],
)

def load_documents():
    """Load all PDF and TXT documents from the data directory."""
    documents = []
    for file in os.listdir(data_directory):
        file_path = os.path.join(data_directory, file)
        if file.lower().endswith(".pdf"):
            loader = PyPDFLoader(file_path)
            documents.extend(loader.load())
        elif file.lower().endswith(".txt"):
            loader = TextLoader(file_path)
            documents.extend(loader.load())
    return documents

def process_documents(documents):
    """Split documents and remove duplicates."""
    docs_processed = []
    unique_texts = {}
    for doc in documents:
        new_docs = text_splitter.split_documents([doc])
        for new_doc in new_docs:
            if new_doc.page_content not in unique_texts:
                unique_texts[new_doc.page_content] = True
                docs_processed.append(new_doc)
    return docs_processed

def get_vector_store():
    """Get or initialize the vector store."""
    embeddings = HuggingFaceInferenceAPIEmbeddings(
        api_key=os.getenv("HF_TOKEN"),
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    # First try to load existing store
    if os.path.exists(chroma_directory):
        return Chroma(
            persist_directory=chroma_directory,
            embedding_function=embeddings
        )
    
    # Initialize new store if it doesn't exist
    documents = load_documents()
    processed_docs = process_documents(documents)
    return Chroma.from_documents(
        processed_docs, 
        embeddings, 
        persist_directory=chroma_directory
    )

def add_document(file_path: str) -> int:
    """
    Add a new document to the vector store.
    Returns the number of chunks added.
    """
    # Load and process the new document
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext == ".txt":
        loader = TextLoader(file_path)
    else:
        raise ValueError("Unsupported file type")
        
    new_docs = loader.load()
    processed_chunks = text_splitter.split_documents(new_docs)
    
    # Add to existing vector store
    embeddings = HuggingFaceInferenceAPIEmbeddings(
        api_key=os.getenv("HF_TOKEN"),
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vector_store = Chroma(
        persist_directory=chroma_directory,
        embedding_function=embeddings
    )
    vector_store.add_documents(processed_chunks)
    
    return len(processed_chunks)

# Initialize the vector store on module import
vector_store = get_vector_store()