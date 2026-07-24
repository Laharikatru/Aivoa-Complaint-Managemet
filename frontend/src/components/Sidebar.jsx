import { useDispatch, useSelector } from "react-redux";
import { setView } from "../store/uiSlice";

export default function Sidebar() {
  const dispatch = useDispatch();
  const view = useSelector((s) => s.ui.view);
  const items = useSelector((s) => s.complaints.items);

  const counts = items.reduce((acc, c) => {
    acc[c.status] = (acc[c.status] || 0) + 1;
    return acc;
  }, {});

  return (
    <aside className="rail">
      <div className="brand">
        AIVOA QMS
        <small>Customer Complaint Module</small>
      </div>

      <div
        className={`nav-item ${view === "intake" ? "active" : ""}`}
        onClick={() => dispatch(setView("intake"))}
      >
        Log Complaint (Copilot)
      </div>
      <div
        className={`nav-item ${view === "dashboard" ? "active" : ""}`}
        onClick={() => dispatch(setView("dashboard"))}
      >
        Dashboard
      </div>

      <div className="rail-section-title">Status Overview</div>
      <div style={{ fontSize: 12.5, color: "var(--ink-soft)", lineHeight: 1.9 }}>
        <div>New: {counts.new || 0}</div>
        <div>Under Investigation: {counts.under_investigation || 0}</div>
        <div>CAPA Assigned: {counts.capa_assigned || 0}</div>
        <div>Closed: {counts.closed || 0}</div>
      </div>
    </aside>
  );
}
