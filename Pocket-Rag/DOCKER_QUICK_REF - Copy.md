# 🐳 Pocket RAG - Quick Docker Reference

## One-Liner Start (After Prerequisites)

### Linux/Mac
```bash
chmod +x start.sh && ./start.sh start
```

### Windows
```bash
start.bat start
```

---

## Prerequisites Checklist

### All Platforms
- [ ] Docker & Docker Compose installed
- [ ] Ollama installed and running
- [ ] Required models pulled:
  ```bash
  ollama pull nomic-embed-text
  ollama pull qwen3:1.7b
  ```

### Linux Only
```bash
# Install Docker
sudo pacman -S docker docker-compose  # Arch Linux
sudo apt-get install docker.io docker-compose  # Ubuntu

# Start Docker
sudo systemctl start docker
sudo usermod -aG docker $USER

# Start Ollama
ollama serve
```

### Windows Only
- [ ] Docker Desktop installed (with WSL2)
- [ ] Ollama installed for Windows
- [ ] Docker Desktop is running (check system tray)

---

## Essential Commands

```bash
# Start all services
./start.sh start          # Linux/Mac
start.bat start           # Windows

# View logs
./start.sh logs backend
./start.sh logs frontend
./start.sh logs qdrant

# Stop services
./start.sh stop           # Linux/Mac
start.bat stop            # Windows

# Check status
./start.sh status         # Linux/Mac
start.bat status          # Windows

# Rebuild after code changes
./start.sh rebuild        # Linux/Mac
start.bat rebuild         # Windows
```

---

## Access Points

Once running, visit:

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend (Streamlit) | http://localhost:8501 | Chat interface |
| Backend (FastAPI) | http://localhost:8000 | API & docs at /docs |
| Qdrant Dashboard | http://localhost:6333/dashboard | Vector DB management |

---

## Troubleshooting

### "Backend not connected"
1. Check if all containers are running:
   ```bash
   docker-compose ps
   ```
2. View backend logs:
   ```bash
   docker-compose logs backend
   ```
3. Ensure Ollama is running on host:
   ```bash
   curl http://localhost:11434
   ```

### "Failed to connect to Ollama"
- Linux: Check that Ollama is running (`ollama serve`)
- Windows: Check that Ollama is running in background
- All: Verify models exist: `ollama list`

### "Qdrant unavailable"
```bash
docker-compose restart qdrant
docker-compose logs qdrant
```

### "Port already in use"
```bash
# Find what's using port 8000 (backend)
lsof -i :8000          # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Change ports in docker-compose.yml if needed
```

---

## File Structure

```
pocket-rag/
├── Dockerfile              # Single containerized app
├── docker-compose.yml      # Orchestrates containers
├── start.sh                # Linux/Mac helper script
├── start.bat               # Windows helper script
├── DOCKER_SETUP.md         # Detailed setup guide
├── DOCKER_QUICK_REF.md     # This file
├── .env.example            # Environment variables template
├── backend/
│   ├── main.py             # FastAPI app
│   ├── services.py         # LLM & Vector DB logic
│   ├── chat_history.py     # Database management
│   ├── requirements.txt    # Python dependencies
│   ├── uploaded_pdfs/      # User-uploaded PDFs (persisted)
│   └── chat_history.db     # Chat data (persisted)
└── frontend/
    ├── app.py              # Streamlit UI
    └── requirements.txt    # Python dependencies
```

---

## Data Persistence

Your data persists across container restarts:

- **Embeddings**: Stored in `qdrant_storage` volume
- **Chat History**: Stored in `backend/chat_history.db`
- **PDFs**: Stored in `backend/uploaded_pdfs/`
- **Ollama Models**: Stay on host machine

To backup:
```bash
cp -r backend/uploaded_pdfs backup/
cp backend/chat_history.db backup/
```

---

## Performance Tips

1. **First run takes longer** (downloading images)
2. **Subsequent runs are instant** (containers already built)
3. **Models persist on host** (Ollama doesn't need to re-download)
4. **Use volumes for data** (automatic persistence)

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| `docker: command not found` | Install Docker and Docker Compose |
| `Cannot connect to Ollama` | Ensure Ollama is running on host |
| `Port 8000 already in use` | Change port in docker-compose.yml |
| `Qdrant won't start` | Check disk space or restart Docker |
| `PDF upload fails` | Check backend logs; ensure ~/uploaded_pdfs exists |
| Models not found | Run `ollama pull nomic-embed-text` and `ollama pull qwen3:1.7b` |

---

## For Your Windows Friend 🪟

1. **Install in order:**
   1. Docker Desktop for Windows
   2. Ollama for Windows
   3. Clone/extract this project
   4. Run: `start.bat start`

2. **To debug:**
   ```bash
   # Check containers
   docker-compose ps
   
   # Check logs
   docker-compose logs backend
   
   # Test Ollama connection
   curl http://localhost:11434
   ```

3. **If still broken:**
   - Restart Docker Desktop
   - Ensure Ollama is running (check system tray)
   - Check that models exist: `ollama list`
   - Review backend logs: `start.bat logs backend`

---

## More Details

For comprehensive documentation, see `DOCKER_SETUP.md`

For architecture diagrams and advanced configuration, see the main `README.md`

---

## Quick Comparison: Before vs After Docker

### Before (Manual Setup)
❌ Platform-specific dependency issues
❌ Python environment conflicts  
❌ Backend connection failures on Windows
❌ Manual service management
❌ "Works on my machine" problems

### After (Docker)
✅ Same environment everywhere (Linux, Mac, Windows)
✅ All dependencies managed by Docker
✅ Single command to start: `docker-compose up -d`
✅ Automatic service orchestration
✅ Guaranteed compatibility
✅ Easy to share with others
✅ Simple to backup/restore data

---

**Happy containerizing! 🚀**
