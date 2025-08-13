import sqlite3
import time
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path='shortcuts.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create events table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    details TEXT,
                    window_title TEXT,
                    app_name TEXT,
                    context_action TEXT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            print("✅ Database initialized successfully")
            
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
    
    def log_event(self, event_type, details="", window_title="", app_name="", context_action=""):
        """Log an event to the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO events (event_type, details, window_title, app_name, context_action, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (event_type, details, window_title, app_name, context_action, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error logging event: {e}")
    
    def get_recent_events(self, limit=100):
        """Get recent events from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT event_type, details, window_title, app_name, timestamp, context_action
                FROM events 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            events = cursor.fetchall()
            conn.close()
            return events
            
        except Exception as e:
            print(f"❌ Error getting events: {e}")
            return []
    
    def get_app_usage_stats(self):
        """Get application usage statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT app_name, COUNT(*) as count, 
                       MIN(timestamp) as first_seen, MAX(timestamp) as last_seen
                FROM events 
                WHERE app_name != 'Unknown' AND app_name != ''
                GROUP BY app_name
                ORDER BY count DESC
            ''')
            
            stats = cursor.fetchall()
            conn.close()
            return stats
            
        except Exception as e:
            print(f"❌ Error getting app stats: {e}")
            return []
