"""
Image processing utilities
"""

import numpy as np
from PIL import Image
from typing import Tuple, Optional


def calculate_optimal_scale(image_size: Tuple[int, int], 
                          canvas_size: Tuple[int, int]) -> float:
    """Calculate optimal scale to fit image in canvas"""
    img_w, img_h = image_size
    canvas_w, canvas_h = canvas_size
    
    scale_w = canvas_w / img_w
    scale_h = canvas_h / img_h
    
    return min(scale_w, scale_h, 1.0)  # Don't scale up beyond 100%


def safe_resize_image(image: Image.Image, size: Tuple[int, int]) -> Optional[Image.Image]:
    """Safely resize image with error handling"""
    try:
        return image.resize(size, Image.LANCZOS)
    except Exception as e:
        print(f"Resize error: {str(e)}")
        return None


def validate_roi_coordinates(coords: Tuple[float, float, float, float],
                           image_size: Tuple[int, int]) -> bool:
    """Validate ROI coordinates are within image bounds"""
    x1, y1, x2, y2 = coords
    img_w, img_h = image_size
    
    # Check bounds
    if x1 < 0 or y1 < 0 or x2 > img_w or y2 > img_h:
        return False
    
    # Check that coordinates form a valid rectangle
    if x1 >= x2 or y1 >= y2:
        return False
    
    return True


def crop_image_safe(image: Image.Image, 
                   coords: Tuple[float, float, float, float]) -> Optional[Image.Image]:
    """Safely crop image with validation"""
    if not validate_roi_coordinates(coords, image.size):
        return None
    
    try:
        return image.crop(coords)
    except Exception as e:
        print(f"Crop error: {str(e)}")
        return None


def convert_to_rgb_array(image: Image.Image) -> np.ndarray:
    """Convert PIL image to RGB numpy array"""
    return np.array(image.convert('RGB'))
