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
        
        # Caps Lock tracking
        self.caps_lock_active = False
        
        # Language tracking
        self.current_language = "Unknown"
        self.last_language_check = 0
        self.language_check_interval = 0.5  # Check every 500ms
    
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
                
                # Use shorter sleep time and check running status more frequently
                for _ in range(10):  # Check 10 times per second
                    if not self.running:
                        break
                    time.sleep(0.1)
                    
                # Also check Caps Lock state and language periodically
                self.refresh_caps_lock_state()
                self.detect_current_language()
                    
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
                print(f"🔤 Keyboard event: {key}")  # Debug output
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
                    self.event_callback("Left Click (Context Menu)", "Context Menu Selection", context_action="MENU_SELECTION")
                    # Call context menu callback for analysis
                    if self.context_menu_callback:
                        self.context_menu_callback(x, y, button, pressed)
                    self.context_menu_active = False
                else:
                    self.event_callback("Left Click", "Left Click")
                    # Call context menu callback for UI element detection on ALL left clicks
                    if self.context_menu_callback:
                        self.context_menu_callback(x, y, button, pressed)
                    
            elif button == Button.right:
                self.event_callback("Right Click", "Right Click", context_action="CONTEXT_MENU_OPENED")
                self.last_right_click_time = time.time()
                self.right_click_coords = (x, y)
                self.context_menu_active = True
                # Call context menu callback for analysis
                if self.context_menu_callback:
                    self.context_menu_callback(x, y, button, pressed)
    
    def on_key_press(self, key):
        """Handle keyboard key press events - log meaningful keys and shortcuts"""
        try:
            # Check for common shortcuts that might be used after right-click
            if hasattr(key, 'char') and key.char:
                # Handle regular character keys
                char = key.char
                
                # Check for context menu shortcuts
                if char.lower() == 'c' and self.context_menu_active:
                    self.event_callback("Key Press", "C", context_action="COPY_SHORTCUT")
                elif char.lower() == 'v' and self.context_menu_active:
                    self.event_callback("Key Press", "V", context_action="PASTE_SHORTCUT")
                elif char.lower() == 'x' and self.context_menu_active:
                    self.event_callback("Key Press", "X", context_action="CUT_SHORTCUT")
                # Log regular characters with proper case handling
                else:
                    # Apply Caps Lock logic to alphabetic characters
                    if char.isalpha():
                        if self.caps_lock_active:
                            # Caps Lock is ON, so show uppercase
                            display_char = char.upper()
                        else:
                            # Caps Lock is OFF, show as typed
                            display_char = char
                    else:
                        # Non-alphabetic characters (numbers, symbols) are not affected by Caps Lock
                        display_char = char
                    
                    # Add context about Caps Lock state and language
                    context = "TYPING"
                    if self.caps_lock_active:
                        context = "TYPING_CAPS"
                    
                    # Debug output to show character, state, and language
                    print(f"🔤 Typing: '{char}' → '{display_char}' (Caps: {'ON' if self.caps_lock_active else 'OFF'}, Lang: {self.current_language})")
                    
                    # Log the properly formatted character with language context
                    self.event_callback("Key Press", display_char, context_action=context)
            else:
                # Handle special keys (Ctrl, Alt, Shift, etc.)
                key_str = str(key)
                formatted_key = self.format_key_name(key_str)
                
                # Handle Caps Lock specifically
                if 'caps_lock' in key_str.lower():
                    self.caps_lock_active = not self.caps_lock_active  # Toggle state
                    status = "ON" if self.caps_lock_active else "OFF"
                    self.event_callback("Key Press", f"Caps Lock {status}", context_action="CAPS_LOCK_TOGGLE")
                # Log other important special keys
                elif any(special in key_str.lower() for special in ['ctrl', 'alt', 'shift', 'win', 'tab', 'enter', 'escape', 'backspace', 'delete']):
                    self.event_callback("Key Press", formatted_key, context_action="SPECIAL_KEY")
                # Skip other special keys to reduce noise
                
        except AttributeError:
            # Skip unknown keys to reduce noise
            pass
    
    def on_key_release(self, key):
        """Handle keyboard key release events - skip to reduce noise"""
        pass
        
    def format_key_name(self, key_str):
        """Format key names to be more user-friendly"""
        # Remove "Key." prefix and format nicely
        if key_str.startswith("Key."):
            key_name = key_str[4:]  # Remove "Key." prefix
        else:
            key_name = key_str
            
        # Format specific keys
        key_mapping = {
            "space": "Space",
            "backspace": "Backspace",
            "delete": "Delete",
            "enter": "Enter",
            "tab": "Tab",
            "escape": "Escape",
            "shift": "Shift",
            "shift_l": "Shift",
            "shift_r": "Shift",
            "ctrl": "Ctrl",
            "ctrl_l": "Ctrl",
            "ctrl_r": "Ctrl",
            "alt": "Alt",
            "alt_l": "Alt",
            "alt_r": "Alt",
            "win": "Windows",
            "up": "↑",
            "down": "↓",
            "left": "←",
            "right": "→",
            "page_up": "Page Up",
            "page_down": "Page Down",
            "home": "Home",
            "end": "End",
            "insert": "Insert",
            "print_screen": "Print Screen",
            "scroll_lock": "Scroll Lock",
            "pause": "Pause",
            "num_lock": "Num Lock",
            "caps_lock": "Caps Lock",
            "f1": "F1",
            "f2": "F2",
            "f3": "F3",
            "f4": "F4",
            "f5": "F5",
            "f6": "F6",
            "f7": "F7",
            "f8": "F8",
            "f9": "F9",
            "f10": "F10",
            "f11": "F11",
            "f12": "F12"
        }
        
        # Return formatted key name or capitalize the original
        return key_mapping.get(key_name.lower(), key_name.title())
    
    def start_listeners(self):
        """Start input listeners with error handling"""
        try:
            print("🎯 Starting mouse listener...")
            self.mouse_listener = mouse.Listener(
                on_click=self.safe_mouse_callback
            )
            
            print("🎯 Starting keyboard listener...")
            self.keyboard_listener = keyboard.Listener(
                on_press=lambda key: self.safe_keyboard_callback(key, True),
                on_release=lambda key: self.safe_keyboard_callback(key, False)
            )
            
            self.mouse_listener.start()
            print("✅ Mouse listener started")
            
            self.keyboard_listener.start()
            print("✅ Keyboard listener started")
            
            print("🎯 Input listeners started successfully")
            return True
            
        except Exception as e:
            print(f"❌ Warning: Could not start input listeners: {e}")
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
        
        # Wait for clipboard monitoring thread to finish
        if self.clipboard_monitor_thread and self.clipboard_monitor_thread.is_alive():
            try:
                self.clipboard_monitor_thread.join(timeout=1.0)  # Wait max 1 second
            except:
                pass
    
    def start(self):
        """Start input monitoring"""
        self.running = True
        
        # Check initial Caps Lock state and language
        self.check_caps_lock_state()
        self.detect_current_language()
        
        self.start_clipboard_monitoring()
        return self.start_listeners()
        
    def check_caps_lock_state(self):
        """Check the current Caps Lock state from the system"""
        try:
            import win32api
            import win32con
            
            # Get the current keyboard state
            state = win32api.GetKeyState(win32con.VK_CAPITAL)
            # If the high-order bit is 1, the key is down
            self.caps_lock_active = (state & 0x0001) != 0
            
            print(f"🔤 Initial Caps Lock state: {'ON' if self.caps_lock_active else 'OFF'}")
            
        except Exception as e:
            print(f"⚠️ Could not detect Caps Lock state: {e}")
            self.caps_lock_active = False
            
    def refresh_caps_lock_state(self):
        """Refresh Caps Lock state from system (call this periodically)"""
        try:
            import win32api
            import win32con
            
            state = win32api.GetKeyState(win32con.VK_CAPITAL)
            new_state = (state & 0x0001) != 0
            
            if new_state != self.caps_lock_active:
                self.caps_lock_active = new_state
                print(f"🔤 Caps Lock state changed to: {'ON' if self.caps_lock_active else 'OFF'}")
                
        except Exception as e:
            pass  # Silently fail if we can't check
            
    def detect_current_language(self):
        """Detect the current input language"""
        try:
            import win32api
            import win32gui
            import win32process
            
            # Get the foreground window
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                # Get the thread ID of the foreground window
                thread_id = win32gui.GetWindowThreadProcessId(hwnd)[0]
                
                # Get the keyboard layout for this thread
                layout_id = win32api.GetKeyboardLayout(thread_id)
                
                # Convert layout ID to language name
                language_map = {
                    0x409: "English (US)",
                    0x40D: "Hebrew",
                    0x40C: "French",
                    0x407: "German",
                    0x410: "Italian",
                    0x40A: "Spanish",
                    0x416: "Portuguese",
                    0x419: "Russian",
                    0x411: "Japanese",
                    0x412: "Korean",
                    0x804: "Chinese (Simplified)",
                    0x404: "Chinese (Traditional)"
                }
                
                language_name = language_map.get(layout_id & 0xFFFF, f"Unknown ({hex(layout_id)})")
                
                if language_name != self.current_language:
                    old_language = self.current_language
                    self.current_language = language_name
                    print(f"🌍 Language changed from {old_language} to {language_name}")
                    
                    # Log language change event
                    if hasattr(self, 'event_callback'):
                        self.event_callback("Language Change", f"Switched to {language_name}", context_action="LANGUAGE_SWITCH")
                    
                return language_name
                
        except Exception as e:
            print(f"⚠️ Could not detect language: {e}")
            return "Unknown"
    
    def stop(self):
        """Stop input monitoring"""
        self.running = False
        self.stop_listeners()
