"""
Context Analyzer - Analyzes context menu selections and suggests keyboard shortcuts
"""

from shortcuts_database import get_shortcut_for_action, search_shortcuts

class ContextAnalyzer:
    def __init__(self, notification_system=None):
        """Initialize the context analyzer"""
        self.notification_system = notification_system
    
    def analyze_context_menu_selection(self, x, y, menu_text):
        """
        Analyze a context menu selection and return the selected action
        Returns the action name if found, None otherwise
        """
        if not menu_text:
            return None
        
        # Clean up the menu text
        menu_text = menu_text.strip()
        
        # Common context menu actions that map to shortcuts
        action_mappings = {
            'copy': 'copy',
            'cut': 'cut', 
            'paste': 'paste',
            'delete': 'delete',
            'rename': 'rename',
            'select all': 'select all',
            'undo': 'undo',
            'redo': 'redo',
            'refresh': 'refresh',
            'new': 'new',
            'open': 'open',
            'save': 'save',
            'print': 'print',
            'properties': 'properties',
            'send to': 'send to',
            'create shortcut': 'create shortcut',
            'pin to start': 'pin to start',
            'pin to taskbar': 'pin to taskbar',
            'run as administrator': 'run as administrator',
            'troubleshoot compatibility': 'troubleshoot compatibility'
        }
        
        # Find the best matching action
        best_match = None
        best_score = 0
        
        for action, mapped_action in action_mappings.items():
            if action in menu_text.lower():
                # Calculate a simple similarity score
                score = len(action) / len(menu_text)
                if score > best_score:
                    best_score = score
                    best_match = mapped_action
        
        return best_match
    
    def suggest_shortcut(self, action):
        """
        Suggest a keyboard shortcut for a given action
        Returns tuple of (shortcut, description) or (None, None) if not found
        """
        if not action:
            return None, None
            
        # Try to find a shortcut for this action
        shortcut, description = get_shortcut_for_action(action)
        
        if shortcut:
            return shortcut, description
        
        # If no direct match, try searching for similar actions
        search_results = search_shortcuts(action)
        if search_results:
            # Return the first (most relevant) result
            return search_results[0]
        
        return None, None
