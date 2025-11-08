#!/bin/bash
# Run RAG System - Workflow Interface

echo "🚀 Starting RAG System - Workflow Interface"
echo "📍 Elasticsearch: http://localhost:9200"
echo "🦙 Ollama: FREE local AI"
echo "🌐 Opening at: http://localhost:7860"
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "⚠️  Virtual environment not found. Using system Python."
fi

cd src
python app_workflow.py
