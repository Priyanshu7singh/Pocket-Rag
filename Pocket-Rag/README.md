# Pocket RAG - ChatGPT-like PDF Q&A Application

A minimal, production-ready RAG (Retrieval Augmented Generation) application with persistent memory across sessions.

## 🎯 Features

- **ChatGPT-like Interface** - Clean, modern UI built with Streamlit
- **PDF Document Processing** - Automatic chunking and embedding generation
- **Semantic Search** - Find relevant document sections using vector embeddings
- **Persistent Memory** - Chat history and document data persists across sessions
- **Local LLM** - Uses Ollama for privacy and offline capability
- **Vector Database** - Qdrant for fast semantic search

## 📋 Requirements

- Python 3.10+
- Ollama installed with models: `nomic-embed-text` and `qwen3:1.7b`
- These models are one i used you can can use any model you like but you will need 1 model for embedding and 1 for other tasks. 
- Docker & Docker Compose (for Qdrant)
- 4GB+ RAM, 2GB+ disk space

## 🚀 Quick Start

### 1. Clone/Setup Repository

```bash
cd pocket-rag
```

### 2. Start Qdrant Database (with persistence)

```bash
sudo docker compose --file docker-compose.db.yml up -d
```

This creates persistent volumes:
- `qdrant_storage` - Main vector database
- `qdrant_snapshots` - Backup snapshots

Data will persist across container restarts!

### 3. Install Ollama Models (if not done)

```bash
ollama pull nomic-embed-text
ollama pull qwen3:1.7b
```

### 4. Start Backend

```bash
cd backend
source venv/bin/activate  # or your Python venv
pip install -r requirements.txt
python main.py
```

Runs on: `http://localhost:8000`

### 5. Start Frontend (in new terminal)

```bash
cd frontend
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Opens on: `http://localhost:8501`

## 💾 Memory & Persistence Architecture

### What Persists?

| Component | Storage | Persistence |
|-----------|---------|-------------|
| **Vector Embeddings** | Qdrant (Docker volume) | ✅ Persists across restarts |
| **Chat History** | SQLite (`backend/chat_history.db`) | ✅ Persists across restarts |
| **Ollama Models** | Local disk | ✅ Persists (no need to re-download) |
| **Uploaded PDFs** | `backend/uploaded_pdfs/` | ✅ Persists for re-processing |

### Data Locations

```
pocket-rag/
├── backend/
│   ├── chat_history.db          # 💾 Chat conversations
│   ├── uploaded_pdfs/           # 📄 PDF files you upload
│   └── documents.db             # (optional) document metadata
├── docker-compose.db.yml        # Qdrant config
└── qdrant_storage/ (Docker)     # Vector embeddings (Docker volume)
```

### To Backup Everything

```bash
# Backup SQLite chat history
cp backend/chat_history.db backup/chat_history.db

# Backup uploaded PDFs
cp -r backend/uploaded_pdfs backup/uploaded_pdfs

# Qdrant snapshots (done via Docker volume)
# Stored in Docker volume - managed automatically
```

### To Clear Everything

```bash
# Remove chat history
rm backend/chat_history.db

# Remove uploaded PDFs
rm -rf backend/uploaded_pdfs

# Remove Qdrant data (requires Docker)
docker volume rm pocket-rag_qdrant_storage
docker volume rm pocket-rag_qdrant_snapshots
```

## 🔄 System Architecture

```
Frontend (Streamlit)
    ↓↓
    Upload PDF / Chat Query
    ↓↓
Backend (FastAPI)
    ├─→ PDF Processing (chunking)
    ├─→ Generate Embeddings (Ollama)
    ├─→ Store in Qdrant (vector DB)
    ├─→ Save Chat History (SQLite)
    └─→ Generate Response (Ollama LLM)
    ↓↓
Response + Context
```

## 🔌 API Endpoints

### POST `/upload`
Upload and process a PDF document

**Request:**
```bash
curl -F "file=@document.pdf" http://localhost:8000/upload
```

**Response:**
```json
{
  "status": "success",
  "doc_name": "document.pdf",
  "collection_name": "document",
  "chunks_count": 42
}
```

### POST `/chat`
Query the RAG system

**Request:**
```json
{
  "query": "What is the main topic?",
  "doc_name": "document"
}
```

**Response:**
```json
{
  "status": "success",
  "answer": "The main topic is...",
  "context": "Retrieved document chunks..."
}
```

### GET `/health`
Check system status

**Response:**
```json
{
  "qdrant": "ok",
  "ollama": "ok"
}
```

### GET `/collections`
List all indexed documents

**Response:**
```json
{
  "status": "success",
  "collections": ["document", "research_paper"]
}
```

## 📊 Performance Tips

1. **PDF Size**: Works best with PDFs < 100MB
2. **Chunk Size**: Tuned for 1000 tokens with 200 overlap
3. **Search Results**: Returns top 3 most relevant chunks
4. **Response Time**: ~5-10 seconds per query

## 🐛 Troubleshooting

### Backend won't start
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Check dependencies
pip install -r requirements.txt

# Check port 8000 isn't in use
lsof -i :8000
```

### Ollama connection error
```bash
# Ensure Ollama is running
ollama serve

# Check models are installed
ollama list
```

### Qdrant connection error
```bash
# Ensure Docker container is running
docker ps | grep qdrant

# Restart container
docker compose --file docker-compose.db.yml restart
```

### Chat history not saving
```bash
# Check permissions on backend folder
ls -la backend/
chmod 755 backend/

# SQLite database will auto-create on first chat
```

## 📝 Configuration

Edit these in the respective files:

**Backend** (`backend/main.py`):
- `UPLOAD_DIR` - Where PDFs are stored
- Chunk size, overlap in `services.py`

**Frontend** (`frontend/app.py`):
- `API_URL` - Backend server address
- Styling and layout

**Ollama** (`.env`):
- Model names
- Base URL (default: `http://localhost:11434`)

## 🎓 Perfect for College Projects!

✅ Shows RAG implementation from scratch  
✅ Demonstrates vector embeddings and semantic search  
✅ Real backend + frontend architecture  
✅ Persistent data management  
✅ Production-like code quality  
✅ Shows understanding of LLMs, embeddings, and vector DBs  

## 📚 Technologies Used

- **FastAPI** - High-performance backend
- **Streamlit** - Beautiful frontend
- **LangChain** - Document processing & LLM integration
- **Ollama** - Local LLM & embeddings
- **Qdrant** - Vector database
- **SQLite** - Chat history persistence
- **Docker** - Containerized database

---

**Questions?** Check the logs in terminal for detailed error messages!
