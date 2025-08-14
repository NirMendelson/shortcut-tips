#!/usr/bin/env python3
"""
Simple Ollama Test
"""

import requests
import json

def test_simple_ollama():
    """Test Ollama with a very simple prompt"""
    print("🤖 Testing simple Ollama connection...")
    
    # Simple test payload
    payload = {
        "model": "mistral:7b",
        "prompt": "Say 'Hello World' and nothing else.",
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 50
        }
    }
    
    try:
        print("Sending request to Ollama...")
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=30  # 30 second timeout
        )
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ Response received: {result.get('response', 'No response')}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_simple_ollama()
