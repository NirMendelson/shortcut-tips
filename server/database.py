import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="shortcuts.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with basic schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Events table for Phase 1
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                details TEXT,
                window_title TEXT,
                app_name TEXT,
                context_action TEXT
            )
        ''')
        
        # Check if context_action column exists, add it if not
        try:
            cursor.execute("SELECT context_action FROM events LIMIT 1")
        except sqlite3.OperationalError:
            print("Adding context_action column to existing database...")
            cursor.execute("ALTER TABLE events ADD COLUMN context_action TEXT")
        
        conn.commit()
        conn.close()
        print("Database initialized successfully")
    
    def log_event(self, event_type, details="", window_title="", app_name="", context_action=""):
        """Log event to database and console"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Log to console
            print(f"{timestamp} | {event_type} | {details}")
            if window_title:
                print(f"Active Window: {app_name} - {window_title}")
            
            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO events (timestamp, event_type, details, window_title, app_name, context_action)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (timestamp, event_type, details, window_title, app_name, context_action))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error logging event: {e}")
