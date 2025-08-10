import os
from datetime import datetime
from PIL import ImageGrab
import pytesseract

class ScreenshotManager:
    def __init__(self, screenshots_dir="screenshots"):
        self.screenshots_dir = screenshots_dir
        self.init_screenshots_directory()
        
        # Set Tesseract path for Windows
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    def init_screenshots_directory(self):
        """Create screenshots directory if it doesn't exist"""
        if not os.path.exists(self.screenshots_dir):
            os.makedirs(self.screenshots_dir)
            print(f"Created screenshots directory: {self.screenshots_dir}")
    
    def capture_context_menu_screenshot(self, x, y):
        """Capture screenshot around cursor position for context menu analysis"""
        try:
            print(f"DEBUG: Capturing screenshot at coordinates ({x}, {y})")
            # Capture wider area - enough to see the full menu item text
            # Context menu items are typically 200-300 pixels wide and 20-30 pixels tall
            left = max(0, x - 100)
            top = max(0, y - 30)
            right = x + 100
            bottom = y + 30
            
            print(f"DEBUG: Screenshot area: left={left}, top={top}, right={right}, bottom={bottom}")
            screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
            print("DEBUG: Screenshot captured successfully")
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"context_menu_{timestamp}_x{x}_y{y}.png"
            filepath = os.path.join(self.screenshots_dir, filename)
            
            # Save screenshot
            screenshot.save(filepath)
            print(f"Screenshot saved: {filename}")
            
            return filepath, screenshot
            
        except Exception as e:
            print(f"Error capturing screenshot: {e}")
            print(f"DEBUG: Screenshot exception type: {type(e)}")
            import traceback
            traceback.print_exc()
            return None, None
    
    def analyze_menu_text(self, screenshot):
        """Use OCR to extract text from context menu screenshot"""
        try:
            print("DEBUG: Starting OCR analysis of screenshot")
            # Use pytesseract with better configuration for menu text
            # --psm 6: Assume a uniform block of text
            # --oem 3: Use LSTM OCR Engine
            config = '--psm 6 --oem 3'
            
            print("DEBUG: Calling pytesseract.image_to_string")
            menu_text = pytesseract.image_to_string(screenshot, config=config)
            print(f"DEBUG: Raw OCR result: {repr(menu_text)}")
            
            # Clean up the text - remove extra whitespace and newlines
            menu_text = ' '.join(menu_text.split())
            print(f"DEBUG: Cleaned menu text: {repr(menu_text)}")
            
            if menu_text:
                print(f"Detected menu text: {menu_text[:100]}...")
                return menu_text
            else:
                print("No text detected in context menu")
                return None
                
        except Exception as e:
            print(f"Error analyzing menu text: {e}")
            print(f"DEBUG: Exception type: {type(e)}")
            import traceback
            traceback.print_exc()
            return None
