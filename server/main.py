import time
import sys
import sqlite3
from datetime import datetime
from pynput import mouse, keyboard
from pynput.mouse import Button
import win32gui
import win32process
import win32clipboard
import psutil
import threading
import win32con
import win32api
from PIL import ImageGrab
import pytesseract
import os

class ShortcutCoach:
    def __init__(self):
        self.db_path = "shortcuts.db"
        self.screenshots_dir = "screenshots"
        
        # Set Tesseract path for Windows
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        self.init_database()
        self.init_screenshots_directory()
        self.current_window = None
        self.last_window_check = 0
        self.window_check_interval = 1.0  # Check window every second
        self.running = False
        self.mouse_listener = None
        self.keyboard_listener = None
        
        # Context menu tracking
        self.last_right_click_time = None
        self.right_click_coords = None
        self.context_menu_active = False
        self.last_clipboard_content = None
        self.clipboard_monitor_thread = None
        
        # Start clipboard monitoring
        self.start_clipboard_monitoring()
        
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
    
    def init_screenshots_directory(self):
        """Create screenshots directory if it doesn't exist"""
        if not os.path.exists(self.screenshots_dir):
            os.makedirs(self.screenshots_dir)
            print(f"Created screenshots directory: {self.screenshots_dir}")
    
    def capture_context_menu_screenshot(self, x, y):
        """Capture screenshot around cursor position for context menu analysis"""
        try:
            # Capture wider area - enough to see the full menu item text
            # Context menu items are typically 200-300 pixels wide and 20-30 pixels tall
            left = max(0, x - 100)
            top = max(0, y - 30)
            right = x + 100
            bottom = y + 30
            
            screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"context_menu_{timestamp}_x{x}_y{y}.png"
            filepath = os.path.join(self.screenshots_dir, filename)
            
            # Save screenshot
            screenshot.save(filepath)
            print(f"Screenshot saved: {filename}")
            
            return filepath, screenshot
            
        except Exception as e:
            print(f"Error capturing screenshot: {e}")
            return None, None
    
    def analyze_menu_text(self, screenshot):
        """Use OCR to extract text from context menu screenshot"""
        try:
            # Use pytesseract with better configuration for menu text
            # --psm 6: Assume a uniform block of text
            # --oem 3: Use LSTM OCR Engine
            config = '--psm 6 --oem 3'
            
            menu_text = pytesseract.image_to_string(screenshot, config=config)
            
            # Clean up the text - remove extra whitespace and newlines
            menu_text = ' '.join(menu_text.split())
            
            if menu_text:
                print(f"Detected menu text: {menu_text[:100]}...")
                return menu_text
            else:
                print("No text detected in context menu")
                return None
                
        except Exception as e:
            print(f"Error analyzing menu text: {e}")
            return None
    
    def start_clipboard_monitoring(self):
        """Start monitoring clipboard changes in background thread"""
        self.clipboard_monitor_thread = threading.Thread(target=self.monitor_clipboard, daemon=True)
        self.clipboard_monitor_thread.start()
    
    def monitor_clipboard(self):
        """Monitor clipboard for changes"""
        try:
            while self.running:
                try:
                    # Try to get clipboard content
                    win32clipboard.OpenClipboard()
                    try:
                        clipboard_content = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
                    except:
                        clipboard_content = None
                    win32clipboard.CloseClipboard()
                    
                    # Check if clipboard changed
                    if clipboard_content != self.last_clipboard_content and clipboard_content:
                        if self.last_clipboard_content is not None:  # Not the first check
                            self.log_event("Clipboard Change", f"Content: {clipboard_content[:50]}...", context_action="COPY_DETECTED")
                        self.last_clipboard_content = clipboard_content
                    
                except Exception as e:
                    pass  # Clipboard might be locked by other applications
                
                time.sleep(0.5)  # Check every 500ms
        except Exception as e:
            print(f"Clipboard monitoring error: {e}")
    
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
    
    def log_event(self, event_type, details="", context_action=""):
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
                INSERT INTO events (timestamp, event_type, details, window_title, app_name, context_action)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (timestamp, event_type, details, window_title, app_name, context_action))
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
        """Handle mouse click events with context menu detection and screenshot capture"""
        if pressed:
            if button == Button.left:
                # Check if this left-click might be a context menu selection
                if self.last_right_click_time and (time.time() - self.last_right_click_time) < 5.0:
                    # Left-click within 5 seconds of right-click - likely context menu selection
                    self.log_event("Left Click (Context Menu)", f"X={x}, Y={y}", context_action="MENU_SELECTION")
                    
                    # Capture screenshot and analyze menu text
                    screenshot_path, screenshot = self.capture_context_menu_screenshot(x, y)
                    if screenshot:
                        menu_text = self.analyze_menu_text(screenshot)
                        if menu_text:
                            # Try to identify which menu item was clicked
                            clicked_item = self.identify_clicked_menu_item(x, y, menu_text)
                            if clicked_item:
                                self.log_event("Menu Item Selected", f"'{clicked_item}' at X={x}, Y={y}", context_action=f"SELECTED_{clicked_item.upper()}")
                    
                    self.context_menu_active = False
                else:
                    self.log_event("Left Click", f"X={x}, Y={y}")
                    
            elif button == Button.right:
                self.log_event("Right Click", f"X={x}, Y={y}", context_action="CONTEXT_MENU_OPENED")
                self.last_right_click_time = time.time()
                self.right_click_coords = (x, y)
                self.context_menu_active = True
                
                # Capture screenshot of the context menu when it opens
                screenshot_path, screenshot = self.capture_context_menu_screenshot(x, y)
                if screenshot:
                    menu_text = self.analyze_menu_text(screenshot)
                    if menu_text:
                        self.log_event("Context Menu Opened", f"Available options: {menu_text[:100]}...", context_action="MENU_OPTIONS_DETECTED")
                
                # Try to detect common context menu actions
                self.detect_context_menu_actions(x, y)
    
    def identify_clicked_menu_item(self, x, y, menu_text):
        """Try to identify which specific menu item was clicked based on coordinates and text"""
        try:
            if not menu_text:
                return None
            
            # Clean up the text and look for specific menu items
            menu_text = menu_text.strip().lower()
            
            # Look for common context menu items - check for exact matches first
            # Handle cases where OCR might detect partial text or multiple items
            if 'copy' in menu_text and len(menu_text) < 20:  # Short text, likely just "Copy"
                return "Copy"
            elif 'cut' in menu_text and len(menu_text) < 20:
                return "Cut"
            elif 'paste' in menu_text and len(menu_text) < 20:
                return "Paste"
            elif 'delete' in menu_text and len(menu_text) < 20:
                return "Delete"
            elif 'rename' in menu_text and len(menu_text) < 20:
                return "Rename"
            elif 'refactor' in menu_text and len(menu_text) < 20:
                return "Refactor"
            elif 'source action' in menu_text:
                return "Source Action"
            elif 'share' in menu_text and len(menu_text) < 20:
                return "Share"
            elif 'run' in menu_text and len(menu_text) < 20:
                return "Run"
            elif 'reload' in menu_text and len(menu_text) < 20:
                return "Reload"
            elif 'duplicate' in menu_text and len(menu_text) < 20:
                return "Duplicate"
            elif 'new' in menu_text and len(menu_text) < 20:
                return "New"
            elif 'open' in menu_text and len(menu_text) < 20:
                return "Open"
            elif 'save' in menu_text and len(menu_text) < 20:
                return "Save"
            elif 'close' in menu_text and len(menu_text) < 20:
                return "Close"
            elif 'exit' in menu_text and len(menu_text) < 20:
                return "Exit"
            elif 'undo' in menu_text and len(menu_text) < 20:
                return "Undo"
            elif 'redo' in menu_text and len(menu_text) < 20:
                return "Redo"
            elif 'select all' in menu_text:
                return "Select All"
            elif 'find' in menu_text and len(menu_text) < 20:
                return "Find"
            elif 'replace' in menu_text and len(menu_text) < 20:
                return "Replace"
            else:
                # If text is long, it might be multiple menu items - try to extract the first one
                if len(menu_text) > 30:
                    # Split by common separators and take the first meaningful item
                    parts = menu_text.split()
                    for part in parts:
                        if len(part) > 2:  # Skip very short parts
                            if 'copy' in part:
                                return "Copy"
                            elif 'cut' in part:
                                return "Cut"
                            elif 'paste' in part:
                                return "Paste"
                            elif 'reload' in part:
                                return "Reload"
                            elif 'duplicate' in part:
                                return "Duplicate"
                            elif 'delete' in part:
                                return "Delete"
                            elif 'rename' in part:
                                return "Rename"
                            elif 'new' in part:
                                return "New"
                            elif 'open' in part:
                                return "Open"
                            elif 'save' in part:
                                return "Save"
                            elif 'close' in part:
                                return "Close"
                            elif 'undo' in part:
                                return "Undo"
                            elif 'redo' in part:
                                return "Redo"
                            elif 'find' in part:
                                return "Find"
                            elif 'replace' in part:
                                return "Replace"
                
                # If no specific item found, return the cleaned text
                return menu_text.title()
            
        except Exception as e:
            print(f"Error identifying clicked menu item: {e}")
            return "Menu Item (See Screenshot)"
    
    def detect_context_menu_actions(self, x, y):
        """Try to detect what context menu action was performed"""
        try:
            # Wait a bit for the context menu to appear
            time.sleep(0.1)
            
            # Check if we can detect common context menu patterns
            # This is a basic implementation - can be enhanced further
            
            # For now, we'll rely on clipboard monitoring and timing
            # to infer what action was taken
            pass
            
        except Exception as e:
            print(f"Context menu detection error: {e}")
    
    def on_key_press(self, key):
        """Handle keyboard key press events"""
        try:
            key_name = key.char if hasattr(key, 'char') else str(key)
            
            # Check for common shortcuts that might be used after right-click
            if hasattr(key, 'char') and key.char:
                if key.char.lower() == 'c' and self.context_menu_active:
                    self.log_event("Key Press", key_name, context_action="COPY_SHORTCUT")
                elif key.char.lower() == 'v' and self.context_menu_active:
                    self.log_event("Key Press", key_name, context_action="PASTE_SHORTCUT")
                elif key.char.lower() == 'x' and self.context_menu_active:
                    self.log_event("Key Press", key_name, context_action="CUT_SHORTCUT")
                else:
                    self.log_event("Key Press", key_name)
            else:
                self.log_event("Key Press", str(key))
                
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
            print("Now tracking context menu actions and clipboard changes!")
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