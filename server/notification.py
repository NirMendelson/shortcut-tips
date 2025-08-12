import tkinter as tk
import threading
import queue

class NotificationWindow:
    """A capsule-shaped liquid glass notification window with blurred transparency"""
    
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
            
            # Make window fully transparent for liquid glass effect
            self.window.attributes('-alpha', 0.0)
            self.window.attributes('-topmost', True)
            self.window.overrideredirect(True)
            
            # Position window in top-right corner
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            window_width = 320
            window_height = 45
            
            x = screen_width - window_width - 30
            y = 120
            self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
            
            # Create canvas for the capsule shape with liquid glass effect
            self.canvas = tk.Canvas(
                self.window, 
                width=window_width, 
                height=window_height,
                highlightthickness=0, 
                borderwidth=0,
                bg='white'  # White background that will be made transparent
            )
            self.canvas.pack(fill='both', expand=True)
            
            # Draw the liquid glass capsule
            self.draw_liquid_glass_capsule()
            
            # Add the text label
            self.add_text_label()
            
            # Fade in the window
            self.fade_in()
            
            # Auto-hide after duration
            self.window.after(int(self.duration * 1000), self.fade_out)
            
            # Start the window
            self.window.mainloop()
            
        except Exception as e:
            print(f"Error creating notification window: {e}")
    
    def draw_liquid_glass_capsule(self):
        """Draw a beautiful liquid glass capsule shape"""
        width = 320
        height = 45
        radius = height // 2
        
        # Create the main capsule shape with liquid glass effect
        # Outer glow (subtle shadow)
        self.canvas.create_oval(
            radius-2, 2, width-radius+2, height-2,
            fill='#000000', outline='', width=0, stipple='gray50'
        )
        
        # Main capsule background (half transparent white)
        self.canvas.create_oval(
            radius, 0, width-radius, height,
            fill='#ffffff', outline='', width=0, stipple='gray75'
        )
        
        # Inner highlight for glass effect
        self.canvas.create_oval(
            radius+2, 2, width-radius-2, height-2,
            fill='#ffffff', outline='', width=0, stipple='gray50'
        )
        
        # Top highlight line for glass shine
        self.canvas.create_line(
            radius+3, 3, width-radius-3, 3,
            fill='#ffffff', width=1, stipple='gray25'
        )
    
    def add_text_label(self):
        """Add the text label to the notification"""
        # Create text label with dark grey color
        self.text_label = tk.Label(
            self.canvas,
            text=self.message,
            font=('Segoe UI', 10, 'normal'),
            fg='#2c2c2e',  # Dark grey text
            bg='white',  # White background that will be made transparent
            anchor='center'
        )
        
        # Position the text in the center of the capsule
        self.canvas.create_window(
            160, 22,  # Center of 320x45 window
            window=self.text_label,
            anchor='center'
        )
    
    def fade_in(self):
        """Fade in the notification with liquid glass effect"""
        self.window.attributes('-alpha', 0.0)
        
        def fade_step(alpha=0.0):
            if alpha < 0.85:  # 85% opacity for liquid glass
                alpha += 0.05
                self.window.attributes('-alpha', alpha)
                self.window.after(20, lambda: fade_step(alpha))
        
        fade_step()
    
    def fade_out(self):
        """Fade out the notification smoothly"""
        def fade_step(alpha=0.85):
            if alpha > 0.0:
                alpha -= 0.05
                self.window.attributes('-alpha', alpha)
                self.window.after(20, lambda: fade_step(alpha))
            else:
                self.hide()
        
        fade_step()
    
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
                continue
    
    def show_notification(self, notification_data):
        """Show a notification with the given data"""
        try:
            message = notification_data.get('message', '')
            shortcut = notification_data.get('shortcut', '')
            duration = notification_data.get('duration', 3.0)
            
            # Create and show the notification
            notification = NotificationWindow(message, shortcut, duration)
            notification.show()
            
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
        if self.notification_thread:
            self.notification_thread.join(timeout=1.0)
