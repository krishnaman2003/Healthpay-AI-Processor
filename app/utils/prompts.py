"""
Prompt templates for Gemini LLM interactions
These prompts were crafted using Claude and iteratively refined
"""

# Document classification prompt
CLASSIFY_DOCUMENT_PROMPT = """You are a medical document classification expert. 

Analyze the following document text and filename, then classify it into ONE of these types:
- "bill": Medical bills, invoices, or payment receipts
- "discharge_summary": Hospital discharge summaries or medical reports
- "id_card": Insurance ID cards or policy documents
- "prescription": Medical prescriptions
- "lab_report": Laboratory test results
- "other": Any other document type

Filename: {filename}

Document Text:
{text}

Respond ONLY with valid JSON in this exact format:
{{
  "document_type": "one of the types above",
  "confidence": 0.95,
  "reasoning": "brief explanation"
}}"""

# Bill extraction prompt
EXTRACT_BILL_DATA_PROMPT = """You are a medical billing data extraction expert.

Extract structured information from this medical bill document.

Document Text:
{text}

Extract and return the following information in JSON format:
- hospital_name: Name of the hospital or medical facility
- total_amount: Total bill amount (numeric value only)
- date_of_service: Date of service (YYYY-MM-DD format)
- bill_number: Bill or invoice number
- items: List of billable items if available

Respond ONLY with valid JSON:
{{
  "hospital_name": "extracted name or null",
  "total_amount": numeric_value_or_null,
  "date_of_service": "YYYY-MM-DD or null",
  "bill_number": "extracted number or null",
  "items": []
}}

If any field cannot be found, use null. Be precise with dates and amounts."""

# Discharge summary extraction prompt
EXTRACT_DISCHARGE_DATA_PROMPT = """You are a medical records data extraction expert.

Extract structured information from this discharge summary document.

Document Text:
{text}

Extract and return the following information in JSON format:
- patient_name: Patient's full name
- diagnosis: Primary diagnosis or medical condition
- admission_date: Hospital admission date (YYYY-MM-DD format)
- discharge_date: Hospital discharge date (YYYY-MM-DD format)
- treatment: Treatment provided (brief summary)
- doctor_name: Attending physician's name

Respond ONLY with valid JSON:
{{
  "patient_name": "extracted name or null",
  "diagnosis": "extracted diagnosis or null",
  "admission_date": "YYYY-MM-DD or null",
  "discharge_date": "YYYY-MM-DD or null",
  "treatment": "treatment summary or null",
  "doctor_name": "doctor name or null"
}}

If any field cannot be found, use null. Be precise with dates and medical terms."""

# ID card extraction prompt
EXTRACT_ID_CARD_DATA_PROMPT = """You are an insurance document data extraction expert.

Extract structured information from this insurance ID card or policy document.

Document Text:
{text}

Extract and return the following information in JSON format:
- policy_number: Insurance policy number
- insured_name: Name of the insured person
- validity: Policy validity period or expiration date
- insurance_company: Name of the insurance company

Respond ONLY with valid JSON:
{{
  "policy_number": "extracted number or null",
  "insured_name": "extracted name or null",
  "validity": "validity period or null",
  "insurance_company": "company name or null"
}}

If any field cannot be found, use null."""

# Validation and decision prompt
VALIDATE_AND_DECIDE_PROMPT = """You are a medical insurance claim validation expert.

Review the extracted claim documents and make a decision on claim approval.

Extracted Documents:
{documents}

Analyze the claim for:
1. Missing Documents: Check if essential documents (bill, discharge summary, ID card) are present
2. Data Discrepancies: Check for inconsistencies in:
   - Patient names across documents
   - Date ranges (admission/discharge dates should match service dates)
   - Amounts and diagnosis codes
3. Claim Decision: Approve or reject based on completeness and consistency

Respond ONLY with valid JSON:
{{
  "missing_documents": ["list of missing document types"],
  "discrepancies": ["list of specific discrepancies found"],
  "claim_decision": {{
    "status": "approved or rejected",
    "reason": "detailed explanation for the decision",
    "confidence_score": 0.95
  }}
}}

Rules for approval:
- Approve if: All essential documents present, no major discrepancies, patient info matches
- Reject if: Missing critical documents, major data inconsistencies, suspicious patterns"""