import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { api } from "../api/client";

export const fetchComplaints = createAsyncThunk("complaints/fetchAll", (params) =>
  api.listComplaints(params)
);

export const createComplaint = createAsyncThunk("complaints/create", (payload) =>
  api.createComplaint(payload)
);

export const runAnalysis = createAsyncThunk("complaints/runAnalysis", (complaintId) =>
  api.runAnalysis(complaintId)
);

export const updateStatus = createAsyncThunk("complaints/updateStatus", ({ id, status }) =>
  api.updateStatus(id, status)
);

const complaintsSlice = createSlice({
  name: "complaints",
  initialState: {
    items: [],
    selectedId: null,
    status: "idle",
    submitStatus: "idle",
    analysisStatus: "idle", // idle | running | succeeded | failed, per complaint handled via analyzingId
    analyzingId: null,
    lastToolCalls: [],
    error: null,
  },
  reducers: {
    selectComplaint(state, action) {
      state.selectedId = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchComplaints.pending, (state) => {
        state.status = "loading";
      })
      .addCase(fetchComplaints.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.items = action.payload;
        if (!state.selectedId && action.payload.length > 0) {
          state.selectedId = action.payload[0].id;
        }
      })
      .addCase(fetchComplaints.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.error.message;
      })

      .addCase(createComplaint.pending, (state) => {
        state.submitStatus = "loading";
      })
      .addCase(createComplaint.fulfilled, (state, action) => {
        state.submitStatus = "succeeded";
        state.items.unshift(action.payload);
        state.selectedId = action.payload.id;
      })
      .addCase(createComplaint.rejected, (state, action) => {
        state.submitStatus = "failed";
        state.error = action.error.message;
      })

      .addCase(runAnalysis.pending, (state, action) => {
        state.analysisStatus = "running";
        state.analyzingId = action.meta.arg;
      })
      .addCase(runAnalysis.fulfilled, (state, action) => {
        state.analysisStatus = "succeeded";
        state.analyzingId = null;
        state.lastToolCalls = action.payload.tool_calls;
        const idx = state.items.findIndex((c) => c.id === action.payload.complaint.id);
        if (idx >= 0) state.items[idx] = action.payload.complaint;
      })
      .addCase(runAnalysis.rejected, (state, action) => {
        state.analysisStatus = "failed";
        state.analyzingId = null;
        state.error = action.error.message;
      })

      .addCase(updateStatus.fulfilled, (state, action) => {
        const idx = state.items.findIndex((c) => c.id === action.payload.id);
        if (idx >= 0) state.items[idx] = action.payload;
      });
  },
});

export const { selectComplaint } = complaintsSlice.actions;
export default complaintsSlice.reducer;

export const selectSelectedComplaint = (state) =>
  state.complaints.items.find((c) => c.id === state.complaints.selectedId) || null;
