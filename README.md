# AIVOA — AI-Powered Customer Complaint Management System

## Current status (honest, for the reviewer)

This build targets the reference demo's core loop: paste/upload a complaint →
AIVOA Copilot extracts fields into the form live → inline risk assessment → chat-based
corrections patch individual fields. That loop is implemented end-to-end on the backend
(`agent/copilot_tools.py`, `agent/copilot_graph.py`, `routers/copilot.py`) and the
frontend (`ComplaintFormPanel.jsx` + `CopilotPanel.jsx`).

**Not yet done / next steps:**
- Drag-and-drop file UI (currently a file-picker button, not a drop zone)
- "Commit" action to formally close out intake and move a complaint into the
  Dashboard/investigation workflow (intake_status flips to `ready_to_commit`
  automatically once core fields are known, but there's no explicit commit button yet)
- End-to-end manual test pass against a real Groq API key (built and reviewed, not
  yet run live)
- Visual polish pass to match the reference screenshots' exact spacing/typography


A Customer Complaint module for a pharmaceutical (API/FDF) manufacturer's Quality
Management System (QMS), built for the AIVOA Round 1 Full Stack Developer assessment.

## What this is

The primary screen is **"Log Customer Complaint"**: a QMS intake form on the left and
the **AIVOA Copilot** chat on the right. A quality specialist pastes a raw complaint
email (or drops a PDF), and the copilot extracts structured fields live into the form
— Complaint Source, Customer Name, Product Name/Strength, Batch/Lot Number, Affected
Quantity, Manufacturing/Expiry Date, Originating Site, Impacted NPM, and a synthesized
Structured Defect Summary — then runs an inline AI risk assessment (Severity,
Suggested Next Action, Initial Risk Assessment). Follow-up messages like "actually the
batch number is BMX240602" patch just that field via the same LangGraph pipeline
(`backend/agent/copilot_graph.py`, `backend/routers/copilot.py`).

Once a complaint is committed, a **second, deeper LangGraph pipeline**
(`backend/agent/graph.py`, reachable from the Dashboard → complaint detail view) runs
six further QMS-relevant AI tools that go beyond the live intake screen:

1. **Complaint Summary** — condenses the free-text narrative into a record-ready summary
2. **Completeness Checker** — scores the record (0–100) against the fields a pharma QMS
   typically requires to open an investigation, and lists what's missing
3. **AI Risk Classification** — classifies the complaint as low / medium / high / critical,
   considering patient-safety impact and regulatory reportability
4. **Duplicate Complaint Detection** — compares the new complaint against prior
   complaints for the same product and flags likely duplicates
5. **Root Cause Recommendation** — proposes investigation-starting hypotheses (never
   presented as confirmed conclusions)
6. **CAPA Recommendation** — drafts a corrective and a preventive action for a quality
   reviewer to refine and approve

Root cause and CAPA drafting are **gated** behind the completeness score in the graph
(see `backend/agent/graph.py`) — below a completeness threshold, the pipeline stops
after triage (summary → completeness → risk → duplicate check) rather than drafting
CAPA on an incomplete record, mirroring how a real QMS investigation would actually
proceed.

## Why this design

- **LangGraph as a deterministic pipeline, not a free-roaming agent.** Every complaint
  needs the same QMS-required checks run reliably, so the graph is a fixed sequence of
  nodes (with one conditional gate) rather than an LLM deciding ad hoc which tools to
  call. Each tool is still independently callable via its own endpoint for testing/demo.
- **Structured JSON prompting instead of native tool-calling**, since the mandated
  `gemma2-9b-it` model's function-calling support is inconsistent — every tool prompts
  for strict JSON output and parses it defensively (see `_invoke_json` in `agent/tools.py`).
- **Hypotheses and drafts, not verdicts.** Root cause and CAPA outputs are explicitly
  framed as starting points for a human quality reviewer — this reflects how QMS
  processes actually work (AI can't sign off a CAPA) and was a deliberate design choice,
  not a hedge.

## Tech stack

- Frontend: React + Redux Toolkit (Vite)
- Backend: Python, FastAPI
- AI agent framework: LangGraph
- LLM: Groq — `gemma2-9b-it` (default), `llama-3.3-70b-versatile` available for
  heavier reasoning steps
- Database: PostgreSQL (or MySQL — swap the SQLAlchemy connection string)
- Font: Google Inter

## Project structure

```
backend/
  main.py              FastAPI app entry point
  database.py          SQLAlchemy engine/session
  models.py             Complaint ORM model
  schemas.py            Pydantic request/response schemas
  seed.py               Demo complaint data (incl. two near-duplicate complaints
                         for the same batch, to demo duplicate detection)
  agent/
    llm.py               Groq LLM client wrapper
    tools.py             The 6 AI tools (plain callables, JSON-prompted)
    graph.py             LangGraph StateGraph wiring the tools into a pipeline
  routers/
    complaints.py        CRUD endpoints
    analysis.py           /api/analysis/run (full pipeline) + per-tool endpoints

frontend/
  src/
    App.jsx              3-panel layout (nav / main / AI readout)
    store/                Redux slices: complaints, ui
    components/
      Sidebar.jsx
      ComplaintDashboard.jsx   Table of all complaints
      NewComplaintForm.jsx     Structured intake form
      ComplaintDetail.jsx      Single complaint + "Run AI Analysis" button
      AIAnalysisPanel.jsx      Live readout of all 6 tools' output
```

## Running it locally

### 1. Database

Create a Postgres (or MySQL) database, e.g.:

```bash
createdb complaint_mgmt
```

### 2. Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# edit .env: add your own GROQ_API_KEY (create one at https://console.groq.com)
#            and your DATABASE_URL

uvicorn main:app --reload --port 8000
```

Tables are auto-created on startup. To load demo data (recommended for the demo video,
since it includes two near-duplicate complaints for the same batch to showcase
duplicate detection):

```bash
python seed.py
```

API docs available at `http://localhost:8000/docs` once running.

### 3. Frontend

```bash
cd frontend
npm install
cp .env.example .env   # defaults to http://localhost:8000, edit if needed
npm run dev
```

Open `http://localhost:5173`.

## Demo flow (for the walkthrough video)

1. Show the dashboard (empty or seeded)
2. Log a new complaint via the structured form
3. Open the complaint detail view, click **Run AI Analysis**
4. Walk through the AI Analysis panel: summary → completeness score + missing fields
   → risk classification + rationale → duplicate check → root cause hypotheses → CAPA draft
5. Log a second complaint for the *same product/batch* with a similar description to
   demonstrate duplicate detection flagging it against the first
6. Log a deliberately sparse complaint (just a product name and one line) to show the
   completeness gate — root cause/CAPA won't populate, only triage will run

## Known limitations / honest scope notes

- No authentication — out of scope for this assessment; would add role-based access
  (QA reviewer vs. intake staff) in a production build
- Duplicate detection compares against the 10 most recent complaints for the same
  product only, for latency reasons — a production system would use embeddings +
  vector search over the full complaint history
- No OCR/document parsing (explicitly out of scope per the assignment)
- CAPA/root-cause outputs are drafts for human review, not final QMS records — this is
  intentional, not a limitation
