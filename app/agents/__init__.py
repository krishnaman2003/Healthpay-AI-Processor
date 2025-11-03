"""
Agent modules for document processing
"""
from app.agents.classifier import classify_documents
from app.agents.extractor import extract_text_from_pdfs
from app.agents.bill_agent import process_bill_documents
from app.agents.discharge_agent import process_discharge_documents
from app.agents.id_card_agent import process_id_card_documents
from app.agents.validator import validate_and_decide

__all__ = [
    "classify_documents",
    "extract_text_from_pdfs",
    "process_bill_documents",
    "process_discharge_documents",
    "process_id_card_documents",
    "validate_and_decide",
]
