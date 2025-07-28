import asyncio
import requests
from typing import List, Optional
from config import Config
from cache import get_cache_key, embedding_cache

async def gemini_embed_async(texts: List[str], batch_size: int = 10) -> List[Optional[List[float]]]:
    """Async embedding with batching and caching"""
    embeddings = []
    uncached_texts = []
    uncached_indices = []
    
    # Check cache first
    for i, text in enumerate(texts):
        cache_key = get_cache_key(text)
        if cache_key in embedding_cache:
            embeddings.append(embedding_cache[cache_key])
        else:
            embeddings.append(None)  # Placeholder
            uncached_texts.append(text)
            uncached_indices.append(i)
    
    if not uncached_texts:
        return embeddings
    
    # Process uncached texts in batches with parallel requests
    loop = asyncio.get_event_loop()
    
    async def process_batch(batch_texts, batch_start_idx):
        tasks = []
        for j, text in enumerate(batch_texts):
            task = loop.run_in_executor(None, get_embedding_sync, text)
            tasks.append(task)
        
        batch_embeddings = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Store in cache and results
        for j, embedding in enumerate(batch_embeddings):
            if not isinstance(embedding, Exception) and embedding is not None:
                original_idx = uncached_indices[batch_start_idx + j]
                embeddings[original_idx] = embedding
                cache_key = get_cache_key(batch_texts[j])
                embedding_cache[cache_key] = embedding
            else:
                # Keep None for failed embeddings
                original_idx = uncached_indices[batch_start_idx + j]
                embeddings[original_idx] = None
                print(f"Failed to embed chunk {original_idx}: {batch_texts[j][:50]}...")
    
    # Process all batches in parallel
    batches = [uncached_texts[i:i + batch_size] for i in range(0, len(uncached_texts), batch_size)]
    batch_tasks = []
    for i, batch in enumerate(batches):
        batch_start_idx = i * batch_size
        batch_tasks.append(process_batch(batch, batch_start_idx))
    
    await asyncio.gather(*batch_tasks)
    
    return embeddings

def get_embedding_sync(text: str, max_retries: int = 3) -> Optional[List[float]]:
    """Get single embedding synchronously with retry logic"""
    if not Config.GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY environment variable is not set")
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/embedding-001:embedContent?key={Config.GOOGLE_API_KEY}"
    headers = {"Content-Type": "application/json"}
    body = {
        "model": "models/embedding-001",
        "content": {"parts": [{"text": text}]}
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=body, headers=headers, timeout=30)
            
            if response.status_code == 503:  # Service unavailable
                if attempt < max_retries - 1:
                    import time
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"503 error, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"Max retries reached for text: {text[:50]}...")
                    return None
            
            if response.status_code != 200:
                print(f"Error: {response.status_code}, {response.text}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(1)
                    continue
                return None
            
            response_data = response.json()
            if 'embedding' in response_data:
                return response_data['embedding']['values']
            else:
                print(f"Unexpected response format: {response_data}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(1)
                    continue
                return None
                
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                print(f"Timeout, retrying... (attempt {attempt + 1}/{max_retries})")
                import time
                time.sleep(1)
                continue
            print(f"Timeout after {max_retries} attempts for text: {text[:50]}...")
            return None
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Error: {e}, retrying... (attempt {attempt + 1}/{max_retries})")
                import time
                time.sleep(1)
                continue
            print(f"Error getting embedding after {max_retries} attempts: {e}")
            return None
    
    return None

# --- Synchronous wrapper for backward compatibility ---
def gemini_embed(texts: List[str]) -> List[Optional[List[float]]]:
    """Synchronous wrapper for async embedding"""
    return asyncio.run(gemini_embed_async(texts))
