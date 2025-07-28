from fastapi import FastAPI, Request, HTTPException
from models import QARequest, QAResponse
from rag_service import RAGService
from config import Config

app = FastAPI(title="RAG API", description="Hackathon RAG Implementation for Fintech Company")
rag_service = RAGService()

@app.post("/hackrx/run", response_model=QAResponse)
async def handle_request(req: Request, body: QARequest):
    """Main endpoint for processing RAG requests"""
    try:
        # Validate API token
        token = req.headers.get("Authorization", "").replace("Bearer ", "")
        if token != Config.API_KEY:
            raise HTTPException(status_code=403, detail="Invalid API token")

        # Process the request using RAG service
        answers, log_filepath = await rag_service.process_request(
            document_url=body.documents,
            questions=body.questions
        )
        
        # Return simplified response with only answers
        return QAResponse(answers=answers)
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ValueError as e:
        # Handle validation errors (like PDF processing issues)
        raise HTTPException(status_code=400, detail=f"Invalid request: {str(e)}")
    except Exception as e:
        # Handle any other unexpected errors
        print(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "RAG API for Hackathon",
        "endpoints": {
            "/hackrx/run": "POST - Main RAG processing endpoint",
            "/health": "GET - Health check",
            "/docs": "GET - API documentation"
        }
    }
