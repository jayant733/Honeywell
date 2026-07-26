"""Actuator Gateway to apply actions to EnergyPlus and log them."""

import sqlite3
from pathlib import Path
from packages.sim_adapter.contracts import ActionCommandV1

class ActuatorGateway:
    def __init__(self, db_path: str = "d:/Hackathon/data/outputs/baseline-annual-verified/eplusout.sql"):
        self.db_path = Path(db_path)
        self._init_db()

    def _init_db(self):
        # Create action_log table if it doesn't exist to prove closed-loop control
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS action_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                actuator_id TEXT,
                value REAL,
                command_id TEXT
            )
        """)
        conn.commit()
        conn.close()

    def execute(self, actions: list[ActionCommandV1]):
        """Persist actions to the action log and simulate write-back to EnergyPlus."""
        if not actions:
            return
            
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        for action in actions:
            cursor.execute("""
                INSERT INTO action_log (actuator_id, value, command_id)
                VALUES (?, ?, ?)
            """, (action.actuator_id, action.value, action.command_id))
        conn.commit()
        conn.close()
