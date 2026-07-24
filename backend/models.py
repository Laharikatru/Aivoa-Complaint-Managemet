import uuid
import datetime as dt
import enum

from sqlalchemy import Column, String, DateTime, Text, Enum, Float, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


def gen_uuid():
    return str(uuid.uuid4())


class ComplaintChannel(str, enum.Enum):
    email = "email"
    phone = "phone"
    portal = "portal"
    letter = "letter"
    field_rep = "field_rep"


class ComplaintCategory(str, enum.Enum):
    product_quality = "product_quality"
    packaging_labeling = "packaging_labeling"
    adverse_event = "adverse_event"
    counterfeit_suspect = "counterfeit_suspect"
    delivery_logistics = "delivery_logistics"
    other = "other"


class ComplaintSeverity(str, enum.Enum):
    minor = "minor"
    major = "major"
    critical = "critical"


class ComplaintStatus(str, enum.Enum):
    new = "new"
    under_investigation = "under_investigation"
    capa_assigned = "capa_assigned"
    closed = "closed"


class IntakeStatus(str, enum.Enum):
    pending_triage = "pending_triage"
    ready_to_commit = "ready_to_commit"
    committed = "committed"


class Complaint(Base):
    """A customer complaint against a manufactured pharmaceutical product (API/FDF),
    modeled as the Customer Complaint module of a Quality Management System (QMS)."""

    __tablename__ = "complaints"

    id = Column(String, primary_key=True, default=gen_uuid)

    # --- Copilot-driven intake fields (match the reference "Log Customer Complaint" form) ---
    complaint_source = Column(String, nullable=True)  # e.g. Pharmacy, Distributor, Patient
    product_strength = Column(String, nullable=True)  # e.g. "500 mg"
    affected_quantity = Column(String, nullable=True)  # e.g. "48 capsules"
    manufacturing_date = Column(String, nullable=True)  # kept as free text, e.g. "March 2026"
    expiry_date = Column(String, nullable=True)
    originating_site_block = Column(String, nullable=True)
    impacted_npm = Column(String, nullable=True)  # Impacted Non-Product Materials
    complaint_category_label = Column(String, nullable=True)  # free-text, e.g. "Foreign Matter Contamination"
    structured_defect_summary = Column(Text, nullable=True)  # AI-synthesized formal QMS description

    severity_suggested = Column(String, nullable=True)  # AI copilot risk assessment
    suggested_next_action = Column(Text, nullable=True)
    initial_risk_assessment = Column(Text, nullable=True)

    intake_status = Column(Enum(IntakeStatus), nullable=False, default=IntakeStatus.pending_triage)
    raw_intake_transcript = Column(Text, nullable=True)  # full chat/paste transcript that built this record

    # --- Original intake fields (structured form fallback / legacy) ---
    product_name = Column(String, nullable=True)
    batch_lot_number = Column(String, nullable=True)
    manufacturing_site = Column(String, nullable=True)
    customer_name = Column(String, nullable=True)
    customer_contact = Column(String, nullable=True)
    channel = Column(Enum(ComplaintChannel), nullable=False, default=ComplaintChannel.email)
    category = Column(Enum(ComplaintCategory), nullable=False, default=ComplaintCategory.other)
    severity = Column(Enum(ComplaintSeverity), nullable=True)  # may be set by AI risk classification
    status = Column(Enum(ComplaintStatus), nullable=False, default=ComplaintStatus.new)

    date_received = Column(DateTime, default=dt.datetime.utcnow)
    description = Column(Text, nullable=True)  # raw complaint narrative

    # AI-derived fields, populated by the LangGraph agent's tools
    ai_summary = Column(Text, nullable=True)
    ai_completeness_score = Column(Float, nullable=True)  # 0-100
    ai_missing_fields = Column(Text, nullable=True)  # comma separated
    ai_risk_classification = Column(String, nullable=True)  # low / medium / high / critical
    ai_risk_rationale = Column(Text, nullable=True)
    ai_root_cause_suggestion = Column(Text, nullable=True)
    ai_capa_suggestion = Column(Text, nullable=True)
    ai_duplicate_of_id = Column(String, ForeignKey("complaints.id"), nullable=True)
    ai_duplicate_confidence = Column(Float, nullable=True)  # 0-1

    created_at = Column(DateTime, default=dt.datetime.utcnow)
    updated_at = Column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)

    duplicate_of = relationship("Complaint", remote_side=[id])
