"""
Embedding functions for text vectorization
Handles communication with the embedding service to generate vector representations
"""
from config import EMBEDDING_URL
import requests
import time

def local_embedding(inputs):
    """
    Get embeddings from the embedding service
    
    Args:
        inputs: List of text strings to embed
        
    Returns:
        List of embedding vectors (each vector is a list of floats)
        
    Raises:
        Exception: If embedding service fails after retries
    """
    if not inputs:
        return []
    
    headers = {"Content-Type": "application/json"}
    data = {"texts": inputs}
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(EMBEDDING_URL, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result['data']['text_vectors']
        except Exception as e:
            print(f"[Embedding] Error (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                raise Exception(f"Failed to get embeddings after {max_retries} attempts")

def batch_embedding(texts, batch_size=25):
    """
    Get embeddings for large number of texts in batches
    Processes texts in smaller batches to avoid timeout and memory issues
    
    Args:
        texts: List of text strings to embed
        batch_size: Number of texts to process in each batch (default: 25)
        
    Returns:
        List of embedding vectors for all input texts
    """
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        embeddings = local_embedding(batch)
        all_embeddings.extend(embeddings)
        print(f"[Embedding] Processed {min(i + batch_size, len(texts))}/{len(texts)} texts")
    return all_embeddings

if __name__ == '__main__':
    # Test embedding functionality
    print("Testing embedding service...")
    inputs = ["Hello, world!", "This is a test of the embedding service."]
    output = local_embedding(inputs)
    print(f"Generated {len(output)} embeddings")
    print(f"Embedding dimension: {len(output[0])}")
    print("Test completed successfully!")
