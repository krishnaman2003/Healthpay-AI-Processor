"""
Document classification agent - classifies documents using Gemini LLM
"""
import logging
from typing import Dict, Any
from app.utils.gemini_client import get_gemini_client
from app.utils.prompts import CLASSIFY_DOCUMENT_PROMPT
from app.models.graph_state import ClaimProcessingState

logger = logging.getLogger(__name__)

async def classify_documents(state: ClaimProcessingState) -> Dict[str, Any]:
    """
    Agent Node: Classify each document using Gemini LLM
    
    Args:
        state: Current graph state with raw extracted texts
        
    Returns:
        Updated state with classified documents
    """
    logger.info("🏷️  Starting document classification")
    
    gemini_client = get_gemini_client()
    raw_texts = state.get("raw_texts", [])
    errors = state.get("errors", [])
    
    for doc in raw_texts:
        try:
            # Prepare classification prompt
            prompt = CLASSIFY_DOCUMENT_PROMPT.format(
                filename=doc["filename"],
                text=doc["text"][:2000]  # Use first 2000 chars for classification
            )
            
            # Get classification from Gemini
            result = await gemini_client.generate_json(prompt)
            
            # Update document with classification
            doc["doc_type"] = result.get("document_type", "other")
            doc["confidence"] = result.get("confidence", 0.0)
            doc["classification_reasoning"] = result.get("reasoning", "")
            
            logger.info(
                f"✅ Classified {doc['filename']} as '{doc['doc_type']}' "
                f"(confidence: {doc['confidence']})"
            )
            
        except Exception as e:
            error_msg = f"Failed to classify {doc['filename']}: {str(e)}"
            errors.append(error_msg)
            logger.error(f"❌ {error_msg}")
            doc["doc_type"] = "other"  # Default classification
    
    return {
        **state,
        "raw_texts": raw_texts,
        "errors": errors
    }