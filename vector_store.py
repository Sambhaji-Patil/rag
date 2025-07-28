import uuid
import asyncio
from typing import List, Optional, Tuple, Any
from pinecone import Pinecone, ServerlessSpec
from config import Config

# Initialize Pinecone
if not Config.PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY environment variable is not set")

pc = Pinecone(api_key=Config.PINECONE_API_KEY)

# Check if index exists and create if needed
existing_indexes = [index_info['name'] for index_info in pc.list_indexes()]
if Config.INDEX_NAME not in existing_indexes:
    pc.create_index(
        name=Config.INDEX_NAME,
        dimension=Config.PINECONE_DIMENSION,
        spec=ServerlessSpec(cloud=Config.PINECONE_CLOUD, region=Config.PINECONE_REGION)
    )

index = pc.Index(Config.INDEX_NAME)

async def store_chunks_async(chunks: List[str], embeddings: List[Optional[List[float]]]) -> None:
    """Async batch upsert with parallel processing"""
    # Filter out failed embeddings
    valid_vectors = []
    failed_count = 0
    
    for chunk, emb in zip(chunks, embeddings):
        if emb is not None and len(emb) > 0:
            valid_vectors.append((str(uuid.uuid4()), emb, {"text": chunk}))
        else:
            failed_count += 1
    
    print(f"Storing {len(valid_vectors)} vectors, skipping {failed_count} failed embeddings")
    
    if not valid_vectors:
        print("No valid vectors to store!")
        return
    
    async def upsert_batch(batch_vectors):
        """Upsert a single batch"""
        try:
            # Run Pinecone upsert in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: index.upsert(batch_vectors))
        except Exception as e:
            print(f"Error upserting batch: {e}")
            raise
    
    # Process batches in parallel (but limit concurrency)
    batches = [valid_vectors[i:i + Config.UPSERT_BATCH_SIZE] for i in range(0, len(valid_vectors), Config.UPSERT_BATCH_SIZE)]
    
    # Limit concurrent uploads to avoid overwhelming Pinecone
    semaphore = asyncio.Semaphore(Config.CONCURRENT_UPLOADS)
    
    async def upload_with_semaphore(batch):
        async with semaphore:
            await upsert_batch(batch)
    
    # Upload all batches in parallel
    await asyncio.gather(*[upload_with_semaphore(batch) for batch in batches])

def retrieve_chunks(query_emb: List[float], top_k: int = None) -> List[str]:
    """Search in Pinecone and retrieve relevant chunks"""
    if top_k is None:
        top_k = Config.TOP_K
    
    results = index.query(vector=query_emb, top_k=top_k, include_metadata=True)
    return [match["metadata"]["text"] for match in results["matches"]]

# --- Synchronous wrapper for backward compatibility ---
def store_chunks(chunks: List[str], embeddings: List[Optional[List[float]]]) -> None:
    """Synchronous wrapper for async storage"""
    return asyncio.run(store_chunks_async(chunks, embeddings))
