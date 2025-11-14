FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements for both backend and frontend
COPY backend/requirements.txt ./backend_requirements.txt
COPY frontend/requirements.txt ./frontend_requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r backend_requirements.txt && \
    pip install --no-cache-dir -r frontend_requirements.txt

# Copy application code
COPY backend /app/backend
COPY frontend /app/frontend

# Create necessary directories
RUN mkdir -p /app/backend/uploaded_pdfs /app/data

# Expose ports (backend API and Streamlit UI)
EXPOSE 8000 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command runs backend (can be overridden to run frontend)
CMD ["python", "backend/main.py"]
