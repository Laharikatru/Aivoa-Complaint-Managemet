import { useSelector } from "react-redux";
import { selectSelectedComplaint } from "../store/complaintsSlice";

function RiskBadge({ risk }) {
  if (!risk) return null;
  return <span className={`badge badge-${risk}`}>{risk}</span>;
}

export default function AIAnalysisPanel() {
  const complaint = useSelector(selectSelectedComplaint);
  const analysisStatus = useSelector((s) => s.complaints.analysisStatus);
  const analyzingId = useSelector((s) => s.complaints.analyzingId);
  const lastToolCalls = useSelector((s) => s.complaints.lastToolCalls);

  if (!complaint) {
    return (
      <aside className="rail rail--right">
        <div className="readout-title">AI Analysis</div>
        <div className="empty-state">No complaint selected.</div>
      </aside>
    );
  }

  const isAnalyzing = analysisStatus === "running" && analyzingId === complaint.id;
  const hasRun = !!complaint.ai_summary;

  return (
    <aside className="rail rail--right">
      <div className="readout-title">AI Analysis</div>

      {isAnalyzing && (
        <div style={{ fontSize: 12.5, color: "var(--ink-soft)", marginBottom: 14 }}>
          <span className="spinner-dot" />
          Running LangGraph pipeline (6 tools)…
        </div>
      )}

      {!hasRun && !isAnalyzing && (
        <div className="empty-state">Run AI Analysis to populate this panel.</div>
      )}

      {hasRun && (
        <>
          <div className="readout-block">
            <div className="label">01 · Complaint Summary</div>
            <div className="value">{complaint.ai_summary}</div>
          </div>

          <div className="readout-block">
            <div className="label">02 · Completeness Checker</div>
            <div className="value">
              Score: <strong>{complaint.ai_completeness_score ?? "—"}/100</strong>
            </div>
            {complaint.ai_missing_fields && (
              <div className="value" style={{ color: "var(--amber)", marginTop: 4 }}>
                Missing: {complaint.ai_missing_fields}
              </div>
            )}
          </div>

          <div className="readout-block">
            <div className="label">03 · AI Risk Classification</div>
            <div className="value">
              <RiskBadge risk={complaint.ai_risk_classification} />
            </div>
            {complaint.ai_risk_rationale && (
              <div className="value" style={{ marginTop: 6 }}>{complaint.ai_risk_rationale}</div>
            )}
          </div>

          <div className="readout-block">
            <div className="label">04 · Duplicate Detection</div>
            <div className="value mono">
              {complaint.ai_duplicate_of_id
                ? `Possible duplicate of #${complaint.ai_duplicate_of_id.slice(0, 8)} (confidence ${Math.round((complaint.ai_duplicate_confidence || 0) * 100)}%)`
                : "No duplicate detected"}
            </div>
          </div>

          {complaint.ai_root_cause_suggestion && (
            <div className="readout-block">
              <div className="label">05 · Root Cause Hypotheses</div>
              <div className="value" style={{ whiteSpace: "pre-wrap" }}>{complaint.ai_root_cause_suggestion}</div>
            </div>
          )}

          {complaint.ai_capa_suggestion && (
            <div className="readout-block">
              <div className="label">06 · Draft CAPA</div>
              <div className="value" style={{ whiteSpace: "pre-wrap" }}>{complaint.ai_capa_suggestion}</div>
            </div>
          )}

          {lastToolCalls.length > 0 && (
            <div className="readout-block">
              <div className="label">Tools invoked</div>
              <div>
                {lastToolCalls.map((t, i) => <span key={i} className="tool-pill">{t}</span>)}
              </div>
            </div>
          )}
        </>
      )}
    </aside>
  );
}
