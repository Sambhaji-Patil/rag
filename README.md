# RAG Implementation - Modular Structure

This project implements a Retri### Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables in .env file (copy from .env.example)
cp .env.example .env
# Edit .env file with your actual API keys

# Test the setup (optional but recommended)
python test_setup.py

# Run the server
python main.py
```

### Troubleshooting

If you encounter errors:

1. **Run the test script first:**
   ```bash
   python test_setup.py
   ```

2. **Check your .env file:** Make sure all required environment variables are set:
   - `GOOGLE_API_KEY` - Your Google Gemini API key
   - `OPENAI_API_KEY` - Your OpenAI API key  
   - `PINECONE_API_KEY` - Your Pinecone API key
   - `API_KEY` - Your custom API authentication key

3. **Google Docs URL Format:** The system automatically converts Google Docs URLs to PDF export format. Supported formats:
   - `https://docs.google.com/document/d/DOCUMENT_ID/edit...`
   - URLs with `id=DOCUMENT_ID` parameter

4. **Common Issues:**
   - **403 Forbidden**: Check your API_KEY in the Authorization header
   - **400 Bad Request**: Usually PDF processing issues - check if the document is publicly accessible
   - **500 Internal Server Error**: Check server logs for specific error detailsGeneration (RAG) system for a fintech hackathon. The system processes PDF documents from URLs and answers questions using vector embeddings and LLM.

## Project Structure

```
RAG-BAJAJ/
├── main.py              # Original monolithic implementation
├── main_new.py          # New entry point (modular)
├── api.py              # FastAPI routes and endpoints
├── config.py           # Configuration and constants
├── models.py           # Pydantic models for API
├── cache.py            # Caching utilities and document tracking
├── document_processor.py # PDF processing and text chunking
├── embeddings.py       # Google Gemini embedding service
├── vector_store.py     # Pinecone vector database operations
├── llm.py              # OpenAI GPT-4 integration
├── rag_service.py      # Main RAG orchestration service
├── requirements.txt    # Dependencies (to be created)
└── .env               # Environment variables
```

## Components

### 1. **config.py**
- Central configuration management
- Environment variables and API keys
- Model parameters and settings

### 2. **models.py**
- Pydantic models for request/response validation
- Type definitions for API contracts

### 3. **cache.py**
- Embedding cache management
- Document processing tracking
- Timing logs and analytics

### 4. **document_processor.py**
- PDF text extraction from URLs
- Text chunking with overlap
- Document preprocessing utilities

### 5. **embeddings.py**
- Google Gemini embedding API integration
- Async batch processing with retry logic
- Caching and error handling

### 6. **vector_store.py**
- Pinecone vector database operations
- Async batch upserts with concurrency control
- Vector similarity search

### 7. **llm.py**
- OpenAI GPT-4 integration
- Async prompt processing
- Response generation

### 8. **rag_service.py**
- Main orchestration service
- End-to-end RAG pipeline
- Performance monitoring and logging

### 9. **api.py**
- FastAPI application setup
- Route definitions and middleware
- Authentication and error handling

### 10. **main_new.py**
- Application entry point
- Server configuration

## Usage

### Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables in .env file
GOOGLE_API_KEY=your_google_api_key
OPENAI_API_KEY=your_openai_api_key  
PINECONE_API_KEY=your_pinecone_api_key
API_KEY=your_api_authentication_key

# Run the server
python main_new.py
```

### API Request Format

```json
{
    "documents": "https://docs.google.com/document/d/1rsSPSAwOvnkTYqY2FlF_7kf_CFWRsWiX/edit?usp=drive_link&ouid=107259714124037946473&rtpof=true&sd=true",
    "questions": [
        "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
        "What is the waiting period for pre-existing diseases (PED) to be covered?",
        "Does this policy cover maternity expenses, and what are the conditions?"
    ]
}
```

### API Response Format

```json
{
    "answers": [
        "The grace period for premium payment is 30 days...",
        "The waiting period for pre-existing diseases is 2 years...",
        "Yes, maternity expenses are covered after 2 years..."
    ]
}
```

## Features

- **Async Processing**: Parallel embedding generation and question processing
- **Caching**: Document and embedding caching to avoid reprocessing
- **Error Handling**: Robust retry logic and error recovery
- **Performance Monitoring**: Detailed timing logs for optimization
- **Modular Architecture**: Clean separation of concerns
- **Scalability**: Configurable batching and concurrency limits

## Benefits of Modular Structure

1. **Maintainability**: Each module has a single responsibility
2. **Testability**: Individual components can be unit tested
3. **Reusability**: Components can be reused across different projects
4. **Scalability**: Easy to scale individual components
5. **Debugging**: Easier to identify and fix issues
6. **Team Collaboration**: Multiple developers can work on different modules
