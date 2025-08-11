#!/usr/bin/env python3
"""
Real-Time UI Element Detector
Uses Windows UI Automation to detect what element was clicked in real-time
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import time
import threading
from pywinauto import Desktop
from pynput import mouse
import psutil
import win32gui
import win32process

class RealTimeUIDetector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Real-Time UI Element Detector")
        self.root.geometry("1200x800")
        
        # UI Automation backend
        self.desk = Desktop(backend="uia")
        
        # Mouse listener
        self.mouse_listener = None
        self.listening = False
        
        # Data storage
        self.click_history = []
        self.max_history = 100
        
        # Current app tracking
        self.current_app = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control panel (left side)
        control_frame = ttk.LabelFrame(main_frame, text="Controls", width=300)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Start/Stop button
        self.control_button = ttk.Button(control_frame, text="Start Listening", 
                                        command=self.toggle_listening)
        self.control_button.pack(fill=tk.X, pady=(0, 10))
        
        # Status
        self.status_var = tk.StringVar(value="Not listening")
        ttk.Label(control_frame, textvariable=self.status_var).pack(anchor=tk.W, pady=(0, 10))
        
        # Current app info
        ttk.Label(control_frame, text="Current Application:").pack(anchor=tk.W, pady=(0, 5))
        self.app_var = tk.StringVar(value="None")
        ttk.Label(control_frame, textvariable=self.app_var, font=("Consolas", 9)).pack(anchor=tk.W, pady=(0, 10))
        
        # Filter controls
        ttk.Label(control_frame, text="Element Filters:").pack(anchor=tk.W, pady=(0, 5))
        
        # App filter
        self.app_filter_var = tk.StringVar(value="All")
        app_filter_combo = ttk.Combobox(control_frame, textvariable=self.app_filter_var,
                                       values=["All", "Excel", "Cursor", "Chrome", "VS Code"])
        app_filter_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Element type filter
        self.type_filter_var = tk.StringVar(value="All")
        type_filter_combo = ttk.Combobox(control_frame, textvariable=self.type_filter_var,
                                        values=["All", "Button", "Edit", "Menu", "Tab", "Custom"])
        type_filter_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Clear history button
        ttk.Button(control_frame, text="Clear History", 
                  command=self.clear_history).pack(fill=tk.X, pady=(0, 10))
        
        # Export button
        ttk.Button(control_frame, text="Export History", 
                  command=self.export_history).pack(fill=tk.X, pady=(0, 10))
        
        # Instructions
        instructions = """
        Instructions:
        1. Click "Start Listening"
        2. Click anywhere on any application
        3. See real-time element detection
        4. Filter by app or element type
        5. Export results when done
        
        This tool detects UI elements
        in real-time using Windows
        UI Automation!
        """
        ttk.Label(control_frame, text=instructions, justify=tk.LEFT).pack(anchor=tk.W)
        
        # Results display (right side)
        results_frame = ttk.LabelFrame(main_frame, text="Real-Time Element Detection", width=800)
        results_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Results text
        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, font=("Consolas", 9))
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Initial message
        self.results_text.insert(tk.END, "Real-Time UI Element Detector\n")
        self.results_text.insert(tk.END, "=" * 50 + "\n\n")
        self.results_text.insert(tk.END, "Click 'Start Listening' to begin detecting UI elements in real-time.\n\n")
        
    def toggle_listening(self):
        """Toggle between listening and not listening"""
        if not self.listening:
            self.start_listening()
        else:
            self.stop_listening()
    
    def start_listening(self):
        """Start listening for mouse clicks"""
        try:
            self.mouse_listener = mouse.Listener(on_click=self.on_click)
            self.mouse_listener.start()
            self.listening = True
            self.control_button.config(text="Stop Listening")
            self.status_var.set("Listening for clicks...")
            self.results_text.insert(tk.END, "🎯 Started listening for mouse clicks...\n\n")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start listening: {e}")
    
    def stop_listening(self):
        """Stop listening for mouse clicks"""
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
        
        self.listening = False
        self.control_button.config(text="Start Listening")
        self.status_var.set("Not listening")
        self.results_text.insert(tk.END, "⏹️ Stopped listening for mouse clicks.\n\n")
    
    def on_click(self, x, y, button, pressed):
        """Handle mouse click events"""
        if not pressed:  # Only on mouse release
            try:
                # Get element at click point using UI Automation
                element = self.desk.from_point(x, y)
                element_info = element.element_info
                rect = element.rectangle()
                
                # Get process info
                process_id = element_info.process_id
                try:
                    process = psutil.Process(process_id)
                    app_name = process.name()
                    self.current_app = app_name
                    self.app_var.set(app_name)
                except:
                    app_name = "Unknown"
                
                # Create click record
                click_record = {
                    "timestamp": time.time(),
                    "button": str(button),
                    "coordinates": (x, y),
                    "element": {
                        "name": element_info.name,
                        "type": str(element_info.control_type),
                        "automation_id": getattr(element_info, "automation_id", None),
                        "class_name": getattr(element_info, "class_name", None),
                        "process_id": process_id,
                        "app_name": app_name,
                        "bounds": (rect.left, rect.top, rect.right, rect.bottom),
                        "center": ((rect.left + rect.right) // 2, (rect.top + rect.bottom) // 2)
                    }
                }
                
                # Add to history
                self.click_history.append(click_record)
                if len(self.click_history) > self.max_history:
                    self.click_history.pop(0)
                
                # Update UI in main thread
                self.root.after(0, lambda: self.display_click(click_record))
                
            except Exception as e:
                # Element not found or error
                error_record = {
                    "timestamp": time.time(),
                    "button": str(button),
                    "coordinates": (x, y),
                    "error": str(e),
                    "app_name": self.current_app or "Unknown"
                }
                
                self.click_history.append(error_record)
                if len(self.click_history) > self.max_history:
                    self.click_history.pop(0)
                
                # Update UI in main thread
                self.root.after(0, lambda: self.display_error(error_record))
    
    def display_click(self, click_record):
        """Display click information in the UI"""
        element = click_record["element"]
        
        # Check filters
        if not self.should_display_click(click_record):
            return
        
        # Format timestamp
        timestamp = time.strftime("%H:%M:%S", time.localtime(click_record["timestamp"]))
        
        # Display click info
        self.results_text.insert(tk.END, f"🖱️ Click at {timestamp}\n")
        self.results_text.insert(tk.END, f"   📍 Coordinates: {click_record['coordinates']}\n")
        self.results_text.insert(tk.END, f"   🏷️ Element: {element['name']}\n")
        self.results_text.insert(tk.END, f"   🔧 Type: {element['type']}\n")
        self.results_text.insert(tk.END, f"   🆔 Automation ID: {element['automation_id'] or 'None'}\n")
        self.results_text.insert(tk.END, f"   📱 App: {element['app_name']}\n")
        self.results_text.insert(tk.END, f"   📐 Bounds: {element['bounds']}\n")
        self.results_text.insert(tk.END, f"   🎯 Center: {element['center']}\n")
        self.results_text.insert(tk.END, "-" * 50 + "\n\n")
        
        # Auto-scroll to bottom
        self.results_text.see(tk.END)
    
    def display_error(self, error_record):
        """Display error information in the UI"""
        timestamp = time.strftime("%H:%M:%S", time.localtime(error_record["timestamp"]))
        
        self.results_text.insert(tk.END, f"❌ Click at {timestamp}\n")
        self.results_text.insert(tk.END, f"   📍 Coordinates: {error_record['coordinates']}\n")
        self.results_text.insert(tk.END, f"   🚫 Error: {error_record['error']}\n")
        self.results_text.insert(tk.END, f"   📱 App: {error_record['app_name']}\n")
        self.results_text.insert(tk.END, "-" * 50 + "\n\n")
        
        # Auto-scroll to bottom
        self.results_text.see(tk.END)
    
    def should_display_click(self, click_record):
        """Check if click should be displayed based on filters"""
        element = click_record["element"]
        
        # App filter
        app_filter = self.app_filter_var.get()
        if app_filter != "All" and app_filter.lower() not in element["app_name"].lower():
            return False
        
        # Element type filter
        type_filter = self.type_filter_var.get()
        if type_filter != "All" and type_filter.lower() not in element["type"].lower():
            return False
        
        return True
    
    def clear_history(self):
        """Clear click history"""
        self.click_history.clear()
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Real-Time UI Element Detector\n")
        self.results_text.insert(tk.END, "=" * 50 + "\n\n")
        self.results_text.insert(tk.END, "Click history cleared.\n\n")
    
    def export_history(self):
        """Export click history to JSON file"""
        if not self.click_history:
            messagebox.showwarning("Warning", "No click history to export")
            return
        
        try:
            filename = f"ui_clicks_{int(time.time())}.json"
            
            export_data = {
                "export_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_clicks": len(self.click_history),
                "clicks": self.click_history
            }
            
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            messagebox.showinfo("Success", f"Exported {len(self.click_history)} clicks to {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {e}")
    
    def run(self):
        """Start the real-time UI detector"""
        try:
            self.root.mainloop()
        finally:
            # Clean up
            if self.mouse_listener:
                self.mouse_listener.stop()

if __name__ == "__main__":
    detector = RealTimeUIDetector()
    detector.run()
