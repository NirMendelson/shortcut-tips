#!/usr/bin/env python3
"""
Ollama Manager for Shortcut Coach
Handles local LLM integration for AI-powered shortcut suggestions
"""

import requests
import json
import time
from typing import List, Dict, Any, Optional

class OllamaManager:
    def __init__(self, model_name: str = "mistral:7b", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"
        
    def is_available(self) -> bool:
        """Check if Ollama service is running and accessible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def generate_suggestions(self, user_behavior_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze user behavior data and generate personalized shortcut suggestions
        
        Args:
            user_behavior_data: List of user actions/events from the live tracker
            
        Returns:
            Dictionary containing suggestions and analysis
        """
        if not self.is_available():
            return {
                "error": "Ollama service not available",
                "suggestions": [],
                "analysis": "Could not connect to local LLM"
            }
        
        try:
            # Prepare the prompt for the LLM
            prompt = self._build_analysis_prompt(user_behavior_data)
            
            # Call Ollama API
            response = self._call_ollama(prompt)
            
            # Parse and structure the response
            suggestions = self._parse_llm_response(response)
            
            return {
                "success": True,
                "suggestions": suggestions,
                "raw_response": response,
                "data_analyzed": len(user_behavior_data)
            }
            
        except Exception as e:
            return {
                "error": f"Failed to generate suggestions: {str(e)}",
                "suggestions": [],
                "analysis": "Error occurred during analysis"
            }
    
    def _build_analysis_prompt(self, behavior_data: List[Dict[str, Any]]) -> str:
        """Build a comprehensive prompt for the LLM to analyze user behavior"""
        
        # Convert behavior data to readable format
        events_summary = []
        for event in behavior_data:
            timestamp = event.get('timestamp', 'Unknown')
            event_type = event.get('event_type', 'Unknown')
            details = event.get('details', '')
            app_name = event.get('app_name', 'Unknown')
            
            events_summary.append(f"- {timestamp}: {event_type} - {details} (in {app_name})")
        
        events_text = "\n".join(events_summary)
        
        prompt = f"""
Analyze this user behavior and suggest CUSTOM shortcuts that don't exist yet.

IMPORTANT: DO NOT suggest standard shortcuts like Ctrl+C, Ctrl+V, Ctrl+Tab, etc.

User Behavior Data:
{events_text}

Look for repetitive workflows: copy from app A → paste in app B, frequently typed text, multi-step processes.

Respond in JSON format:
{{
    "suggestions": [
        {{
            "shortcut": "Custom shortcut (e.g., 'Ctrl+Shift+M for Maps Search')",
            "explanation": "What workflow this automates"
        }}
    ]
}}

Focus on NEW shortcuts that automate repetitive workflows.
"""
        
        return prompt
    
    def _call_ollama(self, prompt: str) -> str:
        """Make API call to Ollama"""
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,  # Lower temperature for more consistent output
                "top_p": 0.9,
                "num_predict": 1024  # Reduced from 2048 for faster generation
            }
        }
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=120  # Increased to 120 seconds
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '')
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ollama API call failed: {str(e)}")
    
    def _parse_llm_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse the LLM response and extract structured suggestions"""
        
        try:
            # Try to extract JSON from the response
            # Sometimes LLMs add extra text before/after JSON
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx]
                parsed = json.loads(json_str)
                
                # Extract suggestions
                suggestions = parsed.get('suggestions', [])
                if isinstance(suggestions, list):
                    return suggestions
                    
            # Fallback: return raw response if JSON parsing fails
            return [{
                "shortcut": "Could not parse suggestions",
                "explanation": response[:200] + "..." if len(response) > 200 else response,
                "frequency": "Unknown",
                "estimated_time_saved": "Unknown",
                "implementation": "JSON parsing failed"
            }]
            
        except json.JSONDecodeError:
            # If JSON parsing fails, return the raw response
            return [{
                "shortcut": "Raw LLM Response",
                "explanation": response[:300] + "..." if len(response) > 300 else response,
                "frequency": "Unknown",
                "estimated_time_saved": "Unknown",
                "implementation": "JSON parsing failed"
            }]
    
    def test_connection(self) -> Dict[str, Any]:
        """Test the connection to Ollama and return status"""
        try:
            if not self.is_available():
                return {
                    "status": "error",
                    "message": "Ollama service not running",
                    "details": "Make sure Ollama is running on localhost:11434"
                }
            
            # Test with a simple prompt
            test_prompt = "Just respond with 'Connection test successful'"
            response = self._call_ollama(test_prompt)
            
            if "Connection test successful" in response:
                return {
                    "status": "success",
                    "message": "Ollama connection working",
                    "model": self.model_name,
                    "response_time": "Test completed"
                }
            else:
                return {
                    "status": "warning",
                    "message": "Ollama responding but not following instructions",
                    "model": self.model_name,
                    "response": response[:100]
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Connection test failed: {str(e)}",
                "model": self.model_name
            }
