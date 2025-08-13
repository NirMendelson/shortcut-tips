#!/usr/bin/env python3
"""
Simple launcher for Shortcut Coach main.py
This will start the tracking system with GUI automatically
"""

import sys
import os

# Add server directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

def main():
    print("🎯 Shortcut Coach - Main System")
    print("=" * 50)
    
    try:
        # Import and run the main system
        from main import main as run_main
        run_main()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all required packages are installed:")
        print("pip install -r requirements.txt")
        
    except Exception as e:
        print(f"❌ Error running main system: {e}")
        print("Check the console for more details")

if __name__ == "__main__":
    main()
