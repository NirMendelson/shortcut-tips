# UI Automation Mapper

## Overview

The **UI Automation Mapper** is a powerful tool that automatically detects and maps all UI elements in Windows applications using **Windows UI Automation**. This is a much more advanced and accurate approach than manual screenshot mapping.

## Why UI Automation is Better

### ✅ **Advantages over Manual Mapping:**
- **100% Accurate**: Gets exact coordinates and properties from Windows
- **Automatic Detection**: No need to draw rectangles or take screenshots
- **Real-time Data**: Always up-to-date with current application state
- **Rich Information**: Gets element names, types, automation IDs, control types
- **Professional Grade**: Uses the same technology as accessibility tools and testing frameworks

### ❌ **Manual Mapping Limitations:**
- **Error-prone**: Human drawing can miss exact boundaries
- **Time-consuming**: Must manually map each button
- **Static**: Screenshots become outdated
- **Limited Info**: Only gets coordinates, no element properties

## How It Works

### **1. Windows UI Automation**
- Uses Microsoft's official UI Automation framework
- Connects directly to running applications
- Accesses the same information that screen readers and testing tools use

### **2. Element Detection Process**
1. **Connect** to target application window
2. **Enumerate** all child elements recursively
3. **Extract** element properties (name, type, coordinates, automation ID)
4. **Filter** elements based on user preferences
5. **Export** results in JSON or Python format

### **3. What Gets Detected**
- **Buttons**: All clickable buttons with names
- **Edit Boxes**: Text input fields
- **Menu Items**: Context menus, dropdown items
- **Toolbars**: Button groups and controls
- **Tabs**: Tab controls and pages
- **Checkboxes**: Checkbox controls
- **Radio Buttons**: Radio button groups
- **List Items**: List view items
- **Tree Items**: Tree view nodes
- **Custom Controls**: Any other named UI elements

## Installation

### **Required Packages:**
```bash
pip install pywinauto>=0.6.8 psutil>=5.9.0 pywin32>=311
```

### **System Requirements:**
- Windows 10/11
- Python 3.7+
- Target application must be running

## Usage

### **Step 1: Launch the Tool**
```bash
python tools/ui_automation_mapper.py
```

### **Step 2: Select Application**
- Choose from predefined apps (Cursor, VS Code, Excel, Chrome)
- Or select "Custom" for any application

### **Step 3: Choose Target Window**
- Tool automatically detects all windows from the selected app
- Click "Refresh Windows" if needed
- Select the specific window you want to scan

### **Step 4: Configure Filters**
- Check/uncheck element types you want to detect
- Default: All element types are selected
- Customize based on your needs

### **Step 5: Start Auto-Scan**
- Click "Start Auto-Scan"
- Tool connects to the application and scans all UI elements
- Progress is shown in real-time
- Scan completes automatically

### **Step 6: Review Results**
- View detected elements in the left panel
- See detailed information in the right panel
- Each element shows:
  - **Name**: What the user sees
  - **Type**: Control type (button, edit, etc.)
  - **Coordinates**: Exact screen position
  - **Center**: Center point of the element
  - **Automation ID**: Unique identifier (if available)
  - **Control Type**: Windows control type

### **Step 7: Export Results**
- **JSON Export**: Full data structure for analysis
- **Python Export**: Ready-to-use Python dictionary

## Example Output

### **Python Dictionary Format:**
```python
CURSOR_UI_ELEMENTS = {
    "New File": {
        "type": "Button",
        "coordinates": [(50, 30), (120, 60)],
        "center": (85, 45),
        "automation_id": "new_file_btn",
        "control_type": "Button"
    },
    "Save": {
        "type": "Button", 
        "coordinates": [(130, 30), (180, 60)],
        "center": (155, 45),
        "automation_id": "save_btn",
        "control_type": "Button"
    }
}
```

### **JSON Format:**
```json
{
  "app": "Cursor",
  "window": "untitled - Cursor",
  "scan_timestamp": "2024-01-15 14:30:25",
  "elements": {
    "element_0": {
      "name": "New File",
      "type": "Button",
      "coordinates": [[50, 30], [120, 60]],
      "center": [85, 45],
      "automation_id": "new_file_btn",
      "control_type": "Button"
    }
  }
}
```

## Integration with Main System

### **Button Click Detection:**
```python
def detect_button_click(x, y, app_name):
    """Detect which button was clicked using UI automation data"""
    if app_name == "Cursor":
        for element_name, element in CURSOR_UI_ELEMENTS.items():
            coords = element["coordinates"]
            x1, y1 = coords[0]
            x2, y2 = coords[1]
            
            if x1 <= x <= x2 and y1 <= y <= y2:
                return {
                    "name": element_name,
                    "action": element_name.lower().replace(" ", "_"),
                    "type": element["type"]
                }
    return None
```

### **Advantages for Shortcut Tips:**
1. **Accurate Detection**: Knows exactly which button was clicked
2. **Rich Context**: Has button names and types
3. **Dynamic Updates**: Can re-scan when applications change
4. **Professional Quality**: Enterprise-grade detection

## Troubleshooting

### **Common Issues:**

#### **"No windows found"**
- Make sure the target application is running
- Check if the app name matches exactly
- Try refreshing windows

#### **"Connection failed"**
- Ensure the application is not running as administrator
- Try running the tool as administrator
- Check if the app supports UI Automation

#### **"Scan incomplete"**
- Some applications have complex UI structures
- Large applications may take time to scan
- Check the progress indicator

### **Best Practices:**
1. **Run target app first** before launching the mapper
2. **Use specific app names** (e.g., "Cursor" not "Custom")
3. **Select the main window** of the application
4. **Wait for scan completion** before exporting

## Comparison with Other Tools

| Feature | UI Automation Mapper | Manual Screenshot Mapping | Inspect.exe |
|---------|----------------------|---------------------------|-------------|
| **Accuracy** | 100% | ~90% | 100% |
| **Speed** | Fast (auto) | Slow (manual) | Fast (manual) |
| **Maintenance** | None needed | High (updates) | None needed |
| **Integration** | Easy (Python) | Medium (coordinates) | Hard (manual) |
| **Professional** | Yes | No | Yes |

## Future Enhancements

### **Planned Features:**
- **Real-time Monitoring**: Watch for UI changes
- **Element Interaction**: Click buttons programmatically
- **Accessibility Testing**: Verify screen reader compatibility
- **Performance Metrics**: Measure UI responsiveness
- **Cross-Application**: Compare UI patterns across apps

## Conclusion

The UI Automation Mapper represents a **major upgrade** from manual screenshot mapping. It provides:

- **Professional-grade** UI element detection
- **Zero maintenance** requirements
- **Rich metadata** for each element
- **Easy integration** with your shortcut tips system

This tool transforms your project from a basic screenshot analyzer to a **professional UI automation platform** that can compete with commercial testing tools.
