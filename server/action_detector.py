import time
from pywinauto import Desktop
import psutil
from shortcut_manager import ShortcutManager

class ActionDetector:
    """Detects user actions and suggests appropriate shortcuts"""
    
    def __init__(self, notification_system):
        self.notification_system = notification_system
        self.ui_desk = Desktop(backend="uia")
        
        # Initialize central shortcut manager
        self.shortcut_manager = ShortcutManager()
        
        # Excel cell tracking
        self.current_excel_cell = None
        self.current_excel_row = None
        self.current_excel_col = None
        self.last_cell_click_time = 0
        self.cell_click_cooldown = 0.1  # 100ms cooldown
        
        # Track if we're in Excel
        self.in_excel = False
        self.excel_process_name = "EXCEL.EXE"
        
        # F2 shortcut detection - track double clicks on same cell
        self.last_cell_click = None
        self.last_cell_click_timestamp = 0
        self.f2_double_click_threshold = 2.0  # 2 seconds threshold for double click (more user-friendly)
        
        # Track repeated actions for Ctrl + Y suggestions
        self.last_action = None
        self.last_action_timestamp = 0
        self.repeat_action_threshold = 10.0  # 10 seconds threshold for repeat action
        
        # Chrome tab switching tracking
        self.last_chrome_tab_title = None
        self.last_chrome_tab_time = 0
        self.tab_switch_threshold = 5.0  # 5 seconds to detect tab switch
    
    def detect_action(self, x, y, app_name):
        """Detect what action the user performed and suggest shortcuts"""
        # Check for Excel-specific actions
        if app_name and "excel" in app_name.lower():
            return self.detect_excel_action(x, y)
        
        # Check for other application actions
        return None
    
    def get_ui_element_info(self, x, y):
        """Get UI element information at coordinates"""
        try:
            element = self.ui_desk.from_point(x, y)
            element_info = element.element_info
            return element_info
        except:
            return None
    
    def detect_excel_action(self, x, y):
        """Detect Excel-specific actions"""
        try:
            
            # Get element at click point
            element = self.ui_desk.from_point(x, y)
            element_info = element.element_info
            
            shortcut_info = None
            
            # Check if this is a cell click
            if self.is_excel_cell(element_info):
                cell_address = self.extract_cell_address(element_info)
                if cell_address:
                    shortcut_info = self.handle_cell_selection(cell_address, x, y)
                    # If we got shortcut info from cell selection, return it immediately
                    if shortcut_info:
                        return shortcut_info
                else:
                    pass # No debug print
            else:
                pass # No debug print
            
            # Check if this is a column header click
            if self.is_excel_column_header(element_info):
                shortcut_info = self.handle_column_header_click(element_info)
            
            # Check if this is a row header click
            elif self.is_excel_row_header(element_info):
                shortcut_info = self.handle_row_header_click(element_info)
            
            # Check if this is a sheet tab click
            elif self.is_excel_sheet_tab(element_info):
                shortcut_info = self.handle_sheet_tab_click(element_info)
            
            # Check if this is a button/ribbon click
            elif self.is_excel_button(element_info):
                # Check specifically for redo/repeat button
                if "redo" in element_info.name.lower() or "repeat" in element_info.name.lower():
                    shortcut_info = self.handle_redo_button_click(element_info)
                # Check for formatting buttons that should show shortcuts immediately
                elif any(format_btn in element_info.name.lower() for format_btn in ['bold', 'italic', 'underline']):
                    shortcut_info = self.handle_formatting_button_click(element_info)
                    # Return immediately to prevent repeated action logic from running
                    return shortcut_info
                else:
                    # Check for repeated actions (like fill color, formatting, etc.)
                    shortcut_info = self.handle_repeated_action(element_info)
            
            return shortcut_info
                
        except Exception as e:
            print(f"Error detecting Excel action: {e}")
            return None
    
    def is_excel_cell(self, element_info):
        """Check if the clicked element is an Excel cell"""
        try:
            # Excel cells typically have names like "A1", "B6", etc.
            name = element_info.name
            if name and len(name) <= 4:  # A1, B10, AA1, etc.
                # Check if it matches cell pattern (letter + number)
                if any(c.isalpha() for c in name) and any(c.isdigit() for c in name):
                    return True
            return False
        except:
            return False
    
    def is_excel_column_header(self, element_info):
        """Check if the clicked element is an Excel column header"""
        try:
            name = element_info.name
            if name and len(name) <= 3:  # A, B, C, AA, BB, etc.
                # Check if it's only letters (column headers)
                if name.isalpha() and name.isupper():
                    return True
            return False
        except:
            return False
    
    def is_excel_row_header(self, element_info):
        """Check if the clicked element is an Excel row header"""
        try:
            name = element_info.name
            if name and len(name) <= 5:  # 1, 2, 3, 10, 100, etc.
                # Check if it's only digits (row headers)
                if name.isdigit():
                    return True
            return False
        except:
            return False
    
    def is_excel_sheet_tab(self, element_info):
        """Check if the clicked element is an Excel sheet tab"""
        try:
            name = element_info.name.lower()
            # Excel sheet tabs typically contain "sheet" or are named like "Sheet1", "Sheet2", etc.
            if "sheet" in name or (name.startswith("sheet") and any(c.isdigit() for c in name)):
                return True
            # Also check for other common sheet naming patterns
            if name in ["sheet1", "sheet2", "sheet3", "sheet4", "sheet5"]:
                return True
            return False
        except:
            return False
    
    def is_excel_button(self, element_info):
        """Check if the clicked element is an Excel button/ribbon item"""
        try:
            name = element_info.name.lower()
            # Common Excel button names
            excel_buttons = ['save', 'new', 'open', 'bold', 'italic', 'underline', 
                           'copy', 'paste', 'cut', 'undo', 'redo', 'repeat',
                           'fill', 'colour', 'color', 'paint', 'format']
            return any(button in name for button in excel_buttons)
        except:
            return False
    
    def extract_cell_address(self, element_info):
        """Extract cell address from element info"""
        try:
            name = element_info.name.strip()
            if not name:
                return None
            
            # Parse cell address (e.g., "B6" -> col="B", row=6)
            col_part = ""
            row_part = ""
            
            for char in name:
                if char.isalpha():
                    col_part += char
                elif char.isdigit():
                    row_part += char
            
            if col_part and row_part:
                return {
                    'address': name,
                    'col': col_part,
                    'row': int(row_part)
                }
            
            return None
        except:
            return None
    
    def handle_cell_selection(self, cell_info, x, y):
        """Handle when user selects a new cell"""
        current_time = time.time()
        
        # Update current cell info
        old_cell = self.current_excel_cell
        old_row = self.current_excel_row
        
        self.current_excel_cell = cell_info['address']
        self.current_excel_row = cell_info['row']
        self.current_excel_col = cell_info['col']
        
        print(f"📍 Excel Cell Selected: {cell_info['address']} (Row {cell_info['row']}, Col {cell_info['col']})")
        
        # Check if this is a boundary jump that suggests Ctrl + Up
        shortcut_info = None
        if old_cell and old_row and old_row > 1:
            if self.is_boundary_jump(old_row, cell_info['row']):
                shortcut_info = self.suggest_ctrl_up_shortcut(old_cell, cell_info['address'])
        
        # Check if this is a double-click on the same cell (suggest F2) - PRIORITY OVER BOUNDARY JUMP
        time_diff = current_time - self.last_cell_click_timestamp
        print(f"🔍 F2 Debug: last_cell_click={self.last_cell_click}, current_cell={cell_info['address']}, time_diff={time_diff:.3f}s, threshold={self.f2_double_click_threshold}")
        
        if (self.last_cell_click == cell_info['address'] and 
            time_diff < self.f2_double_click_threshold):
            # F2 detection takes priority over boundary jump
            shortcut_info = self.suggest_f2_shortcut(cell_info['address'])
            print(f"🔍 F2 shortcut detected for double-click on {cell_info['address']}")
        elif shortcut_info is None:
            # Only show boundary jump if F2 wasn't detected
            print(f"🔍 No F2 detected, boundary jump shortcut: {shortcut_info}")
        
        # Update tracking for next potential double-click
        self.last_cell_click = cell_info['address']
        self.last_cell_click_timestamp = current_time
        
        self.last_cell_click_time = current_time
        
        # Return the shortcut info if we found one
        return shortcut_info
    
    def is_boundary_jump(self, old_row, new_row):
        """Check if user jumped from data cell to boundary (suggesting Ctrl + Up)"""
        # If user jumped from row > 1 to row 1, they might want Ctrl + Up
        if old_row > 1 and new_row == 1:
            return True
        return False
    
    def suggest_ctrl_up_shortcut(self, from_cell, to_cell):
        """Show a tip: Ctrl + Up Arrow goes to the first row."""
        
        # Get shortcut info from central manager
        shortcut_info = ("Ctrl + ↑", "Go to the first row")
        
        # Return shortcut info so it can be logged by the caller
        return shortcut_info

    def suggest_f2_shortcut(self, cell_address):
        """Show a tip: F2 puts the cursor at the end of cell content."""
        
        # Get shortcut info from central manager
        shortcut_info = ("F2", "Edit cell content")
        
        # Return shortcut info so it can be logged by the caller
        return shortcut_info

    def suggest_ctrl_y_shortcut(self, action_name):
        """Show a tip: Ctrl + Y repeats the last action."""
        
        # Get shortcut info from central manager
        shortcut_info = ("Ctrl + Y", "Redo/Repeat action")
        
        # Return shortcut info so it can be logged by the caller
        return shortcut_info
    
    def detect_chrome_tab_switch(self, app_name, window_title):
        """Detect if user manually switched tabs in Chrome"""
        if not app_name or "chrome" not in app_name.lower():
            return None
        
        current_time = time.time()
        
        # If this is the first time or too much time has passed, just update tracking
        if (self.last_chrome_tab_title is None or 
            current_time - self.last_chrome_tab_time > self.tab_switch_threshold):
            self.last_chrome_tab_title = window_title
            self.last_chrome_tab_time = current_time
            return None
        
        # Check if tab title changed (indicating manual tab switch)
        if (window_title and self.last_chrome_tab_title and 
            window_title != self.last_chrome_tab_title):
            
            # Update tracking for next time
            self.last_chrome_tab_title = window_title
            self.last_chrome_tab_time = current_time
            
            # Return shortcut suggestion
            return ("Ctrl + Tab", "Switch between tabs")
        
        return None
    
    def handle_button_click(self, element_info):
        """Handle Excel button clicks (this is already handled in main.py)"""
        # This is handled by the main UI detection system
        return None

    def handle_formatting_button_click(self, element_info):
        """Handle when user clicks on Excel formatting buttons (bold, italic, underline)"""
        button_name = element_info.name.lower()
        
        # Track this action for potential Ctrl + Y suggestions later
        current_time = time.time()
        self.last_action = button_name
        self.last_action_timestamp = current_time
        
        if "bold" in button_name:
            shortcut_info = ("Ctrl + B", "Bold")
        elif "italic" in button_name:
            shortcut_info = ("Ctrl + I", "Italic")
        elif "underline" in button_name:
            shortcut_info = ("Ctrl + U", "Underline")
        else:
            return None
        
        print(f"📍 Excel Formatting Button: {element_info.name} → {shortcut_info[0]}")
        return shortcut_info

    def handle_redo_button_click(self, element_info):
        """Handle when user clicks on Excel redo/repeat button"""
        print(f"📍 Excel Redo Button Selected: {element_info.name}")
        
        # Return shortcut info so it can be logged by the caller
        return ("Ctrl + Y", "Redo/Repeat action")

    def handle_repeated_action(self, element_info):
        """Handle when user clicks on Excel buttons and check for repeated actions"""
        current_time = time.time()
        action_name = element_info.name
        
        print(f"📍 Excel Button Clicked: {action_name}")
        
        # Check if this is the same action as before (within threshold)
        if (self.last_action == action_name and 
            current_time - self.last_action_timestamp < self.repeat_action_threshold):
            
            print(f"🔍 Repeated action detected: {action_name}")
            shortcut_info = self.suggest_ctrl_y_shortcut(action_name)
            
            # Reset tracking after suggesting
            self.last_action = None
            self.last_action_timestamp = 0
            
            return shortcut_info
        else:
            # Update tracking for next potential repeat
            self.last_action = action_name
            self.last_action_timestamp = current_time
            return None

    def handle_column_header_click(self, element_info):
        """Handle when user clicks on an Excel column header"""
        print(f"📍 Excel Column Header Selected: {element_info.name}")
        
        # Return shortcut info so it can be logged by the caller
        return ("Ctrl + Space", "Select entire column")
    
    def handle_row_header_click(self, element_info):
        """Handle when user clicks on an Excel row header"""
        print(f"📍 Excel Row Header Selected: {element_info.name}")
        
        # Return shortcut info so it can be logged by the caller
        return ("Shift + Space", "Select entire row")
    
    def handle_sheet_tab_click(self, element_info):
        """Handle when user clicks on an Excel sheet tab"""
        print(f"📍 Excel Sheet Tab Selected: {element_info.name}")
        
        # Return shortcut info so it can be logged by the caller
        return ("Ctrl + Page Up/Page Down", "Switch between worksheets")
    
    def should_process_action(self):
        """Check if we should process this action (avoid duplicates)"""
        current_time = time.time()
        if current_time - self.last_cell_click_time < self.cell_click_cooldown:
            return False
        return True
    
    def update_excel_status(self, app_name):
        """Update whether we're currently in Excel"""
        self.in_excel = (app_name.lower() == self.excel_process_name.lower())
        if not self.in_excel:
            # Reset Excel tracking when leaving Excel
            self.current_excel_cell = None
            self.current_excel_row = None
            self.current_excel_col = None
    
    def get_current_cell_info(self):
        """Get current Excel cell information for debugging"""
        return {
            'cell': self.current_excel_cell,
            'row': self.current_excel_row,
            'col': self.current_excel_col,
            'in_excel': self.in_excel
        }
