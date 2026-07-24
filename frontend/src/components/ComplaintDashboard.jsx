import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { fetchComplaints, selectComplaint } from "../store/complaintsSlice";
import { setView } from "../store/uiSlice";

function RiskBadge({ risk }) {
  if (!risk) return <span className="badge badge-status">Not analyzed</span>;
  return <span className={`badge badge-${risk}`}>{risk}</span>;
}

export default function ComplaintDashboard() {
  const dispatch = useDispatch();
  const { items, status } = useSelector((s) => s.complaints);

  useEffect(() => {
    dispatch(fetchComplaints());
  }, [dispatch]);

  const openComplaint = (id) => {
    dispatch(selectComplaint(id));
    dispatch(setView("detail"));
  };

  return (
    <div className="main-panel">
      <div className="screen-header">
        <div>
          <div className="screen-title">Complaint Dashboard</div>
          <div className="screen-subtitle">
            All logged customer complaints, with AI risk classification once analyzed
          </div>
        </div>
        <button className="btn btn-primary" onClick={() => dispatch(setView("intake"))}>
          + New Complaint
        </button>
      </div>

      <div className="card" style={{ padding: 0 }}>
        {status === "loading" && <div className="empty-state">Loading complaints…</div>}
        {status === "failed" && (
          <div className="empty-state">Couldn't reach the API. Is the backend running on :8000?</div>
        )}
        {status === "succeeded" && items.length === 0 && (
          <div className="empty-state">No complaints logged yet. Create one to get started.</div>
        )}

        {items.length > 0 && (
          <table className="complaint-table">
            <thead>
              <tr>
                <th>Product</th>
                <th>Customer</th>
                <th>Category</th>
                <th>AI Risk</th>
                <th>Status</th>
                <th>Received</th>
              </tr>
            </thead>
            <tbody>
              {items.map((c) => (
                <tr key={c.id} onClick={() => openComplaint(c.id)}>
                  <td>{c.product_name}</td>
                  <td>{c.customer_name}</td>
                  <td>{c.category.replace(/_/g, " ")}</td>
                  <td><RiskBadge risk={c.ai_risk_classification} /></td>
                  <td><span className="badge badge-status">{c.status.replace(/_/g, " ")}</span></td>
                  <td>{new Date(c.date_received).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
