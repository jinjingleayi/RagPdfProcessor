# Quick Start Guide

Get started with the RAG PDF Processing System in minutes!

## Prerequisites

Before starting, ensure you have:
- ✅ Python 3.8 or higher installed
- ✅ Git installed

## Installation Steps

### 1. Install Elasticsearch

Elasticsearch provides powerful vector search capabilities for RAG systems.

```bash
# Quick installation (local development)
curl -fsSL https://elastic.co/start-local | sh
```

For more details, see the [official Elasticsearch local development guide](https://www.elastic.co/docs/deploy-manage/deploy/self-managed/local-development-installation-quickstart).

**Verify Elasticsearch is running:**
```bash
curl http://localhost:9200
```

**Get your credentials:**
```bash
cat elastic-start-local/.env | grep ES_LOCAL_PASSWORD
cat elastic-start-local/.env | grep ES_LOCAL_API_KEY
```

### 2. Install Ollama (FREE Local LLM)

**macOS:**
```bash
brew install ollama
# Or download from: https://ollama.com/download
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Start Ollama and download model:**
```bash
ollama serve &  # Start service
ollama pull llama3.2:3b  # Download model (~2GB)
```

### 3. Clone and Setup Project

```bash
# Clone repository
git clone https://github.com/jinjingleayi/RagPdfProcessor.git
cd RagPdfProcessor

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Elasticsearch Password

Edit `src/config.py` and update the password:

```python
class ElasticConfig:
    url = 'http://localhost:9200'
    username = 'elastic'
    password = 'YOUR_PASSWORD_HERE'  # From elastic-start-local/.env
```

## 🚀 Run the Application

```bash
./run_app.sh
```

Or manually:

```bash
source venv/bin/activate
cd src
python app_workflow.py
```

Then open your browser to: **http://localhost:7860**

## 📝 Quick Test

### Option 1: Use Test PDFs (Fastest)

1. **STEP 1**: Enter index name → `my_documents` → Click "Create/Select Index"
2. **STEP 2**: Click "📂 Ingest Test PDFs" button
3. **STEP 3**: Ask a question → "What is in these documents?"
4. **Get Answer!** ✅

### Option 2: Use Your Own PDFs

1. **STEP 1**: Create index
2. **STEP 2**: Upload your PDF files (multiple allowed)
3. **STEP 3**: Ask questions about your documents

## 💡 Tips for Best Results

- ✅ Enable image and table extraction for comprehensive coverage
- ✅ Ask specific, clear questions
- ✅ Check source documents to verify answers
- ✅ Use higher retrieval counts for complex queries

## ⚙️ Configuration Options

Edit `src/config.py` to customize:

```python
# Text chunking
CHUNK_SIZE = 1024
CHUNK_OVERLAP = 100

# Retrieval
TOP_K_RETRIEVAL = 10
TOP_K_RERANK = 5

# API endpoints (pre-configured)
EMBEDDING_URL = "http://test.2brain.cn:9800/v1/emb"
RERANK_URL = "http://test.2brain.cn:2260/rerank"
```

## 🔧 Common Issues

**Elasticsearch not accessible:**
```bash
# Check if running
curl http://localhost:9200

# Restart if needed
docker restart $(docker ps -q)
```

**Ollama not responding:**
```bash
# Check if Ollama is running
ollama list

# Start if needed
ollama serve
```

**Port 7860 already in use:**

Edit `src/app_workflow.py`, change the port:
```python
demo.launch(share=False, server_name="0.0.0.0", server_port=7861)
```

## 📚 Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for complete feature list
- Explore the code in `src/` directory
- Try the advanced features (multi-query, decomposition)

---

Happy querying! 🚀
