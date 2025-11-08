"""
Simple Answer Generation - No OpenAI Required
Just returns the most relevant document chunks
"""

def generate_answer_simple(query, retrieved_documents):
    """
    Generate answer from retrieved documents without OpenAI
    Simply presents the most relevant content
    """
    if not retrieved_documents:
        return "No relevant information found in the documents."
    
    # Create answer from top documents
    answer = f"Based on your query about '{query}', here are the most relevant passages:\n\n"
    
    for i, doc in enumerate(retrieved_documents[:3], 1):  # Top 3 most relevant
        answer += f"📄 Passage {i} (Relevance: {doc.get('rerank_score', 0):.1%}):\n"
        answer += f"{doc['text']}\n\n"
        answer += f"{'─'*60}\n\n"
    
    return answer

def generate_answer_with_sources(query, retrieved_documents, chat_history=None):
    """
    Generate answer with source citations - Simple version
    """
    answer = generate_answer_simple(query, retrieved_documents)
    
    # Prepare sources
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

# Fallback - try OpenAI first, then simple
def generate_answer(query, retrieved_documents, chat_history=None):
    """Try OpenAI, fall back to simple version"""
    try:
        from openai import OpenAI
        from config import OPENAI_API_KEY
        
        # Only try OpenAI if key is set
        if OPENAI_API_KEY and OPENAI_API_KEY != 'your-api-key-here':
            # Original OpenAI implementation would go here
            raise Exception("Use simple version")
    except:
        pass
    
    # Use simple version
    return generate_answer_simple(query, retrieved_documents)
