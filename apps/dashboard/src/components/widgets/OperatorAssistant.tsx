"use client";

import { useState } from "react";
import { MessageSquare, Send, ShieldCheck, X } from "lucide-react";

export default function OperatorAssistant() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: "assistant", content: "Sentinel AI Operator ready. How can I assist you with the building today?" }
  ]);
  const [input, setInput] = useState("");

  const handleSend = async () => {
    if (!input.trim()) return;
    
    // Add user message
    const newMessages = [...messages, { role: "user", content: input }];
    setMessages(newMessages);
    setInput("");
    
    try {
      const res = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input })
      });
      const data = await res.json();
      
      let reply = "";
      if (data.intent?.action_type === "HVAC_SETPOINT_UPDATE") {
        const p = data.intent.proposal;
        reply = `I proposed a ${p.hvac_mode} setpoint of ${p.setpoint}°C for ${p.zone_id}.`;
        
        if (data.intent.kernel_clipped) {
           reply += ` However, the Safety Kernel rejected it and CLIPPED the setpoint to ${data.intent.kernel_clipped}°C for safety reasons.`;
        } else {
           reply += ` The Safety Kernel has verified this request.`;
        }
      } else {
        reply = "I'm not sure how to action that. Try 'cool down the conference room'.";
      }
      
      setMessages([...newMessages, { role: "assistant", content: reply }]);
    } catch (e) {
      setMessages([...newMessages, { role: "assistant", content: "Error connecting to Sentinel backend." }]);
    }
  };

  if (!isOpen) {
    return (
      <button 
        onClick={() => setIsOpen(true)}
        className="fixed bottom-24 right-4 p-4 bg-[var(--color-accent)] text-white rounded-full shadow-lg hover:bg-opacity-80 transition-all z-50 flex items-center justify-center"
      >
        <MessageSquare size={24} />
      </button>
    );
  }

  return (
    <div className="fixed bottom-24 right-4 w-80 h-96 glass-panel flex flex-col z-50 shadow-2xl overflow-hidden border border-[var(--color-accent)]/30">
      <div className="bg-[var(--color-surface)] p-3 border-b border-[var(--color-border)] flex justify-between items-center">
        <div className="flex items-center gap-2">
          <ShieldCheck size={16} className="text-[var(--color-success)]" />
          <span className="font-bold text-sm">Operator Assistant</span>
        </div>
        <button onClick={() => setIsOpen(false)} className="text-[var(--color-secondary)] hover:text-white">
          <X size={16} />
        </button>
      </div>
      
      <div className="flex-1 p-4 overflow-y-auto flex flex-col gap-3">
        {messages.map((msg, idx) => (
          <div key={idx} className={`max-w-[85%] p-3 rounded-lg text-sm ${
            msg.role === "assistant" 
              ? "bg-[var(--color-surface)] border border-[var(--color-border)] self-start" 
              : "bg-[var(--color-accent)] text-white self-end"
          }`}>
            {msg.content}
          </div>
        ))}
      </div>
      
      <div className="p-3 border-t border-[var(--color-border)] bg-[var(--color-surface)] flex gap-2">
        <input 
          type="text" 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ask Sentinel..."
          className="flex-1 bg-transparent border border-[var(--color-border)] rounded px-3 py-2 text-sm outline-none focus:border-[var(--color-accent)]"
        />
        <button 
          onClick={handleSend}
          className="p-2 bg-[var(--color-accent)] rounded text-white hover:bg-opacity-80"
        >
          <Send size={16} />
        </button>
      </div>
    </div>
  );
}
