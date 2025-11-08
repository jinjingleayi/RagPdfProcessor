# RAG PDF Processing System

A complete RAG (Retrieval-Augmented Generation) system for intelligent PDF document processing and question answering.

## ✨ Key Features

### 📄 PDF Processing
- **Text Extraction**: Automatically extracts and intelligently chunks text from PDFs
- **Image Processing**: Extracts images and generates descriptions using vision models
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
│  - Image extraction & desc.  │
│  - Table extraction & desc.  │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│  Vectorization               │
│  - Generate text embeddings  │
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
- Elasticsearch 8.x
- Sufficient memory (8GB+ recommended)

### 2. Install Elasticsearch

**macOS (using Homebrew):**
```bash
brew tap elastic/tap
brew install elastic/tap/elasticsearch-full

# Start Elasticsearch
brew services start elasticsearch

# Verify installation
curl http://localhost:9200
```

**Linux:**
```bash
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-8.11.0-linux-x86_64.tar.gz
tar -xzf elasticsearch-8.11.0-linux-x86_64.tar.gz
cd elasticsearch-8.11.0/
./bin/elasticsearch
```

### 3. Install Python Dependencies

```bash
cd ~/Qishi\ AI/RAG_pdfProcess
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# OpenAI API (for answer generation)
OPENAI_API_KEY=your-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1

# Optional: Elasticsearch authentication
ES_USERNAME=elastic
ES_PASSWORD=your-password
```

### 5. Configure System Settings

Edit `src/config.py` to customize settings:

```python
# Elasticsearch configuration
class ElasticConfig:
    url = 'http://localhost:9200'
    # If authentication required: url = 'http://elastic:password@localhost:9200'

# API URLs (provided by your teacher, can be used directly)
EMBEDDING_URL = "http://test.2brain.cn:9800/v1/emb"
RERANK_URL = "http://test.2brain.cn:2260/rerank"
IMAGE_MODEL_URL = 'http://test.2brain.cn:23333/v1'

# RAG Configuration
CHUNK_SIZE = 1024           # Size of each text chunk in tokens
CHUNK_OVERLAP = 100         # Overlap between chunks
TOP_K_RETRIEVAL = 10        # Number of documents to retrieve
TOP_K_RERANK = 5            # Number of documents after reranking
```

## 🚀 Usage

### Method 1: Web Interface (Recommended)

```bash
cd ~/Qishi\ AI/RAG_pdfProcess/src
python app.py
```

Then open your browser to `http://localhost:7860`

#### Steps:

1. **Index Documents**
   - Go to the "Document Indexing" tab
   - Upload a PDF file
   - Set an index name (e.g., `my_knowledge_base`)
   - Choose whether to extract images and tables
   - Click "Start Indexing"

2. **Initialize System**
   - Go to the "Question & Answer" tab
   - Enter the index name you created
   - Optionally enable advanced features
   - Click "Initialize System"

3. **Ask Questions**
   - Enter your question
   - View the answer and sources

### Method 2: Python API

#### Index Documents

```python
from indexing import create_and_index

# Index a single PDF
create_and_index(
    index_name='my_knowledge_base',
    pdf_path_or_directory='data/pdfs/example.pdf',
    extract_images=True,
    extract_tables=True
)

# Index an entire directory
create_and_index(
    index_name='my_knowledge_base',
    pdf_path_or_directory='data/pdfs/',
    extract_images=True,
    extract_tables=True
)
```

#### Query System

```python
from rag_pipeline import RAGPipeline

# Create pipeline
pipeline = RAGPipeline(
    index_name='my_knowledge_base',
    use_multi_query=False,
    use_query_decomposition=False
)

# Simple query
result = pipeline.simple_query("What is machine learning?")
print(result['answer'])
print(f"Used {result['num_sources']} sources")

# Advanced query (with multi-query and decomposition)
pipeline_advanced = RAGPipeline(
    index_name='my_knowledge_base',
    use_multi_query=True,
    use_query_decomposition=True
)

result = pipeline_advanced.query("What is the difference between deep learning and machine learning?")
print(result['answer'])
```

## 📁 Project Structure

```
RAG_pdfProcess/
│
├── src/                          # Source code
│   ├── config.py                 # Configuration file
│   ├── embedding.py              # Vectorization module
│   ├── es_functions.py           # Elasticsearch operations
│   ├── pdf_processor.py          # PDF processing
│   ├── retrieval.py              # Retrieval module
│   ├── query_processing.py       # Query processing
│   ├── answer_generation.py      # Answer generation
│   ├── indexing.py               # Index management
│   ├── rag_pipeline.py           # Main pipeline
│   └── app.py                    # Web interface
│
├── data/                         # Data directory
│   ├── pdfs/                     # PDF files
│   └── images/                   # Extracted images
│
├── logs/                         # Logs
├── requirements.txt              # Dependencies
└── README.md                     # Documentation
```

## ⚙️ Advanced Configuration

### Adjust Retrieval Parameters

In `src/config.py`:

```python
# Text chunking parameters
CHUNK_SIZE = 1024           # Size of each chunk in tokens
CHUNK_OVERLAP = 100         # Overlap between chunks

# Vector dimensions
EMBEDDING_DIM = 1024        # Embedding vector dimension

# Retrieval parameters
TOP_K_RETRIEVAL = 10        # Initial number of documents to retrieve
TOP_K_RERANK = 5            # Number of documents after reranking
```

### Custom Stop Words

Modify the `stop_words` set in `src/retrieval.py` to customize keyword extraction.

### Adjust Image Filtering

In `src/pdf_processor.py`, modify the image filtering conditions:

```python
# Skip small images (likely icons/logos)
if image_width < page_width / 3 or image_width < 200 or image_height < 100:
    continue
```

## 🔧 Troubleshooting

### Elasticsearch Connection Failed

```bash
# Check if Elasticsearch is running
curl http://localhost:9200

# Restart Elasticsearch (macOS)
brew services restart elasticsearch

# Check Elasticsearch logs
tail -f /usr/local/var/log/elasticsearch.log
```

### Out of Memory

- Reduce `CHUNK_SIZE`
- Reduce `TOP_K_RETRIEVAL`
- Reduce batch size in `embedding.py`
- Disable image extraction for faster processing

### Image Extraction Fails

- Check if `IMAGE_MODEL_URL` is accessible
- Set `extract_images=False` to skip image processing
- Ensure sufficient disk space for image storage

## 📊 Performance Optimization

1. **Batch Indexing**: Use `index_directory` instead of individual files
2. **Adjust Batch Size**: Modify `batch_size` in `embedding.py`
3. **Limit Image Size**: Adjust image filtering in `pdf_processor.py`
4. **Use SSD**: Store Elasticsearch data on SSD for faster retrieval
5. **Increase Heap Size**: Configure Elasticsearch JVM heap size for large datasets

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## 📄 License

MIT License

## 🙏 Acknowledgments

This project uses the following technologies:
- **Elasticsearch** - Search and vector storage
- **LangChain** - Document processing framework
- **PyMuPDF** - PDF parsing
- **Gradio** - Web interface
- **OpenAI** - LLM services
- **Jieba** - Chinese text segmentation

## 📞 Support

For questions and support:
- Create an issue on GitHub
- Check the User Guide in the web interface
- Review the troubleshooting section above

---

**Author**: Qishi AI  
**Date**: November 2025  
**Version**: 1.0.0
