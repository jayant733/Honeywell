import sqlite3
conn = sqlite3.connect('d:/Hackathon/data/outputs/baseline-hot-day/eplusout.sql')
c = conn.cursor()

# Check what hours exist for Jan 1
rows = c.execute("""SELECT DISTINCT t.Hour FROM ReportData rd 
    JOIN Time t ON rd.TimeIndex = t.TimeIndex 
    JOIN ReportDataDictionary rdd ON rd.ReportDataDictionaryIndex = rdd.ReportDataDictionaryIndex 
    WHERE rdd.Name = 'Air System Total Cooling Energy' AND t.Month = 1 AND t.Day = 1 
    ORDER BY t.Hour""").fetchall()
print('Distinct hours for Jan 1:', [r[0] for r in rows])

# Check hour 24
r24 = c.execute("""SELECT t.Month, t.Day, t.Hour, SUM(rd.Value) FROM ReportData rd 
    JOIN Time t ON rd.TimeIndex = t.TimeIndex 
    JOIN ReportDataDictionary rdd ON rd.ReportDataDictionaryIndex = rdd.ReportDataDictionaryIndex 
    WHERE rdd.Name IN ('Air System Total Cooling Energy', 'Air System Total Heating Energy', 'Air System Fan Electricity Energy') 
    AND t.Month = 1 AND t.Day = 1 AND t.Hour = 24 
    GROUP BY t.Month, t.Day, t.Hour""").fetchall()
print('Hour 24 query:', r24)

# Check hour 0
r0 = c.execute("""SELECT t.Month, t.Day, t.Hour, SUM(rd.Value) FROM ReportData rd 
    JOIN Time t ON rd.TimeIndex = t.TimeIndex 
    JOIN ReportDataDictionary rdd ON rd.ReportDataDictionaryIndex = rdd.ReportDataDictionaryIndex 
    WHERE rdd.Name IN ('Air System Total Cooling Energy', 'Air System Total Heating Energy', 'Air System Fan Electricity Energy') 
    AND t.Month = 1 AND t.Day = 1 AND t.Hour = 0 
    GROUP BY t.Month, t.Day, t.Hour""").fetchall()
print('Hour 0 query:', r0)

# Check what sim_time produces what ep_hour
from datetime import datetime, timedelta
sim = datetime(2023, 1, 1, 0, 0)
print()
print('Simulation time mapping (first 26 steps):')
for i in range(26):
    t = sim + timedelta(minutes=15*i)
    ep_hour = t.hour + 1
    key = (t.month, t.day, ep_hour)
    row = c.execute("""SELECT SUM(rd.Value) FROM ReportData rd 
        JOIN Time t ON rd.TimeIndex = t.TimeIndex 
        JOIN ReportDataDictionary rdd ON rd.ReportDataDictionaryIndex = rdd.ReportDataDictionaryIndex 
        WHERE rdd.Name IN ('Air System Total Cooling Energy', 'Air System Total Heating Energy', 'Air System Fan Electricity Energy') 
        AND t.Month = ? AND t.Day = ? AND t.Hour = ?""", key).fetchone()
    val = row[0] if row and row[0] else 0
    kw = val / 3600000.0
    print(f'  sim_time={t.strftime("%H:%M")} -> ep_hour={ep_hour} -> key={key} -> Joules={val:.0f} -> kW={kw:.2f}')

conn.close()
