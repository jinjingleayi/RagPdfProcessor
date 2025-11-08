"""
Advanced Query Processing Module
Implements RAG Fusion (multi-query) and Query Decomposition
"""
import json
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_BASE_URL

def rag_fusion(query):
    """
    RAG Fusion: Generate multiple query variations to improve retrieval coverage
    Different phrasings of the same question can retrieve different relevant documents
    
    Args:
        query: Original user query
        
    Returns:
        List of query variations (2 variations by default)
    """
    prompt = f'''Based on the user's query, rewrite it into 2 different queries. These rewritten queries should cover different aspects or angles of the original query to retrieve more comprehensive information. Ensure each rewritten query is still relevant to the original query and different in content.

Output in JSON format:
{{
    "rag_fusion":["query1","query2"]
}}

Original query: {query}
'''
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI assistant that specializes in rewriting user queries. Output in JSON format."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        result = response.choices[0].message.content
        parsed_result = json.loads(result)
        variations = parsed_result.get("rag_fusion", [])
        
        print(f"[RAG Fusion] Generated {len(variations)} query variations")
        return variations
        
    except Exception as e:
        print(f"[RAG Fusion] Error: {e}")
        return []

def query_decomposition(query):
    """
    Query Decomposition: Break down complex queries into simpler sub-queries
    Useful for queries that involve multiple concepts or require multi-step reasoning
    
    Args:
        query: Original complex query
        
    Returns:
        List of sub-queries (empty list if no decomposition needed)
    """
    prompt = f''' 
Goal: Analyze the user's question and determine if it needs to be decomposed into sub-questions to improve information retrieval accuracy. If decomposition is needed, provide a list of sub-questions; if not, return an empty list.

Instructions:
- The user's question may be ambiguous or contain multiple concepts, making it difficult to answer directly.
- To improve the quality and relevance of knowledge base queries, evaluate whether the question should be decomposed into more specific sub-questions.
- Based on the complexity and breadth of the question, determine if decomposition is needed:
  - If the question involves multiple aspects (e.g., comparing multiple entities, containing multiple independent steps), decompose it into sub-questions.
  - If the question is already focused and clear, no decomposition is needed, return an empty list.
- Output must be in JSON format. Output JSON directly without any explanation.

Output format:
{{
  "query": ["sub-question1", "sub-question2"...] 
}}  

Case 1
---
User question: "What are the differences between Lincoln, Guan Yu, and Sun Wukong?"
Reasoning: This question involves comparing multiple entities and requires understanding each entity's characteristics separately.
Output:
{{
  "query": ["What is Lincoln like?", "What is Guan Yu like?", "What is Sun Wukong like?"]
}}

Case 2
---
User question: "What is the difference between LangChain and LangGraph?"
Reasoning: This question involves comparison and can be decomposed into understanding each entity separately to improve retrieval accuracy.
Output:
{{
  "query": ["What is LangChain?", "What is LangGraph?"]
}}

Case 3
---
User question: "How to design a smart home system and monitor device status in real-time?"
Reasoning: The question contains two independent aspects (system design and status monitoring) and needs to be decomposed.
Output:
{{
  "query": ["How to design a smart home system?", "How to monitor smart home device status in real-time?"]
}}

Case 4
---
User question: "What is machine learning?"
Reasoning: The question is focused and clear, no decomposition needed.
Output:
{{
  "query": []
}}

User question:
"{query}"
'''
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI assistant that specializes in query decomposition. Output in JSON format."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        result = response.choices[0].message.content
        parsed_result = json.loads(result)
        sub_queries = parsed_result.get("query", [])
        
        if sub_queries:
            print(f"[Query Decomposition] Decomposed into {len(sub_queries)} sub-queries")
        else:
            print("[Query Decomposition] No decomposition needed")
        
        return sub_queries
        
    except Exception as e:
        print(f"[Query Decomposition] Error: {e}")
        return []

def coreference_resolution(query, chat_history):
    """
    Coreference Resolution: Resolve pronouns/references in queries using chat history
    Replaces pronouns like "it", "they", "that" with actual entities from conversation
    
    Args:
        query: Current user query (may contain pronouns)
        chat_history: Previous conversation history
        
    Returns:
        Resolved query with pronouns replaced by actual entities
    """
    prompt = f'''Goal: Based on the provided conversation history between the user and the knowledge base assistant, perform coreference resolution. Replace pronouns or references in the user's latest question with explicit objects from the history to generate a complete, standalone question.

Instructions:
- Replace referential words in the user's question with specific content from the conversation history to generate a standalone question.

Output in JSON format:
{{"query":"Complete question after resolving references"}}

Here are some examples:

----------
Conversation history:
['user': What is Milvus?
'assistant': Milvus is a vector database]
User question: How to use it?

Output JSON: {{"query":"How to use Milvus?"}}
----------
Conversation history:
['user': What is PyTorch?
'assistant': PyTorch is an open-source machine learning library for Python.
'user': What is TensorFlow?
'assistant': TensorFlow is an open-source machine learning framework.]
User question: What are their differences?

Output JSON: {{"query":"What are the differences between PyTorch and TensorFlow?"}}
----------
Conversation history:
{chat_history}
User question: {query}

Output JSON:
''' 
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI assistant that specializes in coreference resolution. Output in JSON format."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        result = response.choices[0].message.content
        parsed_result = json.loads(result)
        resolved_query = parsed_result.get("query", query)
        
        print(f"[Coreference Resolution] Resolved: {resolved_query}")
        return resolved_query
        
    except Exception as e:
        print(f"[Coreference Resolution] Error: {e}")
        return query

if __name__ == '__main__':
    # Test RAG Fusion
    test_query = "What is deep learning?"
    print(f"Original query: {test_query}")
    variations = rag_fusion(test_query)
    print(f"Variations: {variations}")
    
    # Test Query Decomposition
    complex_query = "What is the difference between LangChain and LangGraph?"
    print(f"\nComplex query: {complex_query}")
    sub_queries = query_decomposition(complex_query)
    print(f"Sub-queries: {sub_queries}")
