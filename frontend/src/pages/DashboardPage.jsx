import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { fetchStats, fetchDailyReport } from "../store/slices/logsSlice";
import { fetchUsers } from "../store/slices/usersSlice";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  LineChart, Line, CartesianGrid, Legend,
} from "recharts";

function StatCard({ icon, label, value, color = "indigo" }) {
  const colors = {
    indigo: "bg-indigo-500/20 text-indigo-400 border-indigo-500/30",
    green: "bg-green-500/20 text-green-400 border-green-500/30",
    red: "bg-red-500/20 text-red-400 border-red-500/30",
    yellow: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
  };
  return (
    <div className={`rounded-xl p-5 border ${colors[color]} backdrop-blur`}>
      <div className="text-3xl mb-2">{icon}</div>
      <div className="text-2xl font-bold text-white">{value ?? "—"}</div>
      <div className="text-sm mt-1 opacity-80">{label}</div>
    </div>
  );
}

export default function DashboardPage() {
  const dispatch = useDispatch();
  const { stats, dailyReport } = useSelector((s) => s.logs);

  useEffect(() => {
    dispatch(fetchStats());
    dispatch(fetchDailyReport());
  }, [dispatch]);

  const today = stats?.today;

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
        <p className="text-slate-400 text-sm mt-1">Real-time access control overview</p>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon="✅" label="Allowed Today" value={today?.allowed} color="green" />
        <StatCard icon="❌" label="Denied Today" value={today?.denied} color="red" />
        <StatCard icon="👥" label="Unique Users" value={today?.unique_users} color="indigo" />
        <StatCard icon="📋" label="Total Logs" value={stats?.total_logs} color="yellow" />
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Bar chart */}
        <div className="bg-slate-800 rounded-xl p-5 border border-slate-700">
          <h3 className="text-white font-semibold mb-4">7-Day Access Overview</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={dailyReport}>
              <XAxis dataKey="date" tick={{ fill: "#94a3b8", fontSize: 11 }} tickFormatter={(d) => d.slice(5)} />
              <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} />
              <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8 }} />
              <Legend />
              <Bar dataKey="allowed" fill="#22c55e" radius={[4, 4, 0, 0]} />
              <Bar dataKey="denied" fill="#ef4444" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Line chart */}
        <div className="bg-slate-800 rounded-xl p-5 border border-slate-700">
          <h3 className="text-white font-semibold mb-4">Total Entries Trend</h3>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={dailyReport}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="date" tick={{ fill: "#94a3b8", fontSize: 11 }} tickFormatter={(d) => d.slice(5)} />
              <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} />
              <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8 }} />
              <Line type="monotone" dataKey="total" stroke="#6366f1" strokeWidth={2} dot={{ fill: "#6366f1" }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent logs */}
      <div className="bg-slate-800 rounded-xl border border-slate-700">
        <div className="p-5 border-b border-slate-700">
          <h3 className="text-white font-semibold">Recent Access Events</h3>
        </div>
        <div className="divide-y divide-slate-700">
          {stats?.recent_logs?.length ? (
            stats.recent_logs.map((log) => (
              <div key={log.id} className="flex items-center justify-between p-4">
                <div className="flex items-center gap-3">
                  <span className={`w-2.5 h-2.5 rounded-full ${log.status === "allowed" ? "bg-green-500" : "bg-red-500"}`} />
                  <div>
                    <p className="text-white text-sm font-medium">{log.user_name || "Unknown"}</p>
                    <p className="text-slate-400 text-xs">{new Date(log.timestamp).toLocaleString()}</p>
                  </div>
                </div>
                <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${
                  log.status === "allowed" ? "bg-green-500/20 text-green-400" : "bg-red-500/20 text-red-400"
                }`}>
                  {log.status.toUpperCase()}
                </span>
              </div>
            ))
          ) : (
            <p className="text-slate-400 text-sm p-5">No recent events.</p>
          )}
        </div>
      </div>
    </div>
  );
}
