#!/usr/bin/env python3
"""
UI Automation Mapper
Uses Windows UI Automation to automatically detect and map all UI elements
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import time
import threading
from pywinauto import Application
import win32gui
import win32con
import win32process
import psutil

class UIAutomationMapper:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("UI Automation Mapper - Auto-Detect UI Elements")
        self.root.geometry("1400x900")
        
        # Data storage
        self.current_app = None
        self.ui_elements = {}
        self.selected_window = None
        
        # UI state
        self.scanning = False
        self.scan_thread = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control panel (left side)
        control_frame = ttk.LabelFrame(main_frame, text="Controls", width=350)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # App selection
        ttk.Label(control_frame, text="Application:").pack(anchor=tk.W, pady=(0, 5))
        self.app_var = tk.StringVar()
        app_combo = ttk.Combobox(control_frame, textvariable=self.app_var, 
                                 values=["Cursor", "VS Code", "Excel", "Chrome", "Custom"])
        app_combo.pack(fill=tk.X, pady=(0, 10))
        app_combo.bind('<<ComboboxSelected>>', self.on_app_selected)
        
        # Window selection
        ttk.Label(control_frame, text="Target Window:").pack(anchor=tk.W, pady=(0, 5))
        self.window_var = tk.StringVar()
        self.window_combo = ttk.Combobox(control_frame, textvariable=self.window_var, 
                                        state="readonly")
        self.window_combo.pack(fill=tk.X, pady=(0, 10))
        self.window_combo.bind('<<ComboboxSelected>>', self.on_window_selected)
        
        # Refresh windows button
        ttk.Button(control_frame, text="Refresh Windows", 
                  command=self.refresh_windows).pack(fill=tk.X, pady=(0, 10))
        
        # Scan controls
        ttk.Label(control_frame, text="UI Element Detection:").pack(anchor=tk.W, pady=(0, 5))
        self.scan_button = ttk.Button(control_frame, text="Start Auto-Scan", 
                                     command=self.start_scan)
        self.scan_button.pack(fill=tk.X, pady=(0, 10))
        
        # Scan progress
        self.progress_var = tk.StringVar(value="Ready to scan")
        ttk.Label(control_frame, textvariable=self.progress_var).pack(anchor=tk.W, pady=(0, 10))
        
        # Filter controls
        ttk.Label(control_frame, text="Element Filters:").pack(anchor=tk.W, pady=(0, 5))
        
        # Element type filters
        self.filter_vars = {}
        filter_types = [
            ("Button", "button"),
            ("Edit Box", "edit"),
            ("Menu Item", "menuitem"),
            ("Toolbar", "toolbar"),
            ("Tab", "tab"),
            ("Checkbox", "checkbox"),
            ("Radio Button", "radiobutton"),
            ("List Item", "listitem"),
            ("Tree Item", "treeitem"),
            ("Ribbon", "ribbon"),
            ("Combo Box", "combobox"),
            ("Drop Down", "dropdown"),
            ("Custom", "custom")
        ]
        
        for label, value in filter_types:
            var = tk.BooleanVar(value=True)
            self.filter_vars[value] = var
            ttk.Checkbutton(control_frame, text=label, variable=var).pack(anchor=tk.W)
        
        # Element list
        ttk.Label(control_frame, text="Detected Elements:").pack(anchor=tk.W, pady=(10, 5))
        self.element_listbox = tk.Listbox(control_frame, height=20)
        self.element_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Export controls
        ttk.Label(control_frame, text="Export:").pack(anchor=tk.W, pady=(0, 5))
        ttk.Button(control_frame, text="Export to JSON", 
                  command=self.export_to_json).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(control_frame, text="Export to Python", 
                  command=self.export_to_python).pack(fill=tk.X, pady=(0, 10))
        
        # Instructions
        instructions = """
        Instructions:
        1. Select application
        2. Choose target window
        3. Click "Start Auto-Scan"
        4. Wait for detection to complete
        5. Review detected elements
        6. Export when ready
        
        This tool automatically detects
        all UI elements using Windows
        UI Automation - no manual mapping!
        """
        ttk.Label(control_frame, text=instructions, justify=tk.LEFT).pack(anchor=tk.W)
        
        # Results display (right side)
        results_frame = ttk.LabelFrame(main_frame, text="Scan Results", width=900)
        results_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Results text
        self.results_text = tk.Text(results_frame, wrap=tk.WORD, font=("Consolas", 9))
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def on_app_selected(self, event):
        """Handle app selection"""
        app_name = self.app_var.get()
        self.current_app = app_name
        self.refresh_windows()
        print(f"Selected app: {app_name}")
        
    def refresh_windows(self):
        """Refresh the list of available windows"""
        if not self.current_app:
            return
            
        try:
            # Get all windows
            windows = []
            
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    window_text = win32gui.GetWindowText(hwnd)
                    if window_text and self.current_app.lower() in window_text.lower():
                        try:
                            # Get process info
                            _, pid = win32process.GetWindowThreadProcessId(hwnd)
                            process = psutil.Process(pid)
                            process_name = process.name()
                            
                            # Only include windows from the target app
                            if self.current_app.lower() in process_name.lower():
                                windows.append({
                                    'hwnd': hwnd,
                                    'title': window_text,
                                    'process': process_name
                                })
                        except:
                            pass
                return True
            
            win32gui.EnumWindows(enum_windows_callback, windows)
            
            # Update combo box
            self.window_combo['values'] = [w['title'] for w in windows]
            if windows:
                self.window_combo.set(windows[0]['title'])
                self.selected_window = windows[0]
            else:
                self.window_combo.set("")
                self.selected_window = None
                
            print(f"Found {len(windows)} windows for {self.current_app}")
            
        except Exception as e:
            print(f"Error refreshing windows: {e}")
            messagebox.showerror("Error", f"Failed to refresh windows: {e}")
    
    def on_window_selected(self, event):
        """Handle window selection"""
        selected_title = self.window_var.get()
        if selected_title:
            # Find the window with this title
            for window in self.get_all_windows():
                if window['title'] == selected_title:
                    self.selected_window = window
                    print(f"Selected window: {selected_title}")
                    break
    
    def get_all_windows(self):
        """Get all available windows for current app"""
        windows = []
        
        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if window_text and self.current_app.lower() in window_text.lower():
                    try:
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        process = psutil.Process(pid)
                        process_name = process.name()
                        
                        if self.current_app.lower() in process_name.lower():
                            windows.append({
                                'hwnd': hwnd,
                                'title': window_text,
                                'process': process_name
                            })
                    except:
                        pass
            return True
        
        win32gui.EnumWindows(enum_windows_callback, windows)
        return windows
    
    def start_scan(self):
        """Start scanning for UI elements"""
        if not self.selected_window:
            messagebox.showerror("Error", "Please select a target window first")
            return
            
        if self.scanning:
            return
            
        self.scanning = True
        self.scan_button.config(text="Scanning...", state="disabled")
        self.progress_var.set("Starting scan...")
        
        # Start scan in separate thread
        self.scan_thread = threading.Thread(target=self.run_scan, daemon=True)
        self.scan_thread.start()
    
    def run_scan(self):
        """Run the UI element scan"""
        try:
            self.progress_var.set("Connecting to application...")
            
            # Connect to the application
            hwnd = self.selected_window['hwnd']
            app = Application().connect(handle=hwnd)
            window = app.window(handle=hwnd)
            
            self.progress_var.set("Detecting UI elements...")
            
            # Get all child elements
            elements = self.get_all_elements(window)
            
            # For Excel, try additional ribbon detection methods
            if self.current_app == "Excel":
                self.progress_var.set("Detecting Excel ribbon elements...")
                ribbon_elements = self.detect_excel_ribbon(app, window)
                elements.extend(ribbon_elements)
            
            # Filter elements based on user preferences
            filtered_elements = self.filter_elements(elements)
            
            # Update UI in main thread
            self.root.after(0, lambda: self.scan_complete(filtered_elements))
            
        except Exception as e:
            print(f"Scan error: {e}")
            self.root.after(0, lambda: self.scan_error(str(e)))
    
    def detect_excel_ribbon(self, app, window):
        """Try multiple methods to detect Excel ribbon elements"""
        ribbon_elements = []
        
        try:
            # Method 1: Look for ribbon by class name
            ribbon_windows = window.children(class_name="NetUIHWND")
            for ribbon in ribbon_windows:
                try:
                    ribbon_info = self.extract_element_info(ribbon)
                    if ribbon_info:
                        ribbon_elements.append(ribbon_info)
                    
                    # Get children of ribbon
                    ribbon_children = self.get_all_elements(ribbon)
                    ribbon_elements.extend(ribbon_children)
                except:
                    continue
            
            # Method 2: Look for specific Excel controls
            excel_controls = window.children(class_name="NetUIRibbonTab")
            for control in excel_controls:
                try:
                    control_info = self.extract_element_info(control)
                    if control_info:
                        ribbon_elements.append(control_info)
                except:
                    continue
            
            # Method 3: Look for toolbar elements
            toolbar_elements = window.children(class_name="ToolbarWindow32")
            for toolbar in toolbar_elements:
                try:
                    toolbar_info = self.extract_element_info(toolbar)
                    if toolbar_info:
                        ribbon_elements.append(toolbar_info)
                    
                    # Get toolbar buttons
                    toolbar_children = self.get_all_elements(toolbar)
                    ribbon_elements.extend(toolbar_children)
                except:
                    continue
                    
        except Exception as e:
            print(f"Error detecting Excel ribbon: {e}")
        
        return ribbon_elements
    
    def get_all_elements(self, window):
        """Recursively get all UI elements"""
        elements = []
        
        try:
            # Get direct children
            children = window.children()
            
            for child in children:
                try:
                    element_info = self.extract_element_info(child)
                    if element_info:
                        elements.append(element_info)
                    
                    # For Excel, try to get deeper into ribbon structure
                    if self.current_app == "Excel":
                        # Try to get ribbon-specific elements
                        try:
                            ribbon_elements = self.get_ribbon_elements(child)
                            elements.extend(ribbon_elements)
                        except:
                            pass
                    
                    # Recursively get children of children
                    child_elements = self.get_all_elements(child)
                    elements.extend(child_elements)
                    
                except Exception as e:
                    print(f"Error processing child element: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error getting children: {e}")
        
        return elements
    
    def get_ribbon_elements(self, element):
        """Get Excel ribbon-specific elements"""
        ribbon_elements = []
        
        try:
            # Look for ribbon tabs and groups
            if hasattr(element, 'children'):
                children = element.children()
                
                for child in children:
                    try:
                        # Look for ribbon tabs (File, Home, Insert, etc.)
                        child_text = child.window_text()
                        if child_text in ["File", "Home", "Insert", "Draw", "Page Layout", "Formulas", "Data", "Review", "View", "Help"]:
                            element_info = self.extract_element_info(child)
                            if element_info:
                                ribbon_elements.append(element_info)
                        
                        # Look for ribbon groups within tabs
                        if hasattr(child, 'children'):
                            group_children = child.children()
                            for group_child in group_children:
                                group_info = self.extract_element_info(group_child)
                                if group_info:
                                    ribbon_elements.append(group_info)
                                    
                    except Exception as e:
                        print(f"Error processing ribbon child: {e}")
                        continue
                        
        except Exception as e:
            print(f"Error getting ribbon elements: {e}")
        
        return ribbon_elements
    
    def extract_element_info(self, element):
        """Extract information from a UI element"""
        try:
            # Get basic properties
            element_type = element.friendly_class_name()
            element_name = element.window_text()
            element_rect = element.rectangle()
            
            # Skip elements without names or with empty names
            if not element_name or element_name.strip() == "":
                return None
            
            # Get automation properties if available
            automation_id = getattr(element, 'automation_id', lambda: '')()
            control_type = getattr(element, 'control_type', lambda: '')()
            
            # Create unique identifier to avoid duplicates
            unique_id = f"{element_name}_{element_rect.left}_{element_rect.top}_{element_rect.right}_{element_rect.bottom}"
            
            return {
                'name': element_name,
                'type': element_type,
                'automation_id': automation_id,
                'control_type': control_type,
                'unique_id': unique_id,
                'rectangle': {
                    'left': element_rect.left,
                    'top': element_rect.top,
                    'right': element_rect.right,
                    'bottom': element_rect.bottom
                },
                'coordinates': [
                    (element_rect.left, element_rect.top),
                    (element_rect.right, element_rect.bottom)
                ],
                'center': (
                    (element_rect.left + element_rect.right) // 2,
                    (element_rect.top + element_rect.bottom) // 2
                )
            }
            
        except Exception as e:
            print(f"Error extracting element info: {e}")
            return None
    
    def filter_elements(self, elements):
        """Filter elements based on user preferences"""
        filtered = []
        seen_ids = set()
        
        for element in elements:
            element_type = element['type'].lower()
            element_name = element['name'].lower()
            
            # Check if this element type should be included
            include = False
            for filter_name, var in self.filter_vars.items():
                if var.get():
                    # Check element type
                    if filter_name in element_type:
                        include = True
                        break
                    # Check element name for specific Excel elements
                    elif filter_name == "ribbon" and any(word in element_name for word in ["save", "new", "open", "bold", "italic", "underline"]):
                        include = True
                        break
                    elif filter_name == "button" and any(word in element_name for word in ["save", "new", "open", "bold", "italic", "underline", "copy", "paste", "cut"]):
                        include = True
                        break
            
            # Special handling for Excel ribbon tabs
            if self.current_app == "Excel":
                # Always include main ribbon tabs
                if element_name in ["file", "home", "insert", "draw", "page layout", "formulas", "data", "review", "view", "help"]:
                    include = True
                # Include common Excel buttons
                elif any(word in element_name for word in ["save", "new", "open", "bold", "italic", "underline", "copy", "paste", "cut", "undo", "redo"]):
                    include = True
            
            if include:
                # Remove duplicates based on unique_id
                if element['unique_id'] not in seen_ids:
                    seen_ids.add(element['unique_id'])
                    filtered.append(element)
        
        return filtered
    
    def scan_complete(self, elements):
        """Handle scan completion"""
        self.scanning = False
        self.scan_button.config(text="Start Auto-Scan", state="normal")
        self.progress_var.set(f"Scan complete! Found {len(elements)} elements")
        
        # Store elements
        self.ui_elements = {f"element_{i}": elem for i, elem in enumerate(elements)}
        
        # Update element list
        self.update_element_list()
        
        # Update results display
        self.update_results_display()
        
        messagebox.showinfo("Scan Complete", f"Found {len(elements)} UI elements!")
    
    def scan_error(self, error_msg):
        """Handle scan error"""
        self.scanning = False
        self.scan_button.config(text="Start Auto-Scan", state="normal")
        self.progress_var.set("Scan failed")
        messagebox.showerror("Scan Error", f"Failed to scan UI elements: {error_msg}")
    
    def update_element_list(self):
        """Update the element listbox"""
        self.element_listbox.delete(0, tk.END)
        
        for element_id, element in self.ui_elements.items():
            display_text = f"{element['name']} ({element['type']})"
            self.element_listbox.insert(tk.END, display_text)
    
    def update_results_display(self):
        """Update the results text display"""
        self.results_text.delete(1.0, tk.END)
        
        if not self.ui_elements:
            self.results_text.insert(tk.END, "No elements detected yet.\n")
            return
        
        # Display summary
        self.results_text.insert(tk.END, f"UI Element Scan Results\n")
        self.results_text.insert(tk.END, f"Application: {self.current_app}\n")
        self.results_text.insert(tk.END, f"Window: {self.selected_window['title']}\n")
        self.results_text.insert(tk.END, f"Total Elements: {len(self.ui_elements)}\n")
        self.results_text.insert(tk.END, "=" * 50 + "\n\n")
        
        # Display each element
        for element_id, element in self.ui_elements.items():
            self.results_text.insert(tk.END, f"Element: {element['name']}\n")
            self.results_text.insert(tk.END, f"Type: {element['type']}\n")
            self.results_text.insert(tk.END, f"Coordinates: {element['coordinates']}\n")
            self.results_text.insert(tk.END, f"Center: {element['center']}\n")
            if element['automation_id']:
                self.results_text.insert(tk.END, f"Automation ID: {element['automation_id']}\n")
            if element['control_type']:
                self.results_text.insert(tk.END, f"Control Type: {element['control_type']}\n")
            self.results_text.insert(tk.END, "-" * 30 + "\n\n")
    
    def export_to_json(self):
        """Export UI elements to JSON file"""
        if not self.ui_elements:
            messagebox.showerror("Error", "No elements to export")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialname=f"{self.current_app.lower()}_ui_elements.json"
        )
        
        if filename:
            try:
                export_data = {
                    "app": self.current_app,
                    "window": self.selected_window['title'] if self.selected_window else "",
                    "scan_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "elements": self.ui_elements
                }
                
                with open(filename, 'w') as f:
                    json.dump(export_data, f, indent=2)
                messagebox.showinfo("Success", f"Exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")
    
    def export_to_python(self):
        """Export UI elements to Python dictionary"""
        if not self.ui_elements:
            messagebox.showerror("Error", "No elements to export")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python files", "*.py")],
            initialname=f"{self.current_app.lower()}_ui_elements.py"
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(f"# {self.current_app} UI Elements Map\n")
                    f.write("# Generated by UI Automation Mapper\n")
                    f.write(f"# Scan Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write(f"{self.current_app.upper()}_UI_ELEMENTS = {{\n")
                    
                    for element_id, element in self.ui_elements.items():
                        f.write(f'    "{element["name"]}": {{\n')
                        f.write(f'        "type": "{element["type"]}",\n')
                        f.write(f'        "coordinates": {element["coordinates"]},\n')
                        f.write(f'        "center": {element["center"]},\n')
                        f.write(f'        "automation_id": "{element["automation_id"]}",\n')
                        f.write(f'        "control_type": "{element["control_type"]}"\n')
                        f.write(f'    }},\n')
                    
                    f.write('}\n')
                
                messagebox.showinfo("Success", f"Exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")
    
    def run(self):
        """Start the UI automation mapper"""
        self.root.mainloop()

if __name__ == "__main__":
    mapper = UIAutomationMapper()
    mapper.run()
