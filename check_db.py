#!/usr/bin/env python3
import sqlite3

def check_facebook_google_events():
    conn = sqlite3.connect('shortcuts.db')
    cursor = conn.cursor()
    
    # Look for Facebook and Google Maps events
    cursor.execute("""
        SELECT timestamp, event_type, details, app_name, window_title 
        FROM events 
        WHERE app_name LIKE '%facebook%' OR app_name LIKE '%google%' OR app_name LIKE '%maps%'
        ORDER BY timestamp DESC 
        LIMIT 15
    """)
    
    events = cursor.fetchall()
    print(f"Found {len(events)} Facebook/Google events:")
    
    for event in events:
        timestamp, event_type, details, app_name, window_title = event
        print(f"{timestamp}: {event_type} - {details} (in {app_name}) - {window_title}")
    
    conn.close()

if __name__ == "__main__":
    check_facebook_google_events()
