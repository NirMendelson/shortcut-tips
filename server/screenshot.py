import time
from datetime import datetime

class ScreenshotManager:
    def __init__(self):
        self.last_screenshot_time = 0
        self.screenshot_interval = 5.0  # Screenshot every 5 seconds
        
    def take_screenshot(self, context=""):
        """Take a screenshot (demo function)"""
        current_time = time.time()
        
        # Only take screenshots at intervals
        if current_time - self.last_screenshot_time < self.screenshot_interval:
            return None
            
        try:
            # In a real implementation, this would use PIL or similar
            # For demo purposes, just log the action
            timestamp = datetime.now().isoformat()
            print(f"📸 Screenshot taken at {timestamp} - Context: {context}")
            
            self.last_screenshot_time = current_time
            return f"screenshot_{timestamp}.png"
            
        except Exception as e:
            print(f"Screenshot error: {e}")
            return None
    
    def get_screenshot_path(self, context=""):
        """Get path to screenshot (demo function)"""
        timestamp = datetime.now().isoformat()
        return f"screenshots/screenshot_{context}_{timestamp}.png"
