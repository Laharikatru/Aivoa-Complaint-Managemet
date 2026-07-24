from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db
from agent.graph import run_full_analysis
from agent import tools as agent_tools

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


def _candidates_for(db: Session, complaint: models.Complaint) -> list[dict]:
    others = (
        db.query(models.Complaint)
        .filter(
            models.Complaint.product_name == complaint.product_name,
            models.Complaint.id != complaint.id,
        )
        .order_by(models.Complaint.date_received.desc())
        .limit(10)
        .all()
    )
    return [{"id": o.id, "description": o.description} for o in others]


@router.post("/run", response_model=schemas.AnalyzeResponse)
def run_analysis(payload: schemas.AnalyzeRequest, db: Session = Depends(get_db)):
    """Run the full LangGraph pipeline (all 6 AI tools, in sequence) on a complaint
    and persist every derived field back to the row."""
    complaint = db.get(models.Complaint, payload.complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    structured_fields = {
        "product_name": complaint.product_name,
        "batch_lot_number": complaint.batch_lot_number,
        "manufacturing_site": complaint.manufacturing_site,
        "date_received": complaint.date_received.isoformat() if complaint.date_received else None,
    }
    candidates = _candidates_for(db, complaint)

    result = run_full_analysis(
        complaint_id=complaint.id,
        description=complaint.description,
        product_name=complaint.product_name,
        category=complaint.category.value if hasattr(complaint.category, "value") else complaint.category,
        structured_fields=structured_fields,
        candidates=candidates,
    )

    complaint.ai_summary = result.get("summary")
    complaint.ai_completeness_score = result.get("completeness_score")
    complaint.ai_missing_fields = ", ".join(result.get("missing_fields") or [])
    complaint.ai_risk_classification = result.get("risk_classification")
    complaint.ai_risk_rationale = result.get("risk_rationale")
    complaint.ai_duplicate_of_id = result.get("duplicate_of_id") if result.get("is_duplicate") else None
    complaint.ai_duplicate_confidence = result.get("duplicate_confidence")

    hypotheses = result.get("root_cause_hypotheses") or []
    complaint.ai_root_cause_suggestion = "\n".join(f"- {h}" for h in hypotheses) if hypotheses else None

    corrective = result.get("corrective_action")
    preventive = result.get("preventive_action")
    if corrective or preventive:
        complaint.ai_capa_suggestion = (
            f"Corrective: {corrective or 'n/a'}\nPreventive: {preventive or 'n/a'}"
        )

    # Severity gets auto-set from AI risk classification if the rep didn't set one manually
    if not complaint.severity and complaint.ai_risk_classification in ("high", "critical"):
        complaint.severity = "major" if complaint.ai_risk_classification == "high" else "critical"

    db.commit()
    db.refresh(complaint)

    return schemas.AnalyzeResponse(
        complaint_id=complaint.id,
        tool_calls=result.get("tool_calls", []),
        complaint=complaint,
    )


# --- Individual tool endpoints, useful for the demo video / ad-hoc testing ---

@router.post("/tools/summarize/{complaint_id}")
def tool_summarize(complaint_id: str, db: Session = Depends(get_db)):
    complaint = _get_or_404(db, complaint_id)
    return agent_tools.summarize_complaint(complaint.description)


@router.post("/tools/completeness/{complaint_id}")
def tool_completeness(complaint_id: str, db: Session = Depends(get_db)):
    complaint = _get_or_404(db, complaint_id)
    fields = {
        "product_name": complaint.product_name,
        "batch_lot_number": complaint.batch_lot_number,
        "manufacturing_site": complaint.manufacturing_site,
    }
    return agent_tools.check_completeness(complaint.description, fields)


@router.post("/tools/risk/{complaint_id}")
def tool_risk(complaint_id: str, db: Session = Depends(get_db)):
    complaint = _get_or_404(db, complaint_id)
    category = complaint.category.value if hasattr(complaint.category, "value") else complaint.category
    return agent_tools.classify_risk(complaint.description, category)


@router.post("/tools/duplicate/{complaint_id}")
def tool_duplicate(complaint_id: str, db: Session = Depends(get_db)):
    complaint = _get_or_404(db, complaint_id)
    candidates = _candidates_for(db, complaint)
    return agent_tools.detect_duplicate(complaint.description, complaint.product_name, candidates)


@router.post("/tools/root-cause/{complaint_id}")
def tool_root_cause(complaint_id: str, db: Session = Depends(get_db)):
    complaint = _get_or_404(db, complaint_id)
    category = complaint.category.value if hasattr(complaint.category, "value") else complaint.category
    return agent_tools.recommend_root_cause(complaint.description, category)


@router.post("/tools/capa/{complaint_id}")
def tool_capa(complaint_id: str, db: Session = Depends(get_db)):
    complaint = _get_or_404(db, complaint_id)
    hypotheses_result = agent_tools.recommend_root_cause(
        complaint.description,
        complaint.category.value if hasattr(complaint.category, "value") else complaint.category,
    )
    return agent_tools.recommend_capa(
        complaint.description,
        complaint.ai_risk_classification or "unknown",
        hypotheses_result.get("hypotheses", []),
    )


def _get_or_404(db: Session, complaint_id: str) -> models.Complaint:
    complaint = db.get(models.Complaint, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint
