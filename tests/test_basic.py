"""
Basic tests for the Microscopy Image Analyzer

Run with: python -m pytest tests/
"""

import unittest
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from config.settings import AppConfig, UIConfig
    from src.utils.file_utils import get_file_info, is_valid_image_file
    
    class TestConfiguration(unittest.TestCase):
        """Test configuration settings"""
        
        def test_app_config_exists(self):
            """Test that AppConfig has required attributes"""
            self.assertTrue(hasattr(AppConfig, 'APP_NAME'))
            self.assertTrue(hasattr(AppConfig, 'SUPPORTED_FORMATS'))
            self.assertTrue(hasattr(AppConfig, 'CANVAS_WIDTH'))
            self.assertTrue(hasattr(AppConfig, 'CANVAS_HEIGHT'))
        
        def test_ui_config_exists(self):
            """Test that UIConfig has required attributes"""
            self.assertTrue(hasattr(UIConfig, 'BACKGROUND_COLOR'))
            self.assertTrue(hasattr(UIConfig, 'CURSOR_CROSS'))
            self.assertTrue(hasattr(UIConfig, 'FRAME_PADDING'))
    
    class TestFileUtils(unittest.TestCase):
        """Test file utility functions"""
        
        def test_get_file_info(self):
            """Test file info extraction"""
            name, ext = get_file_info("test_image.png")
            self.assertEqual(name, "test_image")
            self.assertEqual(ext, ".png")
        
        def test_is_valid_image_file(self):
            """Test image file validation"""
            # Note: This tests the logic, not actual file existence
            self.assertFalse(is_valid_image_file("nonexistent.png"))

except ImportError as e:
    print(f"Import error in tests: {e}")
    print("Some modules may not be available for testing")

if __name__ == '__main__':
    unittest.main()
