const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`API ${options.method || "GET"} ${path} failed: ${res.status} ${text}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  listComplaints: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return request(`/api/complaints/${qs ? `?${qs}` : ""}`);
  },
  createComplaint: (payload) =>
    request("/api/complaints/", { method: "POST", body: JSON.stringify(payload) }),
  getComplaint: (id) => request(`/api/complaints/${id}`),
  updateStatus: (id, status) =>
    request(`/api/complaints/${id}/status`, { method: "PATCH", body: JSON.stringify({ status }) }),
  deleteComplaint: (id) => request(`/api/complaints/${id}`, { method: "DELETE" }),

  runAnalysis: (complaintId) =>
    request("/api/analysis/run", { method: "POST", body: JSON.stringify({ complaint_id: complaintId }) }),

  copilotMessage: (payload) =>
    request("/api/copilot/message", { method: "POST", body: JSON.stringify(payload) }),

  copilotUpload: async (file, sessionId) => {
    const form = new FormData();
    form.append("file", file);
    const qs = sessionId ? `?session_id=${encodeURIComponent(sessionId)}` : "";
    const res = await fetch(`${BASE_URL}/api/copilot/upload${qs}`, { method: "POST", body: form });
    if (!res.ok) throw new Error(`Upload failed: ${res.status}`);
    return res.json();
  },

  commitComplaint: (complaintId) =>
    request(`/api/copilot/commit/${complaintId}`, { method: "POST" }),
};