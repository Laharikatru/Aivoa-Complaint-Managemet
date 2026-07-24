"""
LangGraph pipeline for the Customer Complaint module.

Conceptually, this is the AI layer that sits behind "Analyze Complaint": once a
complaint is logged (via the structured form), it flows through a sequence of
QMS-relevant AI checks -- summarize -> check completeness -> classify risk ->
check for duplicates -> suggest root cause -> draft CAPA -- each a node in the
graph, with the DB row updated incrementally so a partial run still saves useful
progress if a later step fails.

A conditional edge skips root-cause/CAPA drafting when the completeness score is
too low to investigate meaningfully -- modeling a real QMS gate: you don't draft
CAPA on an incomplete record, you request more information first.
"""

from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END

from agent.tools import (
    summarize_complaint,
    check_completeness,
    classify_risk,
    detect_duplicate,
    recommend_root_cause,
    recommend_capa,
)


class ComplaintState(TypedDict):
    complaint_id: str
    description: str
    product_name: str
    category: str
    structured_fields: dict
    candidates: list  # existing complaints for the same product, for duplicate check

    summary: Optional[str]
    completeness_score: Optional[float]
    missing_fields: Optional[list]
    risk_classification: Optional[str]
    risk_rationale: Optional[str]
    is_duplicate: Optional[bool]
    duplicate_of_id: Optional[str]
    duplicate_confidence: Optional[float]
    root_cause_hypotheses: Optional[list]
    corrective_action: Optional[str]
    preventive_action: Optional[str]

    tool_calls: list  # running log, for the frontend's "AI tools used" readout


MIN_COMPLETENESS_FOR_INVESTIGATION = 40


def node_summarize(state: ComplaintState):
    result = summarize_complaint(state["description"])
    return {"summary": result.get("summary"), "tool_calls": state["tool_calls"] + ["summarize_complaint"]}


def node_completeness(state: ComplaintState):
    result = check_completeness(state["description"], state["structured_fields"])
    return {
        "completeness_score": result.get("completeness_score"),
        "missing_fields": result.get("missing_fields", []),
        "tool_calls": state["tool_calls"] + ["check_completeness"],
    }


def node_risk(state: ComplaintState):
    result = classify_risk(state["description"], state["category"])
    return {
        "risk_classification": result.get("risk_classification"),
        "risk_rationale": result.get("rationale"),
        "tool_calls": state["tool_calls"] + ["classify_risk"],
    }


def node_duplicate(state: ComplaintState):
    result = detect_duplicate(state["description"], state["product_name"], state["candidates"])
    return {
        "is_duplicate": result.get("is_duplicate", False),
        "duplicate_of_id": result.get("duplicate_of_id"),
        "duplicate_confidence": result.get("confidence"),
        "tool_calls": state["tool_calls"] + ["detect_duplicate"],
    }


def node_root_cause(state: ComplaintState):
    result = recommend_root_cause(state["description"], state["category"])
    return {
        "root_cause_hypotheses": result.get("hypotheses", []),
        "tool_calls": state["tool_calls"] + ["recommend_root_cause"],
    }


def node_capa(state: ComplaintState):
    result = recommend_capa(
        state["description"],
        state.get("risk_classification") or "unknown",
        state.get("root_cause_hypotheses") or [],
    )
    return {
        "corrective_action": result.get("corrective_action"),
        "preventive_action": result.get("preventive_action"),
        "tool_calls": state["tool_calls"] + ["recommend_capa"],
    }


def gate_investigation_depth(state: ComplaintState):
    """QMS-inspired gate: only draft root cause / CAPA once the record is complete
    enough to investigate. Otherwise stop after triage (summary, completeness, risk,
    duplicate check) and let a human request the missing information first."""
    score = state.get("completeness_score") or 0
    if score >= MIN_COMPLETENESS_FOR_INVESTIGATION:
        return "root_cause"
    return END


def build_graph():
    graph = StateGraph(ComplaintState)
    graph.add_node("summarize", node_summarize)
    graph.add_node("completeness", node_completeness)
    graph.add_node("risk", node_risk)
    graph.add_node("duplicate", node_duplicate)
    graph.add_node("root_cause", node_root_cause)
    graph.add_node("capa", node_capa)

    graph.set_entry_point("summarize")
    graph.add_edge("summarize", "completeness")
    graph.add_edge("completeness", "risk")
    graph.add_edge("risk", "duplicate")
    graph.add_conditional_edges(
        "duplicate", gate_investigation_depth, {"root_cause": "root_cause", END: END}
    )
    graph.add_edge("root_cause", "capa")
    graph.add_edge("capa", END)

    return graph.compile()


compiled_graph = build_graph()


def run_full_analysis(
    complaint_id: str,
    description: str,
    product_name: str,
    category: str,
    structured_fields: dict,
    candidates: list,
) -> dict:
    """Entry point used by the /api/analysis router: runs the full pipeline for one
    complaint and returns the final state, ready to be written back to the DB row."""
    initial_state: ComplaintState = {
        "complaint_id": complaint_id,
        "description": description,
        "product_name": product_name,
        "category": category,
        "structured_fields": structured_fields,
        "candidates": candidates,
        "summary": None,
        "completeness_score": None,
        "missing_fields": None,
        "risk_classification": None,
        "risk_rationale": None,
        "is_duplicate": None,
        "duplicate_of_id": None,
        "duplicate_confidence": None,
        "root_cause_hypotheses": None,
        "corrective_action": None,
        "preventive_action": None,
        "tool_calls": [],
    }
    return compiled_graph.invoke(initial_state)
