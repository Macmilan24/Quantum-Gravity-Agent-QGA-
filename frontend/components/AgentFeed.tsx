import { ScrollArea } from "@/components/ui/scroll-area" // If using shadcn, otherwise simple div
import { motion, AnimatePresence } from "framer-motion";
import { Terminal, Brain, FileText, Activity } from "lucide-react";

export default function AgentFeed({ messages }: { messages: string[] }) {
  return (
    <div className="glass-panel h-full flex flex-col p-4 rounded-xl overflow-hidden">
      <div className="flex items-center gap-2 mb-4 border-b border-gray-800 pb-2">
        <Terminal className="w-4 h-4 text-green-400" />
        <h2 className="text-sm font-bold text-gray-300 tracking-widest">NEURAL_LOG</h2>
      </div>
      
      <div className="flex-1 overflow-y-auto space-y-3 font-mono text-xs">
        {messages.length === 0 && <span className="text-gray-600">Waiting for initialization...</span>}
        
        {messages.map((msg, i) => {
          // Color code agents
          let color = "text-gray-400";
          let Icon = Activity;
          if (msg.includes("Architect")) { color = "text-purple-400"; Icon = Brain; }
          if (msg.includes("Archivist")) { color = "text-yellow-400"; Icon = FileText; }
          if (msg.includes("Formalist")) { color = "text-blue-400"; }
          if (msg.includes("Simulator")) { color = "text-cyan-400"; }

          return (
            <motion.div 
              key={i}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className={`flex items-start gap-2 ${color}`}
            >
              <Icon className="w-3 h-3 mt-1 shrink-0" />
              <span>{msg}</span>
            </motion.div>
          );
        })}
        {/* Auto-scroll anchor */}
        <div id="log-end" /> 
      </div>
    </div>
  );
}