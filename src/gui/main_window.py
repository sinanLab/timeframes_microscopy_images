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
        
        # Callback functions for menu actions
        self.on_select_input_folder = None
        self.on_export = None
        
        # Create menu bar first
        self._create_menu_bar()
        self._create_layout()
    
    def _configure_styles(self) -> None:
        """Configure custom styles"""
        self.style.configure('Accent.TButton', foreground='white', background='#d9534f')
        self.style.configure('Success.TLabel', foreground=UIConfig.SUCCESS_COLOR)
        self.style.configure('Error.TLabel', foreground=UIConfig.ERROR_COLOR)
        self.style.configure('Warning.TLabel', foreground=UIConfig.WARNING_COLOR)
    
    def _create_menu_bar(self) -> None:
        """Create the menu bar"""
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        # File Menu
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Input Folder...", command=self._open_input_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Export...", command=self._show_export_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Help Menu
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label=" User Guide", command=self._show_user_guide)
        help_menu.add_separator()
        help_menu.add_command(label="🔄 Check for Updates", command=self._check_for_updates)
        help_menu.add_separator()
        help_menu.add_command(label="ℹ️ About", command=self._show_about_dialog)
    
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
    
    # Menu Callbacks
    def _open_input_folder(self) -> None:
        """Open input folder dialog"""
        if self.on_select_input_folder:
            self.on_select_input_folder()
    
    def _show_export_dialog(self) -> None:
        """Show export dialog"""
        if self.on_export:
            self.on_export()
    
    def _show_user_guide(self) -> None:
        """Show user guide dialog"""
        guide_text = """Microscopy Image Analyzer - User Guide

1. Select Input Folder:
   - Click 'Browse' to select folder containing your microscopy images
   - Supported formats: PNG, JPG, JPEG, TIF, TIFF

2. Set Cropping Parameters:
   - X, Y: Top-left corner coordinates of the region to crop
   - Width, Height: Dimensions of the cropping region
   - Preview images will update in real-time

3. Export Options:
   - Single Images: Export cropped versions of all images
   - GIF Animation: Create animated GIF from image sequence
   - MP4 Video: Create high-quality video from image sequence

Tips:
• Use the preview images to verify your cropping region
• GIF format is great for presentations and web sharing
• MP4 format provides better quality for detailed analysis
• All exports are saved with unique names to prevent overwrites

Author: Muhammad Sinan
Contact: msinan@ippt.pan.pl
Profile: https://www.ippt.pan.pl/en/staff/?osoba=msinan"""
        
        dialog = tk.Toplevel(self.root)
        dialog.title("User Guide")
        dialog.geometry("600x500")
        dialog.resizable(True, True)
        
        # Create scrollable text widget
        text_frame = ttk.Frame(dialog)
        text_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap='word', font=('Segoe UI', 10))
        scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        text_widget.insert('1.0', guide_text)
        text_widget.config(state='disabled')
        
        # Close button
        close_frame = ttk.Frame(dialog)
        close_frame.pack(fill='x', padx=10, pady=(0, 10))
        ttk.Button(close_frame, text="Close", command=dialog.destroy).pack(side='right')
    
    def _check_for_updates(self) -> None:
        """Check for software updates"""
        import webbrowser
        from tkinter import messagebox
        
        response = messagebox.askyesno(
            "Check for Updates",
            "Current Version: 0.2.20.07.2\n\n"
            "Would you like to check for updates on GitHub?\n"
            "This will open your web browser to the releases page."
        )
        
        if response:
            webbrowser.open("https://github.com/yourusername/timeframes_microscopy_images/releases")
    
    def _show_about_dialog(self) -> None:
        """Show about dialog"""
        about_text = """Microscopy Image Analyzer
Version 0.2.20.07.2

A professional tool for cropping and analyzing 
time-series microscopy images with advanced 
export capabilities.

Features:
• Batch image cropping with real-time preview
• GIF animation creation with quality controls
• MP4 video export for high-quality sequences
• Professional user interface with comprehensive controls

Author Information:
Name: Muhammad Sinan
Email: msinan@ippt.pan.pl
Profile: https://www.ippt.pan.pl/en/staff/?osoba=msinan
Institution: Polish Academy of Sciences

Copyright © 2024 Muhammad Sinan
Licensed under MIT License

Built with Python and Tkinter"""
        
        dialog = tk.Toplevel(self.root)
        dialog.title("About Microscopy Image Analyzer")
        dialog.geometry("500x600")
        dialog.resizable(False, False)
        
        # Main frame
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Icon/Logo placeholder (you can add an icon here)
        icon_frame = ttk.Frame(main_frame)
        icon_frame.pack(fill='x', pady=(0, 20))
        
        # Title
        title_label = ttk.Label(icon_frame, text="🔬 Microscopy Image Analyzer", 
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack()
        
        # About text
        text_widget = tk.Text(main_frame, wrap='word', height=20, font=('Segoe UI', 10))
        text_widget.pack(fill='both', expand=True, pady=(0, 20))
        text_widget.insert('1.0', about_text)
        text_widget.config(state='disabled')
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x')
        
        # Contact button
        def open_profile():
            import webbrowser
            webbrowser.open("https://www.ippt.pan.pl/en/staff/?osoba=msinan")
        
        ttk.Button(button_frame, text="Visit Author Profile", 
                  command=open_profile).pack(side='left')
        
        ttk.Button(button_frame, text="Close", 
                  command=dialog.destroy).pack(side='right')
