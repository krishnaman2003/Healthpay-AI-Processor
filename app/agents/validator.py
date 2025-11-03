"""
Validation and decision agent - validates data and makes claim decision
"""
import logging
import json
from typing import Dict, Any
from app.utils.gemini_client import get_gemini_client
from app.utils.prompts import VALIDATE_AND_DECIDE_PROMPT
from app.models.graph_state import ClaimProcessingState

logger = logging.getLogger(__name__)

async def validate_and_decide(state: ClaimProcessingState) -> Dict[str, Any]:
    """
    Agent Node: Validate extracted data and make final claim decision
    
    Args:
        state: Current graph state with all processed documents
        
    Returns:
        Updated state with validation results and claim decision
    """
    logger.info("✅ Starting validation and decision process")
    
    gemini_client = get_gemini_client()
    documents = state.get("documents", [])
    errors = state.get("errors", [])
    
    try:
        # Prepare documents summary for validation
        documents_json = json.dumps(documents, indent=2)
        
        # Prepare validation prompt
        prompt = VALIDATE_AND_DECIDE_PROMPT.format(documents=documents_json)
        
        # Get validation and decision from Gemini
        result = await gemini_client.generate_json(prompt)
        
        # Extract validation results
        validation = {
            "missing_documents": result.get("missing_documents", []),
            "discrepancies": result.get("discrepancies", [])
        }
        
        # Extract claim decision
        claim_decision = result.get("claim_decision", {
            "status": "rejected",
            "reason": "Validation failed - unable to process claim",
            "confidence_score": 0.0
        })
        
        # Add any processing errors to discrepancies
        if errors:
            validation["discrepancies"].extend([f"Processing error: {e}" for e in errors])
        
        # Log decision
        logger.info(
            f"🎯 Claim Decision: {claim_decision['status'].upper()} - "
            f"{claim_decision['reason']}"
        )
        
        # Log validation issues
        if validation["missing_documents"]:
            logger.warning(f"⚠️  Missing documents: {validation['missing_documents']}")
        if validation["discrepancies"]:
            logger.warning(f"⚠️  Discrepancies found: {validation['discrepancies']}")
        
        return {
            **state,
            "validation": validation,
            "claim_decision": claim_decision
        }
        
    except Exception as e:
        error_msg = f"Validation failed: {str(e)}"
        logger.error(f"❌ {error_msg}")
        
        # Return rejection decision on validation failure
        return {
            **state,
            "validation": {
                "missing_documents": [],
                "discrepancies": [error_msg]
            },
            "claim_decision": {
                "status": "rejected",
                "reason": f"System error during validation: {str(e)}",
                "confidence_score": 0.0
            }
        }