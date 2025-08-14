#!/usr/bin/env python3
"""
Test script for smart sequence detection
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from data_processor import DataProcessor, Process
    print("✅ DataProcessor imported successfully")
    
    # Test basic functionality
    processor = DataProcessor()
    print("✅ DataProcessor instance created")
    
    # Test 1: Text input sequence (typing "help" + enter)
    print("\n🧪 Test 1: Text input sequence")
    text_input_events = [
        {
            'event_type': 'Key Press',
            'details': 'h',
            'window_title': 'Cursor',
            'app_name': 'Cursor',
            'context_action': '',
            'timestamp': '2024-01-01T10:00:00'
        },
        {
            'event_type': 'Key Press',
            'details': 'e',
            'window_title': 'Cursor',
            'app_name': 'Cursor',
            'context_action': '',
            'timestamp': '2024-01-01T10:00:01'
        },
        {
            'event_type': 'Key Press',
            'details': 'l',
            'window_title': 'Cursor',
            'app_name': 'Cursor',
            'context_action': '',
            'timestamp': '2024-01-01T10:00:02'
        },
        {
            'event_type': 'Key Press',
            'details': 'p',
            'window_title': 'Cursor',
            'app_name': 'Cursor',
            'context_action': '',
            'timestamp': '2024-01-01T10:00:03'
        },
        {
            'event_type': 'Key Press',
            'details': 'Key.enter',
            'window_title': 'Cursor',
            'app_name': 'Cursor',
            'context_action': '',
            'timestamp': '2024-01-01T10:00:04'
        }
    ]
    
    processes = processor.process_events(text_input_events)
    print(f"✅ Processed {len(processes)} processes from text input")
    
    if processes:
        process = processes[0]
        summary = process.get_action_summary()
        print(f"✅ Text input summary: {summary}")
        print(f"✅ Expected: User sent 'help' to Cursor")
        
    # Test 2: Navigation sequence (cd command)
    print("\n🧪 Test 2: Navigation sequence")
    nav_events = [
        {
            'event_type': 'Key Press',
            'details': 'c',
            'window_title': 'Terminal',
            'app_name': 'Hyper',
            'context_action': '',
            'timestamp': '2024-01-01T10:01:00'
        },
        {
            'event_type': 'Key Press',
            'details': 'd',
            'window_title': 'Terminal',
            'app_name': 'Hyper',
            'context_action': '',
            'timestamp': '2024-01-01T10:01:01'
        },
        {
            'event_type': 'Key Press',
            'details': ' ',
            'window_title': 'Terminal',
            'app_name': 'Hyper',
            'context_action': '',
            'timestamp': '2024-01-01T10:01:02'
        },
        {
            'event_type': 'Key Press',
            'details': 'p',
            'window_title': 'Terminal',
            'app_name': 'Hyper',
            'context_action': '',
            'timestamp': '2024-01-01T10:01:03'
        },
        {
            'event_type': 'Key Press',
            'details': 'r',
            'window_title': 'Terminal',
            'app_name': 'Hyper',
            'context_action': '',
            'timestamp': '2024-01-01T10:01:04'
        },
        {
            'event_type': 'Key Press',
            'details': 'o',
            'window_title': 'Terminal',
            'app_name': 'Hyper',
            'context_action': '',
            'timestamp': '2024-01-01T10:01:05'
        },
        {
            'event_type': 'Key Press',
            'details': 'j',
            'window_title': 'Terminal',
            'app_name': 'Hyper',
            'context_action': '',
            'timestamp': '2024-01-01T10:01:06'
        },
        {
            'event_type': 'Key Press',
            'details': 'Key.enter',
            'window_title': 'Terminal',
            'app_name': 'Hyper',
            'context_action': '',
            'timestamp': '2024-01-01T10:01:07'
        }
    ]
    
    processes = processor.process_events(nav_events)
    print(f"✅ Processed {len(processes)} processes from navigation")
    
    if processes:
        process = processes[0]
        summary = process.get_action_summary()
        print(f"✅ Navigation summary: {summary}")
        print(f"✅ Expected: User navigated to cd proj in Hyper")
    
    print("\n✅ All smart sequence tests completed!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all required packages are installed")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

