#!/bin/bash
# Run RAG System - Workflow Interface

echo "🚀 Starting RAG System - Workflow Interface"
echo "📍 Elasticsearch: http://localhost:9200"
echo "🌐 Opening at: http://localhost:7860"
echo ""

source venv/bin/activate
cd src
python app_workflow.py
