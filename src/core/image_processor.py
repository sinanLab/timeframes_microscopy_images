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
    
    def create_animation(self, export_folder: str, settings: dict) -> bool:
        """Create animation (GIF or video) from cropped images with custom settings"""
        if not self.cropped_images:
            messagebox.showerror("Error", "No cropped images available for animation.")
            return False
            
        try:
            os.makedirs(export_folder, exist_ok=True)
            
            # Build filename based on export type
            export_type = settings.get('export_type', 'gif')
            filename = settings.get('filename', 'animation')
            extension = ".gif" if export_type == 'gif' else ".mp4"
            
            # Generate unique filename if file exists
            base_path = os.path.join(export_folder, f"{filename}{extension}")
            output_path = self._get_unique_filename(base_path)
            
            # Validate and convert images to frames
            frames = []
            for i, img in enumerate(self.cropped_images):
                if img is None:
                    messagebox.showerror("Error", f"Image {i+1} is invalid (None). Please crop images again.")
                    return False
                try:
                    # Convert to RGB format for consistency
                    rgb_img = img.convert('RGB')
                    frame_array = np.array(rgb_img)
                    
                    # Validate frame dimensions and data type
                    if frame_array.size == 0:
                        messagebox.showerror("Error", f"Image {i+1} is empty.")
                        return False
                    
                    # Debug: print frame shape
                    print(f"Frame {i+1} shape: {frame_array.shape}, dtype: {frame_array.dtype}")
                    
                    # Ensure frame has correct dimensions (height, width, 3)
                    if len(frame_array.shape) != 3 or frame_array.shape[2] != 3:
                        messagebox.showerror("Error", f"Image {i+1} has invalid dimensions: {frame_array.shape}")
                        return False
                    
                    # Ensure uint8 data type and proper range
                    if frame_array.dtype != np.uint8:
                        # Convert to uint8 with proper scaling
                        if frame_array.max() <= 1.0:
                            frame_array = (frame_array * 255).astype(np.uint8)
                        else:
                            frame_array = frame_array.astype(np.uint8)
                    
                    # Ensure values are in valid range
                    frame_array = np.clip(frame_array, 0, 255)
                    
                    frames.append(frame_array)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to process image {i+1}: {str(e)}")
                    return False
            
            if not frames:
                messagebox.showerror("Error", "No valid frames to create animation.")
                return False
            
            # Debug info
            print(f"Creating {export_type} with {len(frames)} frames")
            if frames:
                print(f"Final frame shape: {frames[0].shape}, dtype: {frames[0].dtype}")
                print(f"Frame value range: {frames[0].min()} to {frames[0].max()}")
            
            if export_type == 'gif':
                # Create GIF with custom settings
                gif_kwargs = {
                    'duration': settings.get('duration_per_frame', 0.2),
                    'loop': settings.get('loop_count', 0)
                }
                
                if settings.get('optimize', True):
                    gif_kwargs['optimize'] = True
                    
                imageio.mimsave(output_path, frames, **gif_kwargs)
                
            elif export_type == 'video':
                # Create MP4 video with simpler approach
                fps = settings.get('fps', 5.0)
                
                # Method 1: Try basic imageio approach first
                try:
                    # Convert frames to a simple format that imageio can handle
                    simple_frames = []
                    for frame in frames:
                        # Ensure frame is in the right format
                        if frame.shape[2] == 3:  # RGB
                            simple_frames.append(frame)
                        else:
                            # Convert to RGB if needed
                            simple_frames.append(frame[:,:,:3])
                    
                    # Use basic imageio mimsave
                    imageio.mimsave(output_path, simple_frames, fps=fps, format='MP4')
                    print(f"Video created successfully: {output_path}")
                    
                except Exception as e1:
                    print(f"MP4 creation failed: {e1}")
                    
                    # Method 2: Try using FFMPEG writer directly
                    try:
                        writer = imageio.get_writer(output_path, fps=fps, format='FFMPEG', codec='libx264')
                        for frame in frames:
                            writer.append_data(frame)
                        writer.close()
                        print(f"Video created with FFMPEG writer: {output_path}")
                        
                    except Exception as e2:
                        print(f"FFMPEG writer failed: {e2}")
                        
                        # Method 3: Save as individual images and suggest GIF
                        temp_dir = os.path.join(export_folder, "temp_frames")
                        try:
                            os.makedirs(temp_dir, exist_ok=True)
                            
                            # Save frames as individual images
                            for i, frame in enumerate(frames):
                                frame_path = os.path.join(temp_dir, f"frame_{i:04d}.png")
                                Image.fromarray(frame).save(frame_path)
                            
                            messagebox.showinfo("Video Creation Alternative", 
                                f"Video creation failed, but {len(frames)} individual frames have been saved to:\\n"
                                f"{temp_dir}\\n\\n"
                                f"You can use external tools like FFmpeg to create a video from these frames.\\n\\n"
                                f"Alternatively, try using GIF format which works more reliably.")
                            
                        except Exception as e3:
                            messagebox.showerror("Video Creation Failed", 
                                f"All video creation methods failed:\\n"
                                f"MP4: {str(e1)}\\n"
                                f"FFMPEG: {str(e2)}\\n"
                                f"Frame export: {str(e3)}\\n\\n"
                                f"Please try using GIF format instead.")
                            return False
            
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create animation: {str(e)}")
            return False
    
    def _get_unique_filename(self, filepath: str) -> str:
        """Generate unique filename to avoid overwriting"""
        if not os.path.exists(filepath):
            return filepath
            
        directory = os.path.dirname(filepath)
        basename = os.path.basename(filepath)
        name, ext = os.path.splitext(basename)
        
        counter = 1
        while True:
            new_name = f"{name} ({counter}){ext}"
            new_path = os.path.join(directory, new_name)
            if not os.path.exists(new_path):
                return new_path
            counter += 1
    
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
