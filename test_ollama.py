#!/usr/bin/env python3
"""
Test script for Ollama Manager
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'server'))

from ollama_manager import OllamaManager

def test_ollama_connection():
    """Test the Ollama connection"""
    print("🤖 Testing Ollama Connection...")
    
    # Initialize Ollama manager
    ollama = OllamaManager()
    
    # Test connection
    result = ollama.test_connection()
    
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    print(f"Model: {result['model']}")
    
    if result['status'] == 'success':
        print("✅ Ollama connection successful!")
        return True
    else:
        print("❌ Ollama connection failed!")
        return False

def test_suggestion_generation():
    """Test generating suggestions with sample data"""
    print("\n🧠 Testing Suggestion Generation...")
    
    # Sample user behavior data showing Facebook → Google Maps workflow
    sample_data = [
        {
            "timestamp": "2024-01-15T10:30:00",
            "event_type": "Clipboard Copy",
            "details": "רחוב מיכ\"ל, תל אביב",
            "app_name": "facebook.com"
        },
        {
            "timestamp": "2024-01-15T10:30:05",
            "event_type": "App Switch",
            "details": "Switched to Google Maps",
            "app_name": "maps.google.com"
        },
        {
            "timestamp": "2024-01-15T10:30:06",
            "event_type": "Shortcut",
            "details": "Ctrl + V (Paste)",
            "app_name": "maps.google.com"
        },
        {
            "timestamp": "2024-01-15T10:30:10",
            "event_type": "UI Element Click",
            "details": "Search button clicked",
            "app_name": "maps.google.com"
        },
        {
            "timestamp": "2024-01-15T10:30:15",
            "event_type": "Clipboard Copy",
            "details": "ריינס פינת בן גוריון, תל אביב",
            "app_name": "facebook.com"
        },
        {
            "timestamp": "2024-01-15T10:30:20",
            "event_type": "Shortcut",
            "details": "Ctrl + V (Paste)",
            "app_name": "maps.google.com"
        }
    ]
    
    # Initialize Ollama manager
    ollama = OllamaManager()
    
    # Generate suggestions
    print("Generating suggestions... (this may take 30-60 seconds)")
    result = ollama.generate_suggestions(sample_data)
    
    if result.get('success'):
        print("✅ Suggestions generated successfully!")
        print(f"Data analyzed: {result['data_analyzed']} events")
        print("\n📋 Suggestions:")
        
        for i, suggestion in enumerate(result['suggestions'], 1):
            print(f"\n{i}. {suggestion.get('shortcut', 'N/A')}")
            print(f"   Explanation: {suggestion.get('explanation', 'N/A')}")
            print(f"   Frequency: {suggestion.get('frequency', 'N/A')}")
            print(f"   Time Saved: {suggestion.get('estimated_time_saved', 'N/A')}")
    else:
        print("❌ Failed to generate suggestions:")
        print(f"Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    print("🚀 Starting Ollama Manager Tests...\n")
    
    # Test connection first
    if test_ollama_connection():
        # If connection works, test suggestion generation
        test_suggestion_generation()
    else:
        print("\n❌ Skipping suggestion test due to connection failure")
        print("Make sure Ollama is running with: ollama serve")
