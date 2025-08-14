#!/usr/bin/env python3
"""
Debug script to test the exact GUI flow for Ollama integration
"""

import sqlite3
from datetime import datetime
from server.ollama_manager import OllamaManager

def test_gui_flow():
    """Test the exact same flow that the GUI uses"""
    
    print("🔍 Testing GUI Ollama Integration Flow...")
    
    # Initialize Ollama manager (same as GUI)
    ollama_manager = OllamaManager()
    
    # Get data from database (same as GUI)
    conn = sqlite3.connect('shortcuts.db')
    cursor = conn.cursor()
    
    # Get recent events (same query as GUI)
    gui_start_time = datetime.now().isoformat()
    cursor.execute("""
        SELECT timestamp, event_type, details, app_name, window_title, context_action
        FROM events 
        WHERE timestamp > ?
        ORDER BY timestamp DESC 
        LIMIT 100
    """, (gui_start_time,))
    
    events = cursor.fetchall()
    conn.close()
    
    print(f"📊 Found {len(events)} events in database")
    
    if len(events) == 0:
        print("❌ No events found - this is why GUI shows 'No Data Yet'")
        return
    
    # Convert events to behavior data (same as GUI)
    behavior_data = []
    for event in events:
        behavior_data.append({
            "timestamp": event[0],
            "event_type": event[1],
            "details": event[2] or "",
            "app_name": event[3] or "Unknown",
            "window_title": event[4] or "",
            "context_action": event[5] or ""
        })
    
    print(f"🧠 Generating AI suggestions for {len(behavior_data)} events...")
    
    # Call Ollama manager (same as GUI)
    result = ollama_manager.generate_suggestions(behavior_data)
    
    # Debug logging (same as GUI)
    print(f"🔍 Ollama result: {result}")
    print(f"🔍 Success key: {result.get('success')}")
    print(f"🔍 Error key: {result.get('error')}")
    
    # Check success (same logic as GUI)
    if result.get('success'):
        suggestions = result['suggestions']
        print(f"✅ Success! Found {len(suggestions)} suggestions")
        
        if suggestions and len(suggestions) > 0:
            print("📋 Suggestions:")
            for i, suggestion in enumerate(suggestions, 1):
                shortcut = suggestion.get('shortcut', 'Unknown')
                explanation = suggestion.get('explanation', 'No explanation provided')
                frequency = suggestion.get('frequency', 'Unknown')
                time_saved = suggestion.get('estimated_time_saved', 'Unknown')
                implementation = suggestion.get('implementation', 'No implementation details provided')
                
                print(f"{i}. 🎯 {shortcut}")
                print(f"   💡 {explanation}")
                print(f"   📊 Frequency: {frequency}")
                print(f"   ⏱️ Time Saved: {time_saved}")
                print(f"   🔧 Implementation: {implementation}")
        else:
            print("⚠️ No suggestions found - GUI would show 'No Specific Patterns Detected'")
    else:
        print("❌ Failed - GUI would show 'AI Unavailable'")
        print(f"Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    test_gui_flow()
