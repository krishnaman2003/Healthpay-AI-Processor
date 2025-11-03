"""
Bill processing agent - extracts structured data from medical bills
"""
import logging
from typing import Dict, Any
from app.utils.gemini_client import get_gemini_client
from app.utils.prompts import EXTRACT_BILL_DATA_PROMPT
from app.models.graph_state import ClaimProcessingState

logger = logging.getLogger(__name__)

async def process_bill_documents(state: ClaimProcessingState) -> Dict[str, Any]:
    """
    Agent Node: Process bill documents and extract structured data
    
    Args:
        state: Current graph state with classified documents
        
    Returns:
        Updated state with structured bill data
    """
    logger.info("💰 Processing bill documents")
    
    gemini_client = get_gemini_client()
    raw_texts = state.get("raw_texts", [])
    documents = state.get("documents", [])
    errors = state.get("errors", [])
    
    # Filter bill documents
    bill_docs = [doc for doc in raw_texts if doc.get("doc_type") == "bill"]
    
    for doc in bill_docs:
        try:
            # Prepare extraction prompt
            prompt = EXTRACT_BILL_DATA_PROMPT.format(text=doc["text"])
            
            # Extract structured data using Gemini
            extracted_data = await gemini_client.generate_json(prompt)
            
            # Add document type and source info
            bill_data = {
                "type": "bill",
                "source_file": doc["filename"],
                **extracted_data
            }
            
            documents.append(bill_data)
            
            logger.info(
                f"✅ Processed bill: {doc['filename']} - "
                f"Hospital: {extracted_data.get('hospital_name')}, "
                f"Amount: {extracted_data.get('total_amount')}"
            )
            
        except Exception as e:
            error_msg = f"Failed to process bill {doc['filename']}: {str(e)}"
            errors.append(error_msg)
            logger.error(f"❌ {error_msg}")
    
    logger.info(f"✅ Processed {len(bill_docs)} bill document(s)")
    
    return {
        **state,
        "documents": documents,
        "errors": errors
    }