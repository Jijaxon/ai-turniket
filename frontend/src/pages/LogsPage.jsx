import { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { fetchLogs } from "../store/slices/logsSlice";
import api from "../utils/api";

export default function LogsPage() {
  const dispatch = useDispatch();
  const { items: logs, total, loading } = useSelector((s) => s.logs);
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    const params = filter !== "all" ? { status: filter } : {};
    dispatch(fetchLogs(params));
  }, [dispatch, filter]);

  const exportCsv = async () => {
    const res = await api.get("/logs/export/csv", { responseType: "blob" });
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const a = document.createElement("a");
    a.href = url;
    a.download = `access_logs_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold text-white">Access Logs</h1>
          <p className="text-slate-400 text-sm mt-1">{total} total events</p>
        </div>
        <div className="flex items-center gap-3">
          {/* Filter buttons */}
          {["all", "allowed", "denied"].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition ${
                filter === f
                  ? "bg-indigo-600 text-white"
                  : "border border-slate-600 text-slate-300 hover:bg-slate-700"
              }`}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
          <button
            onClick={exportCsv}
            className="flex items-center gap-2 bg-slate-700 hover:bg-slate-600 text-white px-4 py-1.5 rounded-lg text-sm font-medium transition"
          >
            ⬇ CSV
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-700 text-slate-400 text-xs uppercase tracking-wider">
                <th className="text-left p-4">ID</th>
                <th className="text-left p-4">Timestamp</th>
                <th className="text-left p-4">User</th>
                <th className="text-left p-4">Status</th>
                <th className="text-left p-4">Confidence</th>
                <th className="text-left p-4">Reason</th>
                <th className="text-left p-4">IP</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/50">
              {loading ? (
                <tr><td colSpan={7} className="text-center py-8 text-slate-400">Loading…</td></tr>
              ) : logs.length === 0 ? (
                <tr><td colSpan={7} className="text-center py-8 text-slate-400">No logs found.</td></tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-700/30 transition">
                    <td className="p-4 text-slate-400 font-mono">#{log.id}</td>
                    <td className="p-4 text-slate-300">{new Date(log.timestamp).toLocaleString()}</td>
                    <td className="p-4 text-white font-medium">{log.user_name || <span className="text-slate-500 italic">Unknown</span>}</td>
                    <td className="p-4">
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${
                        log.status === "allowed"
                          ? "bg-green-500/20 text-green-400"
                          : "bg-red-500/20 text-red-400"
                      }`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${log.status === "allowed" ? "bg-green-500" : "bg-red-500"}`} />
                        {log.status.toUpperCase()}
                      </span>
                    </td>
                    <td className="p-4 font-mono text-slate-300">
                      {log.confidence != null ? `${(log.confidence * 100).toFixed(1)}%` : "—"}
                    </td>
                    <td className="p-4 text-slate-400 text-xs max-w-48 truncate">{log.reason || "—"}</td>
                    <td className="p-4 text-slate-400 font-mono text-xs">{log.ip_address || "—"}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
