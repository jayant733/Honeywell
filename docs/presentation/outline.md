# Sentinel Twin: Hackathon Pitch Outline

**Target Length:** 5 Minutes

## 1. The Hook (0:00 - 0:45)
- **Problem**: Commercial buildings waste 30% of their HVAC energy. Existing PID controllers are dumb; existing AI solutions are "black boxes" that facility managers don't trust.
- **Solution**: Sentinel Twin. The intelligence of a local LLM (Qwen 14B), strictly governed by an un-bypassable physical Safety Kernel. 

## 2. The Demo (0:45 - 2:30)
- **Live UI**: Show the cinematic 3D Digital Twin and live KPI panel.
- **The LLM in Action**: The AI detects an upcoming heatwave and a dirty grid at 4 PM. It proposes a pre-cooling strategy.
- **The Safety Guarantee**: Show the "AI Control Center". The AI hallucinated a dangerously low setpoint (14°C). Watch the Safety Kernel instantly catch it, CLIP it to 18°C, and allow operations to continue safely. 
- **The Chatbot**: Use natural language to cool the conference room.

## 3. The Evidence (2:30 - 3:45)
- **Executive Analytics**: Show the Pareto chart.
- **Result**: We achieved 48% energy savings and avoided 1.2 tons of carbon, while comfort debt only rose by a negligible 0.12 °C-hours.

## 4. The Tech Stack & Ask (3:45 - 5:00)
- **Stack**: FastAPI, Next.js 15, Zustand, React Three Fiber, Qwen 14B.
- **Impact**: We've proven that LLMs *can* safely operate critical infrastructure, bridging the gap between Silicon Valley AI and industrial engineering.
