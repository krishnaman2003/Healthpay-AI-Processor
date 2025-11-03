"""
LangGraph state definitions for claim processing workflow
"""
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph

class ClaimProcessingState(TypedDict):
    """
    State object passed through the agent workflow
    Contains all data needed for multi-agent processing
    """
    # Input files
    files: List[Dict[str, Any]]  # List of {filename, content}
    
    # Classified and extracted documents
    documents: List[Dict[str, Any]]
    
    # Validation results
    validation: Dict[str, Any]  # {missing_documents: [], discrepancies: []}
    
    # Final decision
    claim_decision: Dict[str, str]  # {status: str, reason: str}
    
    # Intermediate processing data
    raw_texts: List[Dict[str, str]]  # {filename, text, doc_type}
    
    # Error tracking
    errors: List[str]