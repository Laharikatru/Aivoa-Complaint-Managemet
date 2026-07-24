import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db
from agent.copilot_graph import run_copilot_turn
from agent.copilot_tools import FORM_FIELDS

router = APIRouter(prefix="/api/copilot", tags=["copilot"])

# session_id -> { complaint_id, known_fields } — in-memory for this demo; swap for
# Redis/DB-backed sessions for anything that needs to survive a restart.
_SESSIONS: dict[str, dict] = {}


def _known_fields_from_complaint(c: models.Complaint) -> dict:
    return {f: getattr(c, f, None) for f in FORM_FIELDS}


@router.post("/message", response_model=schemas.CopilotMessageOut)
def copilot_message(payload: schemas.CopilotMessageIn, db: Session = Depends(get_db)):
    session_id = payload.session_id or str(uuid.uuid4())
    session = _SESSIONS.get(session_id)

    if not session:
        # First message in this session: create a new pending-triage complaint record.
        complaint = models.Complaint(intake_status=models.IntakeStatus.pending_triage)
        db.add(complaint)
        db.commit()
        db.refresh(complaint)
        session = {"complaint_id": complaint.id, "transcript": ""}
        _SESSIONS[session_id] = session
    else:
        complaint = db.get(models.Complaint, session["complaint_id"])
        if not complaint:
            raise HTTPException(status_code=404, detail="Session's complaint record no longer exists")

    known_fields = _known_fields_from_complaint(complaint)
    result = run_copilot_turn(known_fields, payload.message, payload.document_text)

    for field, value in result.get("updated_fields", {}).items():
        if field in FORM_FIELDS and value:
            setattr(complaint, field, value)

    if result.get("severity_suggested"):
        complaint.severity_suggested = result["severity_suggested"]
    if result.get("suggested_next_action"):
        complaint.suggested_next_action = result["suggested_next_action"]
    if result.get("initial_risk_assessment"):
        complaint.initial_risk_assessment = result["initial_risk_assessment"]

    # Ready to commit once the core identifying fields are known
    core_fields = ["product_name", "batch_lot_number", "customer_name"]
    if all(getattr(complaint, f, None) for f in core_fields):
        complaint.intake_status = models.IntakeStatus.ready_to_commit

    session["transcript"] += f"\nUser: {payload.message}\nCopilot: {result.get('reply', '')}"
    complaint.raw_intake_transcript = session["transcript"]

    db.commit()
    db.refresh(complaint)

    return schemas.CopilotMessageOut(
        reply=result.get("reply", "Got it."),
        session_id=session_id,
        complaint=complaint,
    )


@router.post("/upload")
async def copilot_upload(
    session_id: str = None,
    file: UploadFile = File(...),
):
    """Accepts a PDF (or plain text file), extracts its text, and returns it so the
    frontend can pass it along as `document_text` in the next /message call. Kept as a
    separate step (rather than doing DB writes here) so the extraction result can be
    shown to the user before it's committed to the form, same as the reference demo."""
    contents = await file.read()

    if file.filename.lower().endswith(".pdf"):
        try:
            from pypdf import PdfReader
            import io

            reader = PdfReader(io.BytesIO(contents))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"Could not read PDF: {e}")
    else:
        text = contents.decode("utf-8", errors="ignore")

    return {"filename": file.filename, "document_text": text}


@router.post("/commit/{complaint_id}", response_model=schemas.ComplaintOut)
def commit_complaint(complaint_id: str, db: Session = Depends(get_db)):
    """Finalize intake: locks the record as committed so it enters the normal
    Dashboard / investigation workflow. Requires the core identifying fields to
    already be known (mirrors the 'Ready to Commit' badge state)."""
    complaint = db.get(models.Complaint, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    core_fields = ["product_name", "batch_lot_number", "customer_name"]
    missing = [f for f in core_fields if not getattr(complaint, f, None)]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot commit yet — missing required fields: {', '.join(missing)}",
        )

    complaint.intake_status = models.IntakeStatus.committed
    db.commit()
    db.refresh(complaint)
    return complaint