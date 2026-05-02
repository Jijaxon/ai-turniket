import { configureStore } from "@reduxjs/toolkit";
import authReducer from "./slices/authSlice";
import usersReducer from "./slices/usersSlice";
import logsReducer from "./slices/logsSlice";

export const store = configureStore({
  reducer: {
    auth: authReducer,
    users: usersReducer,
    logs: logsReducer,
  },
});
