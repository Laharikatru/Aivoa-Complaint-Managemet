import { useDispatch, useSelector } from "react-redux";
import { runAnalysis, updateStatus, selectSelectedComplaint } from "../store/complaintsSlice";

const STATUS_OPTIONS = ["new", "under_investigation", "capa_assigned", "closed"];

export default function ComplaintDetail() {
  const dispatch = useDispatch();
  const complaint = useSelector(selectSelectedComplaint);
  const analysisStatus = useSelector((s) => s.complaints.analysisStatus);
  const analyzingId = useSelector((s) => s.complaints.analyzingId);

  if (!complaint) {
    return (
      <div className="main-panel">
        <div className="empty-state">Select a complaint from the dashboard to view it here.</div>
      </div>
    );
  }

  const isAnalyzing = analysisStatus === "running" && analyzingId === complaint.id;

  return (
    <div className="main-panel">
      <div className="screen-header">
        <div>
          <div className="screen-title">{complaint.product_name}</div>
          <div className="screen-subtitle">
            {complaint.customer_name} · {complaint.channel.replace(/_/g, " ")} · batch {complaint.batch_lot_number || "n/a"}
          </div>
        </div>
        <button
          className="btn btn-primary"
          disabled={isAnalyzing}
          onClick={() => dispatch(runAnalysis(complaint.id))}
        >
          {isAnalyzing ? "Running AI analysis…" : "Run AI Analysis"}
        </button>
      </div>

      <div className="card">
        <div className="field" style={{ marginBottom: 12 }}>
          <label>Status</label>
          <select
            value={complaint.status}
            onChange={(e) => dispatch(updateStatus({ id: complaint.id, status: e.target.value }))}
            style={{ maxWidth: 260 }}
          >
            {STATUS_OPTIONS.map((s) => <option key={s} value={s}>{s.replace(/_/g, " ")}</option>)}
          </select>
        </div>
        <div className="field">
          <label>Description</label>
          <div style={{ fontSize: 13.5, lineHeight: 1.6, whiteSpace: "pre-wrap" }}>
            {complaint.description}
          </div>
        </div>
      </div>
    </div>
  );
}
