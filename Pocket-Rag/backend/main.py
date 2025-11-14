from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
from pathlib import Path
from services import (
    load_and_chunk_pdf, 
    create_embeddings,
    store_in_qdrant,
    search_qdrant,
    call_ollama_llm,
    check_health
)
from chat_history import save_chat, get_all_collections, clear_collection_history
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Pocket RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploaded_pdfs")
UPLOAD_DIR.mkdir(exist_ok=True)

class QueryRequest(BaseModel):
    query: str
    doc_name: str = None

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload PDF and auto-process it"""
    try:
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as f:
            f.write(await file.read())
        
        print(f"[LOG] File saved: {file_path}")
        
        # Load and chunk
        chunks = load_and_chunk_pdf(str(file_path))
        print(f"[LOG] Chunks created: {len(chunks)}")
        
        # Create embeddings
        embeddings = create_embeddings(chunks)
        print(f"[LOG] Embeddings object created")
        
        # Store in Qdrant
        collection_name = file.filename.replace(".pdf", "").replace(" ", "_")
        print(f"[LOG] Storing in Qdrant with collection: {collection_name}")
        store_in_qdrant(chunks, embeddings, collection_name)
        print(f"[LOG] Successfully stored in Qdrant")
        
        return {
            "status": "success",
            "doc_name": file.filename,
            "collection_name": collection_name,
            "chunks_count": len(chunks)
        }
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

@app.post("/chat")
async def chat(request: QueryRequest):
    """Query the RAG system"""
    try:
        # Search Qdrant
        context_chunks = search_qdrant(request.query, request.doc_name)
        
        # Call Ollama LLM
        answer = call_ollama_llm(context_chunks, request.query)
        
        # Save to chat history
        save_chat(request.doc_name, request.query, answer, context_chunks)
        
        return {
            "status": "success",
            "answer": answer,
            "context": context_chunks
        }
    except Exception as e:
        print(f"[ERROR] Chat failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

@app.get("/collections")
async def get_collections():
    """Get list of all indexed collections"""
    try:
        collections = get_all_collections()
        return {
            "status": "success",
            "collections": collections
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/health")
async def health():
    """Check if services are running"""
    return check_health()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)