#!/usr/bin/env python3
"""
UI Automation Manager for Shortcut Coach
Handles Windows UI Automation for detecting UI elements and actions
"""

import time
from pywinauto import Desktop
import psutil
from datetime import datetime

class UIAutomationManager:
    """Manages Windows UI Automation for detecting UI elements"""
    
    def __init__(self, notification_system):
        self.notification_system = notification_system
        self.ui_desk = Desktop(backend="uia")
        self.last_click_time = 0
        self.click_cooldown = 0.1  # 100ms cooldown between clicks
        
        # Cache for active window info
        self.last_active_window = None
        self.last_active_window_time = 0
        self.window_cache_duration = 0.5  # Cache for 500ms
        
        # Session tracking
        self.session_start_time = datetime.now().isoformat()
        print(f"🕐 Session started at: {self.session_start_time}")
        
        # Add deduplication system to prevent double logging
        self.last_events = {}  # Track last event of each type
        self.event_cooldown = 1.0  # 1 second cooldown between same event types
        
    def should_process_click(self, x, y):
        """Check if we should process this click (avoid duplicates)"""
        current_time = time.time()
        if current_time - self.last_click_time < self.click_cooldown:
            return False
        
        self.last_click_time = current_time
        return True
    
    def detect_ui_element(self, x, y):
        """Detect what UI element was clicked at coordinates (x, y)"""
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
            elif "open file" in element_name:
                return "Ctrl + O", "Open File"
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
            elif "find" in element_name:
                return "Ctrl + F", "Find"
            elif "replace" in element_name:
                return "Ctrl + H", "Replace"
        
        # Chrome shortcuts
        elif "chrome" in app_name:
            if "new tab" in element_name:
                return "Ctrl + T", "New Tab"
            elif "close tab" in element_name:
                return "Ctrl + W", "Close Tab"
            elif "refresh" in element_name:
                return "F5", "Refresh"
            elif "back" in element_name:
                return "Alt + ←", "Go Back"
            elif "forward" in element_name:
                return "Alt + →", "Go Forward"
            elif "bookmark" in element_name:
                return "Ctrl + D", "Bookmark"
        
        # Generic shortcuts for any application
        if "copy" in element_name:
            return "Ctrl + C", "Copy"
        elif "paste" in element_name:
            return "Ctrl + V", "Paste"
        elif "cut" in element_name:
            return "Ctrl + X", "Cut"
        elif "save" in element_name:
            return "Ctrl + S", "Save"
        elif "new" in element_name:
            return "Ctrl + N", "New"
        elif "open" in element_name:
            return "Ctrl + O", "Open"
        elif "undo" in element_name:
            return "Ctrl + Z", "Undo"
        elif "redo" in element_name:
            return "Ctrl + Y", "Redo"
        elif "find" in element_name:
            return "Ctrl + F", "Find"
        elif "print" in element_name:
            return "Ctrl + P", "Print"
        
        return None
    
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
        
        # Use cache if still valid
        if (self.last_active_window and 
            current_time - self.last_active_window_time < self.window_cache_duration):
            return self.last_active_window
        
        try:
            # Get active window
            active_window = self.ui_desk.active()
            window_title = active_window.window_text()
            
            # Get process info
            process_id = active_window.process_id()
            try:
                process = psutil.Process(process_id)
                app_name = process.name()
            except:
                app_name = "Unknown"
            
            window_info = {
                "title": window_title,
                "app_name": app_name,
                "timestamp": current_time
            }
            
            # Update cache
            self.last_active_window = window_info
            self.last_active_window_time = current_time
            
            return window_info
            
        except Exception as e:
            return {
                "title": "Unknown",
                "app_name": "Unknown",
                "timestamp": current_time
            }
