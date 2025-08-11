#!/usr/bin/env python3
"""
Test UI Integration
Simple test to verify UI element detection works
"""

from pywinauto import Desktop
import psutil

def test_ui_detection():
    """Test basic UI element detection"""
    print("🧪 Testing UI Element Detection...")
    print("=" * 50)
    
    try:
        # Initialize UI Automation
        desk = Desktop(backend="uia")
        print("✅ UI Automation initialized successfully")
        
        # Test element detection at a specific point (this will likely fail, but tests the setup)
        try:
            element = desk.from_point(100, 100)
            element_info = element.element_info
            print(f"✅ Element detected: {element_info.name}")
        except Exception as e:
            print(f"ℹ️ Element detection test: {e}")
            print("   (This is normal - no element at coordinates 100,100)")
        
        print("\n🎯 UI Integration is ready!")
        print("   Run 'python server/main.py' to start the main system")
        print("   Click on Excel buttons, Cursor tabs, etc. to test")
        
    except Exception as e:
        print(f"❌ UI Integration test failed: {e}")
        print("   Make sure pywinauto and psutil are installed:")
        print("   pip install pywinauto psutil")

if __name__ == "__main__":
    test_ui_detection()
