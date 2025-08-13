#!/usr/bin/env python3
"""
Portfolio Demo Launcher for Shortcut Coach
Run this to start the portfolio demo with GUI and tracking
"""

import sys
import os

# Add server directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

def main():
    print("🎯 Shortcut Coach - Portfolio Demo")
    print("=" * 50)
    
    try:
        # Import and run the portfolio demo
        from portfolio_demo import main as run_demo
        run_demo()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all required packages are installed:")
        print("pip install -r requirements.txt")
        
    except Exception as e:
        print(f"❌ Error running demo: {e}")
        print("Check the console for more details")

if __name__ == "__main__":
    main()
