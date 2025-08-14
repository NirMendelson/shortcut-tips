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

    def _wait_for_title_settle(self, hwnd, timeout=0.5, step=0.04):
        """Poll GetWindowText until it stabilizes or timeout"""
        import win32gui
        t0 = time.time()
        last = win32gui.GetWindowText(hwnd) or ""
        while time.time() - t0 < timeout:
            time.sleep(step)
            cur = win32gui.GetWindowText(hwnd) or ""
            if cur != last:
                # confirm stability with one extra read
                time.sleep(step)
                cur2 = win32gui.GetWindowText(hwnd) or ""
                if cur2 == cur:
                    return cur
                last = cur2
        return last

    def _foreground_info(self, settle_for_chrome=True):
        """Return (app_name, window_title, hwnd) for current foreground window"""
        import win32gui
        import win32process
        try:
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return ("Unknown", "Unknown", None)
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            app_name = "Unknown"
            if pid:
                p = psutil.Process(pid)
                if p and p.name():
                    app_name = p.name().replace(".exe", "")
            if app_name.lower() == "chrome" and settle_for_chrome:
                title = self._wait_for_title_settle(hwnd)
            else:
                title = win32gui.GetWindowText(hwnd) or "Unknown"
            return (app_name, title, hwnd)
        except Exception:
            return ("Unknown", "Unknown", None)

    def _wait_for_foreground_targets(self, targets, timeout=0.5, step=0.02):
        """
        Wait until the foreground app name lower() is in targets.
        If Chrome becomes foreground, also wait for tab title to settle.
        Returns (app_name, window_title, hwnd). Falls back to last reading on timeout.
        """
        t0 = time.time()
        last = self._foreground_info(settle_for_chrome=False)
        while time.time() - t0 < timeout:
            app, title, hwnd = self._foreground_info(settle_for_chrome=False)
            last = (app, title, hwnd)
            if app.lower() in targets:
                # If Chrome, settle the title before returning
                if app.lower() == "chrome" and hwnd:
                    settled_title = self._wait_for_title_settle(hwnd)
                    return (app, settled_title, hwnd)
                return (app, title, hwnd)
            time.sleep(step)
        # Timeout, return last seen
        app, title, hwnd = last
        if app.lower() == "chrome" and hwnd:
            title = self._wait_for_title_settle(hwnd)
        return (app, title, hwnd)

    def detect_ui_element(self, x, y):
        """Detect what UI element was clicked at coordinates (x, y) with foreground reconciliation."""
        try:
            # 1) Read the element under the cursor
            element = self.ui_desk.from_point(x, y)
            info = element.element_info
            rect = element.rectangle()

            # 2) App from the clicked element (may be wrong during app switches or taskbar clicks)
            element_app = "Unknown"
            try:
                if info.process_id:
                    proc = psutil.Process(info.process_id)
                    if proc and proc.name():
                        element_app = proc.name().replace(".exe", "")
            except:
                pass

            # 3) After the click, wait for the real foreground app to become either:
            #    - the app of the clicked element, or
            #    - Chrome (very common when switching into Chrome)
            targets = set(filter(None, [element_app.lower(), "chrome"]))
            fg_app, fg_title, _ = self._wait_for_foreground_targets(targets, timeout=0.5, step=0.02)

            window_title = None
            effective_app = fg_app if fg_app != "Unknown" else element_app
            effective_name = info.name or "Unknown Element"

            # Prefer the settled foreground information
            if effective_app.lower() == "chrome":
                window_title = fg_title
                # If the clicked element is not from Chrome or has no useful name, use tab title as the element name
                if not info.name or not info.name.strip() or element_app.lower() != "chrome":
                    effective_name = fg_title if fg_title and fg_title.strip() else "Chrome Window"
                print(f"🔍 Chrome Debug - Element: '{info.name}' | Type: {info.control_type} | ID: {getattr(info, 'automation_id', 'None')}")

            # If still unknown name, use window title as a fallback label
            if (not effective_name or effective_name == "Unknown Element") and window_title:
                effective_name = window_title

            if effective_app != "Unknown":
                print(f"🔍 Detected app: {effective_app} for element: {effective_name}")

            return {
                "name": effective_name or "Unknown Element",
                "type": str(info.control_type),
                "automation_id": getattr(info, "automation_id", None),
                "class_name": getattr(info, "class_name", None),
                "app_name": effective_app,
                "window_title": window_title,  # set for Chrome
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
            app_name, window_title, _ = self._foreground_info(settle_for_chrome=True)
            window_info = {
                "title": window_title or "Unknown",
                "app_name": app_name,
                "timestamp": current_time
            }

            # Cache only for non-Chrome
            if app_name.lower() != "chrome":
                self.last_active_window = window_info
                self.last_active_window_time = current_time
            else:
                self.last_active_window = None
                self.last_active_window_time = 0

            return window_info

        except Exception:
            return {
                "title": "Unknown",
                "app_name": "Unknown",
                "timestamp": current_time
            }
