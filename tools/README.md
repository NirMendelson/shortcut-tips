# Toolbar Mapping Tool

This tool allows you to visually map toolbar buttons in any application by drawing rectangles on screenshots and capturing their coordinates.

## What It Does

- **Captures screenshots** of application toolbars
- **Draws rectangles** around buttons by clicking and dragging
- **Records coordinates** of each button
- **Exports mappings** to JSON or Python code
- **Integrates** with your main shortcut detection system

## Why Use This Instead of LLM?

✅ **Precise coordinates** - Exact pixel locations  
✅ **Visual confirmation** - See exactly what you're mapping  
✅ **Real-time feedback** - Immediate validation  
✅ **No interpretation errors** - Human accuracy  
✅ **Customizable** - Map any button, not just standard ones  

## Setup

### 1. Install Required Packages
```bash
pip install pillow pyautogui pywin32
```

### 2. Run the Tool
```bash
python tools/toolbar_mapper.py
```

## How to Use

### Step 1: Select Application
- Choose from dropdown: Cursor, VS Code, Excel, Chrome, or Custom
- This helps organize your mappings

### Step 2: Capture Screenshot
- Click "Capture Screenshot"
- Switch to your target application window
- Click OK to capture
- Screenshot saves to `screenshots/` folder

### Step 3: Start Mapping
- Click "Start Mapping Mode"
- Click and drag to draw rectangles around buttons
- Release to add button details

### Step 4: Enter Button Details
For each button, enter:
- **Button Name**: e.g., "save", "copy", "new_file"
- **Action**: e.g., "save", "copy", "create_new_file"
- **Keyboard Shortcut**: e.g., "Ctrl+S", "Ctrl+C", "Ctrl+N"
- **Category**: file_operations, edit_operations, search_operations, etc.

### Step 5: Export
- **Export to JSON**: For data storage
- **Export to Python**: For integration with your main system

## Example Output

### JSON Export
```json
{
  "file_operations_save": {
    "name": "save",
    "action": "save",
    "shortcut": "Ctrl+S",
    "category": "file_operations",
    "coordinates": [[120, 30], [150, 50]],
    "app": "Cursor"
  }
}
```

### Python Export
```python
# cursor_toolbar_map.py
CURSOR_TOOLBAR_MAP = {
    "file_operations": {
        "save": {
            "coordinates": [(120, 30), (150, 50)],
            "shortcut": "Ctrl+S",
            "action": "save"
        }
    }
}
```

## Integration with Main System

### 1. Import the Generated Map
```python
from cursor_toolbar_map import CURSOR_TOOLBAR_MAP
```

### 2. Add Button Detection
```python
def detect_toolbar_button_click(x, y, app_name):
    if app_name == "Cursor":
        app_map = CURSOR_TOOLBAR_MAP
        
        for category, buttons in app_map.items():
            for button_name, button_info in buttons.items():
                x1, y1 = button_info["coordinates"][0]
                x2, y2 = button_info["coordinates"][1]
                
                if x1 <= x <= x2 and y1 <= y <= y2:
                    return button_info
    
    return None
```

### 3. Use in Input Monitor
```python
def on_click(self, x, y, button, pressed):
    if pressed and button.name == 'left':
        current_app = self.get_current_app_name()
        button_info = self.detect_toolbar_button_click(x, y, current_app)
        
        if button_info:
            # Show shortcut suggestion
            self.notification_system.suggest_shortcut(
                button_info['action'], 
                button_info['shortcut']
            )
```

## Tips for Accurate Mapping

### 1. Use High-Resolution Screenshots
- Ensure the application window is clearly visible
- Avoid overlapping windows
- Use consistent zoom levels

### 2. Draw Precise Rectangles
- Start from the top-left corner of the button
- Drag to the bottom-right corner
- Include the entire button area

### 3. Consistent Naming
- Use lowercase with underscores: "save_file", "new_document"
- Be descriptive: "toggle_sidebar" not just "sidebar"
- Match action names with your shortcuts database

### 4. Test Your Mappings
- Export and test the coordinates
- Verify buttons are detected correctly
- Adjust coordinates if needed

## Common Categories

### File Operations
- new_file, open_file, save, save_as, print

### Edit Operations  
- undo, redo, cut, copy, paste, select_all

### Search Operations
- find, replace, find_next, find_previous

### View Operations
- toggle_sidebar, toggle_terminal, zoom_in, zoom_out

### Custom
- Any application-specific buttons

## Troubleshooting

### Screenshot Issues
- **"No active window found"**: Make sure a window is focused
- **"Failed to capture"**: Check if you have permission to take screenshots

### Drawing Issues
- **Rectangles not appearing**: Make sure "Start Mapping Mode" is enabled
- **Wrong coordinates**: Clear and redraw rectangles

### Export Issues
- **No buttons to export**: Make sure you've mapped at least one button
- **File save error**: Check if you have write permissions

## Next Steps

1. **Map Cursor's toolbar** first (your main target)
2. **Test the integration** with your main system
3. **Map other applications** (Excel, Chrome, VS Code)
4. **Refine coordinates** based on testing
5. **Create comprehensive button databases** for all apps

## Files Created

- `toolbar_mapper.py` - The main mapping tool
- `example_usage.py` - How to use generated maps
- `screenshots/` - Folder for captured screenshots
- `*_toolbar_map.py` - Generated button maps (after export)

This tool gives you **precise, visual control** over toolbar mapping and creates **production-ready code** for your main shortcut detection system!
