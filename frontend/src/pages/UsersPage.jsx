import { useEffect, useRef, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { fetchUsers, addUser, deleteUser } from "../store/slices/usersSlice";

export default function UsersPage() {
  const dispatch = useDispatch();
  const { items: users, total, loading, error } = useSelector((s) => s.users);

  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", email: "", department: "" });
  const [faceImage, setFaceImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState(null);
  const fileRef = useRef(null);

  useEffect(() => { dispatch(fetchUsers()); }, [dispatch]);

  const handleFile = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      setFaceImage(ev.target.result);
      setPreview(ev.target.result);
    };
    reader.readAsDataURL(file);
  };

  const handleSubmit = async () => {
    if (!form.name || !form.email || !faceImage) {
      setFormError("Name, email and face photo are required.");
      return;
    }
    setSubmitting(true);
    setFormError(null);
    try {
      await dispatch(addUser({ ...form, face_image: faceImage })).unwrap();
      setShowForm(false);
      setForm({ name: "", email: "", department: "" });
      setFaceImage(null);
      setPreview(null);
    } catch (err) {
      setFormError(typeof err === "string" ? err : "Failed to register user");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id, name) => {
    if (!confirm(`Delete user "${name}"?`)) return;
    dispatch(deleteUser(id));
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Users</h1>
          <p className="text-slate-400 text-sm mt-1">{total} registered users</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition"
        >
          + Add User
        </button>
      </div>

      {/* Add user modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
          <div className="bg-slate-800 rounded-2xl border border-slate-700 w-full max-w-md p-6">
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-lg font-semibold text-white">Register New User</h2>
              <button onClick={() => setShowForm(false)} className="text-slate-400 hover:text-white text-xl">×</button>
            </div>

            {formError && (
              <div className="mb-4 p-3 bg-red-900/40 border border-red-500/40 rounded-lg text-red-300 text-sm">{formError}</div>
            )}

            <div className="space-y-3">
              <input
                placeholder="Full Name *"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2.5 text-white text-sm focus:outline-none focus:border-indigo-500"
              />
              <input
                placeholder="Email *"
                type="email"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2.5 text-white text-sm focus:outline-none focus:border-indigo-500"
              />
              <input
                placeholder="Department"
                value={form.department}
                onChange={(e) => setForm({ ...form, department: e.target.value })}
                className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2.5 text-white text-sm focus:outline-none focus:border-indigo-500"
              />

              {/* Face photo */}
              <div
                onClick={() => fileRef.current?.click()}
                className="border-2 border-dashed border-slate-600 rounded-xl p-4 cursor-pointer hover:border-indigo-500 transition text-center"
              >
                {preview ? (
                  <img src={preview} alt="face preview" className="w-24 h-24 object-cover rounded-full mx-auto" />
                ) : (
                  <>
                    <div className="text-3xl mb-1">📸</div>
                    <p className="text-slate-400 text-sm">Click to upload face photo</p>
                  </>
                )}
              </div>
              <input ref={fileRef} type="file" accept="image/*" onChange={handleFile} className="hidden" />
            </div>

            <div className="flex gap-3 mt-5">
              <button
                onClick={() => setShowForm(false)}
                className="flex-1 py-2.5 rounded-lg border border-slate-600 text-slate-300 text-sm hover:bg-slate-700 transition"
              >
                Cancel
              </button>
              <button
                onClick={handleSubmit}
                disabled={submitting}
                className="flex-1 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm font-medium transition"
              >
                {submitting ? "Registering…" : "Register User"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Users grid */}
      {loading ? (
        <p className="text-slate-400">Loading users…</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {users.map((user) => (
            <div key={user.id} className="bg-slate-800 rounded-xl border border-slate-700 p-4">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-indigo-600 flex items-center justify-center font-bold text-white">
                    {user.name[0].toUpperCase()}
                  </div>
                  <div>
                    <p className="text-white font-medium text-sm">{user.name}</p>
                    <p className="text-slate-400 text-xs">{user.email}</p>
                  </div>
                </div>
                <button
                  onClick={() => handleDelete(user.id, user.name)}
                  className="text-slate-500 hover:text-red-400 text-xs transition"
                >
                  🗑
                </button>
              </div>
              <div className="mt-3 flex items-center gap-2 flex-wrap">
                {user.department && (
                  <span className="text-xs bg-slate-700 text-slate-300 px-2 py-0.5 rounded">
                    {user.department}
                  </span>
                )}
                <span className={`text-xs px-2 py-0.5 rounded font-medium ${
                  user.has_face_encoding
                    ? "bg-green-500/20 text-green-400"
                    : "bg-yellow-500/20 text-yellow-400"
                }`}>
                  {user.has_face_encoding ? "✓ Face enrolled" : "⚠ No face"}
                </span>
                <span className={`text-xs px-2 py-0.5 rounded ${
                  user.is_active ? "bg-slate-700 text-slate-300" : "bg-red-500/20 text-red-400"
                }`}>
                  {user.is_active ? "Active" : "Inactive"}
                </span>
              </div>
            </div>
          ))}
          {users.length === 0 && (
            <p className="text-slate-400 col-span-3 text-center py-8">No users registered yet.</p>
          )}
        </div>
      )}
    </div>
  );
}
