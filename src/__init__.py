"""
Microscopy Image Analyzer - A tool for analyzing microscopy timeframe images

This package provides functionality for:
- Loading and displaying microscopy images
- Defining regions of interest (ROI)
- Cropping image sequences
- Creating animated GIFs from timeframe data
"""

__version__ = "2.0.0"
__author__ = "Microscopy Analysis Team"

from .app import MicroscopyImageAnalyzer, main

__all__ = ["MicroscopyImageAnalyzer", "main"]
