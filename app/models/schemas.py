"""
Pydantic models for claim processing data structures
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date

# Document type models
class BillDocument(BaseModel):
    """Medical bill document structure"""
    type: str = "bill"
    hospital_name: Optional[str] = None
    total_amount: Optional[float] = None
    date_of_service: Optional[str] = None
    bill_number: Optional[str] = None
    items: Optional[List[Dict[str, Any]]] = []

class DischargeSummaryDocument(BaseModel):
    """Discharge summary document structure"""
    type: str = "discharge_summary"
    patient_name: Optional[str] = None
    diagnosis: Optional[str] = None
    admission_date: Optional[str] = None
    discharge_date: Optional[str] = None
    treatment: Optional[str] = None
    doctor_name: Optional[str] = None

class IDCardDocument(BaseModel):
    """Insurance ID card document structure"""
    type: str = "id_card"
    policy_number: Optional[str] = None
    insured_name: Optional[str] = None
    validity: Optional[str] = None
    insurance_company: Optional[str] = None

class GenericDocument(BaseModel):
    """Generic document for unclassified types"""
    type: str
    extracted_data: Optional[Dict[str, Any]] = {}

# Validation models
class ValidationResult(BaseModel):
    """Validation result structure"""
    missing_documents: List[str] = Field(default_factory=list)
    discrepancies: List[str] = Field(default_factory=list)

class ClaimDecision(BaseModel):
    """Final claim decision structure"""
    status: str = Field(..., description="approved, rejected, or pending")
    reason: str = Field(..., description="Explanation for the decision")
    confidence_score: Optional[float] = None

# Main output model
class ClaimProcessingResult(BaseModel):
    """Complete claim processing result"""
    documents: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Extracted and structured document data"
    )
    validation: ValidationResult = Field(
        default_factory=lambda: ValidationResult(),
        description="Validation results"
    )
    claim_decision: ClaimDecision = Field(
        ...,
        description="Final claim approval/rejection decision"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "documents": [
                    {
                        "type": "bill",
                        "hospital_name": "ABC Hospital",
                        "total_amount": 12500,
                        "date_of_service": "2024-04-10"
                    },
                    {
                        "type": "discharge_summary",
                        "patient_name": "John Doe",
                        "diagnosis": "Fracture",
                        "admission_date": "2024-04-01",
                        "discharge_date": "2024-04-10"
                    }
                ],
                "validation": {
                    "missing_documents": [],
                    "discrepancies": []
                },
                "claim_decision": {
                    "status": "approved",
                    "reason": "All required documents present and data is consistent"
                }
            }
        }