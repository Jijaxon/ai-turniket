import { useRef, useState, useCallback, useEffect } from "react";
import api from "../utils/api";

const STATUS_CONFIG = {
  allowed: {
    bg: "bg-green-500/20 border-green-500/50",
    text: "text-green-400",
    icon: "✅",
    label: "ACCESS GRANTED",
  },
  denied: {
    bg: "bg-red-500/20 border-red-500/50",
    text: "text-red-400",
    icon: "❌",
    label: "ACCESS DENIED",
  },
};

export default function RecognitionPage() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const intervalRef = useRef(null);

  const [cameraOn, setCameraOn] = useState(false);
  const [autoMode, setAutoMode] = useState(false);
  const [result, setResult] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState(null);

  // Brauzer konsolida ishga tushiring
  console.log("Protocol:", window.location.protocol);
  console.log("Hostname:", window.location.hostname);

// Kamerani to'g'ridan-to'g'ri tekshirish
  navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => console.log("✅ Camera working!", stream))
    .catch(err => console.error("❌ Camera error:", err));

  // ── Camera ────────────────────────────────────────────────────────────────
  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480, facingMode: "user" },
      });
      streamRef.current = stream;
      if (videoRef.current) videoRef.current.srcObject = stream;
      setCameraOn(true);
      setError(null);
    } catch {
      setError("Camera access denied. Please allow camera permission.");
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
    setCameraOn(false);
    setAutoMode(false);
    clearInterval(intervalRef.current);
  };

  useEffect(() => () => stopCamera(), []);

  // ── Capture & Recognise ───────────────────────────────────────────────────
  const captureAndRecognize = useCallback(async () => {
    if (!videoRef.current || !canvasRef.current || processing) return;
    setProcessing(true);

    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0);

    const base64 = canvas.toDataURL("image/jpeg", 0.85);

    try {
      const { data } = await api.post("/recognize-face", { image: base64 });
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || "Recognition request failed");
    } finally {
      setProcessing(false);
    }
  }, [processing]);

  // ── Auto mode ─────────────────────────────────────────────────────────────
  useEffect(() => {
    if (autoMode && cameraOn) {
      intervalRef.current = setInterval(captureAndRecognize, 2500);
    } else {
      clearInterval(intervalRef.current);
    }
    return () => clearInterval(intervalRef.current);
  }, [autoMode, cameraOn, captureAndRecognize]);

  const cfg = result ? STATUS_CONFIG[result.status] : null;

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Face Recognition</h1>
        <p className="text-slate-400 text-sm mt-1">Real-time webcam access control</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Camera panel */}
        <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
          <div className="p-4 border-b border-slate-700 flex items-center justify-between">
            <h3 className="font-semibold text-white">Live Camera</h3>
            <div className={`flex items-center gap-2 text-xs ${cameraOn ? "text-green-400" : "text-slate-400"}`}>
              <div className={`w-2 h-2 rounded-full ${cameraOn ? "bg-green-500 animate-pulse" : "bg-slate-500"}`} />
              {cameraOn ? "LIVE" : "OFF"}
            </div>
          </div>

          <div className="relative bg-slate-900 aspect-video flex items-center justify-center">
            {!cameraOn && (
              <div className="text-center text-slate-500">
                <div className="text-5xl mb-3">📷</div>
                <p className="text-sm">Camera is off</p>
              </div>
            )}
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className={`w-full h-full object-cover ${!cameraOn ? "hidden" : ""}`}
            />
            {processing && (
              <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                <div className="text-white text-sm animate-pulse">🔍 Analysing…</div>
              </div>
            )}
          </div>

          <canvas ref={canvasRef} className="hidden" />

          <div className="p-4 flex flex-wrap gap-2">
            {!cameraOn ? (
              <button onClick={startCamera} className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white py-2.5 rounded-lg font-medium text-sm transition">
                📷 Start Camera
              </button>
            ) : (
              <>
                <button
                  onClick={captureAndRecognize}
                  disabled={processing}
                  className="flex-1 bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white py-2.5 rounded-lg font-medium text-sm transition"
                >
                  {processing ? "Processing…" : "🔍 Scan Face"}
                </button>
                <button
                  onClick={() => setAutoMode((v) => !v)}
                  className={`flex-1 py-2.5 rounded-lg font-medium text-sm transition border ${
                    autoMode
                      ? "bg-yellow-500/20 border-yellow-500/50 text-yellow-400"
                      : "border-slate-600 text-slate-300 hover:bg-slate-700"
                  }`}
                >
                  {autoMode ? "⏹ Stop Auto" : "▶ Auto Mode"}
                </button>
                <button onClick={stopCamera} className="px-4 py-2.5 rounded-lg text-sm text-red-400 border border-red-500/30 hover:bg-red-900/20 transition">
                  Stop
                </button>
              </>
            )}
          </div>

          {error && (
            <div className="mx-4 mb-4 p-3 bg-red-900/40 border border-red-500/40 rounded-lg text-red-300 text-sm">
              {error}
            </div>
          )}
        </div>

        {/* Result panel */}
        <div className="bg-slate-800 rounded-xl border border-slate-700 flex flex-col">
          <div className="p-4 border-b border-slate-700">
            <h3 className="font-semibold text-white">Recognition Result</h3>
          </div>

          <div className="flex-1 flex items-center justify-center p-8">
            {!result ? (
              <div className="text-center text-slate-500">
                <div className="text-6xl mb-4">🎯</div>
                <p className="text-sm">Scan a face to see the result</p>
              </div>
            ) : (
              <div className={`w-full rounded-xl p-6 border ${cfg.bg} text-center`}>
                <div className="text-6xl mb-3">{cfg.icon}</div>
                <div className={`text-2xl font-bold mb-4 ${cfg.text}`}>{cfg.label}</div>

                {result.status === "allowed" && (
                  <div className="space-y-2 text-left bg-black/20 rounded-lg p-4">
                    <p className="text-white"><span className="text-slate-400 text-sm">Name:</span> <strong>{result.name}</strong></p>
                    <p className="text-white"><span className="text-slate-400 text-sm">User ID:</span> #{result.user_id}</p>
                    <p className="text-white">
                      <span className="text-slate-400 text-sm">Confidence:</span>{" "}
                      <span className="text-green-400 font-mono">{(result.confidence * 100).toFixed(1)}%</span>
                    </p>
                  </div>
                )}

                {result.status === "denied" && (
                  <div className="bg-black/20 rounded-lg p-4">
                    <p className="text-red-300 text-sm">{result.reason}</p>
                    {result.confidence !== null && (
                      <p className="text-slate-400 text-xs mt-1">
                        Best match confidence: {(result.confidence * 100).toFixed(1)}%
                      </p>
                    )}
                  </div>
                )}

                <p className="text-slate-500 text-xs mt-4">
                  {new Date(result.timestamp).toLocaleTimeString()}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
