from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(prefix="/api/complaints", tags=["complaints"])


@router.get("/", response_model=List[schemas.ComplaintOut])
def list_complaints(
    status: Optional[str] = None,
    product_name: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(models.Complaint)
    if status:
        q = q.filter(models.Complaint.status == status)
    if product_name:
        q = q.filter(models.Complaint.product_name == product_name)
    return q.order_by(models.Complaint.date_received.desc()).all()


@router.post("/", response_model=schemas.ComplaintOut, status_code=201)
def create_complaint(payload: schemas.ComplaintCreate, db: Session = Depends(get_db)):
    complaint = models.Complaint(**payload.model_dump())
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint


@router.get("/{complaint_id}", response_model=schemas.ComplaintOut)
def get_complaint(complaint_id: str, db: Session = Depends(get_db)):
    complaint = db.get(models.Complaint, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint


@router.patch("/{complaint_id}/status", response_model=schemas.ComplaintOut)
def update_status(complaint_id: str, payload: schemas.ComplaintStatusUpdate, db: Session = Depends(get_db)):
    complaint = db.get(models.Complaint, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    complaint.status = payload.status
    db.commit()
    db.refresh(complaint)
    return complaint


@router.delete("/{complaint_id}", status_code=204)
def delete_complaint(complaint_id: str, db: Session = Depends(get_db)):
    complaint = db.get(models.Complaint, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    db.delete(complaint)
    db.commit()
