import { useRef, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { sendCopilotMessage, uploadDocument } from "../store/copilotSlice";

export default function CopilotPanel() {
  const dispatch = useDispatch();
  const { messages, status, sessionId, uploadStatus } = useSelector((s) => s.copilot);
  const [input, setInput] = useState("");
  const [pendingDocText, setPendingDocText] = useState(null);
  const fileRef = useRef(null);

  const isBusy = status === "sending" || uploadStatus === "uploading";

  const handleSend = (e) => {
    e.preventDefault();
    if (!input.trim() && !pendingDocText) return;
    dispatch(
      sendCopilotMessage({
        message: input.trim() || "Please process the attached document.",
        sessionId,
        documentText: pendingDocText,
      })
    );
    setInput("");
    setPendingDocText(null);
  };

  const handleFile = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const action = await dispatch(uploadDocument({ file, sessionId }));
    if (uploadDocument.fulfilled.match(action)) {
      setPendingDocText(action.payload.document_text);
    }
    e.target.value = "";
  };

  return (
    <aside className="rail rail--right">
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 4 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ fontSize: 18 }}>🧪</span>
          <strong style={{ fontSize: 14 }}>AIVOA Copilot</strong>
        </div>
        <span
          style={{
            width: 8,
            height: 8,
            borderRadius: "50%",
            background: isBusy ? "var(--amber)" : "var(--sage)",
            display: "inline-block",
          }}
        />
      </div>
      <div style={{ fontSize: 11.5, color: "var(--ink-soft)", marginBottom: 14 }}>
        Drop complaint files or paste text below.
      </div>

      <div className="chat-messages" style={{ height: 420 }}>
        {messages.map((m, i) => (
          <div key={i} className={`chat-bubble ${m.role === "user" ? "user" : "agent"}`}>
            {m.isDocument ? <em>{m.content}</em> : m.content}
          </div>
        ))}
        {isBusy && (
          <div className="chat-bubble agent">
            <span className="spinner-dot" />
            {uploadStatus === "uploading" ? "Reading document…" : "Thinking…"}
          </div>
        )}
      </div>

      {pendingDocText && (
        <div style={{ fontSize: 11.5, color: "var(--teal)", marginBottom: 6 }}>
          📎 Document ready — attach a note and send, or just send to process it.
        </div>
      )}

      <form className="chat-input-row" onSubmit={handleSend}>
        <button
          type="button"
          className="btn btn-ghost"
          style={{ padding: "10px 12px" }}
          onClick={() => fileRef.current?.click()}
          title="Attach PDF or text file"
        >
          📎
        </button>
        <input
          type="file"
          accept=".pdf,.txt"
          ref={fileRef}
          style={{ display: "none" }}
          onChange={handleFile}
        />
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message or paste a complaint…"
          disabled={isBusy}
        />
        <button className="btn btn-primary" type="submit" disabled={isBusy}>
          ➤
        </button>
      </form>
      <div style={{ textAlign: "center", fontSize: 10, color: "var(--ink-soft)", marginTop: 8, letterSpacing: "0.04em" }}>
        POWERED BY LANGGRAPH
      </div>
    </aside>
  );
}
