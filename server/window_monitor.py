import psutil
import time
from datetime import datetime

class WindowMonitor:
    def __init__(self):
        self.last_window_info = ("", "")
        self.last_check_time = 0
        self.check_interval = 0.1  # Check every 100ms
        
    def get_current_window_info(self):
        """Get current active window title and application name"""
        current_time = time.time()
        
        # Only check if enough time has passed
        if current_time - self.last_check_time < self.check_interval:
            return self.last_window_info
            
        try:
            # Get active window using psutil (simplified approach)
            # In a real implementation, you'd use Windows API
            active_process = psutil.Process()
            
            # Get process name
            app_name = active_process.name()
            
            # For demo purposes, simulate window titles
            window_titles = {
                "cursor.exe": "Shortcut Coach - Cursor",
                "chrome.exe": "Google Chrome - Programming",
                "excel.exe": "Excel - Data Analysis",
                "notepad.exe": "Notepad - Notes",
                "code.exe": "VS Code - Project"
            }
            
            window_title = window_titles.get(app_name, f"Active Window - {app_name}")
            
            self.last_window_info = (window_title, app_name)
            self.last_check_time = current_time
            
            return window_title, app_name
            
        except Exception as e:
            print(f"Window monitor error: {e}")
            return "Unknown Window", "Unknown"
    
    def get_window_list(self):
        """Get list of all visible windows (demo function)"""
        # This would use Windows API in real implementation
        demo_windows = [
            ("Shortcut Coach - Cursor", "cursor.exe"),
            ("Google Chrome - Programming", "chrome.exe"),
            ("Excel - Data Analysis", "excel.exe"),
            ("Notepad - Notes", "notepad.exe"),
            ("VS Code - Project", "code.exe")
        ]
        return demo_windows
    
    def check_window_change(self):
        """Check if the active window has changed and return new info"""
        current_window_info = self.get_current_window_info()
        
        # Check if window changed
        if current_window_info != self.last_window_info:
            self.last_window_info = current_window_info
            return current_window_info
        
        return None, None
