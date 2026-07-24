import { useDispatch, useSelector } from "react-redux";
import { commitComplaint } from "../store/copilotSlice";

function Field({ label, value, placeholder }) {
  return (
    <div className="field">
      <label>{label}</label>
      <input readOnly value={value || ""} placeholder={placeholder || "Awaiting AI extraction…"} />
    </div>
  );
}

function StatusBadge({ status }) {
  const map = {
    pending_triage: { text: "Pending Triage", cls: "badge-status" },
    ready_to_commit: { text: "Ready to Commit", cls: "badge-low" },
    committed: { text: "Committed", cls: "badge-medium" },
  };
  const s = map[status] || map.pending_triage;
  return <span className={`badge ${s.cls}`}>{s.text}</span>;
}

export default function ComplaintFormPanel() {
  const dispatch = useDispatch();
  const complaint = useSelector((s) => s.copilot.complaint);
  const canCommit = complaint?.intake_status === "ready_to_commit";
  const isCommitted = complaint?.intake_status === "committed";

  return (
    <div className="main-panel">
      <div className="screen-header">
        <div>
          <div className="screen-title">Log Customer Complaint</div>
          <div className="screen-subtitle">API &amp; FDF Quality Assurance Module</div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <StatusBadge status={complaint?.intake_status || "pending_triage"} />
          <button
            className="btn btn-primary"
            disabled={!canCommit}
            onClick={() => dispatch(commitComplaint(complaint.id))}
            title={!canCommit ? "Extract the core fields (product, batch, customer) before committing" : ""}
          >
            {isCommitted ? "Committed ✓" : "Commit Complaint"}
          </button>
        </div>
      </div>

      <div className="card">
        <div className="rail-section-title" style={{ marginTop: 0 }}>1. Origin &amp; Customer Details</div>
        <div className="form-grid">
          <Field label="Complaint Source" value={complaint?.complaint_source} />
          <Field label="Customer Name" value={complaint?.customer_name} />
        </div>
      </div>

      <div className="card">
        <div className="rail-section-title" style={{ marginTop: 0 }}>2. Product &amp; Batch Identification</div>
        <div className="form-grid">
          <Field label="Product Name (API/FDF)" value={complaint?.product_name} />
          <Field label="Product Strength" value={complaint?.product_strength} />
          <Field label="Batch / Lot Number" value={complaint?.batch_lot_number} />
          <Field label="Affected Quantity" value={complaint?.affected_quantity} />
          <Field label="Manufacturing Date" value={complaint?.manufacturing_date} />
          <Field label="Expiry Date" value={complaint?.expiry_date} />
        </div>
      </div>

      <div className="card">
        <div className="rail-section-title" style={{ marginTop: 0 }}>3. Facility &amp; Material Impact</div>
        <div className="form-grid">
          <Field label="Originating Site Block" value={complaint?.originating_site_block} />
          <Field label="Impacted Non-Product Materials (NPM)" value={complaint?.impacted_npm} placeholder="e.g. Primary packaging…" />
        </div>
      </div>

      <div className="card">
        <div className="rail-section-title" style={{ marginTop: 0 }}>4. Defect Analysis</div>
        <div className="field" style={{ marginBottom: 12 }}>
          <label>Complaint Category</label>
          <input readOnly value={complaint?.complaint_category_label || ""} placeholder="Awaiting AI classification…" />
        </div>
        <div className="field">
          <label>Structured Defect Summary</label>
          <textarea
            readOnly
            value={complaint?.structured_defect_summary || ""}
            placeholder="AI will synthesize the complaint into a formal QMS description…"
          />
        </div>
      </div>

      {(complaint?.severity_suggested || complaint?.suggested_next_action || complaint?.initial_risk_assessment) && (
        <div className="card" style={{ background: "var(--teal-soft)", border: "1px solid var(--teal)" }}>
          <div className="rail-section-title" style={{ marginTop: 0, color: "var(--teal)" }}>
            🛡 AI Copilot Risk Assessment
          </div>
          <div className="form-grid">
            <Field label="Severity (Suggested)" value={complaint?.severity_suggested} />
            <Field label="Suggested Next Action" value={complaint?.suggested_next_action} />
          </div>
          <div className="field full" style={{ marginTop: 14 }}>
            <label>Initial Risk Assessment</label>
            <textarea readOnly value={complaint?.initial_risk_assessment || ""} />
          </div>
        </div>
      )}
    </div>
  );
}