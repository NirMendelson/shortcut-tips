#!/usr/bin/env python3
"""
Example: How to use the generated toolbar map in your main system
"""

# This is what your toolbar mapper will generate:
CURSOR_TOOLBAR_MAP = {
    "file_operations": {
        "new_file": {
            "coordinates": [(50, 30), (80, 50)],
            "shortcut": "Ctrl+N",
            "action": "new_file"
        },
        "save": {
            "coordinates": [(120, 30), (150, 50)],
            "shortcut": "Ctrl+S",
            "action": "save"
        }
    },
    "edit_operations": {
        "copy": {
            "coordinates": [(305, 30), (335, 50)],
            "shortcut": "Ctrl+C",
            "action": "copy"
        },
        "paste": {
            "coordinates": [(340, 30), (370, 50)],
            "shortcut": "Ctrl+V",
            "action": "paste"
        }
    }
}

def detect_toolbar_button_click(x, y, app_name):
    """Detect which toolbar button was clicked based on coordinates"""
    if app_name == "Cursor":
        app_map = CURSOR_TOOLBAR_MAP
        
        # Check each button category
        for category, buttons in app_map.items():
            for button_name, button_info in buttons.items():
                x1, y1 = button_info["coordinates"][0]
                x2, y2 = button_info["coordinates"][1]
                
                # Check if click is within button bounds
                if x1 <= x <= x2 and y1 <= y <= y2:
                    return {
                        "button": button_name,
                        "action": button_info["action"],
                        "shortcut": button_info["shortcut"],
                        "category": category
                    }
    
    return None

# Example usage:
if __name__ == "__main__":
    # Simulate a click on the Save button
    click_x, click_y = 135, 40  # Coordinates within the Save button
    
    button_info = detect_toolbar_button_click(click_x, click_y, "Cursor")
    
    if button_info:
        print(f"✅ Button detected: {button_info['button']}")
        print(f"   Action: {button_info['action']}")
        print(f"   Shortcut: {button_info['shortcut']}")
        print(f"   Category: {button_info['category']}")
        
        # Now you can show the shortcut suggestion:
        print(f"💡 Tip: Use {button_info['shortcut']} instead of clicking the {button_info['button']} button!")
    else:
        print("❌ No button detected at these coordinates")
