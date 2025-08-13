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
from pywinauto import Desktop
import psutil
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QTextEdit,
    QPushButton, QProgressBar, QGroupBox, QScrollArea
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont, QPalette, QColor
from shortcuts_database import SHORTCUTS_DATABASE
import sqlite3
from datetime import datetime, timedelta

class DataCollector:
    """Simple data collector for the GUI"""
    
    def __init__(self):
        self.running = False
        
    def start(self):
        """Start data collection"""
        self.running = True
        
    def stop(self):
        """Stop data collection"""
        self.running = False

class ShortcutCoachGUI(QMainWindow):
    def __init__(self, shortcut_coach):
        super().__init__()
        self.shortcut_coach = shortcut_coach
        self.setWindowTitle("Shortcut Coach - Productivity Analytics")
        self.setGeometry(100, 100, 1200, 800)
        
        # Set modern dark theme
        self.set_dark_theme()
        
        # Initialize UI
        self.init_ui()
        
        # Initialize data collector but don't start it yet
        self.data_collector = DataCollector()
        # Don't start automatically - only when there's real data
        
        # Set up automatic refresh timer for live data
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_live_data)
        self.refresh_timer.start(1000)  # Refresh every 1000ms (1 second)
        
    def set_dark_theme(self):
        """Apply modern dark theme"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #3c3c3c;
                background-color: #2b2b2b;
            }
            QTabBar::tab {
                background-color: #3c3c3c;
                color: #ffffff;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #0078d4;
            }
            QTableWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                gridline-color: #3c3c3c;
                border: none;
            }
            QHeaderView::section {
                background-color: #3c3c3c;
                color: #ffffff;
                padding: 8px;
                border: none;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
    def init_ui(self):
        """Initialize the main UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("Shortcut Coach - Productivity Analytics")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #0078d4; margin: 20px;")
        layout.addWidget(title)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_live_tracker_tab()
        self.create_time_tracker_tab()
        self.create_shortcut_opportunities_tab()
        self.create_custom_suggestions_tab()
        
    def create_live_tracker_tab(self):
        """Tab 1: Live Click Tracker"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Live events table
        self.events_table = QTableWidget()
        self.events_table.setColumnCount(5)
        self.events_table.setHorizontalHeaderLabels([
            "Time", "Details", "App", "Window", "Context Action"
        ])
        
        # Set column widths
        self.events_table.setColumnWidth(0, 150)  # Time
        self.events_table.setColumnWidth(1, 200)  # Details
        self.events_table.setColumnWidth(2, 120)  # App
        self.events_table.setColumnWidth(3, 200)  # Window
        self.events_table.setColumnWidth(4, 150)  # Context Action
        
        # Start with empty table showing "No data yet"
        self.events_table.setRowCount(1)
        self.events_table.setItem(0, 0, QTableWidgetItem("No data yet"))
        self.events_table.setItem(0, 1, QTableWidgetItem(""))
        self.events_table.setItem(0, 2, QTableWidgetItem(""))
        self.events_table.setItem(0, 3, QTableWidgetItem(""))
        self.events_table.setItem(0, 4, QTableWidgetItem(""))
        
        # Live tracker label
        layout.addWidget(QLabel("Live Event Tracker - Data updates automatically as you use your computer"))
        layout.addWidget(self.events_table)
        
        self.tab_widget.addTab(tab, "🔴 Live Tracker")
        
    def create_time_tracker_tab(self):
        """Tab 2: Software Time Tracker"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # App usage table
        self.app_usage_table = QTableWidget()
        self.app_usage_table.setColumnCount(4)
        self.app_usage_table.setHorizontalHeaderLabels([
            "Application", "Events Count", "First Seen", "Last Seen"
        ])
        
        layout.addWidget(QLabel("Time Spent in Each Application - Data will populate as you use apps"))
        layout.addWidget(self.app_usage_table)
        
        self.tab_widget.addTab(tab, "⏱️ Time Tracker")
        
    def create_shortcut_opportunities_tab(self):
        """Tab 3: Shortcut Opportunities"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Missed shortcuts table
        self.missed_shortcuts_table = QTableWidget()
        self.missed_shortcuts_table.setColumnCount(3)
        self.missed_shortcuts_table.setColumnWidth(0, 200)
        self.missed_shortcuts_table.setColumnWidth(1, 100)
        self.missed_shortcuts_table.setColumnWidth(2, 150)
        self.missed_shortcuts_table.setHorizontalHeaderLabels([
            "Missed Action", "Count", "Suggested Shortcut"
        ])
        
        # Start with empty table
        self.missed_shortcuts_table.setRowCount(1)
        self.missed_shortcuts_table.setItem(0, 0, QTableWidgetItem("No data yet"))
        self.missed_shortcuts_table.setItem(0, 1, QTableWidgetItem(""))
        self.missed_shortcuts_table.setItem(0, 2, QTableWidgetItem(""))
        
        layout.addWidget(QLabel("Missed Shortcut Opportunities - Data will appear as you use your computer"))
        layout.addWidget(self.missed_shortcuts_table)
        
        self.tab_widget.addTab(tab, "⌨️ Shortcut Opportunities")
        
    def create_custom_suggestions_tab(self):
        """Tab 4: Custom Shortcut Suggestions"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # AI suggestions area
        suggestions_group = QGroupBox("AI-Powered Workflow Suggestions")
        suggestions_layout = QVBoxLayout(suggestions_group)
        
        self.suggestions_text = QTextEdit()
        self.suggestions_text.setReadOnly(True)
        self.suggestions_text.setMaximumHeight(300)
        
        # Start with empty suggestions
        demo_suggestions = """
🤖 AI Workflow Analysis

No data collected yet. Start using your computer to see personalized shortcut suggestions!

💡 The system will analyze your usage patterns and suggest:
• Custom shortcuts for frequent workflows
• Time-saving opportunities
• Application-specific optimizations
• Multi-app workflow suggestions

Start clicking, typing, and switching between apps to see insights appear!
        """
        
        self.suggestions_text.setPlainText(demo_suggestions)
        suggestions_layout.addWidget(self.suggestions_text)
        
        # Generate new suggestions button
        generate_btn = QPushButton("🔄 Generate New Suggestions")
        generate_btn.clicked.connect(self.generate_suggestions)
        generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        
        suggestions_layout.addWidget(generate_btn)
        layout.addWidget(suggestions_group)
        
        # Usage statistics
        stats_group = QGroupBox("Usage Statistics")
        stats_layout = QVBoxLayout(stats_group)
        
        stats_text = QLabel("""
📈 Your Productivity Stats:
• Total Events Tracked: 0
• Applications Used: 0
• Missed Shortcut Opportunities: 0
• Estimated Time Saved with Shortcuts: 0 minutes
• Most Active Application: None yet
• Most Frequent Action: None yet

💡 Start using your computer to see real-time statistics!
        """)
        stats_text.setStyleSheet("font-size: 12px; line-height: 1.4;")
        stats_layout.addWidget(stats_text)
        
        layout.addWidget(stats_group)
        
        self.tab_widget.addTab(tab, "🤖 AI Suggestions")
        
    def add_demo_shortcut_data(self):
        """Add demo data for shortcut opportunities - now starts empty"""
        # This method is kept for compatibility but no longer adds demo data
        pass
            
    def update_data(self, data):
        """Update all tabs with new data - called from main thread"""
        try:
            if data and isinstance(data, dict):
                self.update_events_table(data.get('events', []))
                self.update_app_usage_table(data.get('app_usage', []))
                self.update_missed_shortcuts_table(data.get('missed_shortcuts', []))
        except Exception as e:
            print(f"Error updating GUI data: {e}")
        
    def start_data_collection(self):
        """Start data collection when there are actual events"""
        if not self.data_collector.running:
            print("📊 Starting data collection in GUI...")
            self.data_collector.start()
            print("🔄 Live Tracker now updating automatically every second!")
            
    def refresh_live_data(self):
        """Manually refresh the live data display"""
        try:
            conn = sqlite3.connect('shortcuts.db')
            cursor = conn.cursor()
            
            # Get recent events
            cursor.execute("""
                SELECT event_type, details, window_title, app_name, timestamp, context_action
                FROM events 
                ORDER BY timestamp DESC 
                LIMIT 20
            """)
            events = cursor.fetchall()
            conn.close()
            
            # Update the table safely
            if events:
                self.update_events_table(events)
            else:
                self.update_events_table([]) # Ensure table shows "No data yet"
            
        except Exception as e:
            print(f"❌ Error refreshing data: {e}")
        
    def update_events_table(self, events):
        """Update the events table with new data"""
        if not events:
            # Keep "No data yet" message if no events
            return
            
        # Clear the "No data yet" row and add real data
        self.events_table.setRowCount(len(events))
        for i, (event_type, details, window_title, app_name, timestamp, context_action) in enumerate(events):
            # Format timestamp
            try:
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime("%H:%M:%S")
            except:
                time_str = timestamp
                
            self.events_table.setItem(i, 0, QTableWidgetItem(time_str))
            self.events_table.setItem(i, 1, QTableWidgetItem(str(details)))
            self.events_table.setItem(i, 2, QTableWidgetItem(app_name))
            self.events_table.setItem(i, 3, QTableWidgetItem(window_title))
            self.events_table.setItem(i, 4, QTableWidgetItem(context_action))
            
    def update_app_usage_table(self, app_usage):
        """Update the app usage table"""
        self.app_usage_table.setRowCount(len(app_usage))
        for i, (app_name, count, first_seen, last_seen) in enumerate(app_usage):
            self.app_usage_table.setItem(i, 0, QTableWidgetItem(app_name))
            self.app_usage_table.setItem(i, 1, QTableWidgetItem(str(count)))
            self.app_usage_table.setItem(i, 2, QTableWidgetItem(str(first_seen)))
            self.app_usage_table.setItem(i, 3, QTableWidgetItem(str(last_seen)))
            
    def update_missed_shortcuts_table(self, missed_shortcuts):
        """Update the missed shortcuts table"""
        if not missed_shortcuts:
            return
            
        self.missed_shortcuts_table.setRowCount(len(missed_shortcuts))
        for i, (context_action, count) in enumerate(missed_shortcuts):
            self.missed_shortcuts_table.setItem(i, 0, QTableWidgetItem(context_action))
            self.missed_shortcuts_table.setItem(i, 1, QTableWidgetItem(str(count)))
            
            # Find suggested shortcut
            shortcut, description = self.get_suggested_shortcut(context_action)
            self.missed_shortcuts_table.setItem(i, 2, QTableWidgetItem(shortcut or "N/A"))
            
    def get_suggested_shortcut(self, action):
        """Get suggested shortcut for an action"""
        # Simple mapping for demo
        shortcuts = {
            "copy": "Ctrl + C",
            "paste": "Ctrl + V", 
            "cut": "Ctrl + X",
            "select all": "Ctrl + A",
            "undo": "Ctrl + Z",
            "save": "Ctrl + S",
            "find": "Ctrl + F"
        }
        
        action_lower = action.lower()
        for key, shortcut in shortcuts.items():
            if key in action_lower:
                return shortcut, key
        return None, None
        
    def generate_suggestions(self):
        """Generate new AI suggestions based on real data"""
        # Get current data from database to show real insights
        try:
            conn = sqlite3.connect('shortcuts.db')
            cursor = conn.cursor()
            
            # Get total events count
            cursor.execute("SELECT COUNT(*) FROM events")
            total_events = cursor.fetchone()[0]
            
            # Get unique applications
            cursor.execute("SELECT COUNT(DISTINCT app_name) FROM events WHERE app_name != 'Unknown'")
            unique_apps = cursor.fetchone()[0]
            
            # Get missed shortcuts
            cursor.execute("SELECT COUNT(*) FROM events WHERE context_action LIKE '%copy%' OR context_action LIKE '%paste%'")
            missed_shortcuts = cursor.fetchone()[0]
            
            conn.close()
            
            if total_events == 0:
                new_suggestions = """
🤖 No Data Yet

Start using your computer to collect data for AI-powered insights!

💡 The system will analyze:
• Your most frequent actions
• Application switching patterns
• Missed shortcut opportunities
• Time-saving workflow suggestions
                """
            else:
                new_suggestions = f"""
🤖 Real-Time Analysis Generated!

Based on your actual usage data:

📊 Current Statistics:
• Total Events: {total_events}
• Applications Used: {unique_apps}
• Potential Shortcuts: {missed_shortcuts}

💡 Keep using your computer to see more personalized suggestions!
                """
                
        except Exception as e:
            new_suggestions = f"""
🤖 Analysis Error

Could not analyze data: {e}

💡 Make sure the database is working properly.
        """
        
        self.suggestions_text.setPlainText(new_suggestions)
        
    def closeEvent(self, event):
        """Clean up when closing"""
        self.data_collector.stop()
        event.accept()

class ShortcutCoach:
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
        
        # Initialize UI Automation
        self.ui_desk = Desktop(backend="uia")
        self.last_click_time = 0
        self.click_cooldown = 0.1  # 100ms cooldown between clicks
        
        # Add deduplication system to prevent double logging
        self.last_events = {}  # Track last event of each type
        self.event_cooldown = 1.0  # 1 second cooldown between same event types
        
        # Initialize input monitor with callbacks
        self.input_monitor = InputMonitor(
            event_callback=self.log_event,
            key_press_callback=self.on_key_press,
            key_release_callback=self.on_key_release,
            context_menu_callback=self.handle_context_menu_click
        )
        
        # Initialize GUI in main thread
        self.gui = ShortcutCoachGUI(self)
        self.gui.show()
        print("📊 GUI initialized and visible!")
        print("🔄 Live Tracker will update automatically every second")
        print("🔄 Deduplication system active - preventing double logging")
        
        self.running = False
        
    def is_duplicate_event(self, event_type, details):
        """Check if this event is a duplicate of the last one"""
        current_time = time.time()
        
        # For mouse clicks, include coordinates in deduplication
        if "Click" in event_type and "X=" in details and "Y=" in details:
            # Extract coordinates for more precise deduplication
            try:
                x_part = details.split("X=")[1].split(",")[0]
                y_part = details.split("Y=")[1].split(")")[0]
                event_key = f"{event_type}:X={x_part},Y={y_part}"
            except:
                event_key = f"{event_type}:{details}"
        else:
            event_key = f"{event_type}:{details}"
        
        if event_key in self.last_events:
            last_time = self.last_events[event_key]
            if current_time - last_time < self.event_cooldown:
                print(f"🚫 Skipping duplicate: {event_type} - {details}")
                return True
        
        # Update last event time
        self.last_events[event_key] = current_time
        
        # Clean up old events (older than 10 seconds) to prevent memory buildup
        self.cleanup_old_events()
        
        return False
        
    def cleanup_old_events(self):
        """Remove old events from tracking to prevent memory buildup"""
        current_time = time.time()
        old_keys = []
        
        for event_key, last_time in self.last_events.items():
            if current_time - last_time > 10.0:  # Remove events older than 10 seconds
                old_keys.append(event_key)
        
        for key in old_keys:
            del self.last_events[key]
        
    def log_event(self, event_type, details="", context_action=""):
        """Log event to database and console"""
        # Check if this is a duplicate event
        if self.is_duplicate_event(event_type, details):
            return  # Skip duplicate events
        
        window_title, app_name = self.window_monitor.get_current_window_info()
        self.db_manager.log_event(event_type, details, window_title, app_name, context_action)
        
        # Start data collection in GUI when first event occurs
        if hasattr(self, 'gui') and self.gui:
            self.gui.start_data_collection()
            
        # Also log to console for debugging
        print(f"📝 {event_type}: {details} in {app_name}")
    
    def on_key_press(self, key):
        """Handle keyboard key press events - only log meaningful keys"""
        # Don't log here - InputMonitor already handles key logging
        pass
    
    def on_key_release(self, key):
        """Handle keyboard key release events - only log meaningful keys"""
        # Skip key releases entirely to reduce noise
        pass
    
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
                
                # Don't log here - InputMonitor already logged it
                
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
                
                # Don't log here - InputMonitor already logged it
                
        elif pressed and button.name == 'right':
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