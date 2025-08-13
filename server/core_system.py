#!/usr/bin/env python3
"""
Core System for Shortcut Coach
Handles the main ShortcutCoach class and core system functionality
"""

import time
import sys
from PyQt6.QtWidgets import QApplication
from database import DatabaseManager
from screenshot import ScreenshotManager
from notification_pyqt6 import PyQt6NotificationSystem as NotificationSystem
from input_monitor import InputMonitor
from context_analyzer import ContextAnalyzer
from window_monitor import WindowMonitor
from action_detector import ActionDetector
from gui_manager import ShortcutCoachGUI
from ui_automation_manager import UIAutomationManager
from shortcut_manager import ShortcutManager

class ShortcutCoach:
    """Main Shortcut Coach system that coordinates all components"""
    
    def __init__(self):
        # Initialize PyQt6 application in main thread
        self.qt_app = QApplication([])
        
        # Initialize all modules
        self.db_manager = DatabaseManager()
        self.screenshot_manager = ScreenshotManager()
        self.notification_system = NotificationSystem()
        self.window_monitor = WindowMonitor()
        
        # Initialize context analyzer with notification system
        self.context_analyzer = ContextAnalyzer(self.notification_system)
        
        # Initialize action detector for Excel actions
        self.action_detector = ActionDetector(self.notification_system)
        
        # Initialize UI automation manager
        self.ui_manager = UIAutomationManager(self.notification_system)
        
        # Initialize central shortcut manager
        self.shortcut_manager = ShortcutManager()
        
        # Initialize GUI
        self.gui = ShortcutCoachGUI(self)
        self.gui.show()  # Make sure the GUI is visible
        
        # Initialize input monitor with callbacks
        self.input_monitor = InputMonitor(
            event_callback=self.log_event,
            key_press_callback=self.on_key_press,
            key_release_callback=lambda key: None,  # We don't need key release events
            context_menu_callback=None,
            mouse_click_callback=self.on_mouse_click
        )
        
        # System state
        self.running = False
        
        print("🎯 Shortcut Coach initialized successfully!")
        print("📊 GUI is now visible with live tracking!")
        print("🎯 Now tracking UI elements in real-time using Windows UI Automation!")
        print("💡 Click on any button, tab, or UI element to get shortcut suggestions!")
        print("🔴 Check the Live Tracker tab to see real-time events!")
        print("-" * 50)
        
    def log_event(self, event_type, details, x=None, y=None, app_name=None, 
                  window_title=None, context_action=None):
        """Log an event to the database"""
        try:
            # Get current window info if not provided
            if not app_name or not window_title:
                window_info = self.ui_manager.get_active_window_info()
                if not app_name:
                    app_name = window_info["app_name"]
                if not window_title:
                    window_title = window_info["title"]
            
            # Check if we should log this event (prevent duplicates)
            if not self.ui_manager.should_log_event(event_type, details, app_name):
                return
            
            # Log to database
            self.db_manager.log_event(
                event_type=event_type,
                details=details,
                app_name=app_name,
                window_title=window_title,
                context_action=context_action
            )
            
            # Print to console for debugging
            print(f"📝 {event_type}: {details} | {app_name} - {window_title}")
            
        except Exception as e:
            print(f"❌ Error logging event: {e}")
    
    def on_key_press(self, key):
        """Handle key press events"""
        try:
            key_name = str(key)
            print(f"⌨️ Key Press: {key_name}")
            
            # Get current active window info to get the app name
            window_info = self.ui_manager.get_active_window_info()
            app_name = window_info.get("app_name", "Unknown")
            window_title = window_info.get("title", "Unknown")
            
            # Debug output for keyboard events
            print(f"🔍 Key press in app: {app_name} - {window_title}")
            
            # Log the key press with proper app name
            self.log_event(
                event_type="Key Press",
                details=key_name,
                app_name=app_name,
                window_title=window_title,
                context_action=f"KEY_{key_name.upper()}"
            )
            
        except Exception as e:
            print(f"❌ Error handling key press: {e}")
    
    def on_mouse_click(self, x, y, button, pressed):
        """Handle mouse click events"""
        try:
            if pressed and button.name == 'left':
                # Handle context menu detection
                if self.input_monitor.context_menu_active:
                    # Context menu was active, analyze the action
                    element_info = self.ui_manager.detect_ui_element(x, y)
                    
                    # Only process if we got valid element info
                    if element_info and 'error' not in element_info:
                        element_name = element_info.get('name', 'Unknown Element')
                        app_name = element_info.get('app_name', 'Unknown App')
                        
                        print(f"🖱️ Context Menu Click: {element_name} in {app_name}")
                        
                        # Get shortcut suggestion
                        result = self.ui_manager.get_shortcut_suggestion(element_info)
                        if result:
                            shortcut, description = result
                            self.notification_system.suggest_shortcut(description, shortcut)
                            # Get database key from central shortcut manager
                            db_key = self.shortcut_manager.get_shortcut_database_key((shortcut, description))
                            self.log_event("Shortcut Suggested", f"{shortcut} for {description}", 
                                         context_action=db_key)
                        else:
                            print(f"ℹ️ No shortcut available for {element_name}")
                        
                        # Also detect actions (like Excel cell navigation)
                        shortcut_info = self.action_detector.detect_action(x, y, app_name)

                        # Log the context menu click with proper app name
                        self.log_event(
                            event_type="Context Menu Click",
                            details=f"Clicked {element_name}",
                            app_name=app_name,
                            context_action="CONTEXT_MENU_CLICK"
                        )

                        # If action detector found a shortcut, log it
                        if shortcut_info:
                            shortcut, description = shortcut_info
                            # Send notification for action detector shortcuts
                            self.notification_system.suggest_shortcut(description, shortcut)
                            db_key = self.shortcut_manager.get_shortcut_database_key((shortcut, description))
                            self.log_event("Shortcut Suggested", f"{shortcut} for {description}",
                                         context_action=db_key)
                
                self.input_monitor.context_menu_active = False
            else:
                # Regular left click - detect UI element
                if self.ui_manager.should_process_click(x, y):
                    element_info = self.ui_manager.detect_ui_element(x, y)
                    
                    # Only process if we got valid element info
                    if element_info and 'error' not in element_info:
                        element_name = element_info.get('name', 'Unknown Element')
                        app_name = element_info.get('app_name', 'Unknown App')
                        
                        print(f"🖱️ Clicked: {element_name} in {app_name}")
                        
                        # Get shortcut suggestion for buttons
                        result = self.ui_manager.get_shortcut_suggestion(element_info)
                        if result:
                            shortcut, description = result
                            self.notification_system.suggest_shortcut(description, shortcut)
                            # Get database key from central shortcut manager
                            db_key = self.shortcut_manager.get_shortcut_database_key((shortcut, description))
                            self.log_event("Shortcut Suggested", f"{shortcut} for {description}", 
                                         context_action=db_key)
                        else:
                            print(f"ℹ️ No shortcut available for {element_name}")
                        
                        # Also detect actions (like Excel cell navigation)
                        shortcut_info = self.action_detector.detect_action(x, y, app_name)

                        # Log the UI element click with proper app name
                        self.log_event(
                            event_type="UI Element Click",
                            details=f"Clicked {element_name}",
                            app_name=app_name,
                            context_action="UI_CLICK"
                        )

                        # If action detector found a shortcut, log it
                        if shortcut_info:
                            shortcut, description = shortcut_info
                            # Send notification for action detector shortcuts
                            self.notification_system.suggest_shortcut(description, shortcut)
                            db_key = self.shortcut_manager.get_shortcut_database_key((shortcut, description))
                            self.log_event("Shortcut Suggested", f"{shortcut} for {description}",
                                         context_action=db_key)
                
                # Now we log UI element clicks with proper app names
                
        except Exception as e:
            print(f"❌ Error handling mouse click: {e}")
        
        # Handle right click separately
        if pressed and button.name == 'right':
            # Don't log here - InputMonitor already logged it
            pass
    
    def start_tracking(self):
        """Start event tracking"""
        try:
            print("🚀 Starting Shortcut Coach...")
            print("📊 GUI is now visible with live tracking!")
            print("🎯 Now tracking UI elements in real-time using Windows UI Automation!")
            print("💡 Click on any button, tab, or UI element to get shortcut suggestions!")
            print("🔴 Check the Live Tracker tab to see real-time events!")
            print("-" * 50)
            
            self.running = True
            
            # Start input monitoring
            input_started = self.input_monitor.start()
            if not input_started:
                print("⚠️ Warning: Input monitoring failed, continuing with window tracking only...")
            
            # Keep the main thread alive and track windows
            try:
                while self.running:
                    # Process Qt events to keep GUI and notifications working
                    self.qt_app.processEvents()
                    time.sleep(0.1)  # Reduced sleep time for better responsiveness
                    
                    # Log window changes periodically
                    window_title, app_name = self.window_monitor.check_window_change()
                    if window_title:
                        print(f"🖥️ Active Window: {app_name} - {window_title}")
                        
            except KeyboardInterrupt:
                print("\n🛑 Stopping Shortcut Coach...")
                self.stop_tracking()
                print("✅ Tracking stopped successfully")
            except Exception as e:
                print(f"❌ Error in main tracking loop: {e}")
                self.stop_tracking()
                
        except PermissionError:
            print("❌ ERROR: Global keyboard/mouse tracking requires administrator privileges.")
            print("Please run this program as administrator and try again.")
            sys.exit(1)
        except Exception as e:
            print(f"❌ ERROR: Failed to start tracking: {e}")
            print("This might be due to permission issues or system restrictions.")
            sys.exit(1)
    
    def stop_tracking(self):
        """Stop all tracking"""
        self.running = False
        self.input_monitor.stop()
        self.notification_system.stop()
        if self.qt_app:
            self.qt_app.quit()
