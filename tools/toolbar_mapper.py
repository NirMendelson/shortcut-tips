#!/usr/bin/env python3
"""
Toolbar Mapping Tool
Maps toolbar buttons by drawing rectangles on screenshots and capturing coordinates
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import pyautogui
import time
from PIL import Image, ImageTk, ImageDraw
import win32gui
import win32con
import threading

class ToolbarMapper:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Toolbar Mapper - Map Application Toolbars")
        self.root.geometry("1200x800")
        
        # Data storage
        self.current_app = ""
        self.toolbar_buttons = {}
        self.screenshot_path = ""
        self.screenshot_image = None
        self.canvas = None
        
        # Drawing state
        self.drawing = False
        self.start_x = 0
        self.start_y = 0
        self.current_rect = None
        self.rectangles = []
        
        # Countdown state
        self.countdown_running = False
        self.countdown_label = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control panel (left side)
        control_frame = ttk.LabelFrame(main_frame, text="Controls", width=300)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # App selection
        ttk.Label(control_frame, text="Application:").pack(anchor=tk.W, pady=(0, 5))
        self.app_var = tk.StringVar()
        app_combo = ttk.Combobox(control_frame, textvariable=self.app_var, 
                                 values=["Cursor", "VS Code", "Excel", "Chrome", "Custom"])
        app_combo.pack(fill=tk.X, pady=(0, 10))
        app_combo.bind('<<ComboboxSelected>>', self.on_app_selected)
        
        # Screenshot controls
        ttk.Label(control_frame, text="Screenshot:").pack(anchor=tk.W, pady=(0, 5))
        ttk.Button(control_frame, text="Capture with Countdown", 
                  command=self.start_countdown_capture).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(control_frame, text="Load Screenshot", 
                  command=self.load_screenshot).pack(fill=tk.X, pady=(0, 10))
        
        # Countdown display
        self.countdown_label = ttk.Label(control_frame, text="", font=("Arial", 16, "bold"))
        self.countdown_label.pack(pady=(0, 10))
        
        # Button mapping controls
        ttk.Label(control_frame, text="Button Mapping:").pack(anchor=tk.W, pady=(0, 5))
        ttk.Button(control_frame, text="Start Mapping Mode", 
                  command=self.start_mapping_mode).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(control_frame, text="Clear All Rectangles", 
                  command=self.clear_rectangles).pack(fill=tk.X, pady=(0, 10))
        
        # Button list
        ttk.Label(control_frame, text="Mapped Buttons:").pack(anchor=tk.W, pady=(0, 5))
        self.button_listbox = tk.Listbox(control_frame, height=15)
        self.button_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
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
        2. Click "Capture with Countdown"
        3. Switch to target app during countdown
        4. Screenshot will be taken automatically
        5. Start mapping mode
        6. Draw rectangles around buttons
        7. Enter button details
        8. Export when done
        
        Alternative: Use "Load Screenshot" to load
        existing screenshots (Print Screen, etc.)
        """
        ttk.Label(control_frame, text=instructions, justify=tk.LEFT).pack(anchor=tk.W)
        
        # Screenshot display (right side)
        display_frame = ttk.LabelFrame(main_frame, text="Screenshot", width=800)
        display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Canvas for screenshot and rectangles
        self.canvas = tk.Canvas(display_frame, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind mouse events for drawing
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        
    def on_app_selected(self, event):
        """Handle app selection"""
        self.current_app = self.app_var.get()
        self.toolbar_buttons = {}
        self.update_button_list()
        print(f"Selected app: {self.current_app}")
        
    def start_countdown_capture(self):
        """Start countdown and capture screenshot"""
        if self.countdown_running:
            return
            
        # Instructions
        messagebox.showinfo("Capture Instructions", 
                          "Click OK to start countdown.\n"
                          "You'll have 5 seconds to switch to your target application.\n"
                          "The screenshot will be taken automatically.")
        
        # Start countdown in separate thread
        self.countdown_running = True
        countdown_thread = threading.Thread(target=self.run_countdown, daemon=True)
        countdown_thread.start()
    
    def run_countdown(self):
        """Run countdown and capture screenshot"""
        try:
            # Countdown from 5 to 1
            for i in range(5, 0, -1):
                if not self.countdown_running:
                    break
                    
                # Update countdown label
                self.root.after(0, lambda x=i: self.countdown_label.config(text=f"Switch to target app in {x}..."))
                time.sleep(1)
            
            if self.countdown_running:
                # Final countdown
                self.root.after(0, lambda: self.countdown_label.config(text="CAPTURING NOW!"))
                time.sleep(0.5)
                
                # Capture screenshot
                self.root.after(0, self.capture_screenshot)
                
                # Reset countdown
                self.root.after(0, lambda: self.countdown_label.config(text=""))
                self.countdown_running = False
                
        except Exception as e:
            print(f"Countdown error: {e}")
            self.countdown_running = False
    
    def capture_screenshot(self):
        """Capture screenshot of current screen"""
        try:
            # Capture full screen
            screenshot = pyautogui.screenshot()
            
            # Save screenshot
            self.screenshot_path = f"screenshots/{self.current_app.lower()}_toolbar.png"
            os.makedirs("screenshots", exist_ok=True)
            screenshot.save(self.screenshot_path)
            
            # Display the captured screenshot directly
            self.display_screenshot()
            
            messagebox.showinfo("Success", f"Screenshot captured and saved to {self.screenshot_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to capture screenshot: {e}")
    
    def display_screenshot(self):
        """Display screenshot from current screenshot_path"""
        try:
            if not self.screenshot_path or not os.path.exists(self.screenshot_path):
                return
                
            # Load and display image
            self.screenshot_image = Image.open(self.screenshot_path)
            
            # Resize to fit canvas
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                self.screenshot_image.thumbnail((canvas_width, canvas_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage for tkinter
            self.photo_image = ImageTk.PhotoImage(self.screenshot_image)
            
            # Clear canvas and display image
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)
            
            # Redraw existing rectangles
            self.redraw_rectangles()
            
            print(f"Displayed screenshot: {self.screenshot_path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display screenshot: {e}")
            print(f"Error displaying screenshot: {e}")
    
    def load_screenshot(self):
        """Load screenshot from file"""
        try:
            # Always show file dialog to select screenshot
            filename = filedialog.askopenfilename(
                title="Select Screenshot",
                filetypes=[
                    ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"),
                    ("All files", "*.*")
                ]
            )
            
            if filename:
                self.screenshot_path = filename
                
                # Load and display image
                self.screenshot_image = Image.open(self.screenshot_path)
                
                # Resize to fit canvas
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()
                
                if canvas_width > 1 and canvas_height > 1:
                    self.screenshot_image.thumbnail((canvas_width, canvas_height), Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage for tkinter
                self.photo_image = ImageTk.PhotoImage(self.screenshot_image)
                
                # Clear canvas and display image
                self.canvas.delete("all")
                self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)
                
                # Redraw existing rectangles
                self.redraw_rectangles()
                
                print(f"Loaded screenshot: {filename}")
            else:
                print("No file selected")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load screenshot: {e}")
            print(f"Error loading screenshot: {e}")
    
    def start_mapping_mode(self):
        """Enable rectangle drawing mode"""
        if not self.screenshot_image:
            messagebox.showerror("Error", "Please load a screenshot first")
            return
            
        self.drawing = True
        messagebox.showinfo("Mapping Mode", 
                          "Click and drag to draw rectangles around buttons.\n"
                          "Release to add button details.")
    
    def on_canvas_click(self, event):
        """Handle canvas click for drawing rectangles"""
        if not self.drawing:
            return
            
        self.start_x = event.x
        self.start_y = event.y
        
        # Create rectangle
        self.current_rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline="red", width=2
        )
    
    def on_canvas_drag(self, event):
        """Handle canvas drag for drawing rectangles"""
        if not self.drawing or not self.current_rect:
            return
            
        # Update rectangle
        self.canvas.coords(self.current_rect, 
                          self.start_x, self.start_y, event.x, event.y)
    
    def on_canvas_release(self, event):
        """Handle canvas release to finish rectangle"""
        if not self.drawing or not self.current_rect:
            return
            
        # Get final coordinates
        end_x = event.x
        end_y = event.y
        
        # Ensure coordinates are in correct order
        x1, y1 = min(self.start_x, end_x), min(self.start_y, end_y)
        x2, y2 = max(self.start_x, end_x), max(self.start_y, end_y)
        
        # Update rectangle with final coordinates
        self.canvas.coords(self.current_rect, x1, y1, x2, y2)
        
        # Get button details from user
        self.get_button_details(x1, y1, x2, y2)
        
        self.current_rect = None
        self.drawing = False
    
    def get_button_details(self, x1, y1, x2, y2):
        """Get button details from user"""
        # Create dialog for button details
        dialog = tk.Toplevel(self.root)
        dialog.title("Button Details")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Button name
        ttk.Label(dialog, text="Button Name:").pack(anchor=tk.W, padx=10, pady=(20, 5))
        name_var = tk.StringVar()
        name_entry = ttk.Entry(dialog, textvariable=name_var, width=30)
        name_entry.pack(padx=10, pady=(0, 20))
        
        # Save button
        def save_button():
            name = name_var.get().strip()
            
            if not name:
                messagebox.showerror("Error", "Please enter a button name")
                return
                
            # Add button to storage with default values
            button_id = f"custom_{name}"
            self.toolbar_buttons[button_id] = {
                "name": name,
                "action": name.lower().replace(" ", "_"),
                "shortcut": "",
                "category": "custom",
                "coordinates": [(x1, y1), (x2, y2)],
                "app": self.current_app
            }
            
            # Add rectangle to canvas with label
            rect_id = self.canvas.create_rectangle(x1, y1, x2, y2, 
                                                 outline="green", width=2)
            label_id = self.canvas.create_text(x1, y2 + 15, 
                                             text=name, anchor=tk.NW, fill="green")
            
            # Store rectangle info
            self.rectangles.append({
                "rect_id": rect_id,
                "label_id": label_id,
                "button_id": button_id
            })
            
            self.update_button_list()
            dialog.destroy()
        
        ttk.Button(dialog, text="Save Button", command=save_button).pack(pady=10)
        
        # Focus on name entry
        name_entry.focus()
    
    def clear_rectangles(self):
        """Clear all drawn rectangles"""
        # Clear canvas
        self.canvas.delete("all")
        
        # Reload screenshot if exists
        if self.screenshot_image:
            self.photo_image = ImageTk.PhotoImage(self.screenshot_image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)
        
        # Clear data
        self.rectangles = []
        self.toolbar_buttons = {}
        self.update_button_list()
    
    def redraw_rectangles(self):
        """Redraw all rectangles after screenshot reload"""
        for rect_info in self.rectangles:
            button = self.toolbar_buttons[rect_info["button_id"]]
            coords = button["coordinates"]
            
            # Redraw rectangle
            rect_id = self.canvas.create_rectangle(
                coords[0][0], coords[0][1], coords[1][0], coords[1][1],
                outline="green", width=2
            )
            
            # Redraw label
            label_id = self.canvas.create_text(
                coords[0][0], coords[0][1] + 15,
                text=button["name"], anchor=tk.NW, fill="green"
            )
            
            # Update rectangle info
            rect_info["rect_id"] = rect_id
            rect_info["label_id"] = label_id
    
    def update_button_list(self):
        """Update the button listbox"""
        self.button_listbox.delete(0, tk.END)
        
        for button_id, button in self.toolbar_buttons.items():
            shortcut_text = f" ({button['shortcut']})" if button['shortcut'] else ""
            self.button_listbox.insert(tk.END, f"{button['name']}{shortcut_text}")
    
    def export_to_json(self):
        """Export button mapping to JSON file"""
        if not self.toolbar_buttons:
            messagebox.showerror("Error", "No buttons to export")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialname=f"{self.current_app.lower()}_toolbar_buttons.json"
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.toolbar_buttons, f, indent=2)
                messagebox.showinfo("Success", f"Exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")
    
    def export_to_python(self):
        """Export button mapping to Python dictionary"""
        if not self.toolbar_buttons:
            messagebox.showerror("Error", "No buttons to export")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python files", "*.py")],
            initialname=f"{self.current_app.lower()}_toolbar_map.py"
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(f"# {self.current_app} Toolbar Button Map\n")
                    f.write("# Generated by Toolbar Mapper\n\n")
                    f.write(f"{self.current_app.upper()}_TOOLBAR_MAP = {{\n")
                    
                    # Group by category
                    categories = {}
                    for button_id, button in self.toolbar_buttons.items():
                        category = button['category']
                        if category not in categories:
                            categories[category] = []
                        categories[category].append(button)
                    
                    for category, buttons in categories.items():
                        f.write(f'    "{category}": {{\n')
                        for button in buttons:
                            shortcut_text = f'"{button["shortcut"]}"' if button["shortcut"] else 'None'
                            f.write(f'        "{button["name"]}": {{\n')
                            f.write(f'            "coordinates": [{button["coordinates"][0]}, {button["coordinates"][1]}],\n')
                            f.write(f'            "shortcut": {shortcut_text},\n')
                            f.write(f'            "action": "{button["action"]}"\n')
                            f.write(f'        }},\n')
                        f.write('    },\n')
                    
                    f.write('}\n')
                
                messagebox.showinfo("Success", f"Exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")
    
    def run(self):
        """Start the toolbar mapper"""
        self.root.mainloop()

if __name__ == "__main__":
    mapper = ToolbarMapper()
    mapper.run()
