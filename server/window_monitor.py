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
        # For now, return generic info - the real app name comes from the click events
        return "Active Window", "Unknown"
    
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
