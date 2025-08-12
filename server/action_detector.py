import time
from pywinauto import Desktop
import psutil

class ActionDetector:
    """Detects user actions and suggests appropriate shortcuts"""
    
    def __init__(self, notification_system):
        self.notification_system = notification_system
        self.ui_desk = Desktop(backend="uia")
        
        # Excel cell tracking
        self.current_excel_cell = None
        self.current_excel_row = None
        self.current_excel_col = None
        self.last_cell_click_time = 0
        self.cell_click_cooldown = 0.1  # 100ms cooldown
        
        # Track if we're in Excel
        self.in_excel = False
        self.excel_process_name = "EXCEL.EXE"
    
    def detect_action(self, x, y, app_name):
        """Detect what action the user performed and suggest shortcuts"""
        if not self.should_process_action():
            return
        
        # Focus on Excel actions for now
        if app_name.lower() == self.excel_process_name.lower():
            self.detect_excel_action(x, y)
    
    def detect_excel_action(self, x, y):
        """Detect Excel-specific actions"""
        try:
            # Get element at click point
            element = self.ui_desk.from_point(x, y)
            element_info = element.element_info
            
            # Check if this is a cell click
            if self.is_excel_cell(element_info):
                cell_address = self.extract_cell_address(element_info)
                if cell_address:
                    self.handle_cell_selection(cell_address, x, y)
            
            # Check if this is a column header click
            elif self.is_excel_column_header(element_info):
                self.handle_column_header_click(element_info)
            
            # Check if this is a row header click
            elif self.is_excel_row_header(element_info):
                self.handle_row_header_click(element_info)
            
            # Check if this is a sheet tab click
            elif self.is_excel_sheet_tab(element_info):
                self.handle_sheet_tab_click(element_info)
            
            # Check if this is a button/ribbon click
            elif self.is_excel_button(element_info):
                self.handle_button_click(element_info)
                
        except Exception as e:
            print(f"Error detecting Excel action: {e}")
    
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
                           'copy', 'paste', 'cut', 'undo', 'redo']
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
        if old_cell and old_row and old_row > 1:
            if self.is_boundary_jump(old_row, cell_info['row']):
                self.suggest_ctrl_up_shortcut(old_cell, cell_info['address'])
        
        self.last_cell_click_time = current_time
    
    def is_boundary_jump(self, old_row, new_row):
        """Check if user jumped from data cell to boundary (suggesting Ctrl + Up)"""
        # If user jumped from row > 1 to row 1, they might want Ctrl + Up
        if old_row > 1 and new_row == 1:
            return True
        return False
    
    def suggest_ctrl_up_shortcut(self, from_cell, to_cell):
        """Show a tip: Ctrl + Up Arrow goes to the first row."""
        message = "Use Ctrl + Up Arrow to go to the first row"
        print(message)

        # Send notification
        self.notification_system.suggest_shortcut(
            "Go to the first row",
            "Ctrl + Up Arrow"
        )

    
    def handle_button_click(self, element_info):
        """Handle Excel button clicks (this is already handled in main.py)"""
        # This is handled by the main UI detection system
        pass

    def handle_column_header_click(self, element_info):
        """Handle when user clicks on an Excel column header"""
        print(f"📍 Excel Column Header Selected: {element_info.name}")
        message = f"💡 Use Ctrl + Space to select the entire column"
        print(message)
        self.notification_system.suggest_shortcut(
            f"Select entire column",
            "Ctrl + Space"
        )
    
    def handle_row_header_click(self, element_info):
        """Handle when user clicks on an Excel row header"""
        print(f"📍 Excel Row Header Selected: {element_info.name}")
        message = f"💡 Use Shift + Space to select the entire row {element_info.name}"
        print(message)
        self.notification_system.suggest_shortcut(
            f"Select entire row",
            "Shift + Space"
        )
    
    def handle_sheet_tab_click(self, element_info):
        """Handle when user clicks on an Excel sheet tab"""
        print(f"📍 Excel Sheet Tab Selected: {element_info.name}")
        message = "💡 Use Ctrl + Page Up/Page Down to switch between worksheets"
        print(message)
        self.notification_system.suggest_shortcut(
            "Switch between worksheets",
            "Ctrl + Page Up/Page Down"
        )
    
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
