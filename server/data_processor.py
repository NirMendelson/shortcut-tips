#!/usr/bin/env python3
"""
Data Processor for Shortcut Coach
Identifies meaningful sequences from live tracker events using process-based grouping
"""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import re

class Process:
    """Represents a user process/workflow"""
    
    def __init__(self, process_id: str, start_time: datetime, context: str = ""):
        self.id = process_id
        self.start_time = start_time
        self.end_time: Optional[datetime] = None
        self.context = context
        self.actions: List[Dict] = []
        self.frequency = 1  # How many times this process appears
        
    def add_action(self, action: Dict):
        """Add an action to this process"""
        self.actions.append(action)
        
    def end_process(self, end_time: datetime):
        """Mark the end of this process"""
        self.end_time = end_time
        
    def get_duration(self) -> float:
        """Get process duration in seconds"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
        
    def get_action_summary(self) -> str:
        """Get a human-readable summary of actions"""
        if not self.actions:
            return "No actions"
            
        # Try to detect meaningful workflows first
        workflow_summary = self._detect_workflow()
        if workflow_summary:
            return workflow_summary
            
        # Fall back to grouping similar consecutive actions
        summary_parts = []
        current_action = None
        current_count = 0
        
        for action in self.actions:
            action_key = f"{action.get('event_type', '')}:{action.get('details', '')}"
            
            if action_key == current_action:
                current_count += 1
            else:
                if current_action:
                    if current_count > 1:
                        summary_parts.append(f"{current_action} ({current_count}x)")
                    else:
                        summary_parts.append(current_action)
                current_action = action_key
                current_count = 1
                
        # Add the last action
        if current_action:
            if current_count > 1:
                summary_parts.append(f"{current_action} ({current_count}x)")
            else:
                summary_parts.append(current_action)
                
        return " → ".join(summary_parts)
        
    def _detect_workflow(self) -> str:
        """Detect common workflows and return human-readable descriptions"""
        if not self.actions:
            return ""
            
        # Get the context (application)
        context = self.context or "Unknown"
        
        # Check for text input sequences (typing + enter)
        text_input = self._detect_text_input()
        if text_input:
            return f"User sent '{text_input}' to {context}"
            
        # Check for navigation sequences
        navigation = self._detect_navigation()
        if navigation:
            return f"User navigated to {navigation} in {context}"
            
        # Check for file operations
        file_op = self._detect_file_operation()
        if file_op:
            return f"User performed {file_op} in {context}"
            
        return ""
        
    def _detect_text_input(self) -> str:
        """Detect if this is a text input sequence (typing + enter)"""
        if len(self.actions) < 2:
            return ""
            
        # Look for sequence: key presses followed by enter
        text_chars = []
        has_enter = False
        
        for action in self.actions:
            event_type = action.get('event_type', '')
            details = action.get('details', '')
            
            if event_type == 'Key Press':
                if details == 'Key.enter' or details == 'Key.return':
                    has_enter = True
                elif len(details) == 1 and details.isprintable():
                    text_chars.append(details)
                    
        # If we have text and enter, this is a text input
        if text_chars and has_enter:
                    return ''.join(text_chars)
            
        return ""
        
    def _detect_navigation(self) -> str:
        """Detect navigation sequences"""
        if len(self.actions) < 2:
            return ""
            
        # Look for cd commands
        cd_sequence = []
        for action in self.actions:
            if (action.get('event_type') == 'Key Press' and 
                action.get('details') in ['c', 'd', ' ', '\\', '/', '.']):
                cd_sequence.append(action.get('details'))
                
        if len(cd_sequence) >= 3 and cd_sequence[0] == 'c' and cd_sequence[1] == 'd':
            # Extract the path
            path_chars = cd_sequence[2:]
            path = ''.join(path_chars).strip()
            if path:
                return f"cd {path}"
                
        return ""
        
    def _detect_file_operation(self) -> str:
        """Detect file operations"""
        if len(self.actions) < 2:
            return ""
            
        # Look for common file operation patterns
        actions_text = ' '.join([f"{a.get('event_type', '')}:{a.get('details', '')}" 
                                for a in self.actions])
        
        if 'copy' in actions_text.lower():
            return "copy operation"
        elif 'paste' in actions_text.lower():
            return "paste operation"
        elif 'save' in actions_text.lower():
            return "save operation"
        elif 'open' in actions_text.lower():
            return "open operation"
            
        return ""
        
    def get_signature(self) -> str:
        """Get a unique signature for this process type"""
        # Create a signature based on action types and order
        action_types = [f"{action.get('event_type', '')}:{action.get('details', '')}" 
                       for action in self.actions]
        return "|".join(action_types)

class DataProcessor:
    """Processes live tracker events to identify meaningful sequences"""
    
    def __init__(self, db_path: str = 'shortcuts.db'):
        self.db_path = db_path
        self.processes: List[Process] = []
        self.current_process: Optional[Process] = None
        self.process_signatures: Dict[str, int] = {}  # signature -> frequency
        
        # Configuration
        self.inactivity_threshold = 3.0  # seconds
        self.min_process_actions = 2  # minimum actions to consider a process
        self.max_process_actions = 50  # maximum actions per process (increased for longer sequences)
        self.text_input_delay = 1.0  # seconds to wait after enter before ending text input process
        self.typing_threshold = 2.0  # seconds between keystrokes to consider same typing session
        
    def detect_process_boundary(self, current_event: Dict, last_event: Optional[Dict]) -> bool:
        """Detect if a new process should start"""
        if not last_event:
            return True
            
        # Time gap > threshold
        if last_event.get('timestamp'):
            try:
                last_time = datetime.fromisoformat(last_event['timestamp'].replace('Z', '+00:00'))
                current_time = datetime.fromisoformat(current_event['timestamp'].replace('Z', '+00:00'))
                time_diff = (current_time - last_time).total_seconds()
                
                # Special handling for text input sequences
                if (last_event.get('details') == 'Key.enter' or last_event.get('details') == 'Key.return'):
                    # After enter, wait a bit longer to see if more text comes
                    if time_diff > self.text_input_delay:
                        return True
                elif (last_event.get('event_type') == 'Key Press' and 
                      current_event.get('event_type') == 'Key Press' and
                      len(last_event.get('details', '')) == 1 and 
                      len(current_event.get('details', '')) == 1):
                    # Between keystrokes, use typing threshold (more lenient)
                    if time_diff > self.typing_threshold:
                        return True
                elif time_diff > self.inactivity_threshold:
                    return True
            except:
                pass
                
        # Different application/window
        if (current_event.get('app_name') and last_event.get('app_name') and 
            current_event['app_name'] != last_event['app_name']):
            return True
            
        # Different window title (significant change)
        if (current_event.get('window_title') and last_event.get('window_title')):
            current_title = current_event['window_title']
            last_title = last_event['window_title']
            
            # Check if it's a significant change (not just minor text updates)
            if self._is_significant_title_change(current_title, last_title):
                return True
                
        # Command completion (Enter key, successful command)
        if (current_event.get('details') == 'Key.enter' or 
            current_event.get('details') == 'Key.return'):
            # Don't start new process immediately after enter - let it group with the typing
            return False
            
        return False
        
    def _is_significant_title_change(self, current: str, last: str) -> bool:
        """Check if window title change is significant"""
        if not current or not last:
            return False
            
        # Remove common dynamic parts
        current_clean = re.sub(r' - [^-]+$', '', current)  # Remove " - App Name"
        last_clean = re.sub(r' - [^-]+$', '', last)
        
        # Check if base title changed
        if current_clean != last_clean:
            return True
            
        # Check if it's a significant file/folder change
        if '\\' in current and '\\' in last:
            current_path = current.split('\\')[-1] if '\\' in current else current
            last_path = last.split('\\')[-1] if '\\' in last else last
            if current_path != last_path:
                return True
                
        return False
        
    def process_events(self, events: List[Dict]) -> List[Process]:
        """Process a list of events to identify meaningful sequences"""
        if not events:
            return []
            
        # Reset process signatures for fresh analysis
        self.process_signatures = {}
        
        # Sort events by timestamp
        sorted_events = sorted(events, key=lambda x: x.get('timestamp', ''))
        
        self.processes = []
        self.current_process = None
        last_event = None
        
        for event in sorted_events:
            # Check if we should start a new process
            if self.detect_process_boundary(event, last_event):
                # End current process if exists
                if self.current_process:
                    self.current_process.end_process(
                        datetime.fromisoformat(last_event['timestamp'].replace('Z', '+00:00'))
                        if last_event and last_event.get('timestamp') else datetime.now()
                    )
                    self.processes.append(self.current_process)
                    
                # Start new process
                process_id = f"process_{len(self.processes)}_{datetime.now().strftime('%H%M%S')}"
                context = event.get('app_name', 'Unknown')
                self.current_process = Process(process_id, 
                                            datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
                                            if event.get('timestamp') else datetime.now(),
                                            context)
                                            
            # Add action to current process
            if self.current_process:
                self.current_process.add_action(event)
                
            last_event = event
            
        # End the last process
        if self.current_process:
            self.current_process.end_process(
                datetime.fromisoformat(last_event['timestamp'].replace('Z', '+00:00'))
                if last_event and last_event.get('timestamp') else datetime.now()
            )
            self.processes.append(self.current_process)
            
        # Filter and analyze processes
        return self._analyze_processes()
        
    def _analyze_processes(self) -> List[Process]:
        """Analyze processes to find meaningful sequences"""
        # Filter out very short or very long processes
        meaningful_processes = [
            p for p in self.processes 
            if len(p.actions) >= self.min_process_actions and 
               len(p.actions) <= self.max_process_actions
        ]
        
        # Count process signatures
        for process in meaningful_processes:
            signature = process.get_signature()
            if signature in self.process_signatures:
                self.process_signatures[signature] += 1
                # Update frequency for all processes with this signature
                for p in meaningful_processes:
                    if p.get_signature() == signature:
                        p.frequency = self.process_signatures[signature]
            else:
                self.process_signatures[signature] = 1
                
        return meaningful_processes
        
    def get_recent_processes(self, hours: int = 3) -> List[Process]:
        """Get processes from the last N hours"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Calculate time threshold
            threshold = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            # Get events from the last N hours
            cursor.execute("""
                SELECT event_type, details, window_title, app_name, context_action, timestamp
                FROM events 
                WHERE timestamp > ?
                ORDER BY timestamp ASC
            """, (threshold,))
            
            events = cursor.fetchall()
            conn.close()
            
            # Convert to list of dicts
            event_dicts = []
            for event in events:
                event_dicts.append({
                    'event_type': event[0],
                    'details': event[1],
                    'window_title': event[2],
                    'app_name': event[3],
                    'context_action': event[4],
                    'timestamp': event[5]
                })
                
            # Process events to find sequences
            return self.process_events(event_dicts)
            
        except Exception as e:
            print(f"Error getting recent processes: {e}")
            return []
            
    def get_frequent_processes(self, min_frequency: int = 2) -> List[Process]:
        """Get processes that appear frequently"""
        processes = self.get_recent_processes()
        return [p for p in processes if p.frequency >= min_frequency]
        
    def get_process_statistics(self) -> Dict:
        """Get statistics about identified processes"""
        processes = self.get_recent_processes()
        
        if not processes:
            return {
                'total_processes': 0,
                'frequent_processes': 0,
                'avg_duration': 0,
                'most_common_context': 'None'
            }
            
        # Calculate statistics
        total_processes = len(processes)
        frequent_processes = len([p for p in processes if p.frequency >= 2])
        avg_duration = sum(p.get_duration() for p in processes) / total_processes
        
        # Find most common context
        context_counts = {}
        for process in processes:
            context = process.context or 'Unknown'
            context_counts[context] = context_counts.get(context, 0) + 1
            
        most_common_context = max(context_counts.items(), key=lambda x: x[1])[0] if context_counts else 'None'
        
        return {
            'total_processes': total_processes,
            'frequent_processes': frequent_processes,
            'avg_duration': round(avg_duration, 2),
            'most_common_context': most_common_context
        }
        
    def clear_process_history(self):
        """Clear all process history and signatures"""
        self.processes = []
        self.current_process = None
        self.process_signatures = {}
        print("🧹 Process history cleared")
        
    def debug_current_events(self):
        """Debug: Print current events being processed"""
        if not self.current_process:
            print("🔍 No current process")
            return
            
        print(f"🔍 Current process: {self.current_process.context} ({len(self.current_process.actions)} actions)")
        # Only show first few actions to avoid spam
        for i, action in enumerate(self.current_process.actions[:5]):
            print(f"   {i}: {action.get('event_type')} - {action.get('details')}")
        if len(self.current_process.actions) > 5:
            print(f"   ... and {len(self.current_process.actions) - 5} more actions")
