"""
Core image processing functionality for the Microscopy Image Analyzer
"""

import os
import glob
import numpy as np
import imageio
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox
from typing import List, Tuple, Optional, Dict, Any

from config.settings import AppConfig


class ImageProcessor:
    """Handles all image processing operations"""
    
    def __init__(self):
        self.image_paths: List[str] = []
        self.current_image_index: int = 0
        self.original_image: Optional[Image.Image] = None
        self.display_image: Optional[Image.Image] = None
        self.tk_image: Optional[ImageTk.PhotoImage] = None
        self.scale_factor: float = 1.0
        self.default_scale: Optional[float] = None
        self.canvas_offset: Dict[str, int] = {"x": 0, "y": 0}
        self.cropped_images: List[Image.Image] = []
        
        # Cell location and crosshair
        self.cell_coords: Dict[str, int] = {"x": 0, "y": 0}
        self.show_crosshair: bool = False
        self.crosshair_lines: List[int] = []
        
    def load_images_from_folder(self, folder_path: str) -> bool:
        """Load all supported images from a folder"""
        self.image_paths = []
        
        for ext in AppConfig.SUPPORTED_FORMATS:
            self.image_paths.extend(glob.glob(os.path.join(folder_path, ext)))
        
        if not self.image_paths:
            return False
            
        self.image_paths.sort()  # Sort for consistent ordering
        self.current_image_index = 0
        return True
    
    def load_current_image(self, canvas_width: int, canvas_height: int) -> bool:
        """Load the current image and calculate default scale"""
        if not self.image_paths:
            return False
            
        try:
            image_path = self.image_paths[self.current_image_index]
            self.original_image = Image.open(image_path)
            self.display_image = self.original_image.copy()
            
            # Calculate default scale to fit image to canvas
            img_w, img_h = self.original_image.size
            scale_w = canvas_width / img_w
            scale_h = canvas_height / img_h
            self.default_scale = min(scale_w, scale_h, 1.0)  # Don't scale up beyond 100%
            
            self.reset_view()
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
            return False
    
    def get_resized_image(self) -> Optional[ImageTk.PhotoImage]:
        """Get the current image resized according to scale factor"""
        if not self.display_image:
            return None
            
        try:
            width, height = self.display_image.size
            new_width = int(width * self.scale_factor)
            new_height = int(height * self.scale_factor)
            
            # Prevent excessive memory usage
            if new_width > AppConfig.MAX_IMAGE_SIZE or new_height > AppConfig.MAX_IMAGE_SIZE:
                self.scale_factor = min(
                    AppConfig.MAX_IMAGE_SIZE / width,
                    AppConfig.MAX_IMAGE_SIZE / height
                )
                new_width = int(width * self.scale_factor)
                new_height = int(height * self.scale_factor)
            
            resized_image = self.display_image.resize((new_width, new_height), Image.LANCZOS)
            return ImageTk.PhotoImage(resized_image)
            
        except Exception as e:
            print(f"Resize error: {str(e)}")
            return self.tk_image  # Return previous image if resize fails
    
    def zoom_in(self, mouse_x: int, mouse_y: int) -> None:
        """Zoom in towards mouse position"""
        if not self.display_image:
            return
            
        old_scale = self.scale_factor
        self.scale_factor = min(self.scale_factor * AppConfig.ZOOM_FACTOR, AppConfig.MAX_ZOOM)
        
        # Calculate new offset to zoom toward mouse position
        self.canvas_offset["x"] = mouse_x - (mouse_x - self.canvas_offset["x"]) * (self.scale_factor / old_scale)
        self.canvas_offset["y"] = mouse_y - (mouse_y - self.canvas_offset["y"]) * (self.scale_factor / old_scale)
    
    def zoom_out(self, mouse_x: int, mouse_y: int) -> None:
        """Zoom out from mouse position"""
        if not self.display_image:
            return
            
        old_scale = self.scale_factor
        self.scale_factor = max(self.scale_factor / AppConfig.ZOOM_FACTOR, AppConfig.MIN_ZOOM)
        
        # Don't go below default scale
        if self.default_scale and self.scale_factor < self.default_scale:
            self.scale_factor = self.default_scale
            self.reset_view()
            return
        
        # Calculate new offset
        self.canvas_offset["x"] = mouse_x - (mouse_x - self.canvas_offset["x"]) * (self.scale_factor / old_scale)
        self.canvas_offset["y"] = mouse_y - (mouse_y - self.canvas_offset["y"]) * (self.scale_factor / old_scale)
    
    def reset_view(self) -> None:
        """Reset view to default scale and position"""
        if not self.display_image or not self.default_scale:
            return
            
        self.scale_factor = self.default_scale
        self.canvas_offset = {"x": 0, "y": 0}
    
    def set_cell_coordinates(self, x: int, y: int) -> None:
        """Set cell coordinates and show crosshair"""
        self.cell_coords = {"x": x, "y": y}
        self.show_crosshair = True
    
    def toggle_crosshair(self) -> bool:
        """Toggle crosshair visibility"""
        self.show_crosshair = not self.show_crosshair
        return self.show_crosshair
    
    def draw_crosshair(self, canvas: tk.Canvas) -> None:
        """Draw crosshair lines at cell coordinates"""
        # Clear existing crosshair
        for line_id in self.crosshair_lines:
            canvas.delete(line_id)
        self.crosshair_lines.clear()
        
        if not self.show_crosshair or not self.original_image:
            return
        
        # Get screen coordinates of cell
        screen_x, screen_y = self.image_to_screen_coords(
            self.cell_coords["x"], self.cell_coords["y"]
        )
        
        # Get canvas dimensions
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        
        # Draw vertical line
        v_line = canvas.create_line(
            screen_x, 0, screen_x, canvas_height,
            fill="red", width=2, dash=(5, 5), tags="crosshair"
        )
        self.crosshair_lines.append(v_line)
        
        # Draw horizontal line
        h_line = canvas.create_line(
            0, screen_y, canvas_width, screen_y,
            fill="red", width=2, dash=(5, 5), tags="crosshair"
        )
        self.crosshair_lines.append(h_line)
        
        # Draw center point
        center_point = canvas.create_oval(
            screen_x - 3, screen_y - 3, screen_x + 3, screen_y + 3,
            fill="red", outline="white", width=2, tags="crosshair"
        )
        self.crosshair_lines.append(center_point)
    
    def center_on_coordinates(self, x: int, y: int, canvas_width: int, canvas_height: int) -> None:
        """Center view on specific image coordinates"""
        if not self.original_image:
            return
            
        self.set_cell_coordinates(x, y)
        target_x = x * self.scale_factor
        target_y = y * self.scale_factor
        
        self.canvas_offset["x"] = (canvas_width // 2) - target_x
        self.canvas_offset["y"] = (canvas_height // 2) - target_y
    
    def screen_to_image_coords(self, screen_x: int, screen_y: int) -> Tuple[int, int]:
        """Convert screen coordinates to image coordinates"""
        img_x = (screen_x - self.canvas_offset["x"]) / self.scale_factor
        img_y = (screen_y - self.canvas_offset["y"]) / self.scale_factor
        return int(img_x), int(img_y)
    
    def image_to_screen_coords(self, img_x: float, img_y: float) -> Tuple[int, int]:
        """Convert image coordinates to screen coordinates"""
        screen_x = img_x * self.scale_factor + self.canvas_offset["x"]
        screen_y = img_y * self.scale_factor + self.canvas_offset["y"]
        return int(screen_x), int(screen_y)
    
    def navigate_to_image(self, index: int) -> bool:
        """Navigate to specific image by index"""
        if not self.image_paths or index < 0 or index >= len(self.image_paths):
            return False
            
        self.current_image_index = index
        return True
    
    def next_image(self) -> bool:
        """Navigate to next image"""
        if not self.image_paths:
            return False
            
        next_index = (self.current_image_index + 1) % len(self.image_paths)
        return self.navigate_to_image(next_index)
    
    def previous_image(self) -> bool:
        """Navigate to previous image"""
        if not self.image_paths:
            return False
            
        prev_index = (self.current_image_index - 1) % len(self.image_paths)
        return self.navigate_to_image(prev_index)
    
    def crop_all_images(self, roi_coords: Tuple[float, float, float, float]) -> bool:
        """Crop all loaded images using ROI coordinates"""
        if not self.image_paths:
            return False
            
        x1, y1, x2, y2 = roi_coords
        self.cropped_images = []
        
        try:
            for img_path in self.image_paths:
                with Image.open(img_path) as img:
                    cropped_img = img.crop((x1, y1, x2, y2))
                    self.cropped_images.append(cropped_img.copy())
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to crop images: {str(e)}")
            self.cropped_images = []
            return False
    
    def save_cropped_images(self, export_folder: str) -> bool:
        """Save all cropped images to export folder"""
        if not self.cropped_images:
            return False
            
        try:
            os.makedirs(export_folder, exist_ok=True)
            
            for i, img in enumerate(self.cropped_images):
                base_name = os.path.basename(self.image_paths[i])
                name, ext = os.path.splitext(base_name)
                output_path = os.path.join(export_folder, f"{name}_cropped{ext}")
                img.save(output_path)
            
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save images: {str(e)}")
            return False
    
    def create_gif(self, export_folder: str, filename: str = "output.gif") -> bool:
        """Create animated GIF from cropped images"""
        if not self.cropped_images:
            return False
            
        try:
            os.makedirs(export_folder, exist_ok=True)
            output_path = os.path.join(export_folder, filename)
            
            frames = [np.array(img.convert('RGB')) for img in self.cropped_images]
            imageio.mimsave(output_path, frames, duration=AppConfig.GIF_DURATION)
            
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create GIF: {str(e)}")
            return False
    
    def get_image_info(self) -> Dict[str, Any]:
        """Get information about current image and loaded images"""
        info = {
            'total_images': len(self.image_paths),
            'current_index': self.current_image_index,
            'current_image_path': self.image_paths[self.current_image_index] if self.image_paths else None,
            'image_size': self.original_image.size if self.original_image else None,
            'scale_factor': self.scale_factor,
            'cropped_count': len(self.cropped_images)
        }
        return info
    
    def reset_all(self) -> None:
        """Reset all processing state"""
        self.cropped_images = []
        self.reset_view()
