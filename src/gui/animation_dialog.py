"""
Animation Export Dialog for creating GIFs and Videos
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from typing import Dict, Any, Optional, Callable
from config.settings import AppConfig, UIConfig


class AnimationExportDialog:
    """Professional dialog for configuring animation export settings"""
    
    def __init__(self, parent: tk.Widget, export_folder: str):
        self.parent = parent
        self.export_folder = export_folder
        self.result: Optional[Dict[str, Any]] = None
        
        # Default settings
        self.settings = {
            'format': 'gif',  # 'gif' or 'video'
            'fps': 5.0,
            'duration_per_frame': 0.2,
            'filename': 'animation',
            'video_codec': 'mp4v',
            'video_quality': 'high',
            'loop_count': 0,  # 0 = infinite loop
            'optimize': True
        }
        
        self._create_dialog()
        
    def _create_dialog(self) -> None:
        """Create the dialog window"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Animation Export Settings")
        self.dialog.geometry("450x650")  # Increased height to 650
        self.dialog.resizable(True, True)  # Make it resizable
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Set minimum size to ensure content is always visible
        self.dialog.minsize(450, 550)
        
        # Center the dialog
        self._center_dialog()
        
        # Create the main frame with scrollbar support
        main_frame = ttk.Frame(self.dialog, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        self._create_format_section(main_frame)
        self._create_timing_section(main_frame)
        self._create_output_section(main_frame)
        self._create_advanced_section(main_frame)
        self._create_preview_section(main_frame)
        
        # Create a separate frame for buttons to keep them at bottom
        button_container = ttk.Frame(self.dialog)
        button_container.pack(fill=tk.X, side=tk.BOTTOM, padx=15, pady=10)
        self._create_buttons(button_container)
        
        # Bind events
        self._bind_events()
        
        # Focus on dialog
        self.dialog.focus_set()
        
    def _center_dialog(self) -> None:
        """Center the dialog on parent window"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (650 // 2)  # Updated for new height
        self.dialog.geometry(f"450x650+{x}+{y}")
        
    def _create_format_section(self, parent: ttk.Frame) -> None:
        """Create format selection section"""
        format_frame = ttk.LabelFrame(parent, text="Export Format", padding="10")
        format_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.format_var = tk.StringVar(value=self.settings['format'])
        
        # GIF option
        gif_radio = ttk.Radiobutton(
            format_frame, 
            text="Animated GIF", 
            variable=self.format_var, 
            value="gif",
            command=self._on_format_change
        )
        gif_radio.pack(anchor=tk.W, pady=2)
        
        gif_desc = ttk.Label(
            format_frame, 
            text="• Best for simple animations and web sharing\n• Smaller file size, universal compatibility",
            font=("TkDefaultFont", 8),
            foreground="gray"
        )
        gif_desc.pack(anchor=tk.W, padx=20, pady=(0, 5))
        
        # Video option
        video_radio = ttk.Radiobutton(
            format_frame, 
            text="MP4 Video", 
            variable=self.format_var, 
            value="video",
            command=self._on_format_change
        )
        video_radio.pack(anchor=tk.W, pady=2)
        
        video_desc = ttk.Label(
            format_frame, 
            text="• Better quality for complex animations\n• Higher frame rates, professional presentations",
            font=("TkDefaultFont", 8),
            foreground="gray"
        )
        video_desc.pack(anchor=tk.W, padx=20)
        
    def _create_timing_section(self, parent: ttk.Frame) -> None:
        """Create timing controls section"""
        timing_frame = ttk.LabelFrame(parent, text="Timing Settings", padding="10")
        timing_frame.pack(fill=tk.X, pady=(0, 10))
        
        # FPS control
        fps_frame = ttk.Frame(timing_frame)
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
        duration_frame = ttk.Frame(timing_frame)
        duration_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(duration_frame, text="Duration per frame:").pack(side=tk.LEFT)
        self.duration_label = ttk.Label(duration_frame, text=f"{self.settings['duration_per_frame']:.2f}s")
        self.duration_label.pack(side=tk.RIGHT)
        
        # Preset buttons
        preset_frame = ttk.Frame(timing_frame)
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
            
    def _create_output_section(self, parent: ttk.Frame) -> None:
        """Create output settings section"""
        output_frame = ttk.LabelFrame(parent, text="Output Settings", padding="10")
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Filename
        filename_frame = ttk.Frame(output_frame)
        filename_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(filename_frame, text="Filename:").pack(side=tk.LEFT)
        self.filename_var = tk.StringVar(value=self.settings['filename'])
        filename_entry = ttk.Entry(filename_frame, textvariable=self.filename_var, width=20)
        filename_entry.pack(side=tk.RIGHT, padx=(10, 0))
        
        # File extension (auto-updated)
        ext_frame = ttk.Frame(output_frame)
        ext_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(ext_frame, text="Will be saved as:").pack(side=tk.LEFT)
        self.extension_label = ttk.Label(ext_frame, text="animation.gif", font=("TkDefaultFont", 9, "bold"))
        self.extension_label.pack(side=tk.RIGHT)
        
    def _create_advanced_section(self, parent: ttk.Frame) -> None:
        """Create advanced options section"""
        self.advanced_frame = ttk.LabelFrame(parent, text="Advanced Options", padding="10")
        self.advanced_frame.pack(fill=tk.X, pady=(0, 10))
        
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
        
        # Quality
        quality_frame = ttk.Frame(self.video_options_frame)
        quality_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(quality_frame, text="Quality:").pack(side=tk.LEFT)
        self.quality_var = tk.StringVar(value=self.settings['video_quality'])
        quality_combo = ttk.Combobox(
            quality_frame,
            textvariable=self.quality_var,
            values=["low", "medium", "high", "best"],
            state="readonly",
            width=15
        )
        quality_combo.pack(side=tk.RIGHT)
        
        # Update visibility based on current format
        self._update_advanced_options()
        
    def _create_preview_section(self, parent: ttk.Frame) -> None:
        """Create preview information section"""
        preview_frame = ttk.LabelFrame(parent, text="Preview", padding="10")
        preview_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.preview_text = tk.Text(
            preview_frame, 
            height=3,  # Reduced from 4 to 3
            wrap=tk.WORD,
            font=("TkDefaultFont", 9),
            state=tk.DISABLED,
            background="#f0f0f0"
        )
        self.preview_text.pack(fill=tk.X)
        
        self._update_preview()
        
    def _create_buttons(self, parent: ttk.Frame) -> None:
        """Create dialog buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X)
        
        # Browse folder button (left side)
        browse_btn = ttk.Button(
            button_frame,
            text="📁 Browse Folder...",
            command=self._on_browse_folder,
            width=16
        )
        browse_btn.pack(side=tk.LEFT)
        
        # Cancel button (right side)
        cancel_btn = ttk.Button(
            button_frame,
            text="Cancel",
            command=self._on_cancel,
            width=12
        )
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Export button (right side, prominent)
        self.export_btn = ttk.Button(
            button_frame,
            text="🎬 Export Animation",
            command=self._on_export,
            width=18
        )
        self.export_btn.pack(side=tk.RIGHT)
        
    def _bind_events(self) -> None:
        """Bind dialog events"""
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.filename_var.trace_add("write", self._on_filename_change)
        
    def _on_format_change(self) -> None:
        """Handle format selection change"""
        self.settings['format'] = self.format_var.get()
        self._update_advanced_options()
        self._update_preview()
        
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
        
    def _update_advanced_options(self) -> None:
        """Update visibility of advanced options based on format"""
        if self.settings['format'] == 'gif':
            self.gif_options_frame.pack(fill=tk.X)
            self.video_options_frame.pack_forget()
        else:
            self.video_options_frame.pack(fill=tk.X)
            self.gif_options_frame.pack_forget()
            
    def _update_preview(self) -> None:
        """Update preview information"""
        format_type = self.settings['format']
        filename = self.settings['filename'] or "animation"
        extension = ".gif" if format_type == 'gif' else ".mp4"
        
        # Update extension label
        self.extension_label.config(text=f"{filename}{extension}")
        
        # Check for existing files and suggest naming
        full_path = os.path.join(self.export_folder, f"{filename}{extension}")
        suggested_name = self._get_unique_filename(full_path)
        
        # Build preview text
        preview_text = f"📁 Export Format: {format_type.upper()}\n"
        preview_text += f"⚡ Frame rate: {self.settings['fps']:.1f} FPS\n"
        preview_text += f"⏱️ Duration per frame: {self.settings['duration_per_frame']:.2f}s\n"
        
        if suggested_name != f"{filename}{extension}":
            preview_text += f"\n💡 Note: File will be saved as '{suggested_name}' to avoid overwriting existing file."
        else:
            preview_text += f"\n✅ Ready to export as '{suggested_name}'"
        
        # Update preview text widget
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(1.0, preview_text)
        self.preview_text.config(state=tk.DISABLED)
        
    def _get_unique_filename(self, filepath: str) -> str:
        """Generate unique filename to avoid overwriting"""
        if not os.path.exists(filepath):
            return os.path.basename(filepath)
            
        directory = os.path.dirname(filepath)
        basename = os.path.basename(filepath)
        name, ext = os.path.splitext(basename)
        
        counter = 1
        while True:
            new_name = f"{name} ({counter}){ext}"
            new_path = os.path.join(directory, new_name)
            if not os.path.exists(new_path):
                return new_name
            counter += 1
            
    def _on_browse_folder(self) -> None:
        """Handle browse folder button"""
        folder = filedialog.askdirectory(
            title="Select Export Folder",
            initialdir=self.export_folder
        )
        if folder:
            self.export_folder = folder
            self._update_preview()
            
    def _on_export(self) -> None:
        """Handle export button"""
        # Validate settings
        if not self.settings['filename'].strip():
            messagebox.showwarning("Invalid Filename", "Please enter a valid filename.")
            return
            
        # Update settings from UI
        self.settings['loop_count'] = self.loop_var.get()
        self.settings['optimize'] = self.optimize_var.get()
        if hasattr(self, 'quality_var'):
            self.settings['video_quality'] = self.quality_var.get()
            
        # Generate final filename
        extension = ".gif" if self.settings['format'] == 'gif' else ".mp4"
        base_filename = f"{self.settings['filename']}{extension}"
        full_path = os.path.join(self.export_folder, base_filename)
        final_filename = self._get_unique_filename(full_path)
        
        # Change button text to show progress
        original_text = self.export_btn.cget("text")
        self.export_btn.config(text="⏳ Exporting...", state="disabled")
        self.dialog.update()
        
        # Prepare result
        self.result = {
            **self.settings,
            'export_folder': self.export_folder,
            'final_filename': final_filename
        }
        
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


def show_animation_export_dialog(parent: tk.Widget, export_folder: str) -> Optional[Dict[str, Any]]:
    """Convenience function to show animation export dialog"""
    dialog = AnimationExportDialog(parent, export_folder)
    return dialog.show()
