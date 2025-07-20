"""
Region of Interest (ROI) management for the Microscopy Image Analyzer
"""

import tkinter as tk
from typing import Optional, Tuple, Dict, Any, Callable
from config.settings import AppConfig, UIConfig


class ROIManager:
    """Manages ROI drawing, editing, and interaction"""
    
    def __init__(self, canvas: tk.Canvas, image_processor):
        self.canvas = canvas
        self.image_processor = image_processor
        self.roi_coords: Optional[Dict[str, float]] = None
        self.roi_rect: Optional[int] = None
        self.resize_handles: list = []
        
        # State variables
        self.is_drawing: bool = False
        self.is_dragging: bool = False
        self.active_handle: Optional[str] = None
        
        # Visual settings
        self.roi_color = AppConfig.ROI_COLOR
        self.handle_color = AppConfig.HANDLE_COLOR
        self.line_width = AppConfig.LINE_WIDTH
        self.dash_pattern = AppConfig.DASH_PATTERN
        self.handle_size = AppConfig.HANDLE_SIZE
        
        # Callbacks
        self.on_roi_changed: Optional[Callable] = None
        
        # Drag data
        self.drag_start = {"x": 0, "y": 0}
        
        # Create context menu
        self._create_context_menu()
        
    def set_roi_changed_callback(self, callback: Callable) -> None:
        """Set callback for when ROI changes"""
        self.on_roi_changed = callback
    
    def start_drawing_mode(self) -> None:
        """Enter ROI drawing mode"""
        self.clear_roi()
        self.is_drawing = True
        self.canvas.config(cursor=UIConfig.CURSOR_CROSS)
    
    def start_roi_drawing(self, screen_x: int, screen_y: int) -> None:
        """Start drawing ROI at given screen coordinates"""
        if not self.is_drawing:
            return
            
        img_x, img_y = self.image_processor.screen_to_image_coords(screen_x, screen_y)
        
        self.roi_coords = {
            "start_x": img_x,
            "start_y": img_y,
            "end_x": img_x,
            "end_y": img_y
        }
        
        self.drag_start = {"x": screen_x, "y": screen_y}
        self._draw_roi_rectangle()
    
    def handle_mouse_drag(self, event: tk.Event) -> bool:
        """Handle mouse drag events. Returns True if event was handled."""
        if self.is_drawing and self.roi_coords:
            self.update_roi_drawing(event.x, event.y)
            return True
        
        if self.active_handle:
            self._resize_roi(event)
            return True
        
        if self.is_dragging:
            self._move_roi(event)
            return True
        
        return False
    
    def update_roi_drawing(self, screen_x: int, screen_y: int) -> None:
        """Update ROI during drawing"""
        if not self.is_drawing or not self.roi_coords:
            return
            
        img_x, img_y = self.image_processor.screen_to_image_coords(screen_x, screen_y)
        
        self.roi_coords["end_x"] = img_x
        self.roi_coords["end_y"] = img_y
        
        self._draw_roi_rectangle()
        self._notify_roi_changed()
    
    def finish_roi_drawing(self) -> None:
        """Finish ROI drawing and enter edit mode"""
        if not self.roi_coords:
            return
            
        # Check if ROI is large enough
        width = abs(self.roi_coords["end_x"] - self.roi_coords["start_x"])
        height = abs(self.roi_coords["end_y"] - self.roi_coords["start_y"])
        
        if width < AppConfig.MIN_ROI_SIZE or height < AppConfig.MIN_ROI_SIZE:
            self.clear_roi()
            return
        
        self.is_drawing = False
        self.canvas.config(cursor=UIConfig.CURSOR_FLEUR)
        self._draw_resize_handles()
        self._notify_roi_changed()
    
    def handle_mouse_press(self, event: tk.Event) -> bool:
        """Handle mouse press events. Returns True if event was handled."""
        # Check if clicking on resize handle first
        item = self.canvas.find_closest(event.x, event.y)[0]
        tags = self.canvas.gettags(item) if item else []
        
        handle_tags = ["nw", "ne", "sw", "se"]
        for tag in tags:
            if tag in handle_tags:
                self.active_handle = tag
                self.drag_start = {"x": event.x, "y": event.y}
                self.canvas.config(cursor="crosshair")
                return True
        
        # Check if clicking on ROI rectangle
        if "roi" in tags and self.roi_coords:
            self.is_dragging = True
            self.drag_start = {"x": event.x, "y": event.y}
            self.canvas.config(cursor="fleur")
            return True
        
        # If in drawing mode, start new ROI
        if self.is_drawing:
            self.start_roi_drawing(event.x, event.y)
            return True
        
        return False
    
    def handle_mouse_release(self, event: tk.Event) -> bool:
        """Handle mouse release events. Returns True if event was handled."""
        if self.is_drawing:
            self.finish_roi_drawing()
            return True
        
        if self.active_handle:
            self.active_handle = None
            self.canvas.config(cursor="fleur")
            return True
        
        if self.is_dragging:
            self.is_dragging = False
            self.canvas.config(cursor="arrow")
            return True
        
        return False
    
    def _resize_roi(self, event: tk.Event) -> None:
        """Handle ROI resizing"""
        if not self.roi_coords or not self.active_handle:
            return
        
        # Calculate movement in image coordinates
        dx_screen = event.x - self.drag_start["x"]
        dy_screen = event.y - self.drag_start["y"]
        
        # Convert to image coordinates
        dx_img = dx_screen / self.image_processor.scale_factor
        dy_img = dy_screen / self.image_processor.scale_factor
        
        # Apply resize based on active handle
        if self.active_handle == "nw":
            self.roi_coords["start_x"] += dx_img
            self.roi_coords["start_y"] += dy_img
        elif self.active_handle == "ne":
            self.roi_coords["end_x"] += dx_img
            self.roi_coords["start_y"] += dy_img
        elif self.active_handle == "sw":
            self.roi_coords["start_x"] += dx_img
            self.roi_coords["end_y"] += dy_img
        elif self.active_handle == "se":
            self.roi_coords["end_x"] += dx_img
            self.roi_coords["end_y"] += dy_img
        
        self.drag_start = {"x": event.x, "y": event.y}
        self._draw_roi_rectangle()
        self._draw_resize_handles()
        self._notify_roi_changed()
    
    def _move_roi(self, event: tk.Event) -> None:
        """Handle ROI movement"""
        if not self.roi_coords:
            return
        
        # Calculate movement in image coordinates
        dx_screen = event.x - self.drag_start["x"]
        dy_screen = event.y - self.drag_start["y"]
        
        dx_img = dx_screen / self.image_processor.scale_factor
        dy_img = dy_screen / self.image_processor.scale_factor
        
        # Move all coordinates
        self.roi_coords["start_x"] += dx_img
        self.roi_coords["start_y"] += dy_img
        self.roi_coords["end_x"] += dx_img
        self.roi_coords["end_y"] += dy_img
        
        self.drag_start = {"x": event.x, "y": event.y}
        self._draw_roi_rectangle()
        self._draw_resize_handles()
    
    def _draw_roi_rectangle(self) -> None:
        """Draw the ROI rectangle on canvas"""
        if not self.roi_coords:
            return
        
        # Get screen coordinates
        x1, y1 = self.image_processor.image_to_screen_coords(
            self.roi_coords["start_x"], self.roi_coords["start_y"]
        )
        x2, y2 = self.image_processor.image_to_screen_coords(
            self.roi_coords["end_x"], self.roi_coords["end_y"]
        )
        
        # Update or create rectangle
        if self.roi_rect:
            self.canvas.coords(self.roi_rect, x1, y1, x2, y2)
        else:
            self.roi_rect = self.canvas.create_rectangle(
                x1, y1, x2, y2,
                outline=self.roi_color,
                width=self.line_width,
                dash=self.dash_pattern,
                tags="roi"
            )
    
    def _draw_resize_handles(self) -> None:
        """Draw resize handles at ROI corners"""
        self._clear_resize_handles()
        
        if not self.roi_coords:
            return
        
        # Get corner coordinates
        x1, y1 = self.image_processor.image_to_screen_coords(
            self.roi_coords["start_x"], self.roi_coords["start_y"]
        )
        x2, y2 = self.image_processor.image_to_screen_coords(
            self.roi_coords["end_x"], self.roi_coords["end_y"]
        )
        
        handles = {
            "nw": (x1, y1),
            "ne": (x2, y1),
            "sw": (x1, y2),
            "se": (x2, y2)
        }
        
        for tag, (x, y) in handles.items():
            handle = self.canvas.create_rectangle(
                x - self.handle_size, y - self.handle_size,
                x + self.handle_size, y + self.handle_size,
                fill=self.roi_color, outline="white",
                tags=("handle", tag)
            )
            self.resize_handles.append(handle)
    
    def _create_context_menu(self):
        """Create context menu for ROI operations"""
        self.context_menu = tk.Menu(self.canvas, tearoff=0)
        self.context_menu.add_command(label="Delete ROI", command=self.clear_roi)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Resize Mode", command=self._enable_resize_mode)
        self.context_menu.add_command(label="Move Mode", command=self._enable_move_mode)
        
        # Bind right-click to show context menu
        self.canvas.bind("<Button-3>", self._show_context_menu)
    
    def _show_context_menu(self, event):
        """Show context menu on right-click"""
        if self.roi_coords:
            try:
                self.context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.context_menu.grab_release()
    
    def _enable_resize_mode(self):
        """Enable resize mode with handles"""
        if self.roi_coords:
            self._draw_resize_handles()
            self.canvas.config(cursor="crosshair")
    
    def _enable_move_mode(self):
        """Enable move mode"""
        if self.roi_coords:
            self._clear_resize_handles()
            self.canvas.config(cursor="fleur")
    
    def _clear_resize_handles(self) -> None:
        """Clear all resize handles"""
        for handle in self.resize_handles:
            self.canvas.delete(handle)
        self.resize_handles = []
    
    def clear_roi(self) -> None:
        """Clear the entire ROI"""
        if self.roi_rect:
            self.canvas.delete(self.roi_rect)
            self.roi_rect = None
        
        self._clear_resize_handles()
        self.roi_coords = None
        self.is_drawing = False
        self.is_dragging = False
        self.active_handle = None
        
        if self.on_roi_changed:
            self.on_roi_changed()
    
    def get_roi_coordinates(self) -> Optional[Tuple[float, float, float, float]]:
        """Get ROI coordinates as (x1, y1, x2, y2)"""
        if not self.roi_coords:
            return None
        
        x1 = min(self.roi_coords["start_x"], self.roi_coords["end_x"])
        y1 = min(self.roi_coords["start_y"], self.roi_coords["end_y"])
        x2 = max(self.roi_coords["start_x"], self.roi_coords["end_x"])
        y2 = max(self.roi_coords["start_y"], self.roi_coords["end_y"])
        
        return (x1, y1, x2, y2)
    
    def get_roi_dimensions(self) -> Tuple[int, int]:
        """Get ROI dimensions as (width, height)"""
        coords = self.get_roi_coordinates()
        if not coords:
            return (0, 0)
        
        x1, y1, x2, y2 = coords
        return (int(x2 - x1), int(y2 - y1))
    
    def update_display(self) -> None:
        """Update ROI display after zoom/pan changes"""
        if self.roi_coords:
            self._draw_roi_rectangle()
            if not self.is_drawing:
                self._draw_resize_handles()
    
    def has_roi(self) -> bool:
        """Check if ROI is defined"""
        return self.roi_coords is not None
    
    def _notify_roi_changed(self) -> None:
        """Notify that ROI has changed"""
        if self.on_roi_changed:
            self.on_roi_changed()
