import { useSelector } from "react-redux";
import Sidebar from "./components/Sidebar";
import ComplaintDashboard from "./components/ComplaintDashboard";
import ComplaintDetail from "./components/ComplaintDetail";
import AIAnalysisPanel from "./components/AIAnalysisPanel";
import ComplaintFormPanel from "./components/ComplaintFormPanel";
import CopilotPanel from "./components/CopilotPanel";

export default function App() {
  const view = useSelector((s) => s.ui.view);

  return (
    <div className="app-shell">
      <Sidebar />

      {view === "intake" && <ComplaintFormPanel />}
      {view === "dashboard" && <ComplaintDashboard />}
      {view === "detail" && <ComplaintDetail />}

      {view === "intake" && <CopilotPanel />}
      {view === "detail" && <AIAnalysisPanel />}
      {view === "dashboard" && <div className="rail rail--right" />}
    </div>
  );
}
