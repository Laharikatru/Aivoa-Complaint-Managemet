import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { api } from "../api/client";

export const sendCopilotMessage = createAsyncThunk(
  "copilot/sendMessage",
  async ({ message, sessionId, documentText }) => {
    return api.copilotMessage({ message, session_id: sessionId, document_text: documentText });
  }
);

export const uploadDocument = createAsyncThunk(
  "copilot/uploadDocument",
  async ({ file, sessionId }) => api.copilotUpload(file, sessionId)
);

export const commitComplaint = createAsyncThunk(
  "copilot/commitComplaint",
  async (complaintId) => api.commitComplaint(complaintId)
);

const copilotSlice = createSlice({
  name: "copilot",
  initialState: {
    sessionId: null,
    messages: [
      {
        role: "agent",
        content:
          "Ready to process new complaints. You can paste the raw email from the customer, or upload a PDF of the complaint report. I will extract the data and run the initial risk assessment.",
      },
    ],
    complaint: null, // latest ComplaintOut, drives the form
    status: "idle", // idle | sending | succeeded | failed
    uploadStatus: "idle",
  },
  reducers: {
    resetIntake(state) {
      state.sessionId = null;
      state.messages = [state.messages[0]];
      state.complaint = null;
      state.status = "idle";
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendCopilotMessage.pending, (state, action) => {
        state.status = "sending";
        state.messages.push({ role: "user", content: action.meta.arg.message });
      })
      .addCase(sendCopilotMessage.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.sessionId = action.payload.session_id;
        state.complaint = action.payload.complaint;
        state.messages.push({ role: "agent", content: action.payload.reply });
      })
      .addCase(sendCopilotMessage.rejected, (state, action) => {
        state.status = "failed";
        state.messages.push({ role: "agent", content: `Something went wrong: ${action.error.message}` });
      })
      .addCase(uploadDocument.pending, (state) => {
        state.uploadStatus = "uploading";
      })
      .addCase(uploadDocument.fulfilled, (state, action) => {
        state.uploadStatus = "succeeded";
        state.messages.push({
          role: "user",
          content: `[Attached document: ${action.payload.filename}]`,
          isDocument: true,
        });
      })
      .addCase(uploadDocument.rejected, (state, action) => {
        state.uploadStatus = "failed";
        state.messages.push({ role: "agent", content: `Couldn't read that file: ${action.error.message}` });
      })
      .addCase(commitComplaint.fulfilled, (state, action) => {
        state.complaint = action.payload;
      });
  },
});

export const { resetIntake } = copilotSlice.actions;
export default copilotSlice.reducer;