"""
The LangGraph graph behind the "AIVOA Copilot" chat panel. Two nodes:

  extract -> risk_assess -> END

`extract` pulls structured field updates (and a natural reply) out of whatever the
user just sent -- a pasted complaint email, a PDF's extracted text, or a correction
to a field already on the form. `risk_assess` then re-runs the inline risk block
using the latest known field state, so severity/next-action/rationale stay in sync
as the record gets more complete or gets corrected. This mirrors the reference demo's
"POWERED BY LANGGRAPH" extract -> populate -> assess -> re-assess loop exactly.
"""

from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END

from agent.copilot_tools import extract_and_update_fields, assess_risk

MIN_FIELDS_FOR_RISK_ASSESSMENT = 3  # don't risk-assess on almost nothing


class CopilotState(TypedDict):
    known_fields: dict
    message: str
    document_text: Optional[str]

    updated_fields: dict
    reply: str

    severity_suggested: Optional[str]
    suggested_next_action: Optional[str]
    initial_risk_assessment: Optional[str]


def node_extract(state: CopilotState):
    result = extract_and_update_fields(state["known_fields"], state["message"], state.get("document_text"))
    return {
        "updated_fields": result.get("updated_fields", {}),
        "reply": result.get("reply", "Got it."),
    }


def gate_has_enough_for_risk(state: CopilotState):
    merged = {**state["known_fields"], **state["updated_fields"]}
    populated = [v for v in merged.values() if v]
    if len(populated) >= MIN_FIELDS_FOR_RISK_ASSESSMENT:
        return "risk_assess"
    return END


def node_risk_assess(state: CopilotState):
    merged = {**state["known_fields"], **state["updated_fields"]}
    result = assess_risk(merged)
    return {
        "severity_suggested": result.get("severity_suggested"),
        "suggested_next_action": result.get("suggested_next_action"),
        "initial_risk_assessment": result.get("initial_risk_assessment"),
    }


def build_graph():
    graph = StateGraph(CopilotState)
    graph.add_node("extract", node_extract)
    graph.add_node("risk_assess", node_risk_assess)

    graph.set_entry_point("extract")
    graph.add_conditional_edges("extract", gate_has_enough_for_risk, {"risk_assess": "risk_assess", END: END})
    graph.add_edge("risk_assess", END)

    return graph.compile()


compiled_copilot_graph = build_graph()


def run_copilot_turn(known_fields: dict, message: str, document_text: Optional[str] = None) -> dict:
    initial_state: CopilotState = {
        "known_fields": known_fields,
        "message": message,
        "document_text": document_text,
        "updated_fields": {},
        "reply": "",
        "severity_suggested": None,
        "suggested_next_action": None,
        "initial_risk_assessment": None,
    }
    return compiled_copilot_graph.invoke(initial_state)
