import sqlite3
from datetime import datetime, timedelta
import json

class BanBotDatabase:
    def __init__(self, db_path="ban_bot.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        conn = self._get_connection()
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS cases
                     (case_id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER NOT NULL,
                      username TEXT,
                      mod_id INTEGER NOT NULL,
                      reason TEXT,
                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                      action TEXT NOT NULL,
                      transcript_path TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS alts
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      primary_id INTEGER NOT NULL,
                      alt_id INTEGER NOT NULL,
                      confidence REAL,
                      detection_method TEXT,
                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)""")
        conn.commit()
        conn.close()

    def log_ban(self, user_id: int, username: str, mod_id: int, reason: str, action: str = "BAN", transcript_path: str = None):
        conn = self._get_connection()
        c = conn.cursor()
        c.execute("INSERT INTO cases (user_id, username, mod_id, reason, action, transcript_path) VALUES (?, ?, ?, ?, ?, ?)",
                  (user_id, username, mod_id, reason, action, transcript_path))
        case_id = c.lastrowid
        conn.commit()
        conn.close()
        return case_id

    def get_user_bans(self, user_id: int):
        conn = self._get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM cases WHERE user_id = ? AND action = 'BAN' ORDER BY timestamp DESC", (user_id,))
        bans = c.fetchall()
        conn.close()
        return [dict(row) for row in bans]

    def get_all_cases(self, user_id: int):
        conn = self._get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM cases WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))
        cases = c.fetchall()
        conn.close()
        return [dict(row) for row in cases]

    def add_alt_record(self, primary_id: int, alt_id: int, confidence: float, detection_method: str):
        conn = self._get_connection()
        c = conn.cursor()
        c.execute("INSERT INTO alts (primary_id, alt_id, confidence, detection_method) VALUES (?, ?, ?, ?)",
                  (primary_id, alt_id, confidence, detection_method))
        conn.commit()
        conn.close()

    def get_alts_for_user(self, user_id: int):
        conn = self._get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM alts WHERE primary_id = ? OR alt_id = ? ORDER BY timestamp DESC", (user_id, user_id))
        alts = c.fetchall()
        conn.close()
        return [dict(row) for row in alts]

    def cleanup_old_records(self, days: int = 365):
        conn = self._get_connection()
        c = conn.cursor()
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        c.execute("DELETE FROM cases WHERE timestamp < ?", (cutoff_date,))
        c.execute("DELETE FROM alts WHERE timestamp < ?", (cutoff_date,))
        conn.commit()
        conn.close()

    def update_transcript_path(self, case_id: int, transcript_path: str):
        conn = self._get_connection()
        c = conn.cursor()
        c.execute("UPDATE cases SET transcript_path = ? WHERE case_id = ?", (transcript_path, case_id))
        conn.commit()
        conn.close()
