"""
Discharge summary processing agent - extracts structured data from discharge summaries
"""
import logging
from typing import Dict, Any
from app.utils.gemini_client import get_gemini_client
from app.utils.prompts import EXTRACT_DISCHARGE_DATA_PROMPT
from app.models.graph_state import ClaimProcessingState

logger = logging.getLogger(__name__)

async def process_discharge_documents(state: ClaimProcessingState) -> Dict[str, Any]:
    """
    Agent Node: Process discharge summary documents and extract structured data
    
    Args:
        state: Current graph state with classified documents
        
    Returns:
        Updated state with structured discharge summary data
    """
    logger.info("🏥 Processing discharge summary documents")
    
    gemini_client = get_gemini_client()
    raw_texts = state.get("raw_texts", [])
    documents = state.get("documents", [])
    errors = state.get("errors", [])
    
    # Filter discharge summary documents
    discharge_docs = [doc for doc in raw_texts if doc.get("doc_type") == "discharge_summary"]
    
    for doc in discharge_docs:
        try:
            # Prepare extraction prompt
            prompt = EXTRACT_DISCHARGE_DATA_PROMPT.format(text=doc["text"])
            
            # Extract structured data using Gemini
            extracted_data = await gemini_client.generate_json(prompt)
            
            # Add document type and source info
            discharge_data = {
                "type": "discharge_summary",
                "source_file": doc["filename"],
                **extracted_data
            }
            
            documents.append(discharge_data)
            
            logger.info(
                f"✅ Processed discharge summary: {doc['filename']} - "
                f"Patient: {extracted_data.get('patient_name')}, "
                f"Diagnosis: {extracted_data.get('diagnosis')}"
            )
            
        except Exception as e:
            error_msg = f"Failed to process discharge summary {doc['filename']}: {str(e)}"
            errors.append(error_msg)
            logger.error(f"❌ {error_msg}")
    
    logger.info(f"✅ Processed {len(discharge_docs)} discharge summary document(s)")
    
    return {
        **state,
        "documents": documents,
        "errors": errors
    }