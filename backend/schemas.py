import datetime as dt
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ComplaintBase(BaseModel):
    product_name: Optional[str] = None
    batch_lot_number: Optional[str] = None
    manufacturing_site: Optional[str] = None
    customer_name: Optional[str] = None
    customer_contact: Optional[str] = None
    channel: str = "email"
    category: str = "other"
    severity: Optional[str] = None
    description: Optional[str] = None


class ComplaintCreate(ComplaintBase):
    pass


class ComplaintOut(ComplaintBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    status: str
    date_received: dt.datetime

    # copilot intake fields
    complaint_source: Optional[str] = None
    product_strength: Optional[str] = None
    affected_quantity: Optional[str] = None
    manufacturing_date: Optional[str] = None
    expiry_date: Optional[str] = None
    originating_site_block: Optional[str] = None
    impacted_npm: Optional[str] = None
    complaint_category_label: Optional[str] = None
    structured_defect_summary: Optional[str] = None
    severity_suggested: Optional[str] = None
    suggested_next_action: Optional[str] = None
    initial_risk_assessment: Optional[str] = None
    intake_status: str = "pending_triage"

    ai_summary: Optional[str] = None
    ai_completeness_score: Optional[float] = None
    ai_missing_fields: Optional[str] = None
    ai_risk_classification: Optional[str] = None
    ai_risk_rationale: Optional[str] = None
    ai_root_cause_suggestion: Optional[str] = None
    ai_capa_suggestion: Optional[str] = None
    ai_duplicate_of_id: Optional[str] = None
    ai_duplicate_confidence: Optional[float] = None
    created_at: dt.datetime
    updated_at: dt.datetime


class CopilotMessageIn(BaseModel):
    message: str
    session_id: Optional[str] = None
    document_text: Optional[str] = None  # extracted text from a pasted/uploaded PDF


class CopilotMessageOut(BaseModel):
    reply: str
    session_id: str
    complaint: ComplaintOut


class ComplaintStatusUpdate(BaseModel):
    status: str


class AnalyzeRequest(BaseModel):
    complaint_id: str
    # Which AI tools to run; defaults to all if omitted
    tools: Optional[list[str]] = None


class AnalyzeResponse(BaseModel):
    complaint_id: str
    tool_calls: list[str]
    complaint: ComplaintOut
