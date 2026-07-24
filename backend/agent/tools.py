"""
AI-powered tools for the Customer Complaint module. Each function takes a complaint's
raw fields (and, for duplicate detection, the existing complaint corpus) and returns a
structured result by prompting the Groq-hosted LLM for strict JSON output.

These are implemented as plain callables (not LangChain @tool-bound functions) because
they're orchestrated as a deterministic LangGraph pipeline rather than an LLM-driven
ReAct tool-selection loop -- appropriate here since every complaint should reliably run
through the same QMS-required checks, not have an agent freely decide which to skip.
Each one is still independently callable via its own API endpoint for ad-hoc use/demo.
"""

import json
import re
from typing import Optional

from agent.llm import get_llm

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _invoke_json(prompt: str, model: Optional[str] = None) -> dict:
    """Call the LLM and coerce its reply into a JSON object, tolerating the odd
    stray markdown fence or preamble sentence smaller models sometimes add."""
    llm = get_llm(model=model)
    raw = llm.invoke(prompt).content
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    text = match.group(0) if match else raw
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"error": "could_not_parse_llm_output", "raw": raw}


# ---------------------------------------------------------------------------
# 1. Complaint Summary
# ---------------------------------------------------------------------------


def summarize_complaint(description: str) -> dict:
    """Produce a concise, QMS-record-ready summary of a free-text complaint narrative."""
    prompt = f"""You are a pharmaceutical Quality Management System (QMS) assistant.
Summarize the following customer complaint narrative in 2-3 sentences, in neutral,
factual, record-ready language suitable for a QMS complaint file. Do not speculate
beyond what is stated.

Complaint narrative:
\"\"\"{description}\"\"\"

Respond with ONLY this JSON object, no other text:
{{"summary": "..."}}"""
    return _invoke_json(prompt)


# ---------------------------------------------------------------------------
# 2. Complaint Completeness Checker
# ---------------------------------------------------------------------------

REQUIRED_QMS_FIELDS = [
    "product name",
    "batch or lot number",
    "date of occurrence or discovery",
    "description of the defect or issue observed",
    "quantity affected",
    "whether the product was administered/used and to whom",
]


def check_completeness(description: str, structured_fields: dict) -> dict:
    """Score how complete a complaint record is against the fields a pharma QMS
    typically requires to begin an investigation, and list what's missing."""
    prompt = f"""You are a pharmaceutical QMS intake reviewer. A complaint should
generally include: {", ".join(REQUIRED_QMS_FIELDS)}.

Structured fields already captured: {json.dumps(structured_fields)}
Free-text narrative: \"\"\"{description}\"\"\"

Evaluate how complete this complaint record is for starting a formal investigation.

Respond with ONLY this JSON object, no other text:
{{"completeness_score": <0-100 integer>, "missing_fields": ["...", "..."], "reasoning": "one sentence"}}"""
    return _invoke_json(prompt)


# ---------------------------------------------------------------------------
# 3. AI Risk Classification
# ---------------------------------------------------------------------------


def classify_risk(description: str, category: str) -> dict:
    """Classify the complaint's risk level per typical pharma QMS severity bands,
    considering patient safety impact, regulatory reportability, and product quality risk."""
    prompt = f"""You are a pharmaceutical QMS risk assessor. Classify the risk level of
this complaint as one of: low, medium, high, critical.

- critical: potential adverse patient outcome, suspected counterfeit, or clear GMP/regulatory
  reportability trigger (e.g. contamination, mislabeling causing dosing error)
- high: credible product quality defect with plausible safety impact, not yet confirmed
- medium: product quality issue with low safety impact (e.g. packaging defect, cosmetic issue)
- low: non-product issues (e.g. delivery delay, customer service complaint)

Complaint category: {category}
Complaint narrative: \"\"\"{description}\"\"\"

Respond with ONLY this JSON object, no other text:
{{"risk_classification": "low|medium|high|critical", "rationale": "one to two sentences"}}"""
    return _invoke_json(prompt)


# ---------------------------------------------------------------------------
# 4. Duplicate Complaint Detection
# ---------------------------------------------------------------------------


def detect_duplicate(description: str, product_name: str, candidates: list[dict]) -> dict:
    """Compare a new complaint against a shortlist of existing complaints for the same
    product (candidates should already be pre-filtered by product_name at the DB layer)
    and flag the closest match if it looks like the same underlying issue."""
    if not candidates:
        return {"is_duplicate": False, "duplicate_of_id": None, "confidence": 0.0, "rationale": "No prior complaints for this product to compare against."}

    candidate_text = "\n".join(
        f"- id={c['id']}: \"{c['description'][:300]}\"" for c in candidates
    )
    prompt = f"""You are a pharmaceutical QMS analyst checking for duplicate complaints
about the same product ({product_name}).

New complaint: \"\"\"{description}\"\"\"

Existing complaints for this product:
{candidate_text}

Does the new complaint describe the same underlying issue as one of the existing ones?

Respond with ONLY this JSON object, no other text:
{{"is_duplicate": true|false, "duplicate_of_id": "id or null", "confidence": <0.0-1.0>, "rationale": "one sentence"}}"""
    return _invoke_json(prompt)


# ---------------------------------------------------------------------------
# 5. Root Cause Recommendation
# ---------------------------------------------------------------------------


def recommend_root_cause(description: str, category: str) -> dict:
    """Suggest plausible root cause hypotheses to seed a formal investigation --
    explicitly framed as hypotheses for a quality investigator to verify, not conclusions."""
    prompt = f"""You are a pharmaceutical manufacturing quality investigator assistant.
Given the complaint below, propose 2-3 plausible root cause HYPOTHESES an investigator
should check first (e.g. process deviation, raw material variability, packaging line
issue, storage/transport condition, labeling error). These are starting hypotheses for
investigation, not confirmed conclusions.

Category: {category}
Complaint narrative: \"\"\"{description}\"\"\"

Respond with ONLY this JSON object, no other text:
{{"hypotheses": ["...", "...", "..."]}}"""
    return _invoke_json(prompt)


# ---------------------------------------------------------------------------
# 6. CAPA Recommendation
# ---------------------------------------------------------------------------


def recommend_capa(description: str, risk_classification: str, root_cause_hypotheses: list[str]) -> dict:
    """Suggest draft Corrective and Preventive Action (CAPA) directions consistent with
    the assessed risk level -- framed as a starting draft for a quality reviewer, since
    CAPA sign-off in a real QMS requires human review."""
    prompt = f"""You are a pharmaceutical QMS CAPA (Corrective and Preventive Action)
assistant. Given the complaint, its risk classification, and candidate root cause
hypotheses, draft brief CAPA recommendations (1 corrective, 1 preventive) a quality
reviewer can refine and approve. Do not present these as final/approved actions.

Risk classification: {risk_classification}
Root cause hypotheses: {root_cause_hypotheses}
Complaint narrative: \"\"\"{description}\"\"\"

Respond with ONLY this JSON object, no other text:
{{"corrective_action": "...", "preventive_action": "..."}}"""
    return _invoke_json(prompt)
