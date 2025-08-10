import time
import sys
import sqlite3
from datetime import datetime
from pynput import mouse, keyboard
from pynput.mouse import Button
import win32gui
import win32process
import psutil
import threading

class ShortcutCoach:
    def __init__(self):
        self.db_path = "shortcuts.db"
        self.init_database()
        self.current_window = None
        self.last_window_check = 0
        self.window_check_interval = 1.0  # Check window every second
        self.running = False
        self.mouse_listener = None
        self.keyboard_listener = None
        
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
                app_name TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print("Database initialized successfully")
    
    def get_active_window_info(self):
        """Get current active window information"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            window_title = win32gui.GetWindowText(hwnd)
            
            # Get process ID and name
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            try:
                process = psutil.Process(pid)
                app_name = process.name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                app_name = "Unknown"
            
            return window_title, app_name
        except Exception as e:
            return "Unknown", "Unknown"
    
    def log_event(self, event_type, details=""):
        """Log event to database and console"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            window_title, app_name = self.get_active_window_info()
            
            # Log to console
            print(f"{timestamp} | {event_type} | {details}")
            if window_title != self.current_window:
                print(f"Active Window: {app_name} - {window_title}")
                self.current_window = window_title
            
            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO events (timestamp, event_type, details, window_title, app_name)
                VALUES (?, ?, ?, ?, ?)
            ''', (timestamp, event_type, details, window_title, app_name))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error logging event: {e}")
    
    def safe_mouse_callback(self, x, y, button, pressed):
        """Safe wrapper for mouse callback to prevent crashes"""
        try:
            self.on_click(x, y, button, pressed)
        except Exception as e:
            print(f"Mouse callback error: {e}")
    
    def safe_keyboard_callback(self, key, is_press=True):
        """Safe wrapper for keyboard callback to prevent crashes"""
        try:
            if is_press:
                self.on_key_press(key)
            else:
                self.on_key_release(key)
        except Exception as e:
            print(f"Keyboard callback error: {e}")
    
    def on_click(self, x, y, button, pressed):
        """Handle mouse click events"""
        if pressed:
            if button == Button.left:
                self.log_event("Left Click", f"X={x}, Y={y}")
            elif button == Button.right:
                self.log_event("Right Click", f"X={x}, Y={y}")
    
    def on_key_press(self, key):
        """Handle keyboard key press events"""
        try:
            key_name = key.char if hasattr(key, 'char') else str(key)
            self.log_event("Key Press", key_name)
        except AttributeError:
            # Special keys like ctrl, alt, etc.
            self.log_event("Key Press", str(key))
    
    def on_key_release(self, key):
        """Handle keyboard key release events"""
        try:
            key_name = key.char if hasattr(key, 'char') else str(key)
            self.log_event("Key Release", key_name)
        except AttributeError:
            self.log_event("Key Release", str(key))
    
    def start_tracking(self):
        """Start event tracking"""
        try:
            print("Starting Shortcut Coach...")
            print("Press Ctrl+C to stop tracking")
            print("-" * 50)
            
            self.running = True
            
            # Start listeners with error handling
            try:
                self.mouse_listener = mouse.Listener(
                    on_click=self.safe_mouse_callback
                )
                self.keyboard_listener = keyboard.Listener(
                    on_press=lambda key: self.safe_keyboard_callback(key, True),
                    on_release=lambda key: self.safe_keyboard_callback(key, False)
                )
                
                self.mouse_listener.start()
                self.keyboard_listener.start()
                print("Input listeners started successfully")
                
            except Exception as e:
                print(f"Warning: Could not start input listeners: {e}")
                print("Continuing with window tracking only...")
            
            # Keep the main thread alive and track windows
            try:
                while self.running:
                    time.sleep(1.0)
                    # Log window changes periodically
                    window_title, app_name = self.get_active_window_info()
                    if window_title != self.current_window:
                        print(f"Active Window: {app_name} - {window_title}")
                        self.current_window = window_title
                        
            except KeyboardInterrupt:
                print("\nStopping Shortcut Coach...")
                self.stop_tracking()
                print("Tracking stopped successfully")
                
        except PermissionError:
            print("ERROR: Global keyboard/mouse tracking requires administrator privileges.")
            print("Please run this program as administrator and try again.")
            sys.exit(1)
        except Exception as e:
            print(f"ERROR: Failed to start tracking: {e}")
            print("This might be due to permission issues or system restrictions.")
            sys.exit(1)
    
    def stop_tracking(self):
        """Stop all tracking"""
        self.running = False
        if self.mouse_listener:
            try:
                self.mouse_listener.stop()
            except:
                pass
        if self.keyboard_listener:
            try:
                self.keyboard_listener.stop()
            except:
                pass

def main():
    try:
        coach = ShortcutCoach()
        coach.start_tracking()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 