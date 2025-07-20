"""
Configuration settings for the Microscopy Image Analyzer
"""

import os

class AppConfig:
    """Application configuration settings"""
    
    # Application settings
    APP_NAME = "Microscopy Image Analyzer"
    VERSION = "2.0.0"
    
    # Window settings
    WINDOW_WIDTH = 1100
    WINDOW_HEIGHT = 850
    CANVAS_WIDTH = 800
    CANVAS_HEIGHT = 600
    
    # Image processing settings
    SUPPORTED_FORMATS = ('*.jpg', '*.jpeg', '*.png', '*.tif', '*.tiff', '*.bmp', '*.gif')
    MAX_ZOOM = 20.0
    MIN_ZOOM = 0.1
    ZOOM_FACTOR = 1.2
    MAX_IMAGE_SIZE = 4000  # Maximum displayed image dimension
    
    # ROI settings
    ROI_COLOR = "#4a6ea9"
    HANDLE_COLOR = "#ff0000"
    LINE_WIDTH = 2
    DASH_PATTERN = (4, 2)
    HANDLE_SIZE = 6
    MIN_ROI_SIZE = 5
    
    # GIF settings
    GIF_DURATION = 0.2  # seconds per frame
    
    # UI Theme
    UI_THEME = 'clam'
    
    # Paths
    DEFAULT_IMPORT_FOLDER = "import"
    DEFAULT_EXPORT_FOLDER = "export"
    
    @classmethod
    def get_default_folders(cls, base_path):
        """Get default import/export folder paths"""
        return {
            'import': os.path.join(base_path, cls.DEFAULT_IMPORT_FOLDER),
            'export': os.path.join(base_path, cls.DEFAULT_EXPORT_FOLDER)
        }

class UIConfig:
    """UI-specific configuration"""
    
    # Colors
    BACKGROUND_COLOR = 'gray20'
    SUCCESS_COLOR = "green"
    ERROR_COLOR = "red"
    WARNING_COLOR = "orange"
    
    # Cursors
    CURSOR_CROSS = "cross"
    CURSOR_FLEUR = "fleur"
    CURSOR_DEFAULT = "arrow"
    
    # Padding
    FRAME_PADDING = "10"
    CONTROL_PADDING = "5"
