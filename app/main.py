"""
FastAPI application for medical claim document processing
Multi-agent agentic workflow using LangGraph and Gemini
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, Response
from fastapi.responses import JSONResponse
from typing import List
import logging
from contextlib import asynccontextmanager

from app.graph import create_claim_processing_graph
from app.models.schemas import ClaimProcessingResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting Superclaims Backend Service")
    yield
    logger.info("🛑 Shutting down Superclaims Backend Service")

# Initialize FastAPI app
app = FastAPI(
    title="Superclaims Backend API",
    description="AI-driven agentic workflow for medical insurance claim processing",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Superclaims Backend",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.post("/process-claim", response_model=ClaimProcessingResult)
async def process_claim(files: List[UploadFile] = File(...)):
    """
    Process medical insurance claim documents using multi-agent workflow
    
    Args:
        files: List of PDF files (bill, discharge summary, ID card, etc.)
        
    Returns:
        ClaimProcessingResult: Structured claim data with validation and decision
    """
    try:
        logger.info(f"📥 Received {len(files)} files for processing")
        
        # Validate file count
        if not files:
            raise HTTPException(status_code=400, detail="No files uploaded")
        
        # Validate file types
        for file in files:
            if not file.filename.endswith('.pdf'):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid file type: {file.filename}. Only PDF files are supported"
                )
        
        # Read file contents
        file_data = []
        for file in files:
            content = await file.read()
            file_data.append({
                "filename": file.filename,
                "content": content
            })
            logger.info(f"✅ Read file: {file.filename} ({len(content)} bytes)")
        
        # Create and execute LangGraph workflow
        logger.info("🔄 Starting multi-agent processing workflow")
        graph = create_claim_processing_graph()
        
        # Execute graph with input files
        result = await graph.ainvoke({
            "files": file_data,
            "documents": [],
            "validation": {"missing_documents": [], "discrepancies": []},
            "claim_decision": {"status": "pending", "reason": ""}
        })
        
        logger.info(f"✅ Processing complete: {result['claim_decision']['status']}")
        
        return ClaimProcessingResult(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error processing claim: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    # Return no content to avoid 404 logs for the browser's favicon request
    return Response(status_code=204)

@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "service": "claim-processor",
        "components": {
            "api": "operational",
            "agents": "ready",
            "llm": "connected"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)