import sqlite3
import pandas as pd
import os
from pathlib import Path

def get_db_connection():
    db_path = Path("d:/Hackathon/data/outputs/baseline-annual-verified/eplusout.sql")
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found at {db_path}")
    return sqlite3.connect(str(db_path))

def fetch_telemetry_for_timestep(month: int, day: int, hour: int, minute: int):
    conn = get_db_connection()
    
    query = """
    SELECT d.Name, d.KeyValue, r.Value 
    FROM ReportData r 
    JOIN ReportDataDictionary d ON r.ReportDataDictionaryIndex = d.ReportDataDictionaryIndex 
    JOIN Time t ON r.TimeIndex = t.TimeIndex 
    WHERE t.Month=? AND t.Day=? AND t.Hour=? AND t.Minute=?
    AND d.Name IN (
        'Zone Mean Air Temperature', 
        'Electricity:Facility',
        'Zone People Occupant Count',
        'Site Outdoor Air Drybulb Temperature',
        'Zone Thermal Comfort Fanger Model PPD'
    )
    """
    
    df = pd.read_sql_query(query, conn, params=(month, day, hour, minute))
    conn.close()
    
    # Process into a structured format
    result = {
        "hvac_power": 0.0, # Will convert J to kW
        "outdoor_temp": 0.0,
        "zones": {}
    }
    
    for _, row in df.iterrows():
        name = row['Name']
        key = row['KeyValue']
        val = row['Value']
        
        if name == 'Electricity:Facility':
            # Electricity is reported in Joules per timestep (15 min)
            # Watts = Joules / (15 * 60)
            # kW = Watts / 1000
            result['hvac_power'] = val / (15 * 60 * 1000)
            
        elif name == 'Site Outdoor Air Drybulb Temperature':
            result['outdoor_temp'] = val
            
        elif name == 'Zone Mean Air Temperature':
            if key not in result['zones']:
                result['zones'][key] = {}
            result['zones'][key]['temp'] = val
            
        elif name == 'Zone People Occupant Count':
            if key not in result['zones']:
                result['zones'][key] = {}
            result['zones'][key]['occupancy'] = val
            
        elif name == 'Zone Thermal Comfort Fanger Model PPD':
            if key not in result['zones']:
                result['zones'][key] = {}
            result['zones'][key]['ppd'] = val

    return result

if __name__ == "__main__":
    print(fetch_telemetry_for_timestep(7, 15, 14, 0)) # Test mid-July
