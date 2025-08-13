#!/usr/bin/env python3
"""
GUI Manager for Shortcut Coach
Handles all PyQt6 GUI functionality and UI components
"""

import sqlite3
from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QTextEdit,
    QPushButton, QProgressBar, QGroupBox, QScrollArea
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont, QPalette, QColor

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
        
        # Track when the GUI was opened to only show new events
        self.gui_start_time = datetime.now().isoformat()
        print(f"🕐 GUI opened at: {self.gui_start_time}")
        
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
            QPushButton {
                background-color: #0078d4;
                color: #ffffff;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
            }
            QLabel {
                color: #ffffff;
            }
            QProgressBar {
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 3px;
            }
        """)
        
    def init_ui(self):
        """Initialize the user interface"""
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_live_tracker_tab()
        self.create_time_tracker_tab()
        self.create_shortcut_opportunities_tab()
        self.create_ai_suggestions_tab()
        
    def create_live_tracker_tab(self):
        """Create the live tracker tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Title
        title = QLabel("🔴 Live Event Tracker")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Real-time tracking of mouse clicks, keystrokes, and window changes")
        desc.setFont(QFont("Arial", 10))
        layout.addWidget(desc)
        
        # Live data table
        self.live_table = QTableWidget()
        self.live_table.setColumnCount(4)
        self.live_table.setHorizontalHeaderLabels([
            "Timestamp", "Event Type", "Details", "Application"
        ])
        self.live_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.live_table)
        
        # Add tab
        self.tab_widget.addTab(tab, "🔴 Live Tracker")
        
    def create_time_tracker_tab(self):
        """Create the time tracker tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Title
        title = QLabel("⏱️ Application Time Tracker")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Track time spent in each application and usage patterns")
        desc.setFont(QFont("Arial", 10))
        layout.addWidget(desc)
        
        # Time tracking table
        self.time_table = QTableWidget()
        self.time_table.setColumnCount(4)
        self.time_table.setHorizontalHeaderLabels([
            "Application", "Time Spent", "Events", "Last Seen"
        ])
        self.time_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.time_table)
        
        # Add tab
        self.tab_widget.addTab(tab, "⏱️ Time Tracker")
        
    def create_shortcut_opportunities_tab(self):
        """Create the shortcut opportunities tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Title
        title = QLabel("⌨️ Shortcut Opportunities")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Discover missed keyboard shortcuts and optimization opportunities")
        desc.setFont(QFont("Arial", 10))
        layout.addWidget(desc)
        
        # Opportunities table
        self.opportunities_table = QTableWidget()
        self.opportunities_table.setColumnCount(4)
        self.opportunities_table.setHorizontalHeaderLabels([
            "Action", "Current Method", "Suggested Shortcut", "Frequency"
        ])
        self.opportunities_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.opportunities_table)
        
        # Add tab
        self.tab_widget.addTab(tab, "⌨️ Shortcuts")
        
    def create_ai_suggestions_tab(self):
        """Create the AI suggestions tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Title
        title = QLabel("🤖 AI Workflow Suggestions")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Description
        desc = QLabel("AI-powered insights to optimize your workflow and productivity")
        desc.setFont(QFont("Arial", 10))
        layout.addWidget(desc)
        
        # Suggestions text area
        self.suggestions_text = QTextEdit()
        self.suggestions_text.setPlaceholderText("AI suggestions will appear here as you use the system...")
        layout.addWidget(self.suggestions_text)
        
        # Generate suggestions button
        generate_btn = QPushButton("🔄 Generate New Suggestions")
        generate_btn.clicked.connect(self.generate_ai_suggestions)
        layout.addWidget(generate_btn)
        
        # Add tab
        self.tab_widget.addTab(tab, "🤖 AI Suggestions")
        
    def refresh_live_data(self):
        """Refresh live data in all tabs"""
        try:
            self.refresh_live_tracker()
            self.refresh_time_tracker()
            self.refresh_shortcut_opportunities()
        except Exception as e:
            print(f"Error refreshing GUI data: {e}")
            
    def refresh_live_tracker(self):
        """Refresh the live tracker tab with recent events"""
        try:
            conn = sqlite3.connect('shortcuts.db')
            cursor = conn.cursor()
            
            # Get only events that happened AFTER the GUI was opened
            cursor.execute("""
                SELECT timestamp, event_type, details, app_name
                FROM events 
                WHERE timestamp > ?
                ORDER BY timestamp DESC 
                LIMIT 50
            """, (self.gui_start_time,))
            
            events = cursor.fetchall()
            conn.close()
            
            # Update table
            self.live_table.setRowCount(len(events))
            for i, event in enumerate(events):
                for j, value in enumerate(event):
                    # Format timestamp to show only time (HH:MM:SS)
                    if j == 0 and value:  # First column is timestamp
                        try:
                            # Parse ISO timestamp and extract time
                            timestamp = datetime.fromisoformat(value.replace('Z', '+00:00'))
                            formatted_time = timestamp.strftime("%H:%M:%S")
                            item = QTableWidgetItem(formatted_time)
                        except:
                            item = QTableWidgetItem(str(value) if value else "")
                    else:
                        item = QTableWidgetItem(str(value) if value else "")
                    self.live_table.setItem(i, j, item)
                    
        except Exception as e:
            print(f"Error refreshing live tracker: {e}")
            
    def refresh_time_tracker(self):
        """Refresh the time tracker tab with application usage data"""
        try:
            conn = sqlite3.connect('shortcuts.db')
            cursor = conn.cursor()
            
            # Get application usage statistics only from after GUI was opened
            cursor.execute("""
                SELECT 
                    app_name,
                    COUNT(*) as events,
                    MIN(timestamp) as first_seen,
                    MAX(timestamp) as last_seen
                FROM events 
                WHERE app_name != 'Unknown' AND timestamp > ?
                GROUP BY app_name
                ORDER BY events DESC
            """, (self.gui_start_time,))
            
            apps = cursor.fetchall()
            conn.close()
            
            # Update table
            self.time_table.setRowCount(len(apps))
            for i, app in enumerate(apps):
                app_name = app[0] or "Unknown"
                events = app[1]
                first_seen = app[2] or "Unknown"
                last_seen = app[3] or "Unknown"
                
                # Calculate time spent (simplified)
                time_spent = f"{events} events"
                
                # Format timestamps to show only time
                try:
                    if first_seen != "Unknown":
                        first_timestamp = datetime.fromisoformat(first_seen.replace('Z', '+00:00'))
                        first_formatted = first_timestamp.strftime("%H:%M:%S")
                    else:
                        first_formatted = "Unknown"
                        
                    if last_seen != "Unknown":
                        last_timestamp = datetime.fromisoformat(last_seen.replace('Z', '+00:00'))
                        last_formatted = last_timestamp.strftime("%H:%M:%S")
                    else:
                        last_formatted = "Unknown"
                except:
                    first_formatted = first_seen
                    last_formatted = last_seen
                
                self.time_table.setItem(i, 0, QTableWidgetItem(app_name))
                self.time_table.setItem(i, 1, QTableWidgetItem(time_spent))
                self.time_table.setItem(i, 2, QTableWidgetItem(str(events)))
                self.time_table.setItem(i, 3, QTableWidgetItem(last_formatted))
                
        except Exception as e:
            print(f"Error refreshing time tracker: {e}")
            
    def refresh_shortcut_opportunities(self):
        """Refresh the shortcut opportunities tab"""
        try:
            conn = sqlite3.connect('shortcuts.db')
            cursor = conn.cursor()
            
            # Get missed shortcut opportunities only from after GUI was opened
            cursor.execute("""
                SELECT 
                    context_action,
                    COUNT(*) as frequency
                FROM events 
                WHERE (context_action LIKE '%copy%' 
                   OR context_action LIKE '%paste%'
                   OR context_action LIKE '%cut%'
                   OR context_action LIKE '%save%')
                   AND timestamp > ?
                GROUP BY context_action
                ORDER BY frequency DESC
            """, (self.gui_start_time,))
            
            opportunities = cursor.fetchall()
            conn.close()
            
            # Update table
            self.opportunities_table.setRowCount(len(opportunities))
            for i, opp in enumerate(opportunities):
                action = opp[0] or "Unknown"
                frequency = opp[1]
                
                # Map actions to shortcuts
                shortcut_map = {
                    "COPY": "Ctrl+C",
                    "PASTE": "Ctrl+V", 
                    "CUT": "Ctrl+X",
                    "SAVE": "Ctrl+S"
                }
                
                suggested_shortcut = shortcut_map.get(action, "Unknown")
                current_method = "Right-click menu"
                
                self.opportunities_table.setItem(i, 0, QTableWidgetItem(action))
                self.opportunities_table.setItem(i, 1, QTableWidgetItem(current_method))
                self.opportunities_table.setItem(i, 2, QTableWidgetItem(suggested_shortcut))
                self.opportunities_table.setItem(i, 3, QTableWidgetItem(str(frequency)))
                
        except Exception as e:
            print(f"Error refreshing shortcut opportunities: {e}")
            
    def generate_ai_suggestions(self):
        """Generate new AI suggestions based on real data"""
        try:
            conn = sqlite3.connect('shortcuts.db')
            cursor = conn.cursor()
            
            # Get current data from database to show real insights (only from after GUI opened)
            cursor.execute("SELECT COUNT(*) FROM events WHERE timestamp > ?", (self.gui_start_time,))
            total_events = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT app_name) FROM events WHERE app_name != 'Unknown' AND timestamp > ?", (self.gui_start_time,))
            unique_apps = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM events WHERE (context_action LIKE '%copy%' OR context_action LIKE '%paste%') AND timestamp > ?", (self.gui_start_time,))
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

Based on your actual usage data since opening the app:

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
