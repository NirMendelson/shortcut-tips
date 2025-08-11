import time
import threading
import win32clipboard
import win32con
from pynput import mouse, keyboard
from pynput.mouse import Button

class InputMonitor:
    """Handles mouse and keyboard input monitoring"""
    
    def __init__(self, event_callback, key_press_callback, key_release_callback, context_menu_callback=None):
        self.event_callback = event_callback
        self.key_press_callback = key_press_callback
        self.key_release_callback = key_release_callback
        self.context_menu_callback = context_menu_callback
        self.running = False
        self.mouse_listener = None
        self.keyboard_listener = None
        self.clipboard_monitor_thread = None
        self.last_clipboard_content = None
        
        # Context menu tracking
        self.last_right_click_time = None
        self.right_click_coords = None
        self.context_menu_active = False
    
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
                            self.event_callback("Clipboard Change", f"Content: {clipboard_content[:50]}...", context_action="COPY_DETECTED")
                        self.last_clipboard_content = clipboard_content
                    
                except Exception as e:
                    pass  # Clipboard might be locked by other applications
                
                time.sleep(0.5)  # Check every 500ms
        except Exception as e:
            print(f"Clipboard monitoring error: {e}")
    
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
        """Handle mouse click events with context menu detection"""
        if pressed:
            if button == Button.left:
                # Check if this left-click might be a context menu selection
                if self.last_right_click_time and (time.time() - self.last_right_click_time) < 5.0:
                    # Left-click within 5 seconds of right-click - likely context menu selection
                    self.event_callback("Left Click (Context Menu)", f"X={x}, Y={y}", context_action="MENU_SELECTION")
                    # Call context menu callback for analysis
                    if self.context_menu_callback:
                        self.context_menu_callback(x, y, button, pressed)
                    self.context_menu_active = False
                else:
                    self.event_callback("Left Click", f"X={x}, Y={y}")
                    # Call context menu callback for UI element detection on ALL left clicks
                    if self.context_menu_callback:
                        self.context_menu_callback(x, y, button, pressed)
                    
            elif button == Button.right:
                self.event_callback("Right Click", f"X={x}, Y={y}", context_action="CONTEXT_MENU_OPENED")
                self.last_right_click_time = time.time()
                self.right_click_coords = (x, y)
                self.context_menu_active = True
                # Call context menu callback for analysis
                if self.context_menu_callback:
                    self.context_menu_callback(x, y, button, pressed)
    
    def on_key_press(self, key):
        """Handle keyboard key press events"""
        try:
            key_name = key.char if hasattr(key, 'char') else str(key)
            
            # Check for common shortcuts that might be used after right-click
            if hasattr(key, 'char') and key.char:
                if key.char.lower() == 'c' and self.context_menu_active:
                    self.event_callback("Key Press", key_name, context_action="COPY_SHORTCUT")
                elif key.char.lower() == 'v' and self.context_menu_active:
                    self.event_callback("Key Press", key_name, context_action="PASTE_SHORTCUT")
                elif key.char.lower() == 'x' and self.context_menu_active:
                    self.event_callback("Key Press", key_name, context_action="CUT_SHORTCUT")
                else:
                    self.event_callback("Key Press", key_name)
            else:
                self.event_callback("Key Press", str(key))
                
        except AttributeError:
            # Special keys like ctrl, alt, etc.
            self.event_callback("Key Press", str(key))
    
    def on_key_release(self, key):
        """Handle keyboard key release events"""
        try:
            key_name = key.char if hasattr(key, 'char') else str(key)
            self.event_callback("Key Release", key_name)
        except AttributeError:
            self.event_callback("Key Release", str(key))
    
    def start_listeners(self):
        """Start input listeners with error handling"""
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
            return True
            
        except Exception as e:
            print(f"Warning: Could not start input listeners: {e}")
            print("Continuing with window tracking only...")
            return False
    
    def stop_listeners(self):
        """Stop all input listeners"""
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
    
    def start(self):
        """Start input monitoring"""
        self.running = True
        self.start_clipboard_monitoring()
        return self.start_listeners()
    
    def stop(self):
        """Stop input monitoring"""
        self.running = False
        self.stop_listeners()
