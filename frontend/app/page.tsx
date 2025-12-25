"use client";
import { useState, useEffect } from "react";
import axios from "axios";
import SimulationCanvas from "@/components/SimulationCanvas";
import AgentFeed from "@/components/AgentFeed";
import MathRenderer from "@/components/MathRenderer"; // <--- NEW IMPORT
import { Play, RotateCw } from "lucide-react";

// Configuration
const API_URL = "http://127.0.0.1:8000"; 

export default function Dashboard() {
  const [objective, setObjective] = useState("Unify Loop Quantum Gravity with String Theory");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [state, setState] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  // Polling Logic
  useEffect(() => {
    if (!sessionId) return;

    const interval = setInterval(async () => {
      try {
        const res = await axios.get(`${API_URL}/api/research/${sessionId}`);
        setState(res.data);
        
        // Auto-scroll logs
        const logEnd = document.getElementById("log-end");
        logEnd?.scrollIntoView({ behavior: "smooth" });
        
      } catch (err) {
        console.error("Polling error", err);
      }
    }, 2000); // Poll every 2 seconds

    return () => clearInterval(interval);
  }, [sessionId]);

  const startResearch = async () => {
    setLoading(true);
    try {
      const res = await axios.post(`${API_URL}/api/research`, { objective });
      setSessionId(res.data.session_id);
    } catch (err) {
      alert("Failed to connect to Python Backend. Is it running?");
      setLoading(false);
    }
  };

  const hypothesis = state?.current_hypothesis || {};
  // Handle case where simulation_data is a summary string or actual data
  const simData = Array.isArray(hypothesis.simulation_data?.data) 
    ? hypothesis.simulation_data.data 
    : [];

  return (
    <main className="h-screen w-full flex flex-col p-2 gap-2">
      {/* HEADER */}
      <header className="h-16 glass-panel rounded-xl flex items-center justify-between px-6 shrink-0">
        <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-cyan-500 rounded-full animate-pulse" />
            <h1 className="font-bold text-xl tracking-[0.2em] neon-text">QUANTUM_GRAVITY_AGENT</h1>
        </div>
        
        <div className="flex gap-2 w-1/2">
            <input 
              className="bg-black/50 border border-gray-700 rounded px-4 py-1 w-full text-sm focus:border-cyan-500 outline-none"
              value={objective}
              onChange={(e) => setObjective(e.target.value)}
              disabled={!!sessionId}
            />
            <button 
                onClick={startResearch}
                disabled={loading || !!sessionId}
                className="bg-cyan-600 hover:bg-cyan-500 text-black font-bold px-6 py-1 rounded flex items-center gap-2 transition-all disabled:opacity-50"
            >
                {loading ? <RotateCw className="animate-spin w-4 h-4"/> : <Play className="w-4 h-4"/>}
                INITIATE
            </button>
        </div>
      </header>

      {/* MAIN CONTENT GRID */}
      <div className="flex-1 grid grid-cols-12 gap-2 min-h-0">
        
        {/* LEFT: VISUALIZATION (8 Cols) */}
        <div className="col-span-8 glass-panel rounded-xl relative overflow-hidden flex flex-col">
            <div className="absolute top-0 left-0 w-full p-4 bg-gradient-to-b from-black/80 to-transparent z-10 pointer-events-none">
                 <h2 className="text-2xl font-bold text-white/90">
                    {hypothesis.title || "AWAITING_HYPOTHESIS..."}
                 </h2>
                 <p className="text-sm text-gray-400 mt-1 max-w-2xl line-clamp-2">
                    {hypothesis.description}
                 </p>
            </div>
            
            {/* 3D Canvas */}
            <SimulationCanvas data={simData} status={hypothesis.status} />
        </div>

        {/* RIGHT: DATA & LOGS (4 Cols) */}
        <div className="col-span-4 flex flex-col gap-2 min-h-0">
            
            {/* Top: Equation Card */}
            <div className="h-1/3 glass-panel rounded-xl p-4 flex flex-col overflow-y-auto relative">
                <h3 className="text-xs font-bold text-gray-500 mb-2 uppercase">Formalism</h3>
                <div className="flex-1 flex items-center justify-center p-2">
                    {hypothesis.mathematical_formulation ? (
                        <MathRenderer expression={hypothesis.mathematical_formulation} />
                    ) : (
                        <span className="text-gray-700 italic">No equation generated yet.</span>
                    )}
                </div>
            </div>

            {/* Bottom: Logs */}
            <div className="h-2/3 min-h-0">
                <AgentFeed messages={state?.messages || []} />
            </div>
        </div>
      </div>
    </main>
  );
}