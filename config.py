import os
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
class Config:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    API_KEY = os.getenv("API_KEY")
    INDEX_NAME = "hackrx-docs"
    
    # Embedding settings
    BATCH_SIZE = 20
    CHUNK_SIZE = 300
    CHUNK_OVERLAP = 50
    
    # Pinecone settings
    PINECONE_DIMENSION = 768
    PINECONE_CLOUD = 'aws'
    PINECONE_REGION = 'us-east-1'
    UPSERT_BATCH_SIZE = 50
    CONCURRENT_UPLOADS = 3
    
    # Search settings
    TOP_K = 10
    
    # GPT settings
    GPT_MODEL = "gpt-4o-mini"
    GPT_TEMPERATURE = 0.0
    GPT_MAX_TOKENS = 300
