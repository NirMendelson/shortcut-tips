import sys
import threading
import time
from PyQt6.QtWidgets import QApplication
from gui_main import ShortcutCoachGUI
from main_simple import ShortcutCoach

def run_tracker():
    """Run the background tracker in a separate thread"""
    try:
        print("🚀 Starting background tracker...")
        coach = ShortcutCoach()
        coach.start()
    except Exception as e:
        print(f"Tracker error: {e}")

def main():
    """Main demo launcher"""
    app = QApplication(sys.argv)
    
    print("🎯 Shortcut Coach Portfolio Demo")
    print("📊 Starting background data collection...")
    
    # Start tracker in background thread
    tracker_thread = threading.Thread(target=run_tracker, daemon=True)
    tracker_thread.start()
    
    # Give tracker time to initialize
    print("⏳ Waiting for tracker to initialize...")
    time.sleep(3)
    
    # Show GUI
    print("🖥️ Launching GUI...")
    window = ShortcutCoachGUI()
    window.show()
    
    print("✅ Portfolio Demo Started Successfully!")
    print("📹 The GUI is now visible - record this for your portfolio video")
    print("🔴 Tab 1: Live click tracking")
    print("⏱️ Tab 2: App usage analytics") 
    print("⌨️ Tab 3: Missed shortcut opportunities")
    print("🤖 Tab 4: AI workflow suggestions")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
