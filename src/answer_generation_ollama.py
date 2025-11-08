"""
Answer Generation with Ollama (Free Local LLM)
"""
import requests
import json

def generate_answer_ollama(query, retrieved_documents):
    """Generate answer using Ollama (free local LLM)"""
    
    if not retrieved_documents:
        return "No relevant information found."
    
    # Format context
    context = "\n\n".join([
        f"[Document {i+1}]\n{doc['text']}"
        for i, doc in enumerate(retrieved_documents)
    ])
    
    # Build prompt
    prompt = f"""You are a helpful assistant. Answer the user's question based ONLY on the provided documents.

Documents:
{context}

Question: {query}

Answer (be clear and concise):"""
    
    try:
        # Call Ollama API (local)
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'llama3.2',  # or qwen2.5
                'prompt': prompt,
                'stream': False
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['response']
        else:
            return f"Error: Ollama API returned {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        return "❌ Ollama is not running. Please start Ollama app."
    except Exception as e:
        return f"❌ Error: {str(e)}"

def generate_answer(query, retrieved_documents, chat_history=None):
    """Main answer generation - tries Ollama first"""
    return generate_answer_ollama(query, retrieved_documents)

def generate_answer_with_sources(query, retrieved_documents, chat_history=None):
    """Generate answer with sources"""
    answer = generate_answer(query, retrieved_documents, chat_history)
    
    sources = []
    for i, doc in enumerate(retrieved_documents):
        source_info = {
            'rank': i + 1,
            'text_preview': doc['text'][:200] + '...' if len(doc['text']) > 200 else doc['text'],
            'content_type': doc.get('content_type', 'text'),
            'metadata': doc.get('metadata', {}),
            'rerank_score': doc.get('rerank_score', 0)
        }
        sources.append(source_info)
    
    return {
        'answer': answer,
        'sources': sources,
        'num_sources': len(sources)
    }
