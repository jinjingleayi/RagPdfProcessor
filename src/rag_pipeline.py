"""
Main RAG Pipeline
Integrates all components: query processing, retrieval, reranking, and answer generation
"""
from retrieval import retrieve_and_rerank
from answer_generation import generate_answer_with_sources
from query_processing import rag_fusion, query_decomposition, coreference_resolution
from config import TOP_K_RETRIEVAL, TOP_K_RERANK

class RAGPipeline:
    """
    Complete RAG Pipeline with advanced features
    Supports multi-query retrieval, query decomposition, and conversational context
    """
    
    def __init__(self, index_name, use_multi_query=False, use_query_decomposition=False):
        """
        Initialize RAG Pipeline
        
        Args:
            index_name: Elasticsearch index to search
            use_multi_query: Whether to use multi-query retrieval (RAG Fusion)
            use_query_decomposition: Whether to use query decomposition for complex queries
        """
        self.index_name = index_name
        self.use_multi_query = use_multi_query
        self.use_query_decomposition = use_query_decomposition
        self.chat_history = []
    
    def query(self, user_query, top_k_retrieval=TOP_K_RETRIEVAL, top_k_rerank=TOP_K_RERANK):
        """
        Process a query through the complete RAG pipeline
        
        Args:
            user_query: User's question
            top_k_retrieval: Number of documents to retrieve initially
            top_k_rerank: Number of documents to return after reranking
            
        Returns:
            dict: Dictionary with 'answer', 'sources', and 'num_sources'
        """
        print(f"\n{'='*60}")
        print(f"[RAG Pipeline] Processing query: {user_query}")
        print(f"{'='*60}\n")
        
        # Step 1: Coreference resolution (if chat history exists)
        if self.chat_history:
            resolved_query = coreference_resolution(user_query, self._format_chat_history())
            print(f"[RAG Pipeline] Resolved query: {resolved_query}")
        else:
            resolved_query = user_query
        
        # Step 2: Query processing (decomposition and/or expansion)
        all_queries = [resolved_query]
        
        if self.use_query_decomposition:
            # Decompose complex queries into sub-queries
            sub_queries = query_decomposition(resolved_query)
            if sub_queries:
                all_queries = sub_queries
                print(f"[RAG Pipeline] Query decomposed into {len(sub_queries)} sub-queries")
        
        if self.use_multi_query:
            # Generate query variations for each query (RAG Fusion)
            expanded_queries = []
            for q in all_queries:
                variations = rag_fusion(q)
                expanded_queries.append(q)
                expanded_queries.extend(variations)
            all_queries = expanded_queries
            print(f"[RAG Pipeline] Expanded to {len(all_queries)} total queries")
        
        # Step 3: Retrieve documents for all queries
        all_documents = {}
        for query in all_queries:
            print(f"\n[RAG Pipeline] Retrieving for: {query}")
            docs = retrieve_and_rerank(query, self.index_name, top_k_retrieval, top_k_rerank)
            
            # Deduplicate by document ID
            for doc in docs:
                doc_id = doc['id']
                if doc_id not in all_documents:
                    all_documents[doc_id] = doc
                else:
                    # Keep the one with higher rerank score
                    if doc.get('rerank_score', 0) > all_documents[doc_id].get('rerank_score', 0):
                        all_documents[doc_id] = doc
        
        # Convert to list and sort by rerank score
        final_documents = sorted(
            all_documents.values(),
            key=lambda x: x.get('rerank_score', 0),
            reverse=True
        )[:top_k_rerank]
        
        print(f"\n[RAG Pipeline] Final document count: {len(final_documents)}")
        
        # Step 4: Generate answer
        result = generate_answer_with_sources(
            user_query,
            final_documents,
            self._get_recent_history(max_turns=3)
        )
        
        # Step 5: Update chat history
        self._update_history(user_query, result['answer'])
        
        print(f"\n[RAG Pipeline] Query processed successfully")
        print(f"{'='*60}\n")
        
        return result
    
    def simple_query(self, user_query, top_k_retrieval=TOP_K_RETRIEVAL, top_k_rerank=TOP_K_RERANK):
        """
        Simple query without advanced features (faster, simpler)
        
        Args:
            user_query: User's question
            top_k_retrieval: Number of documents to retrieve
            top_k_rerank: Number of documents to return after reranking
            
        Returns:
            dict: Dictionary with 'answer', 'sources', and 'num_sources'
        """
        print(f"\n[RAG Pipeline] Simple query: {user_query}")
        
        # Retrieve and rerank
        documents = retrieve_and_rerank(user_query, self.index_name, top_k_retrieval, top_k_rerank)
        
        # Generate answer
        result = generate_answer_with_sources(user_query, documents)
        
        # Update history
        self._update_history(user_query, result['answer'])
        
        return result
    
    def _update_history(self, query, answer):
        """Update chat history with new query-answer pair"""
        self.chat_history.append({
            "role": "user",
            "content": query
        })
        self.chat_history.append({
            "role": "assistant",
            "content": answer
        })
    
    def _get_recent_history(self, max_turns=3):
        """
        Get recent chat history for context
        
        Args:
            max_turns: Maximum number of conversation turns to include
            
        Returns:
            list: Recent chat history messages
        """
        # Return last max_turns * 2 messages (user + assistant pairs)
        return self.chat_history[-(max_turns * 2):]
    
    def _format_chat_history(self):
        """Format chat history for coreference resolution"""
        formatted = ""
        for msg in self.chat_history[-6:]:  # Last 3 turns
            role = msg['role']
            content = msg['content']
            formatted += f"'{role}': {content}\n"
        return formatted
    
    def clear_history(self):
        """Clear chat history"""
        self.chat_history = []
        print("[RAG Pipeline] Chat history cleared")

if __name__ == '__main__':
    # Example usage
    print("RAG Pipeline Example\n")
    
    # Create pipeline
    pipeline = RAGPipeline(
        index_name='my_rag_index',
        use_multi_query=False,
        use_query_decomposition=False
    )
    
    # Simple query
    print("Testing simple query...")
    result = pipeline.simple_query("What is machine learning?")
    print(f"\nAnswer: {result['answer']}")
    print(f"Number of sources: {result['num_sources']}")
