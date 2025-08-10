import time
import sys
import threading
from database import DatabaseManager
from screenshot import ScreenshotManager
from notification import NotificationSystem
from input_monitor import InputMonitor
from context_analyzer import ContextAnalyzer
from window_monitor import WindowMonitor

class ShortcutCoach:
    def __init__(self):
        # Initialize all modules
        self.db_manager = DatabaseManager()
        self.screenshot_manager = ScreenshotManager()
        self.notification_system = NotificationSystem()
        self.window_monitor = WindowMonitor()
        
        # Initialize context analyzer with notification system
        self.context_analyzer = ContextAnalyzer(self.notification_system)
        
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
    
    def handle_context_menu_click(self, x, y, button, pressed):
        """Handle context menu clicks with screenshot capture and analysis"""
        if pressed and button.name == 'left':
            # Check if this left-click might be a context menu selection
            if hasattr(self.input_monitor, 'last_right_click_time') and \
               self.input_monitor.last_right_click_time and \
               (time.time() - self.input_monitor.last_right_click_time) < 5.0:
                
                self.log_event("Left Click (Context Menu)", f"X={x}, Y={y}", context_action="MENU_SELECTION")
                
                # Capture screenshot and analyze menu text
                screenshot_path, screenshot = self.screenshot_manager.capture_context_menu_screenshot(x, y)
                if screenshot:
                    menu_text = self.screenshot_manager.analyze_menu_text(screenshot)
                    if menu_text:
                        # Analyze the context menu selection
                        clicked_item = self.context_analyzer.analyze_context_menu_selection(x, y, menu_text)
                        if clicked_item:
                            print(f"DEBUG: Context menu item selected: {clicked_item}")
                            self.log_event("Menu Item Selected", f"'{clicked_item}' at X={x}, Y={y}", 
                                         context_action=f"SELECTED_{clicked_item.upper()}")
                            
                            # Get shortcut suggestion for this action
                            shortcut, description = self.context_analyzer.suggest_shortcut(clicked_item)
                            if shortcut:
                                print(f"DEBUG: Suggesting shortcut {shortcut} for {clicked_item}")
                                self.notification_system.suggest_shortcut(clicked_item, shortcut)
                            else:
                                print(f"DEBUG: No shortcut found for {clicked_item}")
                        else:
                            print("DEBUG: No context menu item identified")
                
                self.input_monitor.context_menu_active = False
            else:
                self.log_event("Left Click", f"X={x}, Y={y}")
                
        elif pressed and button.name == 'right':
            self.log_event("Right Click", f"X={x}, Y={y}", context_action="CONTEXT_MENU_OPENED")
            
            # Capture screenshot of the context menu when it opens
            screenshot_path, screenshot = self.screenshot_manager.capture_context_menu_screenshot(x, y)
            if screenshot:
                menu_text = self.screenshot_manager.analyze_menu_text(screenshot)
                if menu_text:
                    self.log_event("Context Menu Opened", f"Available options: {menu_text[:100]}...", 
                                 context_action="MENU_OPTIONS_DETECTED")
    
    def start_tracking(self):
        """Start event tracking"""
        try:
            print("Starting Shortcut Coach...")
            print("Press Ctrl+C to stop tracking")
            print("Now tracking context menu actions and clipboard changes!")
            print("-" * 50)
            
            self.running = True
            
            # Start input monitoring
            input_started = self.input_monitor.start()
            if not input_started:
                print("Warning: Input monitoring failed, continuing with window tracking only...")
            
            # Keep the main thread alive and track windows
            try:
                while self.running:
                    time.sleep(1.0)
                    # Log window changes periodically
                    window_title, app_name = self.window_monitor.check_window_change()
                    if window_title:
                        print(f"Active Window: {app_name} - {window_title}")
                        
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
        self.input_monitor.stop()
        self.notification_system.stop()


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