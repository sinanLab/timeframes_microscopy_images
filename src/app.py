"""
Main application controller that coordinates between GUI and core logic
"""

import tkinter as tk
from tkinter import messagebox
from typing import Optional

from src.gui.main_window import MainWindow
from src.core.image_processor import ImageProcessor
from src.core.roi_manager import ROIManager
from config.settings import AppConfig


class MicroscopyImageAnalyzer:
    """Main application controller"""
    
    def __init__(self):
        # Initialize components
        self.window = MainWindow()
        self.image_processor = ImageProcessor()
        self.roi_manager: Optional[ROIManager] = None
        
        # State variables
        self.pan_mode = False
        self.pan_start = {"x": 0, "y": 0}
        
        # Initialize after window is created
        self._initialize_components()
        self._connect_callbacks()
    
    def _initialize_components(self) -> None:
        """Initialize components that depend on GUI"""
        canvas = self.window.get_canvas()
        if canvas:
            self.roi_manager = ROIManager(canvas, self.image_processor)
            self.roi_manager.set_roi_changed_callback(self._on_roi_changed)
    
    def _connect_callbacks(self) -> None:
        """Connect GUI callbacks to handler methods"""
        # Path controls
        if self.window.path_controls:
            self.window.path_controls.on_input_folder_changed = self._on_input_folder_changed
            self.window.path_controls.on_export_folder_changed = self._on_export_folder_changed
        
        # Cell location controls
        if self.window.cell_controls:
            self.window.cell_controls.on_locate_cell = self._on_locate_cell
            self.window.cell_controls.on_toggle_crosshair = self._on_toggle_crosshair
        
        # ROI controls
        if self.window.roi_controls:
            self.window.roi_controls.on_draw_roi = self._on_draw_roi
        
        # Cropping controls
        if self.window.crop_controls:
            self.window.crop_controls.on_crop_all = self._on_crop_all
            self.window.crop_controls.on_save_images = self._on_save_images
            self.window.crop_controls.on_make_gif = self._on_make_gif
        
        # Image canvas events
        if self.window.image_canvas:
            self.window.image_canvas.on_mouse_motion = self._on_mouse_motion
            self.window.image_canvas.on_mouse_press = self._on_mouse_press
            self.window.image_canvas.on_mouse_drag = self._on_mouse_drag
            self.window.image_canvas.on_mouse_release = self._on_mouse_release
            self.window.image_canvas.on_mouse_wheel = self._on_mouse_wheel
        
        # Navigation controls
        if self.window.nav_controls:
            self.window.nav_controls.on_previous = self._on_previous_image
            self.window.nav_controls.on_next = self._on_next_image
            self.window.nav_controls.on_zoom_in = self._on_zoom_in
            self.window.nav_controls.on_zoom_out = self._on_zoom_out
            self.window.nav_controls.on_reset_view = self._on_reset_view
            self.window.nav_controls.on_toggle_pan = self._on_toggle_pan
        
        # Reset button
        if hasattr(self.window, 'reset_button'):
            self.window.reset_button.config(command=self._on_reset_everything)
    
    def _on_input_folder_changed(self, folder_path: str) -> None:
        """Handle input folder selection"""
        if self.image_processor.load_images_from_folder(folder_path):
            canvas = self.window.get_canvas()
            if canvas and self.image_processor.load_current_image(
                canvas.winfo_width() or AppConfig.CANVAS_WIDTH,
                canvas.winfo_height() or AppConfig.CANVAS_HEIGHT
            ):
                info = self.image_processor.get_image_info()
                self.window.update_status(
                    f"Loaded {info['total_images']} images", "success"
                )
                self._update_image_display()
                self._update_image_counter()
            else:
                self.window.update_status("Failed to load images", "error")
        else:
            self.window.update_status("No images found in folder", "error")
            messagebox.showwarning("No Images", "No images found in the selected folder.")
    
    def _on_export_folder_changed(self, folder_path: str) -> None:
        """Handle export folder selection"""
        # Just store the path, no immediate action needed
        pass
    
    def _on_locate_cell(self, x: int, y: int) -> None:
        """Handle cell location"""
        canvas = self.window.get_canvas()
        if canvas:
            self.image_processor.center_on_coordinates(
                x, y, 
                canvas.winfo_width() or AppConfig.CANVAS_WIDTH,
                canvas.winfo_height() or AppConfig.CANVAS_HEIGHT
            )
            self._update_image_display()
    
    def _on_toggle_crosshair(self) -> None:
        """Handle crosshair toggle"""
        show_crosshair = self.image_processor.toggle_crosshair()
        self._update_image_display()
        
        status = "shown" if show_crosshair else "hidden"
        self.window.update_status(f"Crosshair {status}", "success")
    
    def _on_draw_roi(self) -> None:
        """Handle ROI drawing request"""
        if not self.image_processor.original_image:
            messagebox.showwarning("No Image", "Please load an image first.")
            return
        
        if self.roi_manager:
            self.roi_manager.start_drawing_mode()
            messagebox.showinfo("ROI Drawing", "Click and drag to draw ROI rectangle.")
    
    def _on_crop_all(self) -> None:
        """Handle crop all images request"""
        if not self.roi_manager or not self.roi_manager.has_roi():
            messagebox.showwarning("Cannot Crop", "Please define an ROI first.")
            return
        
        if not self.image_processor.image_paths:
            messagebox.showwarning("Cannot Crop", "Please load images first.")
            return
        
        roi_coords = self.roi_manager.get_roi_coordinates()
        if roi_coords and self.image_processor.crop_all_images(roi_coords):
            width, height = self.roi_manager.get_roi_dimensions()
            info = self.image_processor.get_image_info()
            messagebox.showinfo(
                "Success", 
                f"All {info['total_images']} images cropped to ROI: {width}x{height} pixels"
            )
    
    def _on_save_images(self) -> None:
        """Handle save cropped images request"""
        export_folder = self.window.path_controls.get_export_folder() if self.window.path_controls else ""
        if not export_folder:
            messagebox.showwarning("No Folder", "Please select an export folder first.")
            return
        
        if self.image_processor.save_cropped_images(export_folder):
            info = self.image_processor.get_image_info()
            messagebox.showinfo(
                "Success", 
                f"Saved {info['cropped_count']} cropped images to:\\n{export_folder}"
            )
    
    def _on_make_gif(self) -> None:
        """Handle create GIF request"""
        export_folder = self.window.path_controls.get_export_folder() if self.window.path_controls else ""
        if not export_folder:
            messagebox.showwarning("No Folder", "Please select an export folder first.")
            return
        
        if self.image_processor.create_gif(export_folder):
            messagebox.showinfo("Success", f"GIF saved to:\\n{export_folder}")
    
    def _on_mouse_motion(self, event: tk.Event) -> None:
        """Handle mouse motion over canvas"""
        if self.image_processor.original_image and self.window.image_canvas:
            img_x, img_y = self.image_processor.screen_to_image_coords(event.x, event.y)
            self.window.image_canvas.update_coordinates(img_x, img_y)
    
    def _on_mouse_press(self, event: tk.Event) -> None:
        """Handle mouse press on canvas"""
        if self.pan_mode:
            # Handle pan mode - store initial position
            self.pan_start = {"x": event.x, "y": event.y}
        elif self.roi_manager:
            # Let ROI manager handle the event
            self.roi_manager.handle_mouse_press(event)
    
    def _on_mouse_drag(self, event: tk.Event) -> None:
        """Handle mouse drag on canvas"""
        if self.pan_mode:
            # Handle pan mode dragging
            if hasattr(self, 'pan_start'):
                dx = event.x - self.pan_start["x"]
                dy = event.y - self.pan_start["y"]
                
                self.image_processor.canvas_offset["x"] += dx
                self.image_processor.canvas_offset["y"] += dy
                
                self.pan_start = {"x": event.x, "y": event.y}
                self._update_image_display()
        elif self.roi_manager:
            # Let ROI manager handle the event
            self.roi_manager.handle_mouse_drag(event)
    
    def _on_mouse_release(self, event: tk.Event) -> None:
        """Handle mouse release on canvas"""
        if self.roi_manager:
            self.roi_manager.handle_mouse_release(event)
    
    def _on_mouse_wheel(self, event: tk.Event) -> None:
        """Handle mouse wheel for zooming"""
        if event.delta > 0:
            self._on_zoom_in_at_mouse(event.x, event.y)
        else:
            self._on_zoom_out_at_mouse(event.x, event.y)
    
    def _on_previous_image(self) -> None:
        """Handle previous image navigation"""
        canvas = self.window.get_canvas()
        if canvas and self.image_processor.previous_image():
            if self.image_processor.load_current_image(
                canvas.winfo_width() or AppConfig.CANVAS_WIDTH,
                canvas.winfo_height() or AppConfig.CANVAS_HEIGHT
            ):
                self._update_image_display()
                self._update_image_counter()
                
                # Re-center on cell if coordinates are set
                if self.image_processor.cell_coords["x"] != 0 or self.image_processor.cell_coords["y"] != 0:
                    self.image_processor.center_on_coordinates(
                        self.image_processor.cell_coords["x"], self.image_processor.cell_coords["y"],
                        canvas.winfo_width() or AppConfig.CANVAS_WIDTH,
                        canvas.winfo_height() or AppConfig.CANVAS_HEIGHT
                    )
                    self._update_image_display()
    
    def _on_next_image(self) -> None:
        """Handle next image navigation"""
        canvas = self.window.get_canvas()
        if canvas and self.image_processor.next_image():
            if self.image_processor.load_current_image(
                canvas.winfo_width() or AppConfig.CANVAS_WIDTH,
                canvas.winfo_height() or AppConfig.CANVAS_HEIGHT
            ):
                self._update_image_display()
                self._update_image_counter()
                
                # Re-center on cell if coordinates are set
                if self.image_processor.cell_coords["x"] != 0 or self.image_processor.cell_coords["y"] != 0:
                    self.image_processor.center_on_coordinates(
                        self.image_processor.cell_coords["x"], self.image_processor.cell_coords["y"],
                        canvas.winfo_width() or AppConfig.CANVAS_WIDTH,
                        canvas.winfo_height() or AppConfig.CANVAS_HEIGHT
                    )
                    self._update_image_display()
    
    def _on_zoom_in(self) -> None:
        """Handle zoom in button"""
        canvas = self.window.get_canvas()
        if canvas:
            # Zoom towards center
            center_x = canvas.winfo_width() // 2
            center_y = canvas.winfo_height() // 2
            self._on_zoom_in_at_mouse(center_x, center_y)
    
    def _on_zoom_out(self) -> None:
        """Handle zoom out button"""
        canvas = self.window.get_canvas()
        if canvas:
            # Zoom from center
            center_x = canvas.winfo_width() // 2
            center_y = canvas.winfo_height() // 2
            self._on_zoom_out_at_mouse(center_x, center_y)
    
    def _on_zoom_in_at_mouse(self, mouse_x: int, mouse_y: int) -> None:
        """Zoom in at specific mouse position"""
        self.image_processor.zoom_in(mouse_x, mouse_y)
        self._update_image_display()
    
    def _on_zoom_out_at_mouse(self, mouse_x: int, mouse_y: int) -> None:
        """Zoom out from specific mouse position"""
        self.image_processor.zoom_out(mouse_x, mouse_y)
        self._update_image_display()
    
    def _on_reset_view(self) -> None:
        """Handle reset view"""
        self.image_processor.reset_view()
        
        # Re-center on cell if coordinates are set
        if self.image_processor.cell_coords["x"] != 0 or self.image_processor.cell_coords["y"] != 0:
            canvas = self.window.get_canvas()
            if canvas:
                self.image_processor.center_on_coordinates(
                    self.image_processor.cell_coords["x"], self.image_processor.cell_coords["y"],
                    canvas.winfo_width() or AppConfig.CANVAS_WIDTH,
                    canvas.winfo_height() or AppConfig.CANVAS_HEIGHT
                )
        
        self._update_image_display()
    
    def _on_toggle_pan(self) -> None:
        """Handle pan mode toggle"""
        self.pan_mode = not self.pan_mode
        canvas = self.window.get_canvas()
        if canvas:
            cursor = "fleur" if self.pan_mode else "cross"
            canvas.config(cursor=cursor)
        
        if self.window.nav_controls:
            self.window.nav_controls.set_pan_mode(self.pan_mode)
    
    def _on_reset_everything(self) -> None:
        """Handle reset everything"""
        # Clear ROI
        if self.roi_manager:
            self.roi_manager.clear_roi()
        
        # Clear cell coordinates
        self.image_processor.cell_coords = {"x": 0, "y": 0}
        self.image_processor.show_crosshair = False
        if self.window.cell_controls:
            self.window.cell_controls.clear_coordinates()
        
        # Reset image processor
        self.image_processor.reset_all()
        
        # Reset view
        self.image_processor.reset_view()
        self._update_image_display()
        
        # Reset ROI dimensions display
        if self.window.roi_controls:
            self.window.roi_controls.reset_dimensions()
        
        messagebox.showinfo("Reset", "All settings have been reset except loaded images.")
    
    def _on_roi_changed(self) -> None:
        """Handle ROI change notification"""
        if self.roi_manager and self.window.roi_controls:
            width, height = self.roi_manager.get_roi_dimensions()
            self.window.roi_controls.update_dimensions(width, height)
    
    def _update_image_display(self) -> None:
        """Update the image display on canvas"""
        canvas = self.window.get_canvas()
        if not canvas:
            return
        
        # Get the resized image
        tk_image = self.image_processor.get_resized_image()
        if tk_image:
            # Clear canvas and draw image
            canvas.delete("all")
            canvas.create_image(
                self.image_processor.canvas_offset["x"],
                self.image_processor.canvas_offset["y"],
                anchor=tk.NW,
                image=tk_image
            )
            
            # Store reference to prevent garbage collection
            self.image_processor.tk_image = tk_image
            
            # Draw crosshair if cell coordinates are set
            self.image_processor.draw_crosshair(canvas)
            
            # Update ROI display
            if self.roi_manager:
                self.roi_manager.update_display()
    
    def _update_image_counter(self) -> None:
        """Update image counter display"""
        if self.window.image_canvas:
            info = self.image_processor.get_image_info()
            self.window.image_canvas.update_counter(
                info['current_index'] + 1, info['total_images']
            )
    
    def run(self) -> None:
        """Run the application"""
        self.window.run()


def main():
    """Main entry point"""
    app = MicroscopyImageAnalyzer()
    app.run()


if __name__ == "__main__":
    main()
