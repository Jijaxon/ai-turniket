import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import api from "../../utils/api";

export const fetchUsers = createAsyncThunk("users/fetchAll", async (_, { rejectWithValue }) => {
  try {
    const { data } = await api.get("/users/");
    return data;
  } catch (err) {
    return rejectWithValue(err.response?.data?.detail || "Failed to load users");
  }
});

export const addUser = createAsyncThunk("users/add", async (payload, { rejectWithValue }) => {
  try {
    const { data } = await api.post("/users/add", payload);
    return data;
  } catch (err) {
    return rejectWithValue(err.response?.data?.detail || "Failed to add user");
  }
});

export const deleteUser = createAsyncThunk("users/delete", async (userId, { rejectWithValue }) => {
  try {
    await api.delete(`/users/${userId}`);
    return userId;
  } catch (err) {
    return rejectWithValue(err.response?.data?.detail || "Failed to delete user");
  }
});

const usersSlice = createSlice({
  name: "users",
  initialState: { items: [], total: 0, loading: false, error: null },
  reducers: { clearError: (state) => { state.error = null; } },
  extraReducers: (builder) => {
    builder
      // fetch
      .addCase(fetchUsers.pending, (s) => { s.loading = true; s.error = null; })
      .addCase(fetchUsers.fulfilled, (s, a) => { s.loading = false; s.items = a.payload.users; s.total = a.payload.total; })
      .addCase(fetchUsers.rejected, (s, a) => { s.loading = false; s.error = a.payload; })
      // add
      .addCase(addUser.fulfilled, (s, a) => { s.items.unshift(a.payload); s.total += 1; })
      // delete
      .addCase(deleteUser.fulfilled, (s, a) => { s.items = s.items.filter(u => u.id !== a.payload); s.total -= 1; });
  },
});

export const { clearError } = usersSlice.actions;
export default usersSlice.reducer;
