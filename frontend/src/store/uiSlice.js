import { createSlice } from "@reduxjs/toolkit";

const uiSlice = createSlice({
  name: "ui",
  initialState: {
    view: "intake", // 'intake' | 'dashboard' | 'detail'
  },
  reducers: {
    setView(state, action) {
      state.view = action.payload;
    },
  },
});

export const { setView } = uiSlice.actions;
export default uiSlice.reducer;
