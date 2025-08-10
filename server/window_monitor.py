import win32gui
import win32process
import psutil

class WindowMonitor:
    """Monitors active window changes and provides window information"""
    
    def __init__(self):
        self.current_window = None
        self.last_window_check = 0
        self.window_check_interval = 1.0  # Check window every second
    
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
    
    def check_window_change(self):
        """Check if the active window has changed and return new info if so"""
        window_title, app_name = self.get_active_window_info()
        
        if window_title != self.current_window:
            self.current_window = window_title
            return window_title, app_name
        
        return None, None
    
    def get_current_window_info(self):
        """Get current window info without checking for changes"""
        return self.get_active_window_info()
