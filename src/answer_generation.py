"""
Answer Generation - STRICT: Only uses uploaded PDF content
"""
import requests
import json

def generate_answer(query, retrieved_documents, chat_history=None):
    """
    Generate answer using ONLY the retrieved documents (strict mode)
    """
    if not retrieved_documents:
        return "I cannot find any relevant information in your uploaded PDFs to answer this question."
    
    # Format context from retrieved documents
    context = "\n\n".join([
        f"[Source {i+1} - Page {doc.get('metadata', {}).get('page', '?')}]\n{doc['text']}"
        for i, doc in enumerate(retrieved_documents)
    ])
    
    # STRICT prompt - forces LLM to use ONLY provided context
    prompt = f"""You are a document Q&A assistant. You MUST answer based ONLY on the provided documents below. 

IMPORTANT RULES:
1. If the answer is not in the documents, say "I cannot find this information in the provided documents."
2. DO NOT use any external knowledge
3. Quote specific parts from the documents when possible
4. If unsure, say so

DOCUMENTS FROM UPLOADED PDFs:
{context}

USER QUESTION: {query}

YOUR ANSWER (based ONLY on the documents above):"""
    
    try:
        print("[Answer Generation] Generating answer from YOUR PDFs only...")
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'llama3.2:3b',
                'prompt': prompt,
                'stream': False,
                'options': {
                    'temperature': 0.3,  # Lower temperature for more factual answers
                    'top_k': 10,
                    'top_p': 0.9
                }
            },
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result['response'].strip()
            print(f"[Answer Generation] Generated answer from your PDFs ({len(answer)} chars)")
            return answer
        else:
            return f"Error: Ollama returned status {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        return "❌ Ollama is not running. Please open the Ollama app (look for 🦙 icon in menu bar)."
    except Exception as e:
        print(f"[Answer Generation] Error: {e}")
        return f"Error generating answer: {str(e)}"

def generate_answer_with_sources(query, retrieved_documents, chat_history=None):
    """Generate answer with source citations"""
    answer = generate_answer(query, retrieved_documents, chat_history)
    
    sources = []
    for i, doc in enumerate(retrieved_documents):
        source_info = {
            'rank': i + 1,
            'text_preview': doc['text'][:300] + '...' if len(doc['text']) > 300 else doc['text'],
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
