from fastapi import APIRouter, HTTPException, UploadFile, File, status
import os
from db import add_document

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document (PDF or TXT) to be processed by the RAG system.
    The document will be saved to the data directory and added to the vector store.
    """
    allowed_extensions = {".pdf", ".txt"}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    try:
        file_path = os.path.join("data", file.filename)
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        num_chunks = add_document(file_path)
        return {
            "message": "Document processed successfully",
            "filename": file.filename,
            "chunks_added": num_chunks
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing document: {str(e)}"
        )
