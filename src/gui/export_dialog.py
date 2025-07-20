"""
Comprehensive Export Dialog for Images, GIFs, and Videos
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from typing import Dict, Any, Optional, Callable
from config.settings import AppConfig, UIConfig


class ExportDialog:
    """Professional dialog for all export options"""
    
    def __init__(self, parent: tk.Widget, default_folder: str = ""):
        self.parent = parent
        self.default_folder = default_folder or os.getcwd()
        self.result: Optional[Dict[str, Any]] = None
        
        # Default settings
        self.settings = {
            'export_type': 'images',  # 'images', 'gif', or 'video'
            'export_folder': self.default_folder,
            'filename': 'export',
            'fps': 5.0,
            'duration_per_frame': 0.2,
            'video_codec': 'mp4v',
            'video_quality': 'high',
            'loop_count': 0,  # 0 = infinite loop
            'optimize': True
        }
        
        self._create_dialog()
        
    def _create_dialog(self) -> None:
        """Create the dialog window"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("🚀 Export Options")
        self.dialog.geometry("800x600")  # Wider for two-column layout
        self.dialog.resizable(True, True)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Set minimum size
        self.dialog.minsize(750, 500)
        
        # Center the dialog
        self._center_dialog()
        
        # Create the main content with two columns
        main_frame = ttk.Frame(self.dialog, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create two-column layout
        self._create_two_column_layout(main_frame)
        
        # Bind events
        self._bind_events()
        
        # Focus on dialog
        self.dialog.focus_set()
        
        # Update initial display
        self._on_export_type_change()
        
    def _center_dialog(self) -> None:
        """Center the dialog on parent window"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (600 // 2)
        self.dialog.geometry(f"800x600+{x}+{y}")
        
    def _create_two_column_layout(self, parent: ttk.Frame) -> None:
        """Create two-column layout for better organization"""
        # Create left and right columns
        left_column = ttk.Frame(parent, padding="5")
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        right_column = ttk.Frame(parent, padding="5")
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Left column: Basic settings
        self._create_export_type_section(left_column)
        self._create_folder_section(left_column)
        self._create_filename_section(left_column)
        
        # Right column: Advanced settings and preview
        self._create_animation_settings_section(right_column)
        self._create_preview_section(right_column)
        
        # Add some spacing before buttons
        spacer = ttk.Frame(right_column)
        spacer.pack(fill=tk.X, pady=20)
        
        # Export buttons in right column
        self._create_export_buttons(right_column)
        
    def _create_export_type_section(self, parent: ttk.Frame) -> None:
        """Create export type selection section"""
        type_frame = ttk.LabelFrame(parent, text="📦 Export Type", padding="10")
        type_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.export_type_var = tk.StringVar(value=self.settings['export_type'])
        
        # Images option
        images_radio = ttk.Radiobutton(
            type_frame, 
            text="💾 Save Cropped Images", 
            variable=self.export_type_var, 
            value="images",
            command=self._on_export_type_change
        )
        images_radio.pack(anchor=tk.W, pady=2)
        
        images_desc = ttk.Label(
            type_frame, 
            text="• Export individual cropped images as PNG/JPEG files\n• Perfect for manuscripts and publications",
            font=("TkDefaultFont", 8),
            foreground="gray"
        )
        images_desc.pack(anchor=tk.W, padx=20, pady=(0, 5))
        
        # GIF option
        gif_radio = ttk.Radiobutton(
            type_frame, 
            text="🎞️ Create Animated GIF", 
            variable=self.export_type_var, 
            value="gif",
            command=self._on_export_type_change
        )
        gif_radio.pack(anchor=tk.W, pady=2)
        
        gif_desc = ttk.Label(
            type_frame, 
            text="• Best for simple animations and web sharing\n• Smaller file size, universal compatibility",
            font=("TkDefaultFont", 8),
            foreground="gray"
        )
        gif_desc.pack(anchor=tk.W, padx=20, pady=(0, 5))
        
        # Video option
        video_radio = ttk.Radiobutton(
            type_frame, 
            text="🎬 Create MP4 Video", 
            variable=self.export_type_var, 
            value="video",
            command=self._on_export_type_change
        )
        video_radio.pack(anchor=tk.W, pady=2)
        
        video_desc = ttk.Label(
            type_frame, 
            text="• Better quality for complex animations\n• Higher frame rates, professional presentations",
            font=("TkDefaultFont", 8),
            foreground="gray"
        )
        video_desc.pack(anchor=tk.W, padx=20)
        
    def _create_folder_section(self, parent: ttk.Frame) -> None:
        """Create export folder selection section"""
        folder_frame = ttk.LabelFrame(parent, text="📁 Export Location", padding="10")
        folder_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Folder selection
        folder_select_frame = ttk.Frame(folder_frame)
        folder_select_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(folder_select_frame, text="Save to:").pack(side=tk.LEFT)
        
        self.folder_var = tk.StringVar(value=self.settings['export_folder'])
        folder_entry = ttk.Entry(folder_select_frame, textvariable=self.folder_var, state="readonly")
        folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 5))
        
        browse_folder_btn = ttk.Button(
            folder_select_frame,
            text="Browse...",
            command=self._browse_folder,
            width=10
        )
        browse_folder_btn.pack(side=tk.RIGHT)
        
    def _create_filename_section(self, parent: ttk.Frame) -> None:
        """Create filename section"""
        filename_frame = ttk.LabelFrame(parent, text="📝 File Naming", padding="10")
        filename_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Filename entry
        name_frame = ttk.Frame(filename_frame)
        name_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(name_frame, text="Base filename:").pack(side=tk.LEFT)
        self.filename_var = tk.StringVar(value=self.settings['filename'])
        filename_entry = ttk.Entry(name_frame, textvariable=self.filename_var, width=20)
        filename_entry.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Preview of final filename
        preview_frame = ttk.Frame(filename_frame)
        preview_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(preview_frame, text="Will be saved as:").pack(side=tk.LEFT)
        self.filename_preview_label = ttk.Label(preview_frame, text="", font=("TkDefaultFont", 9, "bold"))
        self.filename_preview_label.pack(side=tk.RIGHT)
        
    def _create_animation_settings_section(self, parent: ttk.Frame) -> None:
        """Create animation-specific settings section"""
        self.animation_frame = ttk.LabelFrame(parent, text="🎨 Animation Settings", padding="10")
        self.animation_frame.pack(fill=tk.X, pady=(0, 10))
        
        # FPS control
        fps_frame = ttk.Frame(self.animation_frame)
        fps_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(fps_frame, text="Frames per Second (FPS):").pack(side=tk.LEFT)
        self.fps_var = tk.DoubleVar(value=self.settings['fps'])
        self.fps_scale = ttk.Scale(
            fps_frame, 
            from_=1.0, 
            to=30.0, 
            variable=self.fps_var,
            orient=tk.HORIZONTAL,
            command=self._on_fps_change
        )
        self.fps_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        
        self.fps_label = ttk.Label(fps_frame, text=f"{self.settings['fps']:.1f}")
        self.fps_label.pack(side=tk.RIGHT, padx=(5, 10))
        
        # Duration per frame (calculated)
        duration_frame = ttk.Frame(self.animation_frame)
        duration_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(duration_frame, text="Duration per frame:").pack(side=tk.LEFT)
        self.duration_label = ttk.Label(duration_frame, text=f"{self.settings['duration_per_frame']:.2f}s")
        self.duration_label.pack(side=tk.RIGHT)
        
        # Preset buttons
        preset_frame = ttk.Frame(self.animation_frame)
        preset_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(preset_frame, text="Presets:").pack(side=tk.LEFT)
        
        presets = [
            ("Slow", 2.0),
            ("Normal", 5.0),
            ("Fast", 10.0),
            ("Very Fast", 20.0)
        ]
        
        for name, fps in presets:
            btn = ttk.Button(
                preset_frame, 
                text=name, 
                width=8,
                command=lambda f=fps: self._set_fps_preset(f)
            )
            btn.pack(side=tk.RIGHT, padx=2)
            
        # Advanced options frame
        self.advanced_frame = ttk.Frame(self.animation_frame)
        self.advanced_frame.pack(fill=tk.X, pady=(10, 0))
        
        # GIF-specific options
        self.gif_options_frame = ttk.Frame(self.advanced_frame)
        
        # Loop count
        loop_frame = ttk.Frame(self.gif_options_frame)
        loop_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(loop_frame, text="Loop count:").pack(side=tk.LEFT)
        self.loop_var = tk.IntVar(value=self.settings['loop_count'])
        loop_spinbox = ttk.Spinbox(
            loop_frame, 
            from_=0, 
            to=100, 
            textvariable=self.loop_var,
            width=10
        )
        loop_spinbox.pack(side=tk.RIGHT)
        
        loop_desc = ttk.Label(
            self.gif_options_frame, 
            text="(0 = infinite loop)",
            font=("TkDefaultFont", 8),
            foreground="gray"
        )
        loop_desc.pack(anchor=tk.W, pady=(0, 5))
        
        # Optimization
        self.optimize_var = tk.BooleanVar(value=self.settings['optimize'])
        optimize_check = ttk.Checkbutton(
            self.gif_options_frame,
            text="Optimize file size",
            variable=self.optimize_var
        )
        optimize_check.pack(anchor=tk.W, pady=2)
        
        # Video-specific options
        self.video_options_frame = ttk.Frame(self.advanced_frame)
        
        # Video info note
        info_label = ttk.Label(
            self.video_options_frame,
            text="📹 MP4 video will be created with the specified frame rate",
            font=("TkDefaultFont", 9),
            foreground="gray"
        )
        info_label.pack(anchor=tk.W, pady=5)
        
    def _create_preview_section(self, parent: ttk.Frame) -> None:
        """Create preview information section"""
        preview_frame = ttk.LabelFrame(parent, text="👁️ Export Preview", padding="10")
        preview_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.preview_text = tk.Text(
            preview_frame, 
            height=4,  # Reduced height for two-column layout
            wrap=tk.WORD,
            font=("TkDefaultFont", 9),
            state=tk.DISABLED,
            background="#f0f0f0"
        )
        self.preview_text.pack(fill=tk.X)
        
    def _create_export_buttons(self, parent: ttk.Frame) -> None:
        """Create export dialog buttons"""
        button_frame = ttk.LabelFrame(parent, text="🚀 Actions", padding="15")
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Export button (prominent, full width)
        self.export_btn = ttk.Button(
            button_frame,
            text="🚀 Start Export",
            command=self._on_export,
            style='Accent.TButton'
        )
        self.export_btn.pack(fill=tk.X, pady=(0, 10))
        
        # Cancel button (smaller, right aligned)
        cancel_btn = ttk.Button(
            button_frame,
            text="❌ Cancel",
            command=self._on_cancel
        )
        cancel_btn.pack(side=tk.RIGHT)
        
    def _bind_events(self) -> None:
        """Bind dialog events"""
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.filename_var.trace_add("write", self._on_filename_change)
        self.folder_var.trace_add("write", self._on_folder_change)
        
    def _on_export_type_change(self) -> None:
        """Handle export type selection change"""
        self.settings['export_type'] = self.export_type_var.get()
        
        # Show/hide animation settings based on type
        if self.settings['export_type'] == 'images':
            self.animation_frame.pack_forget()
        else:
            self.animation_frame.pack(fill=tk.X, pady=(0, 10))
            
        # Update advanced options visibility
        self._update_advanced_options()
        self._update_preview()
        
    def _update_advanced_options(self) -> None:
        """Update visibility of advanced options based on format"""
        if self.settings['export_type'] == 'gif':
            self.gif_options_frame.pack(fill=tk.X)
            self.video_options_frame.pack_forget()
        elif self.settings['export_type'] == 'video':
            self.video_options_frame.pack(fill=tk.X)
            self.gif_options_frame.pack_forget()
        else:
            self.gif_options_frame.pack_forget()
            self.video_options_frame.pack_forget()
            
    def _on_fps_change(self, value: str) -> None:
        """Handle FPS change"""
        fps = float(value)
        self.settings['fps'] = fps
        self.settings['duration_per_frame'] = 1.0 / fps
        
        self.fps_label.config(text=f"{fps:.1f}")
        self.duration_label.config(text=f"{self.settings['duration_per_frame']:.2f}s")
        self._update_preview()
        
    def _set_fps_preset(self, fps: float) -> None:
        """Set FPS to preset value"""
        self.fps_var.set(fps)
        self._on_fps_change(str(fps))
        
    def _on_filename_change(self, *args) -> None:
        """Handle filename change"""
        self.settings['filename'] = self.filename_var.get()
        self._update_preview()
        
    def _on_folder_change(self, *args) -> None:
        """Handle folder change"""
        self.settings['export_folder'] = self.folder_var.get()
        self._update_preview()
        
    def _browse_folder(self) -> None:
        """Handle browse folder button"""
        folder = filedialog.askdirectory(
            title="Select Export Folder",
            initialdir=self.settings['export_folder']
        )
        if folder:
            self.folder_var.set(folder)
            
    def _update_preview(self) -> None:
        """Update preview information"""
        export_type = self.settings['export_type']
        filename = self.settings['filename'] or "export"
        
        # Update filename preview
        if export_type == 'images':
            preview_name = f"{filename}_001.png, {filename}_002.png, ..."
        elif export_type == 'gif':
            preview_name = f"{filename}.gif"
        else:  # video
            preview_name = f"{filename}.mp4"
            
        self.filename_preview_label.config(text=preview_name)
        
        # Build preview text
        if export_type == 'images':
            preview_text = "📸 Export Type: Individual Images\\n"
            preview_text += f"📁 Location: {self.settings['export_folder']}\\n"
            preview_text += "✅ Ready to save cropped images as PNG files"
        else:
            preview_text = f"🎬 Export Type: {export_type.upper()}\\n"
            preview_text += f"⚡ Frame rate: {self.settings['fps']:.1f} FPS\\n"
            preview_text += f"📁 Location: {self.settings['export_folder']}"
        
        # Update preview text widget
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(1.0, preview_text)
        self.preview_text.config(state=tk.DISABLED)
        
    def _on_export(self) -> None:
        """Handle export button"""
        # Validate settings
        if not self.settings['filename'].strip():
            messagebox.showwarning("Invalid Filename", "Please enter a valid filename.")
            return
            
        if not self.settings['export_folder']:
            messagebox.showwarning("No Folder", "Please select an export folder.")
            return
            
        # Update settings from UI
        if self.settings['export_type'] in ['gif', 'video']:
            self.settings['loop_count'] = self.loop_var.get()
            self.settings['optimize'] = self.optimize_var.get()
                
        # Change button text to show progress
        original_text = self.export_btn.cget("text")
        self.export_btn.config(text="⏳ Exporting...", state="disabled")
        self.dialog.update()
        
        # Prepare result
        self.result = self.settings.copy()
        
        # Small delay to show the progress state
        self.dialog.after(100, self._finish_export)
        
    def _finish_export(self) -> None:
        """Finish the export process"""
        self.dialog.destroy()
        
    def _on_cancel(self) -> None:
        """Handle cancel button"""
        self.result = None
        self.dialog.destroy()
        
    def show(self) -> Optional[Dict[str, Any]]:
        """Show dialog and return result"""
        self.dialog.wait_window()
        return self.result


def show_export_dialog(parent: tk.Widget, default_folder: str = "") -> Optional[Dict[str, Any]]:
    """Convenience function to show export dialog"""
    dialog = ExportDialog(parent, default_folder)
    return dialog.show()
