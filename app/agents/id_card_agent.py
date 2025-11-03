"""
ID card processing agent - extracts structured data from insurance ID cards
"""
import logging
from typing import Dict, Any
from app.utils.gemini_client import get_gemini_client
from app.utils.prompts import EXTRACT_ID_CARD_DATA_PROMPT
from app.models.graph_state import ClaimProcessingState

logger = logging.getLogger(__name__)

async def process_id_card_documents(state: ClaimProcessingState) -> Dict[str, Any]:
    """
    Agent Node: Process ID card documents and extract structured data
    
    Args:
        state: Current graph state with classified documents
        
    Returns:
        Updated state with structured ID card data
    """
    logger.info("🆔 Processing ID card documents")
    
    gemini_client = get_gemini_client()
    raw_texts = state.get("raw_texts", [])
    documents = state.get("documents", [])
    errors = state.get("errors", [])
    
    # Filter ID card documents
    id_card_docs = [doc for doc in raw_texts if doc.get("doc_type") == "id_card"]
    
    for doc in id_card_docs:
        try:
            # Prepare extraction prompt
            prompt = EXTRACT_ID_CARD_DATA_PROMPT.format(text=doc["text"])
            
            # Extract structured data using Gemini
            extracted_data = await gemini_client.generate_json(prompt)
            
            # Add document type and source info
            id_card_data = {
                "type": "id_card",
                "source_file": doc["filename"],
                **extracted_data
            }
            
            documents.append(id_card_data)
            
            logger.info(
                f"✅ Processed ID card: {doc['filename']} - "
                f"Insured: {extracted_data.get('insured_name')}, "
                f"Policy: {extracted_data.get('policy_number')}"
            )
            
        except Exception as e:
            error_msg = f"Failed to process ID card {doc['filename']}: {str(e)}"
            errors.append(error_msg)
            logger.error(f"❌ {error_msg}")
    
    logger.info(f"✅ Processed {len(id_card_docs)} ID card document(s)")
    
    return {
        **state,
        "documents": documents,
        "errors": errors
    }