"""
Setup script for building executable - fixes import paths
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import and run the main application
if __name__ == "__main__":
    try:
        from src.app import main
        main()
    except Exception as e:
        import tkinter as tk
        from tkinter import messagebox
        
        # Show error in a message box if GUI fails
        try:
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            messagebox.showerror("Error", f"Failed to start application:\n{str(e)}")
            root.destroy()
        except:
            # If even tkinter fails, print to console
            print(f"Error: {e}")
            input("Press Enter to exit...")
        
        sys.exit(1)
