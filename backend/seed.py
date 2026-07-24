"""Run with `python seed.py` after tables exist to add demo complaints for the demo video."""

from database import SessionLocal, Base, engine
import models

Base.metadata.create_all(bind=engine)

DEMO_COMPLAINTS = [
    dict(
        product_name="Metforglide 500mg Tablets",
        product_strength="500 mg",
        batch_lot_number="MFG-2231-B",
        manufacturing_site="Plant 3, Vizag",
        originating_site_block="Plant 3, Vizag",
        complaint_source="Pharmacy",
        customer_name="Sunrise Pharmacy",
        customer_contact="sunrise.pharmacy@example.com",
        channel="email",
        category="product_quality",
        complaint_category_label="Product Defect - Discoloration",
        intake_status="committed",
        description=(
            "Customer reports that several tablets from batch MFG-2231-B appear "
            "discolored (light brown spots) compared to the usual white tablets. "
            "Noticed in 2 out of 10 strips opened. Product was not administered; "
            "pharmacy held the remaining stock and is requesting replacement."
        ),
    ),
    dict(
        product_name="Metforglide 500mg Tablets",
        batch_lot_number="MFG-2231-B",
        manufacturing_site="Plant 3, Vizag",
        customer_name="Care Plus Pharmacy",
        customer_contact="careplus@example.com",
        channel="portal",
        category="product_quality",
        description=(
            "Tablets from the same batch MFG-2231-B showing brownish discoloration "
            "on a subset of tablets. Two strips affected out of a box of 100. Stock "
            "quarantined, no patient exposure reported."
        ),
    ),
    dict(
        product_name="Cardiozyme 10mg Tablets",
        batch_lot_number="CDZ-0917-A",
        manufacturing_site="Plant 1, Hyderabad",
        customer_name="Anjali Rao (patient caregiver)",
        customer_contact="+91-90000-11111",
        channel="phone",
        category="adverse_event",
        description=(
            "Caregiver reports patient experienced dizziness and nausea within an hour "
            "of taking Cardiozyme 10mg. Patient has been on this medication for 3 months "
            "with no prior issues. Batch number CDZ-0917-A. Patient advised to seek "
            "medical attention; caregiver was informed to contact their physician."
        ),
    ),
    dict(
        product_name="Cardiozyme 10mg Tablets",
        batch_lot_number=None,
        manufacturing_site=None,
        customer_name="Delivery Coordinator, MedFast Logistics",
        customer_contact="ops@medfast-example.com",
        channel="email",
        category="delivery_logistics",
        description="Shipment of Cardiozyme 10mg arrived 5 days later than scheduled, no product damage reported.",
    ),
]

if __name__ == "__main__":
    db = SessionLocal()
    try:
        for row in DEMO_COMPLAINTS:
            exists = (
                db.query(models.Complaint)
                .filter_by(customer_name=row["customer_name"], product_name=row["product_name"])
                .first()
            )
            if not exists:
                db.add(models.Complaint(**row))
        db.commit()
        print(f"Seeded {len(DEMO_COMPLAINTS)} demo complaints (skipping any duplicates).")
    finally:
        db.close()
