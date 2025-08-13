#!/usr/bin/env python3
"""
Shortcut Coach - Main Entry Point
Clean, modular main file that coordinates all system components
"""

import sys
from core_system import ShortcutCoach

def main():
    """Main entry point for Shortcut Coach"""
    try:
        print("🎯 Starting Shortcut Coach...")
        print("=" * 50)
        
        # Create and start the main system
        coach = ShortcutCoach()
        coach.start_tracking()
        
    except KeyboardInterrupt:
        print("\n🛑 Exiting Shortcut Coach...")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 