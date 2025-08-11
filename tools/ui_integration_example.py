#!/usr/bin/env python3
"""
UI Integration Example
Shows how to integrate real-time UI detection into the main shortcut tips system
"""

from pywinauto import Desktop
import time

class UIIntegration:
    def __init__(self):
        """Initialize UI Automation integration"""
        self.desk = Desktop(backend="uia")
        self.last_click_time = 0
        self.click_cooldown = 0.1  # 100ms cooldown between clicks
        
    def detect_clicked_element(self, x, y):
        """Detect what element was clicked at coordinates (x, y)"""
        try:
            # Get element at click point
            element = self.desk.from_point(x, y)
            element_info = element.element_info
            rect = element.rectangle()
            
            # Get process info
            process_id = element_info.process_id
            try:
                import psutil
                process = psutil.Process(process_id)
                app_name = process.name()
            except:
                app_name = "Unknown"
            
            # Return element information
            return {
                "name": element_info.name,
                "type": str(element_info.control_type),
                "automation_id": getattr(element_info, "automation_id", None),
                "class_name": getattr(element_info, "class_name", None),
                "app_name": app_name,
                "coordinates": (x, y),
                "bounds": (rect.left, rect.top, rect.right, rect.bottom),
                "center": ((rect.left + rect.right) // 2, (rect.top + rect.bottom) // 2)
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "coordinates": (x, y),
                "app_name": "Unknown"
            }
    
    def should_process_click(self, x, y):
        """Check if we should process this click (avoid duplicates)"""
        current_time = time.time()
        if current_time - self.last_click_time < self.click_cooldown:
            return False
        
        self.last_click_time = current_time
        return True
    
    def get_shortcut_suggestion(self, element_info):
        """Get shortcut suggestion based on clicked element"""
        if "error" in element_info:
            return None
        
        element_name = element_info["name"].lower()
        element_type = element_info["type"].lower()
        app_name = element_info["app_name"].lower()
        
        # Excel shortcuts
        if "excel" in app_name:
            if "save" in element_name:
                return "Ctrl + S", "Save"
            elif "new" in element_name:
                return "Ctrl + N", "New"
            elif "open" in element_name:
                return "Ctrl + O", "Open"
            elif "bold" in element_name:
                return "Ctrl + B", "Bold"
            elif "italic" in element_name:
                return "Ctrl + I", "Italic"
            elif "underline" in element_name:
                return "Ctrl + U", "Underline"
            elif "copy" in element_name:
                return "Ctrl + C", "Copy"
            elif "paste" in element_name:
                return "Ctrl + V", "Paste"
            elif "cut" in element_name:
                return "Ctrl + X", "Cut"
            elif "undo" in element_name:
                return "Ctrl + Z", "Undo"
            elif "redo" in element_name:
                return "Ctrl + Y", "Redo"
        
        # Cursor/VS Code shortcuts
        elif "cursor" in app_name or "code" in app_name:
            if "save" in element_name:
                return "Ctrl + S", "Save"
            elif "new file" in element_name:
                return "Ctrl + N", "New File"
            elif "find" in element_name:
                return "Ctrl + F", "Find"
            elif "replace" in element_name:
                return "Ctrl + H", "Replace"
            elif "comment" in element_name:
                return "Ctrl + /", "Toggle Comment"
        
        # Chrome shortcuts
        elif "chrome" in app_name:
            if "new tab" in element_name:
                return "Ctrl + T", "New Tab"
            elif "close" in element_name:
                return "Ctrl + W", "Close Tab"
            elif "refresh" in element_name:
                return "Ctrl + R", "Refresh"
            elif "back" in element_name:
                return "Alt + ←", "Go Back"
            elif "forward" in element_name:
                return "Alt + →", "Go Forward"
        
        return None

# Example usage in main system
def integrate_with_main_system():
    """Example of how to integrate this with the main shortcut tips system"""
    
    ui_integration = UIIntegration()
    
    def on_mouse_click(x, y, button, pressed):
        """This would be called by your mouse hook in the main system"""
        if not pressed and ui_integration.should_process_click(x, y):
            # Detect what was clicked
            element_info = ui_integration.detect_clicked_element(x, y)
            
            # Get shortcut suggestion
            shortcut, description = ui_integration.get_shortcut_suggestion(element_info)
            
            if shortcut:
                print(f"🎯 Clicked: {element_info['name']} in {element_info['app_name']}")
                print(f"💡 Use {shortcut} for {description}")
                
                # Here you would call your notification system
                # notification_system.suggest_shortcut(description, shortcut)
            else:
                print(f"🖱️ Clicked: {element_info.get('name', 'Unknown')} in {element_info.get('app_name', 'Unknown')}")
                print(f"ℹ️ No shortcut available for this action")
    
    return on_mouse_click

# Test the integration
if __name__ == "__main__":
    print("UI Integration Example")
    print("=" * 50)
    
    ui_integration = UIIntegration()
    
    # Simulate a click on Excel Save button
    print("\nTesting Excel Save button detection:")
    element_info = ui_integration.detect_clicked_element(100, 50)  # Example coordinates
    shortcut, description = ui_integration.get_shortcut_suggestion(element_info)
    
    if shortcut:
        print(f"✅ Found shortcut: {shortcut} for {description}")
    else:
        print("❌ No shortcut found")
    
    print("\nTo use this in your main system:")
    print("1. Import UIIntegration class")
    print("2. Create instance in your main system")
    print("3. Call detect_clicked_element() on mouse clicks")
    print("4. Use get_shortcut_suggestion() to get shortcuts")
    print("5. Display notifications using your existing system")
