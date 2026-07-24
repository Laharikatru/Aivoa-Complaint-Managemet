import { configureStore } from "@reduxjs/toolkit";
import complaintsReducer from "./complaintsSlice";
import uiReducer from "./uiSlice";
import copilotReducer from "./copilotSlice";

export const store = configureStore({
  reducer: {
    complaints: complaintsReducer,
    ui: uiReducer,
    copilot: copilotReducer,
  },
});
