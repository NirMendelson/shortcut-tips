import time
import sys
import threading
from database import DatabaseManager
from screenshot import ScreenshotManager
from notification import NotificationSystem
from input_monitor import InputMonitor
from context_analyzer import ContextAnalyzer
from window_monitor import WindowMonitor
from action_detector import ActionDetector
from pywinauto import Desktop
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
        
        # Initialize UI Automation
        self.ui_desk = Desktop(backend="uia")
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
    
    def detect_ui_element(self, x, y):
        """Detect what UI element was clicked using Windows UI Automation"""
        try:
            # Get element at click point
            element = self.ui_desk.from_point(x, y)
            element_info = element.element_info
            rect = element.rectangle()
            
            # Get process info
            process_id = element_info.process_id
            try:
                process = psutil.Process(process_id)
                app_name = process.name()
            except:
                app_name = "Unknown"
            
            # Return element information
            return {
                "name": element_info.name,
                "type": str(element_info.control_type),
                "automation_id": getattr(element_info, "automation_id", None),
                "class_name": getattr(element_info, "class_name", None),
                "app_name": app_name,
                "coordinates": (x, y),
                "bounds": (rect.left, rect.top, rect.right, rect.bottom),
                "center": ((rect.left + rect.right) // 2, (rect.top + rect.bottom) // 2)
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "coordinates": (x, y),
                "app_name": "Unknown"
            }
    
    def get_shortcut_suggestion(self, element_info):
        """Get shortcut suggestion based on clicked element"""
        if "error" in element_info:
            return None
        
        element_name = element_info["name"].lower()
        element_type = element_info["type"].lower()
        app_name = element_info["app_name"].lower()
        
        # Excel shortcuts
        if "excel" in app_name:
            if "save" in element_name:
                return "Ctrl + S", "Save"
            elif "new" in element_name:
                return "Ctrl + N", "New"
            elif "open" in element_name:
                return "Ctrl + O", "Open"
            elif "bold" in element_name:
                return "Ctrl + B", "Bold"
            elif "italic" in element_name:
                return "Ctrl + I", "Italic"
            elif "underline" in element_name:
                return "Ctrl + U", "Underline"
            elif "copy" in element_name:
                return "Ctrl + C", "Copy"
            elif "paste" in element_name:
                return "Ctrl + V", "Paste"
            elif "cut" in element_name:
                return "Ctrl + X", "Cut"
            elif "undo" in element_name:
                return "Ctrl + Z", "Undo"
            elif "redo" in element_name:
                return "Ctrl + Y", "Redo"
        
        # Cursor/VS Code shortcuts
        elif "cursor" in app_name or "code" in app_name:
            if "save" in element_name:
                return "Ctrl + S", "Save"
            elif "new file" in element_name:
                return "Ctrl + N", "New File"
            elif "find" in element_name:
                return "Ctrl + F", "Find"
            elif "replace" in element_name:
                return "Ctrl + H", "Replace"
            elif "comment" in element_name:
                return "Ctrl + /", "Toggle Comment"
        
        # Chrome shortcuts
        elif "chrome" in app_name:
            if "new tab" in element_name:
                return "Ctrl + T", "New Tab"
            elif "close" in element_name:
                return "Ctrl + W", "Close Tab"
            elif "refresh" in element_name:
                return "Ctrl + R", "Refresh"
            elif "back" in element_name:
                return "Alt + ←", "Go Back"
            elif "forward" in element_name:
                return "Alt + →", "Go Forward"
        
        return None
    
    def should_process_click(self, x, y):
        """Check if we should process this click (avoid duplicates)"""
        current_time = time.time()
        if current_time - self.last_click_time < self.click_cooldown:
            return False
        
        self.last_click_time = current_time
        return True
    
    def handle_context_menu_click(self, x, y, button, pressed):
        """Handle context menu clicks with UI Automation detection"""
        if pressed and button.name == 'left':
            # Check if this left-click might be a context menu selection
            if hasattr(self.input_monitor, 'last_right_click_time') and \
               self.input_monitor.last_right_click_time and \
               (time.time() - self.input_monitor.last_right_click_time) < 5.0:
                
                self.log_event("Left Click (Context Menu)", f"X={x}, Y={y}", context_action="MENU_SELECTION")
                
                # Use UI Automation to detect what was clicked
                if self.should_process_click(x, y):
                    element_info = self.detect_ui_element(x, y)
                    print(f"🎯 UI Element Clicked: {element_info['name']} in {element_info['app_name']}")
                    
                    # Get shortcut suggestion
                    result = self.get_shortcut_suggestion(element_info)
                    if result:
                        shortcut, description = result
                        print(f"💡 Use {shortcut} for {description}")
                        self.notification_system.suggest_shortcut(description, shortcut)
                        self.log_event("Shortcut Suggested", f"{shortcut} for {description}", 
                                     context_action=f"SHORTCUT_{shortcut.replace(' + ', '_').upper()}")
                    else:
                        print(f"ℹ️ No shortcut available for {element_info['name']}")
                    
                    # Also detect actions (like Excel cell navigation)
                    self.action_detector.detect_action(x, y, element_info['app_name'])
                
                self.input_monitor.context_menu_active = False
            else:
                # Regular left click - detect UI element
                if self.should_process_click(x, y):
                    element_info = self.detect_ui_element(x, y)
                    print(f"🖱️ Clicked: {element_info['name']} in {element_info['app_name']}")
                    
                    # Get shortcut suggestion for buttons
                    result = self.get_shortcut_suggestion(element_info)
                    if result:
                        shortcut, description = result
                        print(f"💡 Use {shortcut} for {description}")
                        self.notification_system.suggest_shortcut(description, shortcut)
                        self.log_event("Shortcut Suggested", f"{shortcut} for {description}", 
                                     context_action=f"SHORTCUT_{shortcut.replace(' + ', '_').upper()}")
                    else:
                        print(f"ℹ️ No shortcut available for {element_info['name']}")
                    
                    # Also detect actions (like Excel cell navigation)
                    self.action_detector.detect_action(x, y, element_info['app_name'])
                
                self.log_event("Left Click", f"X={x}, Y={y}")
                
        elif pressed and button.name == 'right':
            self.log_event("Right Click", f"X={x}, Y={y}", context_action="CONTEXT_MENU_OPENED")
    
    def start_tracking(self):
        """Start event tracking"""
        try:
            print("Starting Shortcut Coach...")
            print("Press Ctrl+C to stop tracking")
            print("🎯 Now tracking UI elements in real-time using Windows UI Automation!")
            print("💡 Click on any button, tab, or UI element to get shortcut suggestions!")
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