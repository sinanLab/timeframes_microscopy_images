#!/usr/bin/env python3
"""
Test script for Animation Export Dialog

Author: Muhammad Sinan
"""

import sys
import os
import tkinter as tk

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from src.gui.animation_dialog import show_animation_export_dialog
    
    def test_dialog():
        """Test the animation export dialog"""
        root = tk.Tk()
        root.withdraw()  # Hide main window
        
        # Test with a sample export folder
        export_folder = os.path.join(project_root, "export")
        
        print("Opening Animation Export Dialog...")
        result = show_animation_export_dialog(root, export_folder)
        
        if result:
            print("Dialog returned result:")
            for key, value in result.items():
                print(f"  {key}: {value}")
        else:
            print("Dialog was cancelled")
        
        root.destroy()

    if __name__ == "__main__":
        test_dialog()
        
except Exception as e:
    print(f"Error testing dialog: {e}")
    import traceback
    traceback.print_exc()
