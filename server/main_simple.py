import time
import sys
import threading
from database import DatabaseManager
from screenshot import ScreenshotManager
from notification_pyqt6 import PyQt6NotificationSystem as NotificationSystem
from input_monitor import InputMonitor
from context_analyzer import ContextAnalyzer
from window_monitor import WindowMonitor
from action_detector import ActionDetector
import psutil

class ShortcutCoach:
    def __init__(self):
        # Initialize all modules
        self.db_manager = DatabaseManager()
        self.screenshot_manager = ScreenshotManager()
        self.notification_system = NotificationSystem()
        self.window_monitor = WindowMonitor()
        
        # Initialize context analyzer with notification system
        self.context_analyzer = ContextAnalyzer(self.notification_system)
        
        # Initialize action detector for Excel actions
        self.action_detector = ActionDetector(self.notification_system)
        
        self.last_click_time = 0
        self.click_cooldown = 0.1  # 100ms cooldown between clicks
        
        # Initialize input monitor with callbacks
        self.input_monitor = InputMonitor(
            event_callback=self.log_event,
            key_press_callback=self.on_key_press,
            key_release_callback=self.on_key_release,
            context_menu_callback=self.handle_context_menu_click
        )
        
        self.running = False
        
    def log_event(self, event_type, details="", context_action=""):
        """Log event to database and console"""
        window_title, app_name = self.window_monitor.get_current_window_info()
        self.db_manager.log_event(event_type, details, window_title, app_name, context_action)
    
    def on_key_press(self, key):
        """Handle keyboard key press events"""
        try:
            key_name = key.char if hasattr(key, 'char') else str(key)
            self.log_event("Key Press", key_name)
        except AttributeError:
            self.log_event("Key Press", str(key))
    
    def on_key_release(self, key):
        """Handle keyboard key release events"""
        try:
            key_name = key.char if hasattr(key, 'char') else str(key)
            self.log_event("Key Release", key_name)
        except AttributeError:
            self.log_event("Key Release", str(key))
    
    def handle_context_menu_click(self, x, y):
        """Handle context menu clicks"""
        self.log_event("Context Menu Click", f"X={x}, Y={y}", context_action="CONTEXT_MENU_ACTION")
    
    def should_process_click(self, x, y):
        """Check if we should process this click"""
        current_time = time.time()
        if current_time - self.last_click_time < self.click_cooldown:
            return False
        self.last_click_time = current_time
        return True
    
    def start(self):
        """Start the shortcut coach"""
        try:
            print("🚀 Starting Shortcut Coach...")
            print("📊 Tracking mouse clicks, keystrokes, and window changes...")
            print("💡 You'll see notifications for shortcut opportunities!")
            
            self.running = True
            
            # Start input monitoring
            input_started = self.input_monitor.start()
            if not input_started:
                print("⚠️ Warning: Input monitoring failed, continuing with basic tracking...")
            
            # Keep the main thread alive
            while self.running:
                time.sleep(0.1)
                
        except Exception as e:
            print(f"❌ Error starting Shortcut Coach: {e}")
            self.running = False
    
    def stop(self):
        """Stop the shortcut coach"""
        print("🛑 Stopping Shortcut Coach...")
        self.running = False
        if hasattr(self, 'input_monitor'):
            self.input_monitor.stop()
        if hasattr(self, 'notification_system'):
            self.notification_system.stop()

def main():
    try:
        coach = ShortcutCoach()
        coach.start()
    except KeyboardInterrupt:
        print("\n👋 Exiting...")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
