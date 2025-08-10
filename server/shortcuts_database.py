"""
Shortcuts Database - Common keyboard shortcuts that users want notifications for
Organized by category for easy lookup and suggestion
"""

SHORTCUTS_DATABASE = {
    # Windows (General OS)
    "windows_general": {
        "Ctrl + C": "Copy",
        "Ctrl + X": "Cut",
        "Ctrl + V": "Paste",
        "Ctrl + Z": "Undo",
        "Ctrl + Y": "Redo",
        "Ctrl + A": "Select all",
        "Ctrl + S": "Save",
        "Alt + Tab": "Switch between open apps",
        "Windows + D": "Show/hide desktop",
        "Windows + E": "Open File Explorer",
        "Windows + Shift + S": "Screenshot selection (Snipping Tool)",
        "Windows + L": "Lock computer"
    },
    
    # Excel
    "excel": {
        "Ctrl + Arrow Keys": "Jump to the edge of data region",
        "Ctrl + Shift + Arrow Keys": "Select to edge of data region",
        "Ctrl + Space": "Select entire column",
        "Shift + Space": "Select entire row",
        "Ctrl + Shift + L": "Toggle filters",
        "Ctrl + T": "Convert range to table",
        "Alt + =": "AutoSum",
        "Ctrl + Shift + \"+\"": "Insert row/column",
        "Ctrl + \"-\"": "Delete row/column",
        "F2": "Edit selected cell",
        "Ctrl + 1": "Format cells",
        "Ctrl + Z": "Undo",
        "Ctrl + Y": "Redo"
    },
    
    # VS Code / Cursor
    "vscode_cursor": {
        "Ctrl + P": "Quick open file",
        "Ctrl + Shift + P": "Command palette",
        "Ctrl + /": "Toggle line comment",
        "Alt + Up/Down": "Move line up/down",
        "Shift + Alt + Up/Down": "Duplicate line",
        "Ctrl + Shift + K": "Delete line",
        "Ctrl + D": "Select next occurrence",
        "Ctrl + Shift + L": "Select all occurrences of selection",
        "Ctrl + F": "Find",
        "Ctrl + H": "Replace",
        "Ctrl + `": "Toggle terminal",
        "Ctrl + B": "Toggle sidebar",
        "F12": "Go to definition"
    },
    
    # Chrome
    "chrome": {
        "Ctrl + T": "Open new tab",
        "Ctrl + Shift + T": "Reopen closed tab",
        "Ctrl + W": "Close current tab",
        "Ctrl + Tab": "Switch to next tab",
        "Ctrl + Shift + Tab": "Switch to previous tab",
        "Ctrl + N": "New window",
        "Ctrl + Shift + N": "New incognito window",
        "Ctrl + L": "Focus address bar",
        "Alt + D": "Focus address bar",
        "Ctrl + R": "Reload page",
        "Ctrl + Shift + R": "Hard reload (ignore cache)",
        "Ctrl + J": "Downloads",
        "Ctrl + H": "History",
        "F12": "Open DevTools"
    }
}

def get_shortcut_for_action(action):
    """
    Find a shortcut for a given action
    Returns tuple of (shortcut, description) or (None, None) if not found
    """
    if not action:
        return None, None
        
    action_lower = action.lower()
    
    # Search through all shortcuts
    for category, shortcuts in SHORTCUTS_DATABASE.items():
        for shortcut, description in shortcuts.items():
            if action_lower in description.lower() or action_lower in shortcut.lower():
                return shortcut, description
    
    return None, None

def get_shortcuts_by_category(category):
    """
    Get all shortcuts for a specific category
    Returns dictionary of shortcuts or empty dict if category not found
    """
    return SHORTCUTS_DATABASE.get(category, {})

def get_all_shortcuts():
    """
    Get all shortcuts as a flat dictionary
    Returns dictionary with all shortcuts
    """
    all_shortcuts = {}
    for category, shortcuts in SHORTCUTS_DATABASE.items():
        all_shortcuts.update(shortcuts)
    return all_shortcuts

def search_shortcuts(query):
    """
    Search for shortcuts based on a query string
    Returns list of tuples (shortcut, description) matching the query
    """
    if not query:
        return []
        
    query_lower = query.lower()
    results = []
    
    for category, shortcuts in SHORTCUTS_DATABASE.items():
        for shortcut, description in shortcuts.items():
            if (query_lower in shortcut.lower() or 
                query_lower in description.lower() or
                query_lower in category.lower()):
                results.append((shortcut, description))
    
    return results
