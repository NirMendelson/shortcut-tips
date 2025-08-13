import sys
import time
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QTextEdit,
    QPushButton, QProgressBar, QGroupBox, QScrollArea
)
from PyQt6.QtCore import QTimer, QThread, pyqtSignal, Qt
from PyQt6.QtGui import QFont, QPalette, QColor
from shortcuts_database import SHORTCUTS_DATABASE
import sqlite3
from datetime import datetime, timedelta

class DataCollector(QThread):
    """Background thread to collect data from database"""
    data_updated = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.running = True
        
    def run(self):
        while self.running:
            try:
                # Get data from database
                data = self.collect_data()
                self.data_updated.emit(data)
                time.sleep(1)  # Update every second
            except Exception as e:
                print(f"Data collection error: {e}")
                
    def collect_data(self):
        """Collect all data from database"""
        try:
            conn = sqlite3.connect('shortcuts.db')
            cursor = conn.cursor()
            
            # Get recent events
            cursor.execute("""
                SELECT event_type, details, window_title, app_name, timestamp, context_action
                FROM events 
                ORDER BY timestamp DESC 
                LIMIT 100
            """)
            events = cursor.fetchall()
            
            # Get app usage time
            cursor.execute("""
                SELECT app_name, COUNT(*) as count, 
                       MIN(timestamp) as first_seen, MAX(timestamp) as last_seen
                FROM events 
                WHERE app_name != 'Unknown'
                GROUP BY app_name
                ORDER BY count DESC
            """)
            app_usage = cursor.fetchall()
            
            # Get missed shortcuts
            cursor.execute("""
                SELECT context_action, COUNT(*) as count
                FROM events 
                WHERE context_action LIKE '%copy%' OR context_action LIKE '%paste%'
                GROUP BY context_action
                ORDER BY count DESC
            """)
            missed_shortcuts = cursor.fetchall()
            
            conn.close()
            
            return {
                'events': events,
                'app_usage': app_usage,
                'missed_shortcuts': missed_shortcuts
            }
        except Exception as e:
            print(f"Database error: {e}")
            return {
                'events': [],
                'app_usage': [],
                'missed_shortcuts': []
            }
    
    def stop(self):
        self.running = False

class ShortcutCoachGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shortcut Coach - Productivity Analytics")
        self.setGeometry(100, 100, 1200, 800)
        
        # Set modern dark theme
        self.set_dark_theme()
        
        # Initialize UI
        self.init_ui()
        
        # Start data collection
        self.data_collector = DataCollector()
        self.data_collector.data_updated.connect(self.update_data)
        self.data_collector.start()
        
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
        self.events_table.setColumnCount(6)
        self.events_table.setHorizontalHeaderLabels([
            "Time", "Event", "Details", "App", "Window", "Context Action"
        ])
        
        # Set column widths
        self.events_table.setColumnWidth(0, 150)  # Time
        self.events_table.setColumnWidth(1, 100)  # Event
        self.events_table.setColumnWidth(2, 150)  # Details
        self.events_table.setColumnWidth(3, 120)  # App
        self.events_table.setColumnWidth(4, 200)  # Window
        self.events_table.setColumnWidth(5, 150)  # Context Action
        
        layout.addWidget(QLabel("Live Event Tracker - Every click and keystroke"))
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
        
        layout.addWidget(QLabel("Time Spent in Each Application"))
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
        
        layout.addWidget(QLabel("Missed Shortcut Opportunities"))
        layout.addWidget(self.missed_shortcuts_table)
        
        # Add some example data for demo
        self.add_demo_shortcut_data()
        
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
        
        # Add demo suggestions
        demo_suggestions = """
🤖 AI Workflow Analysis

Based on your usage patterns, here are some custom shortcuts you might find useful:

1. 🖥️ Multi-Screen Setup
   • Action: Open ChatGPT on left screen + Cursor on right screen
   • Frequency: You do this setup 3-5 times per day
   • Suggested Shortcut: Ctrl + Shift + G
   • Time Saved: ~15 seconds per session

2. 📊 Excel + Browser Combo
   • Action: Switch between Excel and Chrome for data lookup
   • Frequency: 8-12 times per day
   • Suggested Shortcut: Alt + Shift + E
   • Time Saved: ~5 seconds per switch

3. 🎯 Code Review Workflow
   • Action: Open file in Cursor + switch to browser for documentation
   • Frequency: 6-10 times per day
   • Suggested Shortcut: Ctrl + Shift + R
   • Time Saved: ~10 seconds per workflow

💡 These suggestions are based on analyzing 2,847 events from your last 24 hours of computer usage.
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
📈 Your Productivity Stats (Last 24 Hours):
• Total Events Tracked: 2,847
• Applications Used: 12
• Missed Shortcut Opportunities: 47
• Estimated Time Saved with Shortcuts: 23 minutes
• Most Active Application: Cursor (4.2 hours)
• Most Frequent Action: Copy/Paste (156 times)
        """)
        stats_text.setStyleSheet("font-size: 12px; line-height: 1.4;")
        stats_layout.addWidget(stats_text)
        
        layout.addWidget(stats_group)
        
        self.tab_widget.addTab(tab, "🤖 AI Suggestions")
        
    def add_demo_shortcut_data(self):
        """Add demo data for shortcut opportunities"""
        demo_data = [
            ("Right-click + Copy", "47", "Ctrl + C"),
            ("Right-click + Paste", "32", "Ctrl + V"),
            ("Right-click + Cut", "18", "Ctrl + X"),
            ("Right-click + Select All", "12", "Ctrl + A"),
            ("Right-click + Undo", "8", "Ctrl + Z"),
            ("Menu → File → Save", "15", "Ctrl + S"),
            ("Menu → Edit → Find", "9", "Ctrl + F"),
            ("Menu → View → Zoom In", "6", "Ctrl + +")
        ]
        
        self.missed_shortcuts_table.setRowCount(len(demo_data))
        for i, (action, count, shortcut) in enumerate(demo_data):
            self.missed_shortcuts_table.setItem(i, 0, QTableWidgetItem(action))
            self.missed_shortcuts_table.setItem(i, 1, QTableWidgetItem(count))
            self.missed_shortcuts_table.setItem(i, 2, QTableWidgetItem(shortcut))
            
    def update_data(self, data):
        """Update all tabs with new data"""
        self.update_events_table(data['events'])
        self.update_app_usage_table(data['app_usage'])
        self.update_missed_shortcuts_table(data['missed_shortcuts'])
        
    def update_events_table(self, events):
        """Update the events table with new data"""
        self.events_table.setRowCount(len(events))
        for i, (event_type, details, window_title, app_name, timestamp, context_action) in enumerate(events):
            # Format timestamp
            try:
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime("%H:%M:%S")
            except:
                time_str = timestamp
                
            self.events_table.setItem(i, 0, QTableWidgetItem(time_str))
            self.events_table.setItem(i, 1, QTableWidgetItem(event_type))
            self.events_table.setItem(i, 2, QTableWidgetItem(str(details)))
            self.events_table.setItem(i, 3, QTableWidgetItem(app_name))
            self.events_table.setItem(i, 4, QTableWidgetItem(window_title))
            self.events_table.setItem(i, 5, QTableWidgetItem(context_action))
            
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
        """Generate new AI suggestions (demo function)"""
        # This would integrate with Ollama in the real version
        new_suggestions = """
🤖 New AI Suggestions Generated!

Based on your recent activity:

4. 📄 Document Workflow
   • Action: Switch between Word and PDF viewer
   • Frequency: 5-8 times per day
   • Suggested Shortcut: Alt + Shift + D

5. 🎨 Design Workflow  
   • Action: Open Figma + browser for assets
   • Frequency: 3-6 times per day
   • Suggested Shortcut: Ctrl + Shift + F

💡 These suggestions are based on your latest usage patterns.
        """
        
        self.suggestions_text.setPlainText(new_suggestions)
        
    def closeEvent(self, event):
        """Clean up when closing"""
        self.data_collector.stop()
        self.data_collector.wait()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = ShortcutCoachGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
