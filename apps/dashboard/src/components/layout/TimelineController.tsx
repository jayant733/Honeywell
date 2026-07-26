"use client";

import { useState } from "react";
import { Play, Pause, SkipBack, SkipForward } from "lucide-react";
import { useStore } from "@/lib/store";

export default function TimelineController() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(100); // 100% is live
  const setMode = useStore((state) => state.setMode);

  const handleScrub = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseInt(e.target.value);
    setProgress(val);
    
    if (val < 100) {
      setMode('REPLAY');
      // In real implementation: fetch `/api/replay?time=...` and update `setTelemetry`
    } else {
      setMode('SHADOW'); // Back to live
    }
  };

  return (
    <div className="fixed bottom-0 left-0 right-0 glass-panel border-t border-[var(--color-border)] p-4 flex items-center justify-between z-50 rounded-none bg-black/80">
      <div className="flex items-center gap-4">
        <button className="p-2 hover:bg-[var(--color-surface)] rounded text-[var(--color-secondary)] hover:text-[var(--color-primary)]">
          <SkipBack size={20} />
        </button>
        <button 
          onClick={() => setIsPlaying(!isPlaying)}
          className="p-3 bg-[var(--color-primary)] text-black rounded-full hover:bg-[var(--color-secondary)] transition-colors"
        >
          {isPlaying ? <Pause size={20} /> : <Play size={20} />}
        </button>
        <button className="p-2 hover:bg-[var(--color-surface)] rounded text-[var(--color-secondary)] hover:text-[var(--color-primary)]">
          <SkipForward size={20} />
        </button>
      </div>

      <div className="flex-1 mx-8 flex items-center gap-4">
        <span className="text-xs font-mono text-[var(--color-secondary)]">00:00</span>
        <input 
          type="range" 
          min="0" 
          max="100" 
          value={progress}
          onChange={handleScrub}
          className="w-full h-2 bg-[var(--color-surface)] rounded-lg appearance-none cursor-pointer accent-[var(--color-accent)]"
        />
        <span className="text-xs font-mono text-[var(--color-primary)] font-bold">LIVE</span>
      </div>

      <div className="text-xs font-bold px-3 py-1 bg-[var(--color-surface)] rounded border border-[var(--color-border)]">
        {progress < 100 ? <span className="text-[var(--color-energy)]">REPLAY MODE</span> : <span className="text-[var(--color-success)]">LIVE TELEMETRY</span>}
      </div>
    </div>
  );
}
