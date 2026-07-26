"""PyEnergyPlus Runtime Wrapper for Live Co-Simulation."""

import sys
import os
import glob
from pathlib import Path
import queue
import time
from datetime import datetime, timedelta

def trace_energyplus_startup():
    print("=" * 60)
    print("ENERGYPLUS STARTUP TRACE")
    print("=" * 60)
    
    # 1. Environment variables
    python_path = os.environ.get('PYTHONPATH', 'None')
    print(f"[TRACE] PYTHONPATH environment variable: {python_path}")
    print(f"[TRACE] sys.path:")
    for p in sys.path:
        print(f"  - {p}")
        
    # 2. Search for EnergyPlus installation
    print("[TRACE] Searching for EnergyPlus installation in C:\\...")
    eplus_installs = glob.glob("C:\\EnergyPlusV*")
    eplus_path = None
    if eplus_installs:
        # Pick the latest version
        eplus_installs.sort(reverse=True)
        eplus_path = eplus_installs[0]
        print(f"[TRACE] Found EnergyPlus installations: {eplus_installs}")
        print(f"[TRACE] Selected EnergyPlus path: {eplus_path}")
        
        # Inject into sys.path so we can import pyenergyplus if it isn't already there
        eplus_python_api = os.path.join(eplus_path)
        if eplus_python_api not in sys.path:
            sys.path.append(eplus_python_api)
            print(f"[TRACE] Appended {eplus_python_api} to sys.path")
    else:
        print("[TRACE] No EnergyPlus installations found in C:\\")
        
    # 3. Import pyenergyplus
    try:
        from pyenergyplus.api import EnergyPlusAPI
        print("[TRACE] pyenergyplus module imported SUCCESSFULLY.")
        api = EnergyPlusAPI()
        print("[TRACE] EnergyPlusAPI initialized SUCCESSFULLY.")
        return api
    except Exception as e:
        print(f"[TRACE] FAILED to import or initialize pyenergyplus: {str(e)}")
        print("=" * 60)
        raise RuntimeError(f"EnergyPlus failed to start: {str(e)}") from e

class LiveCoSimulation:
    def __init__(self, idf_path: Path, epw_path: Path):
        self.idf_path = idf_path
        self.epw_path = epw_path
        
        print(f"[TRACE] IDF Path: {self.idf_path}")
        print(f"[TRACE] EPW Path: {self.epw_path}")
        
        self.state_queue = queue.Queue()
        self.action_queue = queue.Queue()
        
        self.api = trace_energyplus_startup()
        
        print("[TRACE] Creating new EnergyPlus State...")
        self.state = self.api.state_manager.new_state()
        print("[TRACE] State creation SUCCESSFUL.")
        
        self._handles = {}
        self._last_meters = {'hvac': 0.0, 'cool': 0.0, 'heat': 0.0, 'fan': 0.0}
        self.sim_time = datetime(2023, 1, 1, 0, 0)
        
    def _callback_begin_zone_timestep(self, state) -> None:
        """Called by EnergyPlus at each timestep."""
        if not self.api.exchange.api_data_fully_ready(state):
            return
            
        # 1. Map Handles if not done
        if not self._handles:
            self._handles['z1_temp'] = self.api.exchange.get_variable_handle(state, "Zone Mean Air Temperature", "PERIMETER_MID_ZN_1")
            self._handles['z2_temp'] = self.api.exchange.get_variable_handle(state, "Zone Mean Air Temperature", "CORE_MID")
            self._handles['z1_occ'] = self.api.exchange.get_variable_handle(state, "Zone People Occupant Count", "PERIMETER_MID_ZN_1")
            self._handles['z2_occ'] = self.api.exchange.get_variable_handle(state, "Zone People Occupant Count", "CORE_MID")
            self._handles['z1_pmv'] = self.api.exchange.get_variable_handle(state, "Zone Thermal Comfort Fanger Model PMV", "PERIMETER_MID_ZN_1 PEOPLE")
            self._handles['z2_pmv'] = self.api.exchange.get_variable_handle(state, "Zone Thermal Comfort Fanger Model PMV", "CORE_MID PEOPLE")
            self._handles['z1_ppd'] = self.api.exchange.get_variable_handle(state, "Zone Thermal Comfort Fanger Model PPD", "PERIMETER_MID_ZN_1 PEOPLE")
            self._handles['z2_ppd'] = self.api.exchange.get_variable_handle(state, "Zone Thermal Comfort Fanger Model PPD", "CORE_MID PEOPLE")
            self._handles['z1_rh'] = self.api.exchange.get_variable_handle(state, "Zone Air Relative Humidity", "PERIMETER_MID_ZN_1")
            self._handles['z2_rh'] = self.api.exchange.get_variable_handle(state, "Zone Air Relative Humidity", "CORE_MID")
            
            # Meters (Accumulated Joules)
            self._handles['meter_hvac'] = self.api.exchange.get_meter_handle(state, "Electricity:Facility")
            self._handles['meter_cool'] = self.api.exchange.get_meter_handle(state, "Cooling:Electricity")
            self._handles['meter_heat'] = self.api.exchange.get_meter_handle(state, "Heating:Electricity")
            self._handles['meter_fan'] = self.api.exchange.get_meter_handle(state, "Fans:Electricity")
            
            # Actuators (Schedules)
            self._handles['clg_sch'] = self.api.exchange.get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "CLGSETP_SCH")
            self._handles['htg_sch'] = self.api.exchange.get_actuator_handle(state, "Schedule:Compact", "Schedule Value", "HTGSETP_SCH")
            
            # Additional for telemetry
            self._handles['out_temp'] = self.api.exchange.get_variable_handle(state, "Site Outdoor Air Drybulb Temperature", "Environment")
            
        # 2. Extract Data
        z1_t = self.api.exchange.get_variable_value(state, self._handles['z1_temp'])
        z2_t = self.api.exchange.get_variable_value(state, self._handles['z2_temp'])
        
        z1_occ = self.api.exchange.get_variable_value(state, self._handles['z1_occ']) if self._handles['z1_occ'] > 0 else 0.0
        z2_occ = self.api.exchange.get_variable_value(state, self._handles['z2_occ']) if self._handles['z2_occ'] > 0 else 0.0
        z1_pmv = self.api.exchange.get_variable_value(state, self._handles['z1_pmv']) if self._handles['z1_pmv'] > 0 else 0.0
        z2_pmv = self.api.exchange.get_variable_value(state, self._handles['z2_pmv']) if self._handles['z2_pmv'] > 0 else 0.0
        
        z1_ppd = self.api.exchange.get_variable_value(state, self._handles['z1_ppd']) if self._handles['z1_ppd'] > 0 else 5.0
        z2_ppd = self.api.exchange.get_variable_value(state, self._handles['z2_ppd']) if self._handles['z2_ppd'] > 0 else 5.0
        
        z1_rh = self.api.exchange.get_variable_value(state, self._handles['z1_rh']) if self._handles['z1_rh'] > 0 else 50.0
        z2_rh = self.api.exchange.get_variable_value(state, self._handles['z2_rh']) if self._handles['z2_rh'] > 0 else 50.0
        
        # Read Meters (Joules)
        m_hvac = self.api.exchange.get_meter_value(state, self._handles['meter_hvac']) if self._handles['meter_hvac'] > 0 else 0.0
        m_cool = self.api.exchange.get_meter_value(state, self._handles['meter_cool']) if self._handles['meter_cool'] > 0 else 0.0
        m_heat = self.api.exchange.get_meter_value(state, self._handles['meter_heat']) if self._handles['meter_heat'] > 0 else 0.0
        m_fan = self.api.exchange.get_meter_value(state, self._handles['meter_fan']) if self._handles['meter_fan'] > 0 else 0.0
        
        # Convert delta Joules over 15 minutes to Watts
        dt_seconds = 15.0 * 60.0
        
        # Special case for first timestep to prevent massive spikes
        if self._last_meters['hvac'] == 0.0 and m_hvac > 0.0:
            hvac_power = m_hvac / dt_seconds
            cool_coil_pwr = m_cool / dt_seconds
            heat_coil_pwr = m_heat / dt_seconds
            fan_pwr = m_fan / dt_seconds
        else:
            hvac_power = max(0.0, (m_hvac - self._last_meters['hvac']) / dt_seconds)
            cool_coil_pwr = max(0.0, (m_cool - self._last_meters['cool']) / dt_seconds)
            heat_coil_pwr = max(0.0, (m_heat - self._last_meters['heat']) / dt_seconds)
            fan_pwr = max(0.0, (m_fan - self._last_meters['fan']) / dt_seconds)
            
        self._last_meters['hvac'] = m_hvac
        self._last_meters['cool'] = m_cool
        self._last_meters['heat'] = m_heat
        self._last_meters['fan'] = m_fan
        
        self.sim_time += timedelta(minutes=15)
        
        # Additional Variables
        out_temp = self.api.exchange.get_variable_value(state, self._handles['out_temp']) if self._handles.get('out_temp', -1) > 0 else 0.0
        clg_sch_val = self.api.exchange.get_actuator_value(state, self._handles['clg_sch']) if self._handles.get('clg_sch', -1) > 0 else 0.0
        htg_sch_val = self.api.exchange.get_actuator_value(state, self._handles['htg_sch']) if self._handles.get('htg_sch', -1) > 0 else 0.0

        # Skip blocking during warmup
        if self.api.exchange.warmup_flag(state):
            return

        print("================ ENERGYPLUS RAW ================")
        print(f"Simulation Time: {self.sim_time}")
        print(f"Zone1 Temperature: {z1_t}")
        print(f"Zone2 Temperature: {z2_t}")
        print(f"Outdoor Temperature: {out_temp}")
        print(f"Cooling Coil Electricity: {cool_coil_pwr}")
        print(f"Heating Coil Electricity: {heat_coil_pwr}")
        print(f"Fan Electricity: {fan_pwr}")
        print(f"Facility Electricity: {hvac_power}")
        print(f"Facility HVAC Electricity: {hvac_power}")
        print(f"Zone Occupancy: {z1_occ + z2_occ}")
        print(f"PMV: Z1={z1_pmv}, Z2={z2_pmv}")
        print(f"PPD: Z1={z1_ppd}, Z2={z2_ppd}")
        
        print(f"Current Cooling Schedule: {clg_sch_val}")
        print(f"Current Heating Schedule: {htg_sch_val}")
        print("=================================================")


        # 3. Publish State to Orchestrator
        current_state = {
            "time": self.sim_time,
            "z1_temp": z1_t,
            "z2_temp": z2_t,
            "hvac_power": hvac_power,
            "z1_occ": z1_occ,
            "z2_occ": z2_occ,
            "z1_pmv": z1_pmv,
            "z2_pmv": z2_pmv,
            "z1_ppd": z1_ppd,
            "z2_ppd": z2_ppd,
            "z1_rh": z1_rh,
            "z2_rh": z2_rh,
            "cool_coil_pwr": cool_coil_pwr,
            "heat_coil_pwr": heat_coil_pwr,
            "fan_pwr": fan_pwr,
            "out_temp": out_temp
        }
        self.state_queue.put(current_state)
        
        # 4. Wait for LLM Action (Blocking E+ Execution)
        try:
            # We wait up to 60 seconds for the LLM to decide to ensure true closed-loop sync
            actions = self.action_queue.get(timeout=60.0)
            
            # 5. Inject Actions via Actuators
            print("================ ACTUATOR ================")
            
            if 'z1_setpoint' in actions and self._handles['clg_sch'] > 0:
                handle = self._handles['clg_sch']
                old_val = self.api.exchange.get_actuator_value(state, handle)
                new_val = actions['z1_setpoint']
                print(f"Requested actuator: PERIMETER_MID_ZN_1_COOLING_SETPOINT")
                print(f"Mapped actuator: CLGSETP_SCH")
                print(f"EnergyPlus Handle: {handle}")
                print(f"Old Value: {old_val}")
                print(f"New Value: {new_val}")
                self.api.exchange.set_actuator_value(state, handle, new_val)
                print("set_actuator_value result: YES")
                
            print("=================================================")
                
        except queue.Empty:
            print("WARNING: LLM timeout (60s). Proceeding with default E+ schedule.")

    def run(self):
        """Starts the EnergyPlus binary execution in a background thread."""
        print("[TRACE] Registering callback: callback_begin_zone_timestep_after_init_heat_balance")
        self.api.runtime.callback_begin_zone_timestep_after_init_heat_balance(
            self.state, self._callback_begin_zone_timestep
        )
        print("[TRACE] Callback registered SUCCESSFULLY.")
        
        print(f"[TRACE] Launching EnergyPlus runtime with args: -w {self.epw_path} -d out {self.idf_path}")
        # This is a blocking call to the C++ EnergyPlus engine
        self.api.runtime.run_energyplus(
            self.state,
            [
                "-w", str(self.epw_path),
                "-d", "out",
                str(self.idf_path)
            ]
        )
