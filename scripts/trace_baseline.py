import os
import sqlite3
import subprocess
from pathlib import Path

def trace():
    print("-" * 40)
    print("BASELINE TRACE")
    print("-" * 40)
    
    hackathon_dir = Path("d:/Hackathon")
    output_dir = hackathon_dir / "data/outputs/baseline-hot-day"
    sql_path = output_dir / "eplusout.sql"
    eso_path = output_dir / "eplusout.eso"
    
    print("1. Did baseline simulation execute?")
    print("YES (We will run it now to trace)")
    
    print("\n2. What command launched EnergyPlus?")
    script_path = hackathon_dir / "scripts/run_baseline.ps1"
    cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(script_path), "-OutputDirectory", str(output_dir)]
    print(f"{' '.join(cmd)}")
    
    print("\n3. Did EnergyPlus finish? Exit code?")
    result = subprocess.run(cmd, cwd=str(hackathon_dir), capture_output=True, text=True)
    print(f"Exit Code: {result.returncode}")
    if result.returncode != 0:
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
    
    print("\n4. Was eplusout.sql generated?")
    print(f"Absolute path: {sql_path.absolute()}")
    print(f"File exists?: {sql_path.exists()}")
    
    print("\n5. Was eplusout.eso generated?")
    print(f"Absolute path: {eso_path.absolute()}")
    print(f"File exists?: {eso_path.exists()}")
    
    if not sql_path.exists():
        print("STOPPING: eplusout.sql is missing.")
        return
        
    print("\n6. Was SQL opened successfully?")
    try:
        conn = sqlite3.connect(str(sql_path))
        cursor = conn.cursor()
        print("YES")
    except Exception as e:
        print(f"NO ({e})")
        return
        
    print("\n7. What query is executed?")
    query_facility = """
    SELECT t.Month, t.Day, t.Hour, t.Minute, SUM(rd.Value)
    FROM ReportData rd
    JOIN Time t ON rd.TimeIndex = t.TimeIndex
    JOIN ReportDataDictionary rdd ON rd.ReportDataDictionaryIndex = rdd.ReportDataDictionaryIndex
    WHERE rdd.Name IN ('Air System Total Cooling Energy', 'Air System Total Heating Energy', 'Air System Fan Electricity Energy')
    GROUP BY t.Month, t.Day, t.Hour, t.Minute
    """
    print(query_facility)
    
    print("\n8. How many rows returned?")
    rows = cursor.execute(query_facility).fetchall()
    print(len(rows))
    
    if len(rows) == 0:
        print("Querying fallback (Electricity:Facility)...")
        query_fallback = """
        SELECT t.Month, t.Day, t.Hour, t.Minute, rd.Value
        FROM ReportData rd
        JOIN Time t ON rd.TimeIndex = t.TimeIndex
        JOIN ReportDataDictionary rdd ON rd.ReportDataDictionaryIndex = rdd.ReportDataDictionaryIndex
        WHERE rdd.Name = 'Electricity:Facility'
        """
        rows = cursor.execute(query_fallback).fetchall()
        print(f"Fallback returned {len(rows)} rows.")
        
        print("\nLet's check what meters DO exist in the DB:")
        meters = cursor.execute("SELECT DISTINCT Name FROM ReportDataDictionary").fetchall()
        print([m[0] for m in meters])
        
    print("\n9. Raw values returned (first 5)")
    print(rows[:5] if rows else "EMPTY LIST")
    
    if len(rows) == 0:
        print("\nSTOPPING: empty list. No matching records in DB.")
        return
        
    print("\n10. Computed baseline_energy_kwh.")
    print("Baseline power is sampled per timestamp. Let's compute average kW.")
    month, day, hour, minute, joules = rows[0]
    power_kw = joules / 900000.0 if joules else 0.0
    print(f"Sample First timestep -> {joules} Joules = {power_kw:.2f} kW")
    
if __name__ == "__main__":
    trace()
