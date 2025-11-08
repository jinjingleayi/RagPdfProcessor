"""
Answer Generation Module
Generates answers based on retrieved documents using LLM
"""
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_BASE_URL

def generate_answer(query, retrieved_documents, chat_history=None):
    """
    Generate answer based on retrieved documents using LLM
    
    Args:
        query: User's question
        retrieved_documents: List of retrieved and reranked documents
        chat_history: Optional chat history for context-aware responses
        
    Returns:
        str: Generated answer
    """
    if not retrieved_documents:
        return "Sorry, I couldn't find relevant information to answer your question."
    
    # Format retrieved documents as context
    context = "\n\n".join([
        f"[Document {i+1}]\n{doc['text']}"
        for i, doc in enumerate(retrieved_documents)
    ])
    
    # Build system prompt
    system_prompt = """You are an intelligent Q&A assistant that answers user questions based on provided reference documents.

Requirements:
1. Accurate: Answers must be based on the provided reference documents. Do not fabricate information.
2. Complete: Answer the user's question as comprehensively as possible.
3. Clear: Use clear and understandable language. Use bullet points or numbered lists when appropriate.
4. Citations: Appropriately reference the document content to enhance credibility.
5. Honest: If the reference documents do not contain sufficient information to answer the question, clearly inform the user.

If the reference documents do not contain enough information to answer the question, please honestly inform the user."""
    
    # Build user prompt
    user_prompt = f"""Reference documents:
{context}

User question: {query}

Please answer the user's question based on the above reference documents:"""
    
    # Add chat history if available
    messages = [{"role": "system", "content": system_prompt}]
    
    if chat_history:
        messages.extend(chat_history)
    
    messages.append({"role": "user", "content": user_prompt})
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=2000
        )
        
        answer = response.choices[0].message.content
        print(f"[Answer Generation] Generated answer ({len(answer)} chars)")
        return answer
        
    except Exception as e:
        print(f"[Answer Generation] Error: {e}")
        return f"Sorry, an error occurred while generating the answer: {str(e)}"

def generate_answer_with_sources(query, retrieved_documents, chat_history=None):
    """
    Generate answer with source citations for transparency
    
    Args:
        query: User's question
        retrieved_documents: List of retrieved and reranked documents
        chat_history: Optional chat history for context
        
    Returns:
        dict: Dictionary containing answer and source information
    """
    answer = generate_answer(query, retrieved_documents, chat_history)
    
    # Prepare source information
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

if __name__ == '__main__':
    # Test answer generation
    test_query = "What is machine learning?"
    test_docs = [
        {
            'text': 'Machine learning is a branch of artificial intelligence that enables computers to learn from data and make decisions or predictions without being explicitly programmed.',
            'content_type': 'text',
            'metadata': {'page': 1},
            'rerank_score': 0.95
        }
    ]
    
    result = generate_answer_with_sources(test_query, test_docs)
    print(f"Answer: {result['answer']}")
    print(f"Number of sources: {result['num_sources']}")
