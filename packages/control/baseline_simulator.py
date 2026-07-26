"""Module to generate and load real baseline data from EnergyPlus."""

import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime

class BaselineSimulator:
    def __init__(self, hackathon_dir: Path):
        self.hackathon_dir = hackathon_dir
        self.output_dir = hackathon_dir / "data/outputs/baseline-hot-day"
        self.sql_path = self.output_dir / "eplusout.sql"
        self.baseline_power = {} # (month, day, hour) -> kW
        
    def generate_baseline(self):
        """Runs the baseline simulation via powershell script if not already present."""
        print("[BASELINE] Running baseline simulation...")
        script_path = self.hackathon_dir / "scripts/run_baseline.ps1"
        try:
            subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(script_path), "-OutputDirectory", str(self.output_dir)],
                cwd=str(self.hackathon_dir),
                check=True
            )
            print("[BASELINE] Baseline simulation completed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"[BASELINE] Error running baseline simulation: {e}")
            raise

    def load_baseline_data(self):
        """Loads baseline HVAC power from SQLite database into memory map."""
        if not self.sql_path.exists():
            self.generate_baseline()
            
        print(f"[BASELINE] Loading data from {self.sql_path}")
        conn = sqlite3.connect(str(self.sql_path))
        cursor = conn.cursor()
        
        # Use the SAME electrical meters as the live simulation:
        # Cooling:Electricity + Heating:Electricity + Fans:Electricity
        # These match the live E+ meter handles in eplus_runner.py (lines 95-97)
        query_facility = """
        SELECT t.Month, t.Day, t.Hour, SUM(rd.Value)
        FROM ReportData rd
        JOIN Time t ON rd.TimeIndex = t.TimeIndex
        JOIN ReportDataDictionary rdd ON rd.ReportDataDictionaryIndex = rdd.ReportDataDictionaryIndex
        WHERE rdd.Name IN ('Cooling:Electricity', 'Heating:Electricity', 'Fans:Electricity')
        GROUP BY t.Month, t.Day, t.Hour
        """
        
        try:
            rows = cursor.execute(query_facility).fetchall()
            print("================ BASELINE SQL ===================")
            print("SELECT t.Month, t.Day, t.Hour, SUM(rd.Value) FROM ReportData rd ...")
            if rows:
                print(f"Sample Row 0: Month={rows[0][0]}, Day={rows[0][1]}, Hour={rows[0][2]}, Value={rows[0][3]}")
            print("=================================================")
            for row in rows:
                month, day, hour, joules = row
                # Convert Joules (per hour) to average kW: Joules / 3,600,000
                power_kw = joules / 3600000.0 if joules else 0.0
                self.baseline_power[(month, day, hour)] = power_kw
                
            # If no Air System variables found, fallback to Facility
            if not self.baseline_power:
                query_fallback = """
                SELECT t.Month, t.Day, t.Hour, rd.Value
                FROM ReportData rd
                JOIN Time t ON rd.TimeIndex = t.TimeIndex
                JOIN ReportDataDictionary rdd ON rd.ReportDataDictionaryIndex = rdd.ReportDataDictionaryIndex
                WHERE rdd.Name = 'Electricity:Facility'
                """
                rows = cursor.execute(query_fallback).fetchall()
                for row in rows:
                    month, day, hour, joules = row
                    power_kw = joules / 3600000.0 if joules else 0.0
                    self.baseline_power[(month, day, hour)] = power_kw

        except Exception as e:
            print(f"[BASELINE] Error querying baseline DB: {e}")
            
        conn.close()
        print(f"[BASELINE] Loaded {len(self.baseline_power)} baseline timesteps.")

    def get_baseline_power(self, current_time: datetime) -> float:
        """Returns the baseline power in kW for a given timestamp."""
        # EnergyPlus hours are 1-24, python datetime hours are 0-23
        ep_hour = current_time.hour + 1
        key = (current_time.month, current_time.day, ep_hour)
        return self.baseline_power.get(key, 0.0)
