import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import api from "../../utils/api";

export const fetchStats = createAsyncThunk("logs/stats", async (_, { rejectWithValue }) => {
  try {
    const { data } = await api.get("/logs/stats");
    return data;
  } catch (err) {
    return rejectWithValue(err.response?.data?.detail || "Failed to load stats");
  }
});

export const fetchLogs = createAsyncThunk("logs/fetchAll", async (params = {}, { rejectWithValue }) => {
  try {
    const { data } = await api.get("/logs/", { params });
    return data;
  } catch (err) {
    return rejectWithValue(err.response?.data?.detail || "Failed to load logs");
  }
});

export const fetchDailyReport = createAsyncThunk("logs/daily", async (_, { rejectWithValue }) => {
  try {
    const { data } = await api.get("/logs/daily-report");
    return data;
  } catch (err) {
    return rejectWithValue(err.response?.data?.detail || "Failed to load report");
  }
});

const logsSlice = createSlice({
  name: "logs",
  initialState: {
    items: [], total: 0,
    stats: null,
    dailyReport: [],
    loading: false, error: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchStats.fulfilled, (s, a) => { s.stats = a.payload; })
      .addCase(fetchLogs.pending, (s) => { s.loading = true; })
      .addCase(fetchLogs.fulfilled, (s, a) => { s.loading = false; s.items = a.payload.logs; s.total = a.payload.total; })
      .addCase(fetchLogs.rejected, (s, a) => { s.loading = false; s.error = a.payload; })
      .addCase(fetchDailyReport.fulfilled, (s, a) => { s.dailyReport = a.payload; });
  },
});

export default logsSlice.reducer;
