#!/usr/bin/env python3
"""
Test script for DataProcessor
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
    
    # Test with sample data
    sample_events = [
        {
            'event_type': 'Key Press',
            'details': 'c',
            'window_title': 'Terminal',
            'app_name': 'Hyper',
            'context_action': '',
            'timestamp': '2024-01-01T10:00:00'
        },
        {
            'event_type': 'Key Press',
            'details': 'd',
            'window_title': 'Terminal',
            'app_name': 'Hyper',
            'context_action': '',
            'timestamp': '2024-01-01T10:00:01'
        },
        {
            'event_type': 'Key Press',
            'details': ' ',
            'window_title': 'Terminal',
            'app_name': 'Hyper',
            'context_action': '',
            'timestamp': '2024-01-01T10:00:02'
        },
        {
            'event_type': 'Key Press',
            'details': 'p',
            'window_title': 'Terminal',
            'app_name': 'Hyper',
            'context_action': '',
            'timestamp': '2024-01-01T10:00:03'
        }
    ]
    
    processes = processor.process_events(sample_events)
    print(f"✅ Processed {len(processes)} processes from sample data")
    
    if processes:
        process = processes[0]
        print(f"✅ First process: {process.get_action_summary()}")
        print(f"✅ Process duration: {process.get_duration():.1f}s")
    
    print("✅ All tests passed!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all required packages are installed")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

