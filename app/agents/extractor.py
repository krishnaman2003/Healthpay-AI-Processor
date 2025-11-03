"""
Text extraction agent - extracts text from PDF files
"""
import logging
from typing import Dict, Any
from app.utils.pdf_handler import PDFHandler
from app.models.graph_state import ClaimProcessingState

logger = logging.getLogger(__name__)

async def extract_text_from_pdfs(state: ClaimProcessingState) -> Dict[str, Any]:
    """
    Agent Node: Extract text from uploaded PDF files
    
    Args:
        state: Current graph state with uploaded files
        
    Returns:
        Updated state with extracted raw texts
    """
    logger.info("📄 Starting text extraction from PDFs")
    
    pdf_handler = PDFHandler()
    raw_texts = []
    errors = state.get("errors", [])
    
    for file_data in state["files"]:
        filename = file_data["filename"]
        content = file_data["content"]
        
        try:
            # Extract text from PDF
            text = pdf_handler.extract_text_from_bytes(content)
            
            if text:
                raw_texts.append({
                    "filename": filename,
                    "text": text,
                    "doc_type": "unknown"  # Will be classified in next step
                })
                logger.info(f"✅ Extracted text from {filename}: {len(text)} chars")
            else:
                error_msg = f"No text extracted from {filename}"
                errors.append(error_msg)
                logger.warning(f"⚠️  {error_msg}")
                
        except Exception as e:
            error_msg = f"Failed to extract text from {filename}: {str(e)}"
            errors.append(error_msg)
            logger.error(f"❌ {error_msg}")
    
    return {
        **state,
        "raw_texts": raw_texts,
        "errors": errors
    }