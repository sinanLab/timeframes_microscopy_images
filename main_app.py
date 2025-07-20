#!/usr/bin/env python3
"""
Microscopy Image Analyzer - Main Entry Point

A comprehensive tool for analyzing microscopy timeframe images with features for:
- Image sequence loading and navigation
- ROI definition and manipulation
- Batch image cropping
- Animated GIF generation

Usage:
    python main_app.py

Requirements:
    - Python 3.7+
    - tkinter (usually included with Python)
    - PIL/Pillow
    - numpy
    - imageio

Author: Microscopy Analysis Team
Version: 2.0.0
"""

import sys
import os

# Add the project root to Python path to enable imports
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from src import main
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"Import Error: {e}")
    print("Please ensure all required packages are installed:")
    print("  pip install pillow numpy imageio")
    sys.exit(1)
    
except Exception as e:
    print(f"Error starting application: {e}")
    sys.exit(1)
