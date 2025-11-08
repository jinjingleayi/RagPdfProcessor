"""
Elasticsearch index management functions
Handles index creation, deletion, and document indexing operations
"""
from config import get_es, EMBEDDING_DIM

def create_elastic_index(index_name, embedding_dim=EMBEDDING_DIM):
    """
    Create Elasticsearch index with proper mappings for hybrid search
    
    Args:
        index_name: Name of the index to create
        embedding_dim: Dimension of embedding vectors (default: 1024)
        
    Returns:
        bool: True if index created successfully, False if already exists
    """
    es = get_es()
    
    mappings = {
        "properties": {
            "text": {
                "type": "text",
                "analyzer": "standard"  # Standard analyzer for full-text search
            }, 
            "vector": {
                "type": "dense_vector",
                "dims": embedding_dim,
                "index": True,
                "similarity": "cosine"  # Use cosine similarity for vector search
            },
            "metadata": {
                "type": "object",
                "enabled": True
            },
            "file_name": {
                "type": "keyword"  # Exact match for file names
            },
            "page": {
                "type": "integer"  # Page number
            },
            "chunk_id": {
                "type": "keyword"  # Unique identifier for each chunk
            },
            "content_type": {
                "type": "keyword"  # text, image, or table
            },
            "image_path": {
                "type": "keyword"  # Path to extracted image
            },
            "table_markdown": {
                "type": "text"  # Original table in markdown format
            }
        }
    }
    
    try:
        if es.indices.exists(index=index_name):
            print(f'[Elasticsearch] Index {index_name} already exists')
            return False
        
        es.indices.create(index=index_name, mappings=mappings)
        print(f'[Elasticsearch] Index {index_name} created successfully')
        return True
    except Exception as e:
        print(f'[Elasticsearch] Error creating index: {e}')
        return False

def delete_elastic_index(index_name):
    """
    Delete an Elasticsearch index
    
    Args:
        index_name: Name of the index to delete
        
    Returns:
        bool: True if deleted successfully, False if doesn't exist
    """
    es = get_es()
    try:
        if es.indices.exists(index=index_name):
            es.indices.delete(index=index_name)
            print(f'[Elasticsearch] Index {index_name} deleted')
            return True
        else:
            print(f'[Elasticsearch] Index {index_name} does not exist')
            return False
    except Exception as e:
        print(f'[Elasticsearch] Error deleting index: {e}')
        return False

def index_document(index_name, document):
    """
    Index a single document in Elasticsearch
    
    Args:
        index_name: Name of the index
        document: Dictionary containing document data
        
    Returns:
        Response from Elasticsearch
    """
    es = get_es()
    try:
        response = es.index(index=index_name, body=document)
        return response
    except Exception as e:
        print(f'[Elasticsearch] Error indexing document: {e}')
        raise

def bulk_index_documents(index_name, documents):
    """
    Bulk index multiple documents for better performance
    
    Args:
        index_name: Name of the index
        documents: List of document dictionaries
        
    Returns:
        tuple: (success_count, failed_count)
    """
    from elasticsearch import helpers
    
    es = get_es()
    
    # Prepare bulk actions
    actions = [
        {
            "_index": index_name,
            "_source": doc
        }
        for doc in documents
    ]
    
    try:
        success, failed = helpers.bulk(es, actions, raise_on_error=False)
        print(f'[Elasticsearch] Bulk indexed {success} documents, {failed} failed')
        return success, failed
    except Exception as e:
        print(f'[Elasticsearch] Error bulk indexing: {e}')
        raise

def get_index_stats(index_name):
    """
    Get statistics about an index
    
    Args:
        index_name: Name of the index
        
    Returns:
        int: Number of documents in the index
    """
    es = get_es()
    try:
        count = es.count(index=index_name)
        doc_count = count["count"]
        print(f'[Elasticsearch] Index {index_name} has {doc_count} documents')
        return doc_count
    except Exception as e:
        print(f'[Elasticsearch] Error getting index stats: {e}')
        return 0

if __name__ == '__main__':
    # Test index operations
    test_index = 'test_rag_index'
    print("Testing Elasticsearch operations...")
    create_elastic_index(test_index)
    get_index_stats(test_index)
    print("Test completed!")
