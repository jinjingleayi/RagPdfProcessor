# Quick Start Guide

Get started with the RAG PDF Processing System in minutes!

## Prerequisites Check

Before starting, ensure you have:
- ✅ Python 3.8 or higher installed
- ✅ Elasticsearch 8.x running at `http://localhost:9200`

### Check Elasticsearch

```bash
curl http://localhost:9200
```

You should see a JSON response with cluster information.

## Installation Steps

### 1. Install Dependencies

```bash
cd ~/Qishi\ AI/RAG_pdfProcess
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file or edit `src/config.py` with your OpenAI API key:

```bash
# Create .env file
echo "OPENAI_API_KEY=your-api-key-here" > .env
echo "OPENAI_BASE_URL=https://api.openai.com/v1" >> .env
```

### 3. Test Elasticsearch Connection

```bash
cd src
python -c "from config import get_es; es = get_es(); print('✅ Elasticsearch connected!')"
```

## Quick Test

### Option 1: Use the Web Interface (Easiest)

```bash
cd src
python app.py
```

Then:
1. Open `http://localhost:7860` in your browser
2. Upload a PDF in the "Document Indexing" tab
3. Go to "Question & Answer" tab
4. Initialize the system
5. Ask questions!

### Option 2: Use Python Code

```python
cd src
python
```

Then run:

```python
# Import modules
from indexing import create_and_index
from rag_pipeline import RAGPipeline

# Index a PDF (replace with your PDF path)
create_and_index(
    index_name='test_index',
    pdf_path_or_directory='../data/pdfs/your_document.pdf',
    extract_images=False,  # Set to True if you want image extraction
    extract_tables=False    # Set to True if you want table extraction
)

# Create pipeline
pipeline = RAGPipeline(index_name='test_index')

# Ask a question
result = pipeline.simple_query("What is this document about?")
print(result['answer'])
```

## Common Issues

### Issue: Elasticsearch not running

**Solution:**
```bash
# macOS
brew services start elasticsearch

# Linux - if installed via tar.gz
cd elasticsearch-8.11.0/
./bin/elasticsearch
```

### Issue: Port 7860 already in use

**Solution:**
Edit `src/app.py` and change the port:
```python
demo.launch(share=False, server_name="0.0.0.0", server_port=7861)  # Change 7860 to 7861
```

### Issue: Module not found

**Solution:**
```bash
pip install -r requirements.txt --upgrade
```

### Issue: Out of memory during indexing

**Solution:**
- Start with image/table extraction disabled
- Process smaller PDFs first
- Reduce batch size in `src/embedding.py`

## Next Steps

1. **Read the full documentation**: See `README.md`
2. **Explore advanced features**: Try multi-query retrieval and query decomposition
3. **Optimize performance**: Adjust parameters in `src/config.py`
4. **Add more documents**: Index multiple PDFs into the same index

## Example Workflow

```bash
# 1. Start Elasticsearch (if not running)
brew services start elasticsearch

# 2. Navigate to project
cd ~/Qishi\ AI/RAG_pdfProcess

# 3. Install dependencies (first time only)
pip install -r requirements.txt

# 4. Place your PDF files in data/pdfs/
cp ~/Documents/my_document.pdf data/pdfs/

# 5. Start the web interface
cd src
python app.py

# 6. Open browser to http://localhost:7860

# 7. Follow the web interface instructions to:
#    - Index your PDF
#    - Initialize the system
#    - Ask questions!
```

## Tips for Best Results

1. **Start Simple**: Begin with text-only extraction (no images/tables) for faster testing
2. **Use Good PDFs**: Text-based PDFs work best (scanned PDFs may need OCR)
3. **Clear Questions**: Ask specific, clear questions for better answers
4. **Adjust Parameters**: Experiment with retrieval parameters for optimal results
5. **Monitor Resources**: Watch memory usage when processing large PDFs

## Need Help?

- Check the full `README.md` for detailed documentation
- Review the User Guide in the web interface
- Check Elasticsearch logs: `/usr/local/var/log/elasticsearch.log` (macOS)

Happy querying! 🚀
