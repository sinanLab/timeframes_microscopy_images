"""
Main application window and GUI setup
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional

from config.settings import AppConfig, UIConfig
from .components import (
    PathControls, CellLocationControls, ROIControls, 
    CroppingControls, ImageCanvas, NavigationControls
)


class MainWindow:
    """Main application window"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(AppConfig.APP_NAME)
        self.root.geometry(f"{AppConfig.WINDOW_WIDTH}x{AppConfig.WINDOW_HEIGHT}")
        
        # Setup theme
        self.style = ttk.Style()
        self.style.theme_use(AppConfig.UI_THEME)
        self._configure_styles()
        
        # GUI components
        self.path_controls: Optional[PathControls] = None
        self.cell_controls: Optional[CellLocationControls] = None
        self.roi_controls: Optional[ROIControls] = None
        self.crop_controls: Optional[CroppingControls] = None
        self.image_canvas: Optional[ImageCanvas] = None
        self.nav_controls: Optional[NavigationControls] = None
        
        # Status label
        self.status_label: Optional[ttk.Label] = None
        
        self._create_layout()
    
    def _configure_styles(self) -> None:
        """Configure custom styles"""
        self.style.configure('Accent.TButton', foreground='white', background='#d9534f')
        self.style.configure('Success.TLabel', foreground=UIConfig.SUCCESS_COLOR)
        self.style.configure('Error.TLabel', foreground=UIConfig.ERROR_COLOR)
        self.style.configure('Warning.TLabel', foreground=UIConfig.WARNING_COLOR)
    
    def _create_layout(self) -> None:
        """Create the main layout"""
        # Main container
        main_frame = ttk.Frame(self.root, padding=UIConfig.FRAME_PADDING)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel for controls
        control_frame = ttk.Frame(main_frame, width=250, padding=UIConfig.FRAME_PADDING)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Right panel for image display
        image_frame = ttk.Frame(main_frame, padding=UIConfig.FRAME_PADDING)
        image_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create control components
        self._create_control_panels(control_frame)
        
        # Create image display components
        self._create_image_panels(image_frame)
    
    def _create_control_panels(self, parent: ttk.Frame) -> None:
        """Create all control panels"""
        # Path controls
        self.path_controls = PathControls(parent)
        self.path_controls.pack(fill=tk.X, pady=UIConfig.CONTROL_PADDING)
        
        # Status label
        self.status_label = ttk.Label(parent, text="No images loaded", 
                                     style='Error.TLabel')
        self.status_label.pack(fill=tk.X, pady=UIConfig.CONTROL_PADDING)
        
        # Cell location controls
        self.cell_controls = CellLocationControls(parent)
        self.cell_controls.pack(fill=tk.X, pady=UIConfig.CONTROL_PADDING)
        
        # ROI controls
        self.roi_controls = ROIControls(parent)
        self.roi_controls.pack(fill=tk.X, pady=UIConfig.CONTROL_PADDING)
        
        # Cropping controls
        self.crop_controls = CroppingControls(parent)
        self.crop_controls.pack(fill=tk.X, pady=UIConfig.CONTROL_PADDING)
        
        # Reset button
        reset_button = ttk.Button(parent, text="Reset Everything", 
                                 style='Accent.TButton')
        reset_button.pack(fill=tk.X, pady=UIConfig.FRAME_PADDING)
        
        # Store reference for callback binding
        self.reset_button = reset_button
    
    def _create_image_panels(self, parent: ttk.Frame) -> None:
        """Create image display panels"""
        # Image canvas
        self.image_canvas = ImageCanvas(parent)
        self.image_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Navigation controls
        self.nav_controls = NavigationControls(parent)
        self.nav_controls.pack(fill=tk.X, pady=UIConfig.CONTROL_PADDING)
    
    def update_status(self, message: str, status_type: str = "normal") -> None:
        """Update status label"""
        if not self.status_label:
            return
            
        style_map = {
            "success": "Success.TLabel",
            "error": "Error.TLabel", 
            "warning": "Warning.TLabel"
        }
        
        style = style_map.get(status_type, "TLabel")
        self.status_label.config(text=message, style=style)
    
    def get_canvas(self) -> tk.Canvas:
        """Get the image canvas widget"""
        return self.image_canvas.canvas if self.image_canvas else None
    
    def run(self) -> None:
        """Run the application"""
        self.root.mainloop()
    
    def destroy(self) -> None:
        """Destroy the window"""
        self.root.destroy()
