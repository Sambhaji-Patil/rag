# RAG

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
