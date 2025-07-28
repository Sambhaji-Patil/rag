import os
import json
import hashlib
from datetime import datetime
from typing import Dict, Any

# --- Caching ---
embedding_cache = {}
document_cache = {}  # Cache for processed documents

def get_cache_key(text: str) -> str:
    """Generate a cache key for text"""
    return hashlib.md5(text.encode()).hexdigest()

def get_document_key(url: str) -> str:
    """Generate a cache key for document URL"""
    return hashlib.md5(url.encode()).hexdigest()

def is_document_processed(doc_url: str) -> bool:
    """Check if document was already processed"""
    doc_key = get_document_key(doc_url)
    return doc_key in document_cache

def mark_document_processed(doc_url: str, chunks_count: int):
    """Mark document as processed"""
    doc_key = get_document_key(doc_url)
    document_cache[doc_key] = {
        "url": doc_url,
        "processed_at": datetime.now().isoformat(),
        "chunks_count": chunks_count
    }
    print(f"Document cached: {chunks_count} chunks from {doc_url[:50]}...")

def save_timing_logs(request_id: str, timing_data: Dict[str, Any]) -> str:
    """Save timing logs to a file with unique ID"""
    # Create logs directory if it doesn't exist
    logs_dir = "timing_logs"
    os.makedirs(logs_dir, exist_ok=True)
    
    # Create filename with timestamp and request ID
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"timing_log_{timestamp}_{request_id}.json"
    filepath = os.path.join(logs_dir, filename)
    
    # Save to file
    with open(filepath, 'w') as f:
        json.dump(timing_data, f, indent=2)
    
    print(f"Timing logs saved to: {filepath}")
    return filepath
