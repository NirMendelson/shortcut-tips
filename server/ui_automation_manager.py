#!/usr/bin/env python3
"""
UI Automation Manager for Shortcut Coach
Handles Windows UI Automation for detecting UI elements and actions
"""

import time
from pywinauto import Desktop
import psutil
from datetime import datetime
from shortcut_manager import ShortcutManager

class UIAutomationManager:
    """Manages Windows UI Automation for detecting UI elements"""

    def __init__(self, notification_system):
        self.notification_system = notification_system
        self.ui_desk = Desktop(backend="uia")
        self.last_click_time = 0
        self.click_cooldown = 0.1  # 100ms cooldown between clicks

        # Initialize central shortcut manager
        self.shortcut_manager = ShortcutManager()

        # Cache for active window info (kept minimal)
        self.last_active_window = None
        self.last_active_window_time = 0
        self.window_cache_duration = 0.25  # 250ms for non-Chrome

        # Session tracking
        self.session_start_time = datetime.now().isoformat()
        print(f"🕐 Session started at: {self.session_start_time}")

        # Dedup to prevent double logging
        self.last_events = {}  # Track last event of each type
        self.event_cooldown = 1.0  # 1 second cooldown between same event types

    def should_process_click(self, x, y):
        """Check if we should process this click (avoid duplicates)"""
        current_time = time.time()
        if current_time - self.last_click_time < self.click_cooldown:
            return False

        self.last_click_time = current_time
        return True

    def _wait_for_title_settle(self, hwnd, timeout=0.35, step=0.04):
        """Poll GetWindowText until it stabilizes or timeout"""
        import win32gui
        t0 = time.time()
        last = win32gui.GetWindowText(hwnd) or ""
        while time.time() - t0 < timeout:
            time.sleep(step)
            cur = win32gui.GetWindowText(hwnd) or ""
            # If title changed and then stayed the same for one more step, assume it's settled
            if cur != last:
                # one more short check
                time.sleep(step)
                cur2 = win32gui.GetWindowText(hwnd) or ""
                if cur2 == cur:
                    return cur
                last = cur2
            else:
                # unchanged this cycle; keep looping until timeout
                pass
        return last

    def detect_ui_element(self, x, y):
        """Detect what UI element was clicked at coordinates (x, y)"""
        try:
            # Get element at click point
            element = self.ui_desk.from_point(x, y)
            element_info = element.element_info
            rect = element.rectangle()

            # Get process info with multiple fallback methods
            app_name = "Unknown"
            try:
                # Method 1: from element process ID
                process_id = element_info.process_id
                if process_id:
                    process = psutil.Process(process_id)
                    app_name = process.name().replace('.exe', '') if process.name() else "Unknown"
            except:
                try:
                    # Method 2: from active window
                    active_window = self.ui_desk.active()
                    if active_window:
                        process_id = active_window.process_id()
                        if process_id:
                            process = psutil.Process(process_id)
                            app_name = process.name().replace('.exe', '') if process.name() else "Unknown"
                except:
                    try:
                        # Method 3: from foreground HWND
                        import win32gui
                        import win32process
                        hwnd = win32gui.GetForegroundWindow()
                        if hwnd:
                            _, process_id = win32process.GetWindowThreadProcessId(hwnd)
                            if process_id:
                                process = psutil.Process(process_id)
                                app_name = process.name().replace('.exe', '') if process.name() else "Unknown"
                        else:
                            app_name = "Unknown"
                    except:
                        app_name = "Unknown"

            # Debug output for application detection
            if app_name != "Unknown":
                print(f"🔍 Detected app: {app_name} for element: {element_info.name}")

            # Extra handling for Chrome: force-refresh the window title AFTER the click
            # so we don't log the previous tab name.
            if "chrome" in app_name.lower():
                try:
                    import win32gui
                    import win32process
                    hwnd = win32gui.GetForegroundWindow()
                    if hwnd:
                        # Wait briefly for Chrome to apply the new title
                        settled_title = self._wait_for_title_settle(hwnd)
                        print(f"🔍 Chrome Debug - Element: '{element_info.name}' | Type: {element_info.control_type} | ID: {getattr(element_info, 'automation_id', 'None')}")
                        # Attach the fresh, settled title to the returned info
                        window_title = settled_title
                    else:
                        window_title = None
                except:
                    window_title = None
            else:
                window_title = None

            # Return element information
            return {
                "name": element_info.name or "Unknown Element",
                "type": str(element_info.control_type),
                "automation_id": getattr(element_info, "automation_id", None),
                "class_name": getattr(element_info, "class_name", None),
                "app_name": app_name,
                "window_title": window_title,  # may hold fresh Chrome tab title
                "coordinates": (x, y),
                "bounds": (rect.left, rect.top, rect.right, rect.bottom),
                "center": ((rect.left + rect.right) // 2, (rect.top + rect.bottom) // 2)
            }

        except Exception as e:
            return {
                "error": str(e),
                "coordinates": (x, y),
                "app_name": "Unknown",
                "window_title": None
            }

    def get_shortcut_suggestion(self, element_info):
        """Get shortcut suggestion using central shortcut manager"""
        return self.shortcut_manager.get_shortcut_suggestion(element_info)

    def should_log_event(self, event_type, details, app_name=None):
        """Check if we should log this event (prevent duplicates)"""
        current_time = time.time()
        event_key = f"{event_type}_{details}_{app_name}"

        if event_key in self.last_events:
            last_time = self.last_events[event_key]
            if current_time - last_time < self.event_cooldown:
                return False

        self.last_events[event_key] = current_time
        return True

    def get_active_window_info(self):
        """Get current active window information"""
        current_time = time.time()

        # Use cache only for non-Chrome to avoid stale tab titles
        if self.last_active_window:
            cached = self.last_active_window
            if cached.get("app_name", "").lower() != "chrome":
                if current_time - self.last_active_window_time < self.window_cache_duration:
                    return cached

        try:
            import win32gui
            import win32process

            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                _, process_id = win32process.GetWindowThreadProcessId(hwnd)
                if process_id:
                    process = psutil.Process(process_id)
                    app_name = process.name().replace('.exe', '') if process.name() else "Unknown"
                else:
                    app_name = "Unknown"
            else:
                app_name = "Unknown"

            # For Chrome, wait for the title to settle to avoid one-click lag
            if app_name.lower() == "chrome" and hwnd:
                window_title = self._wait_for_title_settle(hwnd)
            else:
                window_title = win32gui.GetWindowText(hwnd) if hwnd else "Unknown"

            window_info = {
                "title": window_title or "Unknown",
                "app_name": app_name,
                "timestamp": current_time
            }

            # Update cache only for non-Chrome
            if app_name.lower() != "chrome":
                self.last_active_window = window_info
                self.last_active_window_time = current_time
            else:
                # Do not cache Chrome so next query can pick up new tab immediately
                self.last_active_window = None
                self.last_active_window_time = 0

            return window_info

        except Exception:
            return {
                "title": "Unknown",
                "app_name": "Unknown",
                "timestamp": current_time
            }
