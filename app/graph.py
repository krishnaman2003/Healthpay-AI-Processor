"""
LangGraph workflow orchestration for multi-agent claim processing
"""
from langgraph.graph import StateGraph, END
from typing import Dict, Any
import logging

from app.models.graph_state import ClaimProcessingState
from app.agents.classifier import classify_documents
from app.agents.extractor import extract_text_from_pdfs
from app.agents.bill_agent import process_bill_documents
from app.agents.discharge_agent import process_discharge_documents
from app.agents.id_card_agent import process_id_card_documents
from app.agents.validator import validate_and_decide

logger = logging.getLogger(__name__)

def create_claim_processing_graph():
    """
    Creates the LangGraph workflow for claim processing
    
    Graph flow:
    1. Extract text from PDFs (extractor agent)
    2. Classify documents (classifier agent)
    3. Process documents in parallel by type (specialized agents)
    4. Validate and make decision (validator agent)
    """
    
    # Initialize the state graph
    workflow = StateGraph(ClaimProcessingState)
    
    # Add nodes (agents) to the graph
    workflow.add_node("extract_text", extract_text_from_pdfs)
    workflow.add_node("classify_documents", classify_documents)
    workflow.add_node("process_bills", process_bill_documents)
    workflow.add_node("process_discharge", process_discharge_documents)
    workflow.add_node("process_id_cards", process_id_card_documents)
    workflow.add_node("validate_and_decide", validate_and_decide)
    
    # Define the workflow edges
    workflow.set_entry_point("extract_text")
    
    # Sequential flow: extract -> classify -> process -> validate
    workflow.add_edge("extract_text", "classify_documents")
    workflow.add_edge("classify_documents", "process_bills")
    workflow.add_edge("process_bills", "process_discharge")
    workflow.add_edge("process_discharge", "process_id_cards")
    workflow.add_edge("process_id_cards", "validate_and_decide")
    workflow.add_edge("validate_and_decide", END)
    
    # Compile the graph
    app = workflow.compile()
    
    logger.info("✅ LangGraph workflow compiled successfully")
    return app

# Graph visualization helper
def visualize_graph():
    """Generate mermaid diagram of the workflow"""
    graph = create_claim_processing_graph()
    try:
        return graph.get_graph().draw_mermaid()
    except Exception as e:
        logger.warning(f"Could not generate graph visualization: {e}")
        return None