#!/usr/bin/env python3
"""
Central Shortcut Manager for Shortcut Coach
Single source of truth for all shortcut detection and mapping logic
"""

class ShortcutManager:
    """Central manager for all shortcut detection and mapping"""
    
    def __init__(self):
        # Excel-specific shortcuts
        self.excel_shortcuts = {
            "copy": ("Ctrl + C", "Copy"),
            "paste": ("Ctrl + V", "Paste"),
            "cut": ("Ctrl + X", "Cut"),
            "save": ("Ctrl + S", "Save"),
            "new": ("Ctrl + N", "New workbook"),
            "open": ("Ctrl + O", "Open workbook"),
            "undo": ("Ctrl + Z", "Undo"),
            "redo": ("Ctrl + Y", "Redo/Repeat action"),
            "find": ("Ctrl + F", "Find"),
            "replace": ("Ctrl + H", "Replace"),
            "print": ("Ctrl + P", "Print"),
            "space": ("Ctrl + Space", "Select current region"),
            "arrow_up": ("Ctrl + ↑", "Move to top of data"),
            "arrow_down": ("Ctrl + ↓", "Move to bottom of data"),
            "arrow_left": ("Ctrl + ←", "Move to left edge of data"),
            "arrow_right": ("Ctrl + →", "Move to right edge of data"),
            "edit_cell": ("F2", "Edit cell content"),
            "bold": ("Ctrl + B", "Bold"),
            "italic": ("Ctrl + I", "Italic"),
            "underline": ("Ctrl + U", "Underline")
        }
        
        # Cursor/VS Code shortcuts
        self.editor_shortcuts = {
            "save": ("Ctrl + S", "Save"),
            "new_file": ("Ctrl + N", "New File"),
            "open_file": ("Ctrl + O", "Open File"),
            "copy": ("Ctrl + C", "Copy"),
            "paste": ("Ctrl + V", "Paste"),
            "cut": ("Ctrl + X", "Cut"),
            "undo": ("Ctrl + Z", "Undo"),
            "redo": ("Ctrl + Y", "Redo"),
            "find": ("Ctrl + F", "Find"),
            "replace": ("Ctrl + H", "Replace"),
            "select_all": ("Ctrl + A", "Select All"),
            "comment": ("Ctrl + /", "Toggle Comment"),
            "indent": ("Tab", "Indent"),
            "unindent": ("Shift + Tab", "Unindent")
        }
        
        # Chrome shortcuts
        self.browser_shortcuts = {
            "new_tab": ("Ctrl + T", "New Tab"),
            "close_tab": ("Ctrl + W", "Close Tab"),
            "refresh": ("F5", "Refresh"),
            "back": ("Alt + ←", "Go Back"),
            "forward": ("Alt + →", "Go Forward"),
            "bookmark": ("Ctrl + D", "Bookmark"),
            "find": ("Ctrl + F", "Find"),
            "select_all": ("Ctrl + A", "Select All"),
            "copy": ("Ctrl + C", "Copy"),
            "paste": ("Ctrl + V", "Paste")
        }
        
        # Generic shortcuts for any application
        self.generic_shortcuts = {
            "copy": ("Ctrl + C", "Copy"),
            "paste": ("Ctrl + V", "Paste"),
            "cut": ("Ctrl + X", "Cut"),
            "save": ("Ctrl + S", "Save"),
            "new": ("Ctrl + N", "New"),
            "open": ("Ctrl + O", "Open"),
            "undo": ("Ctrl + Z", "Undo"),
            "redo": ("Ctrl + Y", "Redo"),
            "find": ("Ctrl + F", "Find"),
            "print": ("Ctrl + P", "Print"),
            "select_all": ("Ctrl + A", "Select All")
        }
    
    def get_shortcut_suggestion(self, element_info, app_name=None):
        """Get shortcut suggestion based on clicked element and app context"""
        if "error" in element_info:
            return None
        
        element_name = element_info.get("name", "").lower()
        element_type = element_info.get("type", "").lower()
        app_name = app_name or element_info.get("app_name", "").lower()
        
        # Prevent false positives from UI navigation elements
        if "shortcut" in element_name:
            return None
        
        # Excel-specific shortcuts
        if "excel" in app_name:
            return self._check_excel_shortcuts(element_name, element_type)
        
        # Cursor/VS Code shortcuts
        elif "cursor" in app_name or "code" in app_name:
            return self._check_editor_shortcuts(element_name, element_type)
        
        # Chrome shortcuts
        elif "chrome" in app_name:
            return self._check_browser_shortcuts(element_name, element_type)
        
        # Generic shortcuts for any application
        return self._check_generic_shortcuts(element_name, element_type)
    
    def _check_excel_shortcuts(self, element_name, element_type):
        """Check for Excel-specific shortcuts"""
        # Check for cell navigation (most common Excel shortcut)
        if element_type == "edit" and any(char.isdigit() for char in element_name):
            return self.excel_shortcuts["cell_navigation"]
        
        # Check for other Excel shortcuts
        for keyword, shortcut_info in self.excel_shortcuts.items():
            if keyword in element_name:
                return shortcut_info
        
        return None
    
    def _check_editor_shortcuts(self, element_name, element_type):
        """Check for editor-specific shortcuts"""
        for keyword, shortcut_info in self.editor_shortcuts.items():
            if keyword in element_name:
                return shortcut_info
        
        return None
    
    def _check_browser_shortcuts(self, element_name, element_type):
        """Check for browser-specific shortcuts"""
        for keyword, shortcut_info in self.browser_shortcuts.items():
            if keyword in element_name:
                return shortcut_info
        
        return None
    
    def _check_generic_shortcuts(self, element_name, element_type):
        """Check for generic shortcuts (lowest priority)"""
        for keyword, shortcut_info in self.generic_shortcuts.items():
            if keyword in element_name:
                return shortcut_info
        
        return None
    
    def get_shortcut_database_key(self, shortcut_tuple):
        """Convert shortcut tuple to database key for consistent logging"""
        if not shortcut_tuple:
            return None
        
        shortcut, description = shortcut_tuple
        
        # Map common shortcuts to database keys
        shortcut_mapping = {
            "Ctrl + C": "SHORTCUT_CTRL_C",
            "Ctrl + V": "SHORTCUT_CTRL_V",
            "Ctrl + X": "SHORTCUT_CTRL_X",
            "Ctrl + S": "SHORTCUT_CTRL_S",
            "Ctrl + N": "SHORTCUT_CTRL_N",
            "Ctrl + O": "SHORTCUT_CTRL_O",
            "Ctrl + Z": "SHORTCUT_CTRL_Z",
            "Ctrl + Y": "SHORTCUT_CTRL_Y",
            "Ctrl + F": "SHORTCUT_CTRL_F",
            "Ctrl + H": "SHORTCUT_CTRL_H",
            "Ctrl + P": "SHORTCUT_CTRL_P",
            "Ctrl + A": "SHORTCUT_CTRL_A",
            "Ctrl + B": "SHORTCUT_CTRL_B",
            "Ctrl + I": "SHORTCUT_CTRL_I",
            "Ctrl + U": "SHORTCUT_CTRL_U",
            "Ctrl + Arrow Keys": "SHORTCUT_CTRL_ARROW",
            "Ctrl + ↑": "SHORTCUT_CTRL_ARROW_UP",
            "Ctrl + ↓": "SHORTCUT_CTRL_ARROW_DOWN",
            "Ctrl + ←": "SHORTCUT_CTRL_ARROW_LEFT",
            "Ctrl + →": "SHORTCUT_CTRL_ARROW_RIGHT",
            "Ctrl + Space": "SHORTCUT_CTRL_SPACE",
            "Shift + Space": "SHORTCUT_SHIFT_SPACE",
            "Ctrl + Page Up/Page Down": "SHORTCUT_CTRL_PAGE_UP_DOWN",
            "F5": "SHORTCUT_F5",
            "Alt + ←": "SHORTCUT_ALT_LEFT",
            "Alt + →": "SHORTCUT_ALT_RIGHT",
            "Tab": "SHORTCUT_TAB",
            "Shift + Tab": "SHORTCUT_SHIFT_TAB",
            "F2": "SHORTCUT_F2"
        }
        
        return shortcut_mapping.get(shortcut, f"SHORTCUT_{shortcut.replace(' + ', '_').replace(' ', '_').upper()}")
    
    def get_all_supported_shortcuts(self):
        """Get list of all supported shortcuts for GUI display"""
        all_shortcuts = set()
        
        # Collect all shortcuts from all categories
        for shortcuts_dict in [self.excel_shortcuts, self.editor_shortcuts, 
                             self.browser_shortcuts, self.generic_shortcuts]:
            for shortcut_tuple in shortcuts_dict.values():
                all_shortcuts.add(shortcut_tuple[0])  # Just the shortcut, not description
        
        return sorted(list(all_shortcuts))
