"""
GUI components for the Microscopy Image Analyzer
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, Callable, Any

from config.settings import AppConfig, UIConfig


class PathControls(ttk.LabelFrame):
    """Controls for input/output folder paths"""
    
    def __init__(self, parent: tk.Widget):
        super().__init__(parent, text="Paths to folders", padding=UIConfig.FRAME_PADDING)
        
        self.input_folder_var = tk.StringVar()
        self.export_folder_var = tk.StringVar()
        
        # Callbacks
        self.on_input_folder_changed: Optional[Callable[[str], None]] = None
        self.on_export_folder_changed: Optional[Callable[[str], None]] = None
        
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """Create path control widgets"""
        # Input folder
        ttk.Label(self, text="Input folder:").pack(anchor=tk.W)
        self.input_entry = ttk.Entry(self, textvariable=self.input_folder_var)
        self.input_entry.pack(fill=tk.X, pady=2)
        ttk.Button(self, text="Browse...", command=self._browse_input).pack(fill=tk.X, pady=2)
        
        # Export folder
        ttk.Label(self, text="Export folder:", ).pack(anchor=tk.W, pady=(10, 0))
        self.export_entry = ttk.Entry(self, textvariable=self.export_folder_var)
        self.export_entry.pack(fill=tk.X, pady=2)
        ttk.Button(self, text="Browse...", command=self._browse_export).pack(fill=tk.X, pady=2)
    
    def _browse_input(self) -> None:
        """Browse for input folder"""
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.input_folder_var.set(folder_path)
            if self.on_input_folder_changed:
                self.on_input_folder_changed(folder_path)
    
    def _browse_export(self) -> None:
        """Browse for export folder"""
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.export_folder_var.set(folder_path)
            if self.on_export_folder_changed:
                self.on_export_folder_changed(folder_path)
    
    def get_input_folder(self) -> str:
        """Get input folder path"""
        return self.input_folder_var.get()
    
    def get_export_folder(self) -> str:
        """Get export folder path"""
        return self.export_folder_var.get()
    
    def set_input_folder(self, path: str) -> None:
        """Set input folder path"""
        self.input_folder_var.set(path)
    
    def set_export_folder(self, path: str) -> None:
        """Set export folder path"""
        self.export_folder_var.set(path)


class CellLocationControls(ttk.LabelFrame):
    """Controls for cell location"""
    
    def __init__(self, parent: tk.Widget):
        super().__init__(parent, text="Locate cell", padding=UIConfig.FRAME_PADDING)
        
        self.x_var = tk.StringVar()
        self.y_var = tk.StringVar()
        
        # Callbacks
        self.on_locate_cell: Optional[Callable[[int, int], None]] = None
        self.on_toggle_crosshair: Optional[Callable[[], None]] = None
        
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """Create cell location widgets"""
        # X coordinate
        ttk.Label(self, text="X coordinate:").pack(anchor=tk.W)
        self.x_entry = ttk.Entry(self, textvariable=self.x_var)
        self.x_entry.pack(fill=tk.X, pady=2)
        
        # Y coordinate
        ttk.Label(self, text="Y coordinate:").pack(anchor=tk.W, pady=(10, 0))
        self.y_entry = ttk.Entry(self, textvariable=self.y_var)
        self.y_entry.pack(fill=tk.X, pady=2)
        
        # Locate button
        ttk.Button(self, text="Locate Cell", command=self._locate_cell).pack(fill=tk.X, pady=5)
        
        # Toggle crosshair button
        ttk.Button(self, text="Toggle Crosshair", command=self._toggle_crosshair).pack(fill=tk.X, pady=5)
    
    def _locate_cell(self) -> None:
        """Handle locate cell button click"""
        try:
            x = int(self.x_var.get()) if self.x_var.get() else 0
            y = int(self.y_var.get()) if self.y_var.get() else 0
            
            if self.on_locate_cell:
                self.on_locate_cell(x, y)
                
        except ValueError:
            messagebox.showerror("Error", "Please enter valid integer coordinates")
    
    def _toggle_crosshair(self) -> None:
        """Handle toggle crosshair button click"""
        if self.on_toggle_crosshair:
            self.on_toggle_crosshair()
    
    def clear_coordinates(self) -> None:
        """Clear coordinate entries"""
        self.x_var.set("")
        self.y_var.set("")
    
    def set_coordinates(self, x: int, y: int) -> None:
        """Set coordinate values"""
        self.x_var.set(str(x))
        self.y_var.set(str(y))


class ROIControls(ttk.LabelFrame):
    """Controls for ROI definition"""
    
    def __init__(self, parent: tk.Widget):
        super().__init__(parent, text="Define ROI", padding=UIConfig.FRAME_PADDING)
        
        # Callbacks
        self.on_draw_roi: Optional[Callable[[], None]] = None
        
        self.dimension_label: Optional[ttk.Label] = None
        
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """Create ROI control widgets"""
        # Draw ROI button
        ttk.Button(self, text="Draw ROI", command=self._draw_roi).pack(fill=tk.X, pady=5)
        
        # ROI dimensions display
        dimension_frame = ttk.Frame(self)
        dimension_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(dimension_frame, text="ROI Dimensions:").pack(side=tk.LEFT)
        self.dimension_label = ttk.Label(dimension_frame, text="0 x 0 px")
        self.dimension_label.pack(side=tk.LEFT, padx=5)
    
    def _draw_roi(self) -> None:
        """Handle draw ROI button click"""
        if self.on_draw_roi:
            self.on_draw_roi()
    
    def update_dimensions(self, width: int, height: int) -> None:
        """Update ROI dimensions display"""
        if self.dimension_label:
            self.dimension_label.config(text=f"{width} x {height} px")
    
    def reset_dimensions(self) -> None:
        """Reset dimensions display"""
        self.update_dimensions(0, 0)


class CroppingControls(ttk.LabelFrame):
    """Controls for image cropping operations"""
    
    def __init__(self, parent: tk.Widget):
        super().__init__(parent, text="Cropping area", padding=UIConfig.FRAME_PADDING)
        
        # Callbacks
        self.on_crop_all: Optional[Callable[[], None]] = None
        self.on_save_images: Optional[Callable[[], None]] = None
        self.on_make_animation: Optional[Callable[[], None]] = None
        
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """Create cropping control widgets"""
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X)
        
        # Crop All button
        crop_btn = ttk.Button(button_frame, text="Crop All", command=self._crop_all)
        crop_btn.pack(side=tk.LEFT, expand=True, padx=2)
        
        # Save button
        save_btn = ttk.Button(button_frame, text="Save Images", command=self._save_images)
        save_btn.pack(side=tk.LEFT, expand=True, padx=2)
        
        # Animation button (replaces Make GIF)
        animation_btn = ttk.Button(button_frame, text="Make Animation", command=self._make_animation)
        animation_btn.pack(side=tk.LEFT, expand=True, padx=2)
    
    def _crop_all(self) -> None:
        """Handle crop all button click"""
        if self.on_crop_all:
            self.on_crop_all()
    
    def _save_images(self) -> None:
        """Handle save images button click"""
        if self.on_save_images:
            self.on_save_images()
    
    def _make_animation(self) -> None:
        """Handle make animation button click"""
        if self.on_make_animation:
            self.on_make_animation()


class ImageCanvas(ttk.LabelFrame):
    """Image display canvas with controls"""
    
    def __init__(self, parent: tk.Widget):
        super().__init__(parent, text="Image Preview", padding=UIConfig.FRAME_PADDING)
        
        self.canvas: Optional[tk.Canvas] = None
        self.coord_label: Optional[ttk.Label] = None
        self.counter_label: Optional[ttk.Label] = None
        
        # Callbacks
        self.on_mouse_motion: Optional[Callable[[tk.Event], None]] = None
        self.on_mouse_press: Optional[Callable[[tk.Event], None]] = None
        self.on_mouse_drag: Optional[Callable[[tk.Event], None]] = None
        self.on_mouse_release: Optional[Callable[[tk.Event], None]] = None
        self.on_mouse_wheel: Optional[Callable[[tk.Event], None]] = None
        
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """Create canvas widgets"""
        # Main canvas
        self.canvas = tk.Canvas(
            self, 
            bg=UIConfig.BACKGROUND_COLOR, 
            cursor=UIConfig.CURSOR_CROSS,
            width=AppConfig.CANVAS_WIDTH, 
            height=AppConfig.CANVAS_HEIGHT
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Info frame
        info_frame = ttk.Frame(self)
        info_frame.pack(fill=tk.X, pady=5)
        
        # Coordinate display
        self.coord_label = ttk.Label(info_frame, text="X: 0, Y: 0")
        self.coord_label.pack(side=tk.LEFT)
        
        # Image counter
        self.counter_label = ttk.Label(info_frame, text="0/0")
        self.counter_label.pack(side=tk.RIGHT)
        
        # Bind mouse events
        self._bind_events()
    
    def _bind_events(self) -> None:
        """Bind mouse events to canvas"""
        if not self.canvas:
            return
            
        self.canvas.bind("<Motion>", self._on_motion)
        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<MouseWheel>", self._on_wheel)
    
    def _on_motion(self, event: tk.Event) -> None:
        """Handle mouse motion"""
        if self.on_mouse_motion:
            self.on_mouse_motion(event)
    
    def _on_press(self, event: tk.Event) -> None:
        """Handle mouse press"""
        if self.on_mouse_press:
            self.on_mouse_press(event)
    
    def _on_drag(self, event: tk.Event) -> None:
        """Handle mouse drag"""
        if self.on_mouse_drag:
            self.on_mouse_drag(event)
    
    def _on_release(self, event: tk.Event) -> None:
        """Handle mouse release"""
        if self.on_mouse_release:
            self.on_mouse_release(event)
    
    def _on_wheel(self, event: tk.Event) -> None:
        """Handle mouse wheel"""
        if self.on_mouse_wheel:
            self.on_mouse_wheel(event)
    
    def update_coordinates(self, x: int, y: int) -> None:
        """Update coordinate display"""
        if self.coord_label:
            self.coord_label.config(text=f"X: {x}, Y: {y}")
    
    def update_counter(self, current: int, total: int) -> None:
        """Update image counter display"""
        if self.counter_label:
            self.counter_label.config(text=f"{current}/{total}")


class NavigationControls(ttk.Frame):
    """Navigation and view controls"""
    
    def __init__(self, parent: tk.Widget):
        super().__init__(parent)
        
        # Callbacks
        self.on_previous: Optional[Callable[[], None]] = None
        self.on_next: Optional[Callable[[], None]] = None
        self.on_zoom_in: Optional[Callable[[], None]] = None
        self.on_zoom_out: Optional[Callable[[], None]] = None
        self.on_reset_view: Optional[Callable[[], None]] = None
        self.on_toggle_pan: Optional[Callable[[], None]] = None
        
        self.pan_button: Optional[ttk.Button] = None
        
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """Create navigation control widgets"""
        # Navigation buttons
        nav_frame = ttk.Frame(self)
        nav_frame.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        ttk.Button(nav_frame, text="← Previous", command=self._previous).pack(side=tk.LEFT, expand=True)
        ttk.Button(nav_frame, text="Next →", command=self._next).pack(side=tk.LEFT, expand=True)
        
        # Zoom buttons
        zoom_frame = ttk.Frame(self)
        zoom_frame.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        ttk.Button(zoom_frame, text="Zoom Out", command=self._zoom_out).pack(side=tk.LEFT, expand=True)
        ttk.Button(zoom_frame, text="Zoom In", command=self._zoom_in).pack(side=tk.LEFT, expand=True)
        ttk.Button(zoom_frame, text="Reset View", command=self._reset_view).pack(side=tk.LEFT, expand=True)
        
        # Pan button
        pan_frame = ttk.Frame(self)
        pan_frame.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        self.pan_button = ttk.Button(pan_frame, text="Pan Mode", command=self._toggle_pan)
        self.pan_button.pack(side=tk.LEFT, expand=True)
    
    def _previous(self) -> None:
        """Handle previous button click"""
        if self.on_previous:
            self.on_previous()
    
    def _next(self) -> None:
        """Handle next button click"""
        if self.on_next:
            self.on_next()
    
    def _zoom_in(self) -> None:
        """Handle zoom in button click"""
        if self.on_zoom_in:
            self.on_zoom_in()
    
    def _zoom_out(self) -> None:
        """Handle zoom out button click"""
        if self.on_zoom_out:
            self.on_zoom_out()
    
    def _reset_view(self) -> None:
        """Handle reset view button click"""
        if self.on_reset_view:
            self.on_reset_view()
    
    def _toggle_pan(self) -> None:
        """Handle toggle pan button click"""
        if self.on_toggle_pan:
            self.on_toggle_pan()
    
    def set_pan_mode(self, enabled: bool) -> None:
        """Set pan mode visual state"""
        if self.pan_button:
            style = 'Accent.TButton' if enabled else 'TButton'
            self.pan_button.config(style=style)
