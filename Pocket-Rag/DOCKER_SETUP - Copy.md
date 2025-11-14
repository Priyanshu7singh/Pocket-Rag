# Pocket RAG - Docker Setup Guide

## 🐳 Docker Deployment Architecture

This setup runs the application in Docker containers while connecting to Ollama on the host machine.

### Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│              HOST MACHINE (Arch Linux)              │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │ Ollama (LLM Server)                         │   │
│  │ Port: 11434                                 │   │
│  └─────────────────────────────────────────────┘   │
│                      ▲                              │
│                      │ (connection via bridge)      │
│                      │                              │
│  ┌──────────────────────────────────────────────┐  │
│  │         Docker Network (bridge)              │  │
│  │                                              │  │
│  │ ┌──────────────────┐  ┌─────────────────┐  │  │
│  │ │  Backend (FastAPI)  │  │ Frontend (Streamlit)│  │
│  │ │  Port: 8000      │  │ Port: 8501      │  │  │
│  │ └────────┬─────────┘  └────────┬────────┘  │  │
│  │          │                     │           │  │
│  │ ┌────────▼──────────────────────▼────────┐ │  │
│  │ │  Qdrant Vector Database                │ │  │
│  │ │  Port: 6333                            │ │  │
│  │ │  Volumes: qdrant_storage, snapshots    │ │  │
│  │ └────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

## 📋 Prerequisites

### For Linux (Arch Linux)
1. **Docker & Docker Compose**
   ```bash
   sudo pacman -S docker docker-compose
   sudo systemctl start docker
   sudo usermod -aG docker $USER
   ```

2. **Ollama** (running on host)
   ```bash
   # Install Ollama
   curl https://ollama.ai/install.sh | sh
   
   # Pull required models
   ollama pull nomic-embed-text
   ollama pull qwen3:1.7b
   
   # Start Ollama (if not already running)
   ollama serve
   ```

### For Windows (Using Docker Desktop)
1. **Docker Desktop for Windows**
   - Download from https://www.docker.com/products/docker-desktop
   - Install and enable WSL2 backend
   - Enable "Expose daemon on tcp://localhost:2375" (optional)

2. **Ollama** (running on Windows host)
   - Download from https://ollama.ai
   - Install and run
   - Pull models:
     ```bash
     ollama pull nomic-embed-text
     ollama pull qwen3:1.7b
     ```

## 🚀 Quick Start

### Option 1: Run Everything at Once (Recommended)

```bash
cd pocket-rag

# Start all services (backend, frontend, and Qdrant)
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

Access the application:
- **Frontend UI**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **Qdrant Dashboard**: http://localhost:6333/dashboard

### Option 2: Run Services Individually

```bash
# Terminal 1: Start Qdrant
docker-compose up -d qdrant

# Terminal 2: Start Backend
docker-compose up -d backend

# Terminal 3: Start Frontend
docker-compose up -d frontend

# View logs
docker-compose logs -f
```

## 🛠️ Common Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f qdrant
```

### Stop Services
```bash
# Stop without removing containers
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove everything (including volumes!)
docker-compose down -v
```

### Rebuild After Code Changes
```bash
docker-compose up -d --build
```

### Access Container Shells
```bash
# Backend shell
docker exec -it pocket-rag-backend bash

# Frontend shell
docker exec -it pocket-rag-frontend bash

# Qdrant shell
docker exec -it pocket-rag-qdrant bash
```

### Check Service Health
```bash
# Check backend health
curl http://localhost:8000/health

# Check Qdrant health
curl http://localhost:6333/health
```

## 🔧 Troubleshooting

### Issue: "Backend not connected" on Frontend
**Causes & Solutions:**
1. Backend container not running
   ```bash
   docker-compose logs backend
   docker-compose restart backend
   ```

2. Ollama not accessible from backend container
   ```bash
   # Check if Ollama is running
   curl http://localhost:11434
   
   # Inside container, test connection
   docker exec pocket-rag-backend curl http://host.docker.internal:11434
   ```

3. Qdrant not running
   ```bash
   docker-compose restart qdrant
   docker-compose logs qdrant
   ```

### Issue: "Failed to install dependencies"
**Solution:** The Dockerfile handles this. If it still fails:
```bash
# Rebuild without cache
docker-compose build --no-cache

# Then restart
docker-compose up -d
```

### Issue: PDF Upload Fails
**Solution:**
1. Check disk space
   ```bash
   docker exec pocket-rag-backend df -h
   ```

2. Check uploaded_pdfs directory permissions
   ```bash
   ls -la backend/uploaded_pdfs/
   ```

3. View backend logs
   ```bash
   docker-compose logs backend
   ```

### Issue: Qdrant Collection Errors
**Solution:** Clear Qdrant volume and restart
```bash
# Stop and remove data
docker-compose down -v

# Restart
docker-compose up -d
```

### Issue: On Windows - "docker-desktop" network resolution fails
**Solution:** 
- Docker Desktop automatically provides `host.docker.internal`
- If not working, update docker-compose.yml extra_hosts section

### Issue: On Linux - "host.docker.internal" not found
**Solution:**
In docker-compose.yml, `extra_hosts` automatically converts `host.docker.internal:host-gateway`
- This works on Docker 20.10+
- For older Docker versions, use the host IP address instead:
  ```yaml
  extra_hosts:
    - "host.docker.internal:172.17.0.1"  # Default docker0 bridge IP
  ```

## 📊 Data Persistence

All important data is persisted:

| Component | Storage | Persistence |
|-----------|---------|-------------|
| Vector Embeddings | Qdrant volume | ✅ Persists across restarts |
| Chat History | SQLite file | ✅ Persists across restarts |
| Uploaded PDFs | Host directory | ✅ Persists across restarts |
| Ollama Models | Host disk | ✅ Models stay on host |

**Backup your data:**
```bash
# Backup chat history and PDFs
cp -r backend/uploaded_pdfs backup/
cp backend/chat_history.db backup/

# Qdrant data is in Docker volumes
# List volumes
docker volume ls | grep qdrant

# Inspect volume location
docker volume inspect pocket-rag_qdrant_storage
```

## 🐧 Linux-Specific Notes (Arch Linux)

### Running Ollama on Host
```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Create systemd service (optional)
sudo tee /etc/systemd/system/ollama.service > /dev/null <<EOF
[Unit]
Description=Ollama Service
After=network-online.target

[Service]
ExecStart=/usr/local/bin/ollama serve
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable ollama
sudo systemctl start ollama

# Check if running
systemctl status ollama
curl http://localhost:11434
```

### Docker User Permissions
```bash
# Add your user to docker group
sudo usermod -aG docker $USER

# Apply group membership without logout
newgrp docker

# Verify
docker ps
```

## 🪟 Windows-Specific Notes

### Using Docker Desktop with WSL2
1. Docker Desktop must be running
2. Ollama must be running on Windows
3. Docker Desktop automatically provides network bridge

### Testing Container Connectivity to Ollama
```bash
# Inside backend container
docker exec pocket-rag-backend curl http://host.docker.internal:11434
```

### If Host Connection Fails
1. Check Windows Firewall allows Docker Desktop
2. Ensure Ollama is listening on all interfaces
3. Try explicitly using IP address instead of `host.docker.internal`

## 🔐 Environment Variables

Configuration through environment variables (see docker-compose.yml):

```yaml
environment:
  OLLAMA_BASE_URL: http://host.docker.internal:11434
  QDRANT_URL: http://qdrant:6333
  QDRANT_API_KEY: pocket-rag-secret
  PYTHONUNBUFFERED: 1
```

To modify:
1. Edit `docker-compose.yml`
2. Rebuild: `docker-compose up -d --build`

## 📝 File Structure After Docker Setup

```
pocket-rag/
├── Dockerfile                    # Single image for app
├── docker-compose.yml            # Multi-container orchestration
├── backend/
│   ├── main.py
│   ├── services.py              # Updated for env vars
│   ├── chat_history.py
│   ├── requirements.txt
│   ├── uploaded_pdfs/           # Persisted volume
│   └── chat_history.db          # Persisted file
├── frontend/
│   ├── app.py
│   └── requirements.txt
└── DOCKER_SETUP.md              # This file
```

## 🎯 Next Steps

1. ✅ Ensure Ollama is running with required models
2. ✅ Build and start all containers: `docker-compose up -d`
3. ✅ Verify all services are healthy: `docker-compose ps`
4. ✅ Access frontend: http://localhost:8501
5. ✅ Upload a PDF and test chat functionality
6. ✅ Check backend logs if any issues: `docker-compose logs backend`

## 💡 Tips for Your Friend (Windows User)

1. **Install in this order:**
   - Docker Desktop for Windows
   - Ollama for Windows
   - Clone your project
   - Run `docker-compose up -d`

2. **Common Mistakes:**
   - ❌ Not running Docker Desktop before docker-compose commands
   - ❌ Not having Ollama running on Windows
   - ❌ Not having models pulled (run `ollama pull nomic-embed-text` and `ollama pull qwen3:1.7b`)
   - ✅ Do start Ollama first, then Docker containers

3. **Quick Diagnosis:**
   ```bash
   # Check all running containers
   docker-compose ps
   
   # If backend shows "unhealthy", check:
   docker-compose logs backend
   
   # If Qdrant won't start, ensure ports 6333 isn't in use
   netstat -ano | findstr :6333
   ```

## 🚀 Performance Notes

- **First run** will take longer (downloading images, pulling models)
- **Subsequent runs** will be much faster (containers reuse images)
- **Models** persist on the host, so they don't need re-downloading
- **Volumes** persist data across container restarts

## 📞 Support Resources

- [Docker Compose Docs](https://docs.docker.com/compose/)
- [Ollama Docs](https://github.com/ollama/ollama)
- [Qdrant Docs](https://qdrant.tech/documentation/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Streamlit Docs](https://docs.streamlit.io/)
