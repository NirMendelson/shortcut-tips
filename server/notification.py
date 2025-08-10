import tkinter as tk
import threading
import queue

class NotificationWindow:
    """A capsule-shaped, Apple-style liquid glass UI notification window with blurred transparency"""
    
    def __init__(self, message, shortcut, duration=3.0):
        self.message = message
        self.shortcut = shortcut
        self.duration = duration
        self.window = None
        
    def show(self):
        """Show the notification window"""
        try:
            # Create the main window
            self.window = tk.Tk()
            self.window.title("Shortcut Tip")
            
            # Make window more transparent for liquid glass effect
            self.window.attributes('-alpha', 0.80)
            self.window.attributes('-topmost', True)
            self.window.overrideredirect(True)
            
            # Position window in top-right corner
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            window_width = 280
            window_height = 50
            
            x = screen_width - window_width - 30
            y = 120
            self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
            
            # Create main frame with capsule shape
            main_frame = tk.Frame(self.window, bg='#000000', relief='flat', borderwidth=0)
            main_frame.pack(fill='both', expand=True)
            
            # Create inner frame for the glass effect
            glass_frame = tk.Frame(main_frame, bg='#ffffff', relief='flat', borderwidth=0)
            glass_frame.pack(fill='both', expand=True, padx=2, pady=2)
            
            # Create content frame with rounded corners
            content_frame = tk.Frame(glass_frame, bg='#f8f9fa', relief='flat', borderwidth=0)
            content_frame.pack(fill='both', expand=True, padx=12, pady=8)
            
            # Create the main text label (single line)
            text_label = tk.Label(
                content_frame,
                text=self.message,
                font=('Segoe UI', 11, 'normal'),
                fg='#2c2c2e',
                bg='#f8f9fa',
                anchor='center'
            )
            text_label.pack(expand=True, fill='both')
            
            # Apply capsule shape and glass effects
            self.apply_capsule_shape(main_frame)
            self.apply_liquid_glass_effect(glass_frame, content_frame)
            
            # Auto-hide after duration
            self.window.after(int(self.duration * 1000), self.hide)
            
            # Start the window
            self.window.mainloop()
            
        except Exception as e:
            print(f"Error creating notification window: {e}")
    
    def apply_capsule_shape(self, frame):
        """Apply capsule shape to the frame with no outlines and liquid glass effect"""
        try:
            # Create a canvas for the capsule shape
            canvas = tk.Canvas(frame, bg='#000000', highlightthickness=0, borderwidth=0)
            canvas.pack(fill='both', expand=True)
            
            # Draw capsule shape using arcs and lines - NO OUTLINES
            width = 280
            height = 50
            radius = height // 2
            
            # Draw the capsule: two semicircles connected by lines - NO OUTLINES
            # Left semicircle
            canvas.create_arc(0, 0, height, height, start=90, extent=180, 
                            fill='#ffffff', outline='', width=0)
            # Right semicircle  
            canvas.create_arc(width-height, 0, width, height, start=270, extent=180,
                            fill='#ffffff', outline='', width=0)
            # Top rectangle
            canvas.create_rectangle(radius, 0, width-radius, height, 
                                 fill='#ffffff', outline='', width=0)
            
            # Add subtle inner glow effect for liquid glass appearance
            # Inner left semicircle (slightly smaller)
            inner_radius = radius - 2
            canvas.create_arc(2, 2, height-2, height-2, start=90, extent=180, 
                            fill='#fafafa', outline='', width=0)
            # Inner right semicircle
            canvas.create_arc(width-height+2, 2, width-2, height-2, start=270, extent=180,
                            fill='#fafafa', outline='', width=0)
            # Inner rectangle
            canvas.create_rectangle(inner_radius, 2, width-inner_radius, height-2, 
                                 fill='#fafafa', outline='', width=0)
            
        except Exception as e:
            print(f"Error applying capsule shape: {e}")
    
    def apply_liquid_glass_effect(self, glass_frame, content_frame):
        """Apply Apple-style liquid glass effect with blurred transparency"""
        try:
            # Add subtle shadow effect (more transparent)
            shadow_frame = tk.Frame(glass_frame, bg='#000000', height=2)
            shadow_frame.pack(fill='x', side='bottom')
            shadow_frame.configure(relief='flat', borderwidth=0)
            
            # Add inner glow effect (more transparent)
            glow_frame = tk.Frame(content_frame, bg='#ffffff', height=2)
            glow_frame.pack(fill='x', side='top')
            glow_frame.configure(relief='flat', borderwidth=0)
            
            # Configure glass-like appearance with no borders
            glass_frame.configure(relief='flat', borderwidth=0)
            content_frame.configure(relief='flat', borderwidth=0)
            
            # Add very subtle border (almost invisible)
            border_frame = tk.Frame(content_frame, bg='#f0f0f0', height=1)
            border_frame.pack(fill='x', side='bottom')
            border_frame.configure(relief='flat', borderwidth=0)
            
            # Add additional transparency layers for liquid effect
            # Top highlight
            highlight_frame = tk.Frame(content_frame, bg='#ffffff', height=1)
            highlight_frame.pack(fill='x', side='top')
            highlight_frame.configure(relief='flat', borderwidth=0)
            
            # Bottom highlight
            bottom_highlight = tk.Frame(content_frame, bg='#e8e8e8', height=1)
            bottom_highlight.pack(fill='x', side='bottom')
            bottom_highlight.configure(relief='flat', borderwidth=0)
            
            # Add liquid glass layers with varying transparency
            # Middle highlight for depth
            middle_highlight = tk.Frame(content_frame, bg='#fafafa', height=1)
            middle_highlight.pack(fill='x', side='top', pady=(15, 0))
            middle_highlight.configure(relief='flat', borderwidth=0)
            
            # Subtle inner shadow for depth
            inner_shadow = tk.Frame(content_frame, bg='#f5f5f5', height=1)
            inner_shadow.pack(fill='x', side='bottom', pady=(0, 15))
            inner_shadow.configure(relief='flat', borderwidth=0)
            
        except Exception as e:
            print(f"Error applying liquid glass effect: {e}")
    
    def hide(self):
        """Hide and destroy the notification window"""
        try:
            if self.window:
                self.window.destroy()
                self.window = None
        except Exception as e:
            print(f"Error hiding notification: {e}")


class NotificationSystem:
    """Manages the notification system in a separate thread"""
    
    def __init__(self):
        self.notification_queue = queue.Queue()
        self.notification_thread = None
        self.running = False
        self.start_notification_system()
    
    def start_notification_system(self):
        """Start the notification system in a separate thread"""
        self.running = True
        self.notification_thread = threading.Thread(target=self.notification_worker, daemon=True)
        self.notification_thread.start()
        print("Notification system started")
    
    def notification_worker(self):
        """Worker thread for handling notifications"""
        while True:
            try:
                # Get notification from queue with timeout
                notification_data = self.notification_queue.get(timeout=1.0)
                if notification_data:
                    self.show_notification(notification_data)
            except queue.Empty:
                # Check if we should continue running
                if not self.running:
                    break
                continue
            except Exception as e:
                print(f"Error in notification worker: {e}")
                # Check if we should continue running
                if not self.running:
                    break
    
    def show_notification(self, notification_data):
        """Show a notification with the specified message and shortcut"""
        try:
            # Create notification window
            notification_window = NotificationWindow(
                notification_data['message'],
                notification_data['shortcut'],
                notification_data.get('duration', 3.0)
            )
            notification_window.show()
        except Exception as e:
            print(f"Error showing notification: {e}")
    
    def suggest_shortcut(self, action, shortcut):
        """Suggest a keyboard shortcut for an action"""
        message = f"Use {shortcut} for {action.lower()}"
        notification_data = {
            'message': message,
            'shortcut': "",
            'duration': 3.0
        }
        self.notification_queue.put(notification_data)
    
    def stop(self):
        """Stop the notification system"""
        self.running = False
