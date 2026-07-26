"""Main FastAPI application entry point with Live PyEnergyPlus Co-Simulation."""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from apps.api.routes import router
import asyncio
import time
import threading
from contextlib import asynccontextmanager
from typing import List
from datetime import datetime, timedelta
from pathlib import Path
import queue
import json

from apps.api.websocket import manager

# Domain and Control imports
from packages.state_engine.normalizer import StateBuilder
from packages.ai.ollama_client import OllamaClient
from packages.control.decision_engine import DecisionEngine
from packages.control.safety_kernel import SafetyKernel
from packages.control.baseline_policy import BaselinePolicy
from packages.control.objective import ObjectiveScorer
from packages.sim_adapter.gateway import ActuatorGateway
from packages.sim_adapter.contracts import TelemetryV1
from packages.sim_adapter.eplus_runner import LiveCoSimulation
from packages.control.baseline_simulator import BaselineSimulator

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    task = asyncio.create_task(autonomous_control_loop())
    yield
    # Shutdown
    task.cancel()

app = FastAPI(title="Sentinel Twin API", lifespan=lifespan)

# Allow CORS for local Next.js development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

# Global state for demo purposes
SIMULATION_MODE = "AUTONOMOUS"

async def autonomous_control_loop():
    """Runs the live autonomous Building Management System using PyEnergyPlus and LLM."""
    print("Starting Autonomous BMS Control loop...")
    
    # Initialize Core Components
    hackathon_dir = Path("d:/Hackathon")
    try:
        qwen = await asyncio.to_thread(OllamaClient, hackathon_dir / ".env")
    except Exception as e:
        print(f"Failed to initialize Ollama: {e}")
        # Let it crash if Ollama doesn't exist, as per the user's strict rules
        raise
    state_builder = StateBuilder(hackathon_dir / "configs/zone_map.yaml")
    safety = SafetyKernel(hackathon_dir / "configs/safety_limits.yaml")
    baseline = BaselinePolicy(hackathon_dir / "configs/policy.yaml")
    scorer = ObjectiveScorer()
    decision_engine = DecisionEngine(baseline, scorer)
    actuator = ActuatorGateway(str(hackathon_dir / "data/outputs/baseline-annual-verified/eplusout.sql"))
    
    # Initialize PyEnergyPlus Runner
    idf = hackathon_dir / "models/energyplus/building.epJSON"
    epw = hackathon_dir / "models/energyplus/weather.epw"
    runner = LiveCoSimulation(idf, epw)
    
    # Run Baseline Simulation synchronously before starting AI
    baseline_sim = BaselineSimulator(hackathon_dir)
    try:
        baseline_sim.load_baseline_data()
        has_baseline = True
    except Exception as e:
        print(f"Failed to load baseline: {e}")
        has_baseline = False
    
    # Start the C++ E+ Engine in a background thread so it doesn't block FastAPI
    sim_thread = threading.Thread(target=runner.run, daemon=True)
    sim_thread.start()
    
    comfort_debt_val = 0.0 # Starts at zero — accumulated from real PMV × occupancy × dt
    last_telemetry_point = None
    ai_energy_kwh = 0.0
    baseline_energy_kwh = 0.0
    
    while True:
        try:
            # 1. OBSERVE: Fetch real simulation data from PyEnergyPlus queue (non-blocking)
            try:
                ep_state = runner.state_queue.get_nowait()
                print("[OK] Receiving data from EnergyPlus")
            except queue.Empty:
                await asyncio.sleep(0.1)
                continue
                
            current_time = ep_state["time"]
            
            # Map zones to TelemetryV1 (sim_adapter contract)
            raw_temps = {
                'PERIMETER_MID_ZN_1': ep_state.get('z1_temp', 22.0),
                'CORE_MID': ep_state.get('z2_temp', 22.0)
            }
            
            raw_pmvs = {
                'PERIMETER_MID_ZN_1': ep_state.get('z1_pmv', 0.0),
                'CORE_MID': ep_state.get('z2_pmv', 0.0)
            }
            
            # Use real outdoor temperature from EnergyPlus
            real_outdoor_temp = ep_state.get('out_temp', 0.0)
            if real_outdoor_temp == 0.0:
                real_outdoor_temp = 22.0  # Reasonable default only if E+ handle failed
            
            telemetry = TelemetryV1(
                timestamp=current_time,
                zone_temperatures=raw_temps,
                outdoor_temperature=real_outdoor_temp,
                hvac_power=0.0, # Placeholder, will update after coils
                zone_ppd=raw_pmvs
            )
            
            # Extract new E+ Variables
            real_occ_z1 = ep_state.get('z1_occ', 0.0)
            real_occ_z2 = ep_state.get('z2_occ', 0.0)
            real_pmv_z1 = ep_state.get('z1_pmv', 0.0)
            real_pmv_z2 = ep_state.get('z2_pmv', 0.0)
            
            z1_rh = ep_state.get('z1_rh', 50.0)
            z2_rh = ep_state.get('z2_rh', 50.0)
            cool_coil_pwr = ep_state.get('cool_coil_pwr', 0.0) / 1000.0
            heat_coil_pwr = ep_state.get('heat_coil_pwr', 0.0) / 1000.0
            fan_pwr = ep_state.get('fan_pwr', 0.0) / 1000.0
            
            real_hvac_power = cool_coil_pwr + heat_coil_pwr + fan_pwr
            telemetry.hvac_power = real_hvac_power
            
            # Approximate PPD from PMV is removed because we now fetch real PPD
            # from EnergyPlus directly via z1_ppd, z2_ppd
            ppd_z1 = ep_state.get('z1_ppd', 5.0)
            ppd_z2 = ep_state.get('z2_ppd', 5.0)

            # Cumulative Energy Tracking (15 min timestep = 0.25 hours)
            baseline_before = baseline_energy_kwh
            ai_before = ai_energy_kwh
            
            ai_increment = real_hvac_power * 0.25
            ai_energy_kwh += ai_increment
            
            baseline_pwr = 0.0
            if has_baseline:
                baseline_pwr = baseline_sim.get_baseline_power(current_time)
                baseline_increment = baseline_pwr * 0.25
                baseline_energy_kwh += baseline_increment
            else:
                baseline_increment = 0.0
                baseline_energy_kwh += 0.0
            # ENERGYPLUS TIMESTEP removed, output moved to eplus_runner.py
            
            # Normalize into generic BuildingStateV1
            state = state_builder.build(telemetry)
            print("================ BUILDING STATE ================")
            print(state.model_dump_json(indent=2))
            print("=================================================")
            
            # Use Real Occupancy from E+ instead of time-based mock
            total_occupancy = real_occ_z1 + real_occ_z2
            
            # Dynamic carbon (g/kWh)
            hour_float = current_time.hour + current_time.minute / 60.0
            carbon = 300.0 + 100.0 * (hour_float / 24.0) + (50 if 14 <= hour_float <= 18 else 0)

            # Update continuous comfort debt (OccupancyWeight * |PMV| * Time)
            # Time step is 15 mins (0.25 hours)
            pmv_z1 = raw_pmvs['PERIMETER_MID_ZN_1']
            pmv_z2 = raw_pmvs['CORE_MID']
            debt_increment = (real_occ_z1 * abs(pmv_z1) * 0.25) + (real_occ_z2 * abs(pmv_z2) * 0.25)
            comfort_debt_val += debt_increment

            # 2. REASON: Ask Qwen for action via MCP/Local
            ai_proposal = None
            if SIMULATION_MODE == "AUTONOMOUS":
                system_prompt = (
                    "You are a Building BMS AI. Minimize energy while keeping PPD < 20%.\n"
                    "CRITICAL: You MUST ONLY output actuator IDs from the following list:\n"
                    "- PERIMETER_MID_ZN_1_COOLING_SETPOINT\n"
                    "- CORE_MID_COOLING_SETPOINT\n"
                    "DO NOT invent or hallucinate other actuator names. If you do, the command will be rejected."
                )
                state_json = state.model_dump_json()
                user_prompt = f"Current State: {state_json}\nCarbon: {carbon}\nPropose a setpoint action."
                
                critic_feedback = None
                
                # Infinite loop as requested by user - NO SILENT FALLBACK
                while True:
                    start_inf = time.time()
                    try:
                        ai_proposal = await asyncio.to_thread(
                            qwen.complete_structured, system_prompt, user_prompt, critic_feedback
                        )
                        decision = decision_engine.build_candidates(state, ai_proposal)
                        
                        # Validate against allowed actuators
                        valid_actuators = ["perimeter_mid_zn_1_cooling_setpoint", "core_mid_cooling_setpoint"]
                        if ai_proposal.actuator_id.lower() not in valid_actuators:
                            print(f"[AI] Reflection triggered. Action rejected: Actuator '{ai_proposal.actuator_id}' is not in the allowed list.")
                            critic_feedback = f"REJECTED: Actuator {ai_proposal.actuator_id} is invalid. Use ONLY PERIMETER_MID_ZN_1_COOLING_SETPOINT or CORE_MID_COOLING_SETPOINT."
                            continue
                        
                        validation = safety.evaluate(decision, state)
                        
                        print("================ SAFETY ================")
                        print(f"Requested Action: {ai_proposal.actuator_id} -> {ai_proposal.target_value}")
                        print(f"Accepted?: {'YES' if validation.safe else 'NO'}")
                        print(f"Reason: {validation.message}")
                        print(f"Clipped?: {'YES' if validation.clipped_actions else 'NO'}")
                        print(f"Reflection?: {'NO' if validation.safe else 'YES'}")
                        print("=================================================")
                        
                        if validation.safe:
                            print("================ AI DECISION ================")
                            print(f"Model: {ai_proposal.model_name if hasattr(ai_proposal, 'model_name') else 'ollama-qwen3'}")
                            print(f"Prompt: {user_prompt}")
                            print(f"Inference latency: {(time.time() - start_inf)*1000:.0f} ms")
                            print("Tokens/sec: N/A")
                            print(f"Confidence: {ai_proposal.confidence_score}")
                            print(f"Reasoning: {ai_proposal.rationale if hasattr(ai_proposal, 'rationale') else 'N/A'}")
                            print(f"Returned JSON: {ai_proposal.model_dump_json()}")
                            print("=================================================")
                            final_decision = decision
                            final_validation = validation
                            break
                        else:
                            print(f"[AI] Reflection triggered. Action rejected: {validation.message}")
                            critic_feedback = f"REJECTED: {validation.message}. Try again."
                    except Exception as e:
                        print(f"[AI] Exception in loop: {e}")
                        await asyncio.sleep(2)
            else:
                final_decision = decision_engine.build_candidates(state, None)
                final_validation = safety.evaluate(final_decision, state)
            
            # Extract applied setpoints
            z1_sp = 22.0; z2_sp = 22.0
            
            for a in final_validation.clipped_actions:
                aid = a.actuator_id.lower()
                if aid == "perimeter_mid_zn_1_cooling_setpoint": z1_sp = a.value
                elif aid == "core_mid_cooling_setpoint": z2_sp = a.value
            
            # Print the required audit block
            print("=====================================================")
            print("CLOSED LOOP ACTUATION DISPATCH")
            print(f"Requested Action: {ai_proposal.actuator_id if ai_proposal else 'NONE'}")
            print(f"Resolved Actuators: z1_setpoint={z1_sp}, z2_setpoint={z2_sp}")
            print(f"Telemetry Before: Pwr={real_hvac_power:.2f}kW, Z1={raw_temps['PERIMETER_MID_ZN_1']:.1f}°C")
            print("=====================================================")
            
            # 3. EXECUTE: Send Action back to EnergyPlus Co-Simulation loop
            runner.action_queue.put({
                'z1_setpoint': z1_sp,
                'z2_setpoint': z2_sp
            })
            
            # Store Memory to SQL Gateway
            actuator.execute(final_validation.clipped_actions)

            # Calculate savings
            if has_baseline:
                energy_savings = baseline_energy_kwh - ai_energy_kwh
                co2_avoided = energy_savings * (carbon / 1000.0) # approx g to kg
            else:
                energy_savings = 0.0
                co2_avoided = 0.0
                
            debug_output = f"""
================ BASELINE DEBUG ================
Current Simulation Time: {current_time.strftime("%H:%M")}
Date used for SQL lookup: Month={current_time.month}, Day={current_time.day}
Hour used for SQL lookup: {current_time.hour + 1}
SQL Row Found: {"YES" if has_baseline and baseline_pwr > 0 else "NO"}
Baseline Power (kW): {baseline_pwr:.2f}
Baseline Energy Before: {baseline_before:.2f}
Baseline Increment: {baseline_increment:.2f}
Baseline Energy After: {baseline_energy_kwh:.2f}
AI Power (kW): {real_hvac_power:.2f}
AI Energy Before: {ai_before:.2f}
AI Increment: {ai_increment:.2f}
AI Energy After: {ai_energy_kwh:.2f}
Energy Savings Formula: {baseline_energy_kwh:.2f} - {ai_energy_kwh:.2f}
Energy Savings Result: {energy_savings:.2f}
CO2 Formula: {energy_savings:.2f} * ({carbon:.2f} / 1000.0)
CO2 Result: {co2_avoided:.2f}
================================================
"""
            print(debug_output)
            
            with open(hackathon_dir / "data/outputs/baseline_debug.log", "w") as f:
                f.write(debug_output)
                
            print("telemetry.energy_today =", ai_energy_kwh)
            print("telemetry.energy_savings =", energy_savings)
            print("telemetry.co2_avoided =", co2_avoided)
            
            # Build current state payload for UI
            telemetry_point = {
                "timestamp": time.time(),
                "sim_time": current_time.strftime("%H:%M"),
                "hvac_power": real_hvac_power,
                "cool_coil_pwr": cool_coil_pwr,
                "fan_pwr": fan_pwr,
                "carbon_intensity": round(carbon),
                "comfort_debt": round(comfort_debt_val, 2),
                "occupancy_ratio": round(total_occupancy, 2),
                "energy_today": ai_energy_kwh,
                "energy_savings": energy_savings,
                "co2_avoided": co2_avoided,
                "pmv": real_pmv_z1,
                "ppd": ppd_z1,
                "zones": {
                    "Z1": {"temp": round(raw_temps['PERIMETER_MID_ZN_1'], 1), "setpoint": z1_sp, "occupants": real_occ_z1},
                    "Z2": {"temp": round(raw_temps['CORE_MID'], 1), "setpoint": z2_sp, "occupants": real_occ_z2}
                },
                "outdoor_temp": telemetry.outdoor_temperature,
                "ai_decision": {
                    "Z1_setpoint": z1_sp,
                    "Z2_setpoint": z2_sp,
                    "rationale": f"[{final_decision.source}] {final_decision.rationale} | Kernel: {final_validation.message}"
                }
            }

            if last_telemetry_point:
                print("================ AFTER ACTUATION ================")
                print(f"Previous HVAC Power: {last_telemetry_point['hvac_power']:.2f}")
                print(f"Current HVAC Power: {telemetry_point['hvac_power']:.2f}")
                print(f"Previous Zone1 Temp: {last_telemetry_point['zones']['Z1']['temp']:.2f}")
                print(f"Current Zone1 Temp: {telemetry_point['zones']['Z1']['temp']:.2f}")
                print(f"Previous Zone2 Temp: {last_telemetry_point['zones']['Z2']['temp']:.2f}")
                print(f"Current Zone2 Temp: {telemetry_point['zones']['Z2']['temp']:.2f}")
                print(f"Previous Cooling Coil: {last_telemetry_point.get('cool_coil_pwr', 0.0):.2f}")
                print(f"Current Cooling Coil: {cool_coil_pwr:.2f}")
                print(f"Previous Fan Power: {last_telemetry_point.get('fan_pwr', 0.0):.2f}")
                print(f"Current Fan Power: {fan_pwr:.2f}")
                print("=================================================")

            last_telemetry_point = telemetry_point
            
            print("================ WEBSOCKET PAYLOAD ================")
            print(json.dumps({
                "energy_today": telemetry_point["energy_today"],
                "baseline_energy": baseline_energy_kwh,
                "energy_savings": telemetry_point["energy_savings"],
                "co2_avoided": telemetry_point["co2_avoided"]
            }, indent=2))
            print("=================================================")

            # Broadcast to Dashboard
            await manager.broadcast(telemetry_point)
            
        except Exception as e:
            print(f"Error in telemetry loop: {e}")
            await asyncio.sleep(1)
            
@app.websocket("/ws/telemetry")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
