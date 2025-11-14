import streamlit as st
import requests
import os
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Use backend service name for Docker network communication
# When running in Docker, use the service name from docker-compose
# When running locally, use localhost
API_URL = os.getenv("API_URL", "http://backend:8000")

# Page config
st.set_page_config(
    page_title="Pocket RAG",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for ChatGPT-like appearance
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
    }
    
    .main {
        max-width: 900px;
        margin: 0 auto;
    }
    
    .stChatMessage {
        background-color: transparent;
        padding: 12px 0;
    }
    
    [data-testid="stChatMessageContent"] {
        font-size: 15px;
        line-height: 1.5;
    }
    
    .user-message {
        margin-left: auto;
        width: 80%;
        text-align: right;
    }
    
    .assistant-message {
        margin-right: auto;
        width: 80%;
    }
    
    .stButton > button {
        width: 100%;
        background-color: #10a37f;
        color: white;
        border-radius: 4px;
        height: 40px;
        font-size: 14px;
    }
    
    .stButton > button:hover {
        background-color: #0e8262;
    }
    
    .sidebar-content {
        padding: 20px;
    }
    
    .document-list {
        background-color: #f7f7f7;
        padding: 12px;
        border-radius: 6px;
        margin: 10px 0;
    }
    
    .collection-item {
        padding: 8px;
        margin: 5px 0;
        background-color: white;
        border-left: 3px solid #10a37f;
        border-radius: 2px;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_collection" not in st.session_state:
    st.session_state.current_collection = None

if "available_collections" not in st.session_state:
    st.session_state.available_collections = []

if "show_context" not in st.session_state:
    st.session_state.show_context = False

if "last_context" not in st.session_state:
    st.session_state.last_context = ""

# Helper functions
def get_available_collections():
    """Fetch list of available document collections"""
    try:
        # For now, we'll use a simple approach - this would need a backend endpoint
        # to list collections properly. For MVP, we'll keep track in session state
        pass
    except:
        pass

def upload_pdf(file):
    """Upload and process PDF"""
    files = {"file": (file.name, file.getbuffer(), "application/pdf")}
    try:
        response = requests.post(f"{API_URL}/upload", files=files, timeout=120)
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                return result
        return None
    except Exception as e:
        st.error(f"Upload failed: {str(e)}")
        return None

def send_message(query, collection_name):
    """Send message to backend and get response"""
    try:
        response = requests.post(
            f"{API_URL}/chat",
            json={
                "query": query,
                "doc_name": collection_name
            },
            timeout=120
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

# HEADER
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("# 💬 Pocket RAG")

# Health indicator in columns
health_col1, health_col2, health_col3 = st.columns(3)
try:
    response = requests.get(f"{API_URL}/health", timeout=5)
    if response.status_code == 200:
        health_data = response.json()
        with health_col1:
            st.markdown("**Backend:** ✅ Online")
        with health_col2:
            st.markdown(f"**Qdrant:** {'✅' if health_data.get('qdrant') == 'ok' else '❌'}")
        with health_col3:
            st.markdown(f"**Ollama:** {'✅' if health_data.get('ollama') == 'ok' else '❌'}")
    else:
        st.markdown("**Status:** ❌ Backend not connected")
except Exception as e:
    st.markdown(f"**Status:** ❌ Backend not connected ({str(e)})")

st.divider()

# MAIN LAYOUT
if st.session_state.current_collection is None:
    # Welcome/Upload state
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📚 Upload a PDF")
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf", key="pdf_uploader")
        
        if uploaded_file is not None:
            if st.button("📤 Upload & Process", use_container_width=True):
                with st.spinner("⏳ Processing PDF... This may take a minute"):
                    result = upload_pdf(uploaded_file)
                    
                    if result:
                        st.session_state.current_collection = result['collection_name']
                        st.success(f"✅ Successfully uploaded: **{result['doc_name']}**")
                        st.info(f"📊 Processed into {result['chunks_count']} chunks")
                        st.rerun()
                    else:
                        st.error("Failed to upload PDF. Check backend logs.")
    
    with col2:
        st.subheader("📖 How it works")
        st.markdown("""
        1. **Upload** a PDF document
        2. **Wait** for processing (chunking & embedding)
        3. **Ask** questions about your document
        4. **Get** AI-generated answers based on your document
        
        Uses:
        - 🤖 Qwen 2.5 (LLM)
        - 🔍 Nomic Embeddings (Vector search)
        - 💾 Qdrant (Vector database)
        """)

else:
    # Chat interface
    st.markdown(f"### 📄 Currently viewing: `{st.session_state.current_collection}`")
    
    col1, col2 = st.columns([5, 1])
    with col2:
        if st.button("🔄 New Chat", use_container_width=True):
            st.session_state.current_collection = None
            st.session_state.messages = []
            st.rerun()
    
    st.divider()
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        if len(st.session_state.messages) == 0:
            st.markdown("""
            <div style='text-align: center; color: #999; padding: 40px;'>
                <h3>Start a conversation</h3>
                <p>Ask questions about your PDF document. I'll search for relevant sections and provide answers.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            for message in st.session_state.messages:
                with st.chat_message(message["role"], avatar="🧑" if message["role"] == "user" else "🤖"):
                    st.markdown(message["content"])
                    
                    if message["role"] == "assistant" and "context" in message:
                        with st.expander("📄 Show source"):
                            st.markdown(message["context"])
    
    # Input area
    st.divider()
    
    col1, col2 = st.columns([20, 1])
    
    with col1:
        user_input = st.chat_input(
            "Ask me anything about the document...",
            key="chat_input"
        )
    
    with col2:
        st.write("")  # Spacing
    
    # Process message
    if user_input:
        # Add user message to history
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })
        
        # Display user message
        with st.chat_message("user", avatar="🧑"):
            st.markdown(user_input)
        
        # Get response from backend
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("🔍 Searching and thinking..."):
                result = send_message(user_input, st.session_state.current_collection)
                
                if result and result.get("status") == "success":
                    answer = result.get("answer", "No response")
                    context = result.get("context", "")
                    
                    # Display answer
                    st.markdown(answer)
                    
                    # Store in session with context
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "context": context
                    })
                    
                    # Show context option
                    with st.expander("📄 Show source"):
                        st.markdown(context)
                else:
                    st.error("Failed to get response. Check backend connection.")