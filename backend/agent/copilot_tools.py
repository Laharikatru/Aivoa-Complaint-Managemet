"""
The copilot's core capability: given the running conversation/known field state plus a
new message (raw pasted complaint text, a correction like "actually the batch number
is X", or extracted PDF text), extract or update the structured "Log Customer
Complaint" form fields and produce an updated AI risk assessment -- mirroring the
reference AIVOA Copilot demo exactly (extract -> populate form -> risk assess ->
accept corrections -> re-assess).
"""

import json
import re
from typing import Optional

from agent.llm import get_llm

FORM_FIELDS = [
    "complaint_source",       # e.g. Pharmacy, Distributor, Patient, Physician
    "customer_name",
    "product_name",
    "product_strength",
    "batch_lot_number",
    "affected_quantity",
    "manufacturing_date",
    "expiry_date",
    "originating_site_block",  # manufacturing site / facility block
    "impacted_npm",             # Impacted Non-Product Materials, e.g. "Primary packaging"
    "complaint_category_label",  # complaint category, e.g. "Product Defect - Discoloration"
    "structured_defect_summary",  # formal QMS-style narrative synthesized from raw input
]


def _invoke_json(prompt: str) -> dict:
    llm = get_llm()
    raw = llm.invoke(prompt).content
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    text = match.group(0) if match else raw
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"error": "could_not_parse_llm_output", "raw": raw}


def extract_and_update_fields(known_fields: dict, message: str, document_text: Optional[str] = None) -> dict:
    """Extract new/updated structured fields from a chat message (and optional pasted
    document text), given what's already known. Only fields that are new or changed
    should be returned -- this is what makes incremental correction messages work
    ("actually the batch number is BMX240602") without clobbering everything else."""

    context = f"""Known fields so far (JSON): {json.dumps(known_fields)}

New input from the user (this may be a raw complaint email/description, a correction
to a previously extracted field, or both):
\"\"\"{message}\"\"\""""

    if document_text:
        context += f"""

Additionally, the user attached a document. Extracted text from it:
\"\"\"{document_text[:4000]}\"\"\""""

    prompt = f"""You are the AIVOA Copilot, an AI assistant embedded in a pharmaceutical
QMS "Log Customer Complaint" form. Your job is to extract or update structured intake
fields from whatever the user gives you, exactly the way a quality intake specialist
would fill out the form.

Fields you can populate: {", ".join(FORM_FIELDS)}

{context}

Rules:
- Only include fields in your response that you can confidently extract or that the
  user is explicitly correcting. Do not guess values you have no basis for.
- If the user is correcting a specific field (e.g. "the batch number is actually X"),
  only that field (and any others explicitly mentioned) should appear in updated_fields.
- "structured_defect_summary" should be a concise, formal, QMS-record-ready synthesis
  of the complaint narrative (2-3 sentences), not a copy-paste of the raw input.
- "complaint_category_label" should be a short human-readable label like
  "Product Defect - Discoloration" or "Foreign Matter Contamination", inferred from
  the narrative.
- Write a short, natural confirmation reply (1-2 sentences) telling the user what you
  extracted or updated, in the voice of a helpful copilot -- e.g. "Got it. I've updated
  the Batch/Lot Number to X and the Affected Quantity to Y in the form."

Respond with ONLY this JSON object, no other text:
{{"updated_fields": {{"field_name": "value", "...": "..."}}, "reply": "..."}}"""

    return _invoke_json(prompt)


def assess_risk(fields: dict) -> dict:
    """Produce the inline 'AI copilot risk assessment' block: suggested severity,
    suggested next action, and an initial risk assessment narrative -- shaped exactly
    like the reference form's risk block. Runs whenever enough fields are known to make
    a reasonable initial call; re-runs automatically as fields are corrected."""

    prompt = f"""You are the AIVOA Copilot performing an initial risk triage on a
pharmaceutical customer complaint, based on the fields extracted so far.

Known fields (JSON): {json.dumps(fields)}

Provide:
- severity_suggested: one of "Minor", "Major", "Critical"
- suggested_next_action: a short, concrete QMS next step, e.g. "Laboratory investigation
  & manufacturing record review" or "Route to QA Investigation & Issue Replacement"
- initial_risk_assessment: 1-2 sentences of plain-language risk reasoning a quality
  reviewer would find useful as a starting point (not a final determination)

Respond with ONLY this JSON object, no other text:
{{"severity_suggested": "...", "suggested_next_action": "...", "initial_risk_assessment": "..."}}"""

    return _invoke_json(prompt)
