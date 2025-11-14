from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import ResponseHandlingException
import os

# Use environment variables for URLs (Docker-compatible)
# Docker network: qdrant -> http://qdrant:6333
# Host Ollama: http://host.docker.internal:11434 (Docker Desktop) or http://localhost:11434 (native)
QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")

def load_and_chunk_pdf(file_path):
    """Load PDF and split into chunks"""
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(docs)
    return chunks

def create_embeddings(chunks):
    """Create embeddings using Ollama"""
    embedder = OllamaEmbeddings(
        model="nomic-embed-text",
        base_url=OLLAMA_BASE_URL
    )
    # Just return the embedder, will be used in store_in_qdrant
    return embedder

def store_in_qdrant(chunks, embedder, collection_name):
    """Store chunks and embeddings in Qdrant"""
    try:
        # Check if collection already exists, if so delete it
        client = QdrantClient(url=QDRANT_URL)
        collections = client.get_collections()
        collection_names = [c.name for c in collections.collections]
        
        if collection_name in collection_names:
            print(f"[LOG] Collection {collection_name} already exists, recreating...")
            client.delete_collection(collection_name)
        
        vector_store = QdrantVectorStore.from_documents(
            documents=chunks,
            embedding=embedder,
            url=QDRANT_URL,
            collection_name=collection_name,
            path=None
        )
        print(f"[LOG] Stored {len(chunks)} chunks in collection {collection_name}")
        return vector_store
    except Exception as e:
        print(f"[ERROR] Failed to store in Qdrant: {str(e)}")
        raise

def search_qdrant(query, collection_name):
    """Search Qdrant for relevant chunks"""
    embedder = OllamaEmbeddings(
        model="nomic-embed-text",
        base_url=OLLAMA_BASE_URL
    )
    
    vector_store = QdrantVectorStore(
        client=QdrantClient(url=QDRANT_URL),
        collection_name=collection_name,
        embedding=embedder
    )
    
    results = vector_store.similarity_search(query, k=3)
    context = "\n\n".join([doc.page_content for doc in results])
    return context

def call_ollama_llm(context, query):
    """Get answer from Ollama LLM"""
    llm = Ollama(
        model="qwen3:1.7b",
        base_url=OLLAMA_BASE_URL
    )
    
    prompt = f"""Based on the following context, answer the question concisely.

Context:
{context}

Question: {query}

Answer:"""
    
    response = llm.invoke(prompt)
    return response

def check_health():
    """Check if all services are running"""
    health_status = {}
    
    # Check Qdrant
    try:
        client = QdrantClient(url=QDRANT_URL)
        client.get_collections()
        health_status["qdrant"] = "ok"
    except Exception as e:
        health_status["qdrant"] = f"error: {str(e)}"
    
    # Check Ollama
    try:
        llm = Ollama(base_url=OLLAMA_BASE_URL, model="qwen3:1.7b")
        llm.invoke("test")
        health_status["ollama"] = "ok"
    except Exception as e:
        health_status["ollama"] = f"error: {str(e)}"
    
    return health_status