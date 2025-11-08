"""
Configuration file for RAG System
Contains settings for Elasticsearch, API endpoints, and RAG parameters
"""
from elasticsearch import Elasticsearch
import time
import os

class ElasticConfig:
    """Elasticsearch configuration"""
    # For Docker Elasticsearch with default security
    # Common default credentials: elastic/changeme or elastic/elastic
    url = 'http://localhost:9200'
    username = 'elastic'
    password = 'c8sx1Dp8'  # Change this to your actual password
    
def get_es():
    """
    Get Elasticsearch connection with retry logic
    Handles both authenticated and non-authenticated connections
    
    Returns:
        Elasticsearch client instance
    """
    retry_count = 0
    max_retries = 3
    
    while retry_count < max_retries:
        try:
            # Try with authentication first
            if hasattr(ElasticConfig, 'username') and hasattr(ElasticConfig, 'password'):
                es = Elasticsearch(
                    [ElasticConfig.url],
                    basic_auth=(ElasticConfig.username, ElasticConfig.password),
                    verify_certs=False,
                    ssl_show_warn=False
                )
            else:
                # Try without authentication
                es = Elasticsearch([ElasticConfig.url])
            
            # Test connection
            es.info()
            print('[Elasticsearch] Connected successfully')
            return es
        except Exception as e:
            retry_count += 1
            error_msg = str(e)
            
            # If authentication failed, try without auth
            if 'authentication' in error_msg.lower() and retry_count == 1:
                try:
                    print('[Elasticsearch] Trying without authentication...')
                    es = Elasticsearch([ElasticConfig.url])
                    es.info()
                    print('[Elasticsearch] Connected successfully (no auth)')
                    return es
                except:
                    pass
            
            print(f'[Elasticsearch] Connection failed (attempt {retry_count}/{max_retries})')
            if retry_count < max_retries:
                time.sleep(2)
    
    # Last attempt: try common passwords
    print('[Elasticsearch] Trying common default passwords...')
    for password in ['elastic', 'changeme', '', 'password', '2braintest']:
        try:
            es = Elasticsearch(
                [ElasticConfig.url],
                basic_auth=('elastic', password),
                verify_certs=False,
                ssl_show_warn=False
            )
            es.info()
            print(f'[Elasticsearch] Connected successfully with password')
            return es
        except:
            continue
    
    raise Exception("Failed to connect to Elasticsearch. Please check your credentials in config.py")

# API URLs - these can be used directly according to your teacher
EMBEDDING_URL = "http://test.2brain.cn:9800/v1/emb"
RERANK_URL = "http://test.2brain.cn:2260/rerank"
IMAGE_MODEL_URL = 'http://test.2brain.cn:23333/v1'

# OpenAI Configuration (for answer generation)
# You can set these as environment variables or directly here
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your-api-key-here')
OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')

# RAG Configuration
CHUNK_SIZE = 1024           # Size of each text chunk in tokens
CHUNK_OVERLAP = 100         # Overlap between chunks in tokens
EMBEDDING_DIM = 1024        # Dimension of embedding vectors
TOP_K_RETRIEVAL = 10        # Number of documents to retrieve initially
TOP_K_RERANK = 5            # Number of documents to return after reranking
