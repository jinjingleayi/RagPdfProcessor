"""
Retrieval Module
Implements hybrid search (vector + keyword) with RRF and reranking
"""
from config import get_es, RERANK_URL, TOP_K_RETRIEVAL
from embedding import local_embedding
import jieba
import re
import requests

# Chinese stop words for keyword extraction
stop_words = set([
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "was", "are", "were", "been",
    "be", "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "can", "this", "that", "these", "those", "it",
    "its", "what", "which", "who", "when", "where", "why", "how",
    # Chinese stop words
    "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一个", 
    "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "与", 
    "如何", "为", "得", "里", "后", "自己", "之", "过", "给", "然后", "那", "下", 
    "能", "而", "来", "个", "这", "之间", "应该", "可以", "到", "由", "及", "对", 
    "中", "会", "但", "年", "还", "并", "如果", "我们", "为了", "而且", "或者", 
    "因为", "所以", "对于", "而言", "与否", "只是", "已经", "可能", "同时", "比如", 
    "这样", "当然", "并且", "大家", "之后", "那么", "越", "虽然", "比", "还是", 
    "只有", "现在", "应该", "由于", "尽管", "除了", "以外", "然而", "哪些", "这些", 
    "所有", "并非", "例如", "尤其", "哪里", "那里", "何时", "多少", "以至", "以至于", 
    "几乎", "已经", "仍然", "甚至", "更加", "无论", "不过", "不是", "从来", "何处", 
    "到底", "尽管", "何况", "不会", "何以", "怎样", "为何", "此外", "其中", "怎么", 
    "什么", "为什么", "是否", '。', '？', '！', '.', '?', '!', '，', ','
])

def get_keyword(query):
    """
    Extract keywords from query using jieba (Chinese) or simple splitting (English)
    
    Args:
        query: Query string
        
    Returns:
        List of keywords with stop words removed
    """
    if not isinstance(query, str):
        print(f'[Keyword Extraction] Received non-string query, converting to string')
        query = str(query) if query is not None else ''
    
    if not query.strip():
        print('[Keyword Extraction] Empty query string, returning empty list')
        return []
    
    try:
        # Use jieba for Chinese text segmentation
        seg_list = jieba.cut_for_search(query)
        # Filter out stop words
        filtered_keywords = [word for word in seg_list if word not in stop_words]
        return filtered_keywords
    except Exception as e:
        print(f'[Keyword Extraction] Error processing query "{query}": {e}')
        return []

def hybrid_search_rrf(keyword_hits, vector_hits, k=60):
    """
    Reciprocal Rank Fusion (RRF) for combining keyword and vector search results
    Formula: RRF_score = sum(1 / (k + rank)) for each result list
    
    Args:
        keyword_hits: Results from keyword search
        vector_hits: Results from vector search
        k: RRF parameter (default: 60, commonly used value)
        
    Returns:
        Combined and ranked results sorted by RRF score
    """
    scores = {}
    
    # Process keyword search results
    for hit in keyword_hits:
        doc_id = hit['id']
        if doc_id not in scores:
            scores[doc_id] = {
                'score': 0,
                'text': hit['text'],
                'id': doc_id,
                'metadata': hit.get('metadata', {}),
                'content_type': hit.get('content_type', 'text')
            }
        scores[doc_id]['score'] += 1 / (k + hit['rank'])
    
    # Process vector search results
    for hit in vector_hits:
        doc_id = hit['id']
        if doc_id not in scores:
            scores[doc_id] = {
                'score': 0,
                'text': hit['text'],
                'id': doc_id,
                'metadata': hit.get('metadata', {}),
                'content_type': hit.get('content_type', 'text')
            }
        scores[doc_id]['score'] += 1 / (k + hit['rank'])
    
    # Sort documents by RRF score (descending)
    ranked_docs = sorted(scores.values(), key=lambda x: x['score'], reverse=True)
    
    # Clean up timestamps if present (e.g., from video transcripts)
    for doc in ranked_docs:
        timestamp_pattern = re.compile(r'\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}\.\d{3}')
        doc['text'] = re.sub(timestamp_pattern, '', doc['text'])
    
    # Format final results with ranks
    final_results = [
        {
            'id': doc['id'],
            'text': doc['text'],
            'metadata': doc['metadata'],
            'content_type': doc['content_type'],
            'rank': idx + 1,
            'rrf_score': doc['score']
        }
        for idx, doc in enumerate(ranked_docs)
    ]
    
    return final_results

def elastic_search(query, index_name, top_k=TOP_K_RETRIEVAL):
    """
    Hybrid search: combines keyword search + vector search using RRF
    
    Args:
        query: Search query
        index_name: Elasticsearch index name
        top_k: Number of top results to retrieve from each search method
        
    Returns:
        Combined search results ranked by RRF
    """
    es = get_es()
    
    # Step 1: Keyword Search (BM25)
    keywords = get_keyword(query)
    
    keyword_query = {
        "bool": {
            "should": [
                {"match": {"text": {"query": keyword, "fuzziness": "AUTO"}}} 
                for keyword in keywords
            ],
            "minimum_should_match": 1
        }
    }
    
    try:
        res_keyword = es.search(index=index_name, query=keyword_query, size=top_k)
        keyword_hits = [
            {
                'id': hit['_id'],
                'text': hit['_source'].get('text', ''),
                'metadata': hit['_source'].get('metadata', {}),
                'content_type': hit['_source'].get('content_type', 'text'),
                'rank': idx + 1
            }
            for idx, hit in enumerate(res_keyword['hits']['hits'])
        ]
        print(f"[Retrieval] Keyword search found {len(keyword_hits)} results")
    except Exception as e:
        print(f"[Retrieval] Keyword search error: {e}")
        keyword_hits = []
    
    # Step 2: Vector Search (Cosine Similarity)
    try:
        embedding = local_embedding([query])
        vector_query = {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": "cosineSimilarity(params.queryVector, 'vector') + 1.0",
                    "params": {"queryVector": embedding[0]}
                }
            }
        }
        
        res_vector = es.search(index=index_name, query=vector_query, size=top_k)
        vector_hits = [
            {
                'id': hit['_id'],
                'text': hit['_source'].get('text', ''),
                'metadata': hit['_source'].get('metadata', {}),
                'content_type': hit['_source'].get('content_type', 'text'),
                'rank': idx + 1
            }
            for idx, hit in enumerate(res_vector['hits']['hits'])
        ]
        print(f"[Retrieval] Vector search found {len(vector_hits)} results")
    except Exception as e:
        print(f"[Retrieval] Vector search error: {e}")
        vector_hits = []
    
    # Step 3: Combine with RRF
    combined_results = hybrid_search_rrf(keyword_hits, vector_hits)
    print(f"[Retrieval] Combined results: {len(combined_results)} documents")
    
    return combined_results

def rerank(query, documents, top_k=None):
    """
    Rerank documents using reranker model for improved relevance
    
    Args:
        query: Search query
        documents: List of retrieved documents
        top_k: Number of top results to return (None for all)
        
    Returns:
        Reranked documents sorted by reranker score
    """
    if not documents:
        return []
    
    try:
        response = requests.post(
            RERANK_URL,
            json={
                "query": query,
                "documents": [doc['text'] for doc in documents]
            },
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        
        if result and 'scores' in result and len(result['scores']) == len(documents):
            # Add rerank scores to documents
            for idx, doc in enumerate(documents):
                documents[idx]['rerank_score'] = result['scores'][idx]
            
            # Sort by rerank score (descending - higher is better)
            documents.sort(key=lambda x: x['rerank_score'], reverse=True)
            print(f"[Reranking] Reranked {len(documents)} documents")
        else:
            print("[Reranking] Invalid response from reranker")
    
    except Exception as e:
        print(f"[Reranking] Error: {e}")
    
    # Return top_k if specified
    if top_k:
        return documents[:top_k]
    return documents

def retrieve_and_rerank(query, index_name, top_k_retrieval=TOP_K_RETRIEVAL, top_k_rerank=5):
    """
    Complete retrieval pipeline: hybrid search + reranking
    
    Args:
        query: Search query
        index_name: Elasticsearch index name
        top_k_retrieval: Number of documents to retrieve initially
        top_k_rerank: Number of documents to return after reranking
        
    Returns:
        Top reranked documents
    """
    print(f"\n[Retrieval Pipeline] Query: {query}")
    
    # Step 1: Hybrid Search (keyword + vector with RRF)
    search_results = elastic_search(query, index_name, top_k=top_k_retrieval)
    
    if not search_results:
        print("[Retrieval Pipeline] No results found")
        return []
    
    # Step 2: Rerank using reranker model
    reranked_results = rerank(query, search_results, top_k=top_k_rerank)
    
    print(f"[Retrieval Pipeline] Returning top {len(reranked_results)} results")
    return reranked_results

if __name__ == '__main__':
    # Test retrieval
    test_query = "What is machine learning?"
    test_index = "test_rag_index"
    
    print("Testing retrieval pipeline...")
    results = retrieve_and_rerank(test_query, test_index)
    for i, doc in enumerate(results):
        print(f"\n--- Result {i+1} ---")
        print(f"Text: {doc['text'][:200]}...")
        print(f"Rerank Score: {doc.get('rerank_score', 'N/A')}")
