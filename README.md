# RAG PDF Processing System

A complete RAG (Retrieval-Augmented Generation) system for intelligent PDF document processing and question answering.

## ✨ Key Features

### 📄 PDF Processing
- **Text Extraction**: Automatically extracts and intelligently chunks text from PDFs
- **Image Processing**: Extracts images and generates descriptions
- **Table Processing**: Extracts tables and converts them to structured descriptions

### 🔍 Intelligent Retrieval
- **Hybrid Search**: Combines vector search and keyword search for better recall
- **RRF Fusion**: Uses Reciprocal Rank Fusion to merge search results
- **Intelligent Reranking**: Uses Reranker model to optimize retrieval results

### 🚀 Advanced Features
- **Multi-Query Retrieval (RAG Fusion)**: Generates multiple query variations to improve recall
- **Query Decomposition**: Breaks complex questions into sub-questions
- **Coreference Resolution**: Understands context based on conversation history

### 🎯 Answer Generation
- Generates accurate answers based on retrieved documents
- Provides source citations
- Supports multi-turn conversations
- Works with Ollama (FREE local LLM) or OpenAI

## 🏗️ System Architecture

```
┌─────────────┐
│  PDF Files  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────┐
│  Document Processing         │
│  - Text chunking             │
│  - Image extraction          │
│  - Table extraction          │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│  Vectorization               │
│  - Generate embeddings       │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│  Elasticsearch Index         │
│  - Vector storage            │
│  - Full-text indexing        │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│  Query Processing            │
│  - Query rewrite/decompose   │
│  - Coreference resolution    │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│  Hybrid Retrieval            │
│  - Vector search             │
│  - Keyword search            │
│  - RRF fusion                │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│  Reranking                   │
│  - Reranker model            │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│  Answer Generation           │
│  - LLM generates answer      │
│  - Provides source citations │
└─────────────────────────────┘
```

## 📦 Installation

### 1. System Requirements

- Python 3.8+
- Elasticsearch 9.x
- Sufficient memory (8GB+ recommended)

### 2. Install Elasticsearch

Elasticsearch provides powerful vector search capabilities essential for RAG systems.

**Quick Installation Method:**

```bash
curl -fsSL https://elastic.co/start-local | sh
```

For more details, see the [official Elasticsearch local development guide](https://www.elastic.co/docs/deploy-manage/deploy/self-managed/local-development-installation-quickstart).

**Get Elasticsearch Password and API Key:**

After installation, retrieve your credentials:

```bash
cat elastic-start-local/.env | grep ES_LOCAL_PASSWORD
cat elastic-start-local/.env | grep ES_LOCAL_API_KEY
```

**Verify Installation:**

```bash
curl http://localhost:9200
```

You should see cluster information in JSON format.

### 3. Clone This Repository

```bash
git clone https://github.com/jinjingleayi/RagPdfProcessor.git
cd RagPdfProcessor
```

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or use a virtual environment (recommended):

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 5. Install Ollama (FREE Local LLM)

**For macOS:**
```bash
# Download from https://ollama.com/download
# Or use Homebrew:
brew install ollama
```

**For Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**For Windows:**
Download from https://ollama.com/download

**Start Ollama and download a model:**
```bash
ollama serve  # Start in background
ollama pull llama3.2:3b  # Download free AI model (~2GB)
```

### 6. Configure System Settings

Edit `src/config.py` with your Elasticsearch password:

```python
class ElasticConfig:
    url = 'http://localhost:9200'
    username = 'elastic'
    password = 'YOUR_PASSWORD_HERE'  # From elastic-start-local/.env
```

## 🚀 Usage

### Quick Start with Web Interface

```bash
# Make sure Elasticsearch and Ollama are running
# Then start the app:
./run_app.sh
```

Open your browser to: **http://localhost:7860**

### Step-by-Step Workflow

**STEP 1: Create/Select Index**
- Enter an index name (e.g., `my_documents`)
- Click "Create/Select Index"

**STEP 2: Ingest PDF Documents**
- Upload one or more PDF files
- Enable image and table extraction (recommended)
- Click "Start Ingestion"
- Watch the progress as each PDF is processed

**STEP 3: Query System**
- Enter your question
- Click "Search & Answer"
- Get AI-generated answer with source citations

**STEP 4: Settings & Optimization**
- View current settings
- Manage indexes

### Python API Usage

```python
from indexing import create_and_index
from rag_pipeline import RAGPipeline

# Index documents
create_and_index(
    index_name='my_knowledge_base',
    pdf_path_or_directory='data/pdfs/your_document.pdf',
    extract_images=True,
    extract_tables=True
)

# Query system
pipeline = RAGPipeline(
    index_name='my_knowledge_base',
    use_multi_query=False,
    use_query_decomposition=False
)

result = pipeline.simple_query("What is this document about?")
print(result['answer'])
print(f"Sources: {result['num_sources']}")
```

## 📁 Project Structure

```
RagPdfProcessor/
│
├── src/                          # Source code
│   ├── config.py                 # Configuration
│   ├── embedding.py              # Vectorization
│   ├── es_functions.py           # Elasticsearch operations
│   ├── pdf_processor.py          # PDF processing
│   ├── retrieval.py              # Hybrid search + reranking
│   ├── query_processing.py       # Advanced query processing
│   ├── answer_generation.py      # Answer generation
│   ├── indexing.py               # Document indexing
│   ├── rag_pipeline.py           # Main pipeline
│   ├── app_workflow.py           # Web interface (main)
│   ├── app_simple.py             # Simplified interface
│   └── app.py                    # Advanced interface
│
├── data/                         # Data directory
│   ├── pdfs/                     # Place your PDF files here
│   └── images/                   # Extracted images
│
├── logs/                         # Log files
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── QUICKSTART.md                 # Quick start guide
├── PROJECT_SUMMARY.md            # Feature summary
├── run_app.sh                    # Convenience script to run app
└── .gitignore                    # Git ignore rules
```

## ⚙️ Configuration

### API Endpoints

The system is pre-configured with embedding and reranking API endpoints in `src/config.py`:

```python
EMBEDDING_URL = "http://test.2brain.cn:9800/v1/emb"
RERANK_URL = "http://test.2brain.cn:2260/rerank"
```

### Elasticsearch Configuration

Update `src/config.py` with your Elasticsearch credentials:

```python
class ElasticConfig:
    url = 'http://localhost:9200'
    username = 'elastic'
    password = 'YOUR_PASSWORD'  # Get from elastic-start-local/.env
```

### RAG Parameters

Adjust these in `src/config.py`:

```python
CHUNK_SIZE = 1024           # Size of each text chunk in tokens
CHUNK_OVERLAP = 100         # Overlap between chunks
EMBEDDING_DIM = 1024        # Embedding vector dimension
TOP_K_RETRIEVAL = 10        # Documents to retrieve initially
TOP_K_RERANK = 5            # Documents after reranking
```

## 📊 Performance Optimization

1. **Batch Processing**: Process multiple PDFs at once
2. **Adjust Chunk Size**: Modify `CHUNK_SIZE` for your use case
3. **Limit Extraction**: Disable image/table extraction for faster indexing
4. **Tune Retrieval**: Adjust `TOP_K_RETRIEVAL` and `TOP_K_RERANK` parameters

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## 📄 License

MIT License

## 🙏 Acknowledgments

This project uses:
- **Elasticsearch** - Search and vector storage ([Documentation](https://www.elastic.co/docs))
- **LangChain** - Document processing framework
- **PyMuPDF** - PDF parsing
- **Gradio** - Web interface
- **Ollama** - Free local LLM
- **Jieba** - Chinese text segmentation

---

**Version**: 1.0.0
