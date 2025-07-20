"""
File handling utilities
"""

import os
import glob
from typing import List, Tuple
from config.settings import AppConfig


def get_image_files(folder_path: str) -> List[str]:
    """Get all image files from a folder"""
    image_paths = []
    for ext in AppConfig.SUPPORTED_FORMATS:
        image_paths.extend(glob.glob(os.path.join(folder_path, ext)))
    return sorted(image_paths)


def ensure_directory(path: str) -> bool:
    """Ensure directory exists, create if it doesn't"""
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except OSError:
        return False


def get_file_info(file_path: str) -> Tuple[str, str]:
    """Get file name and extension"""
    base_name = os.path.basename(file_path)
    name, ext = os.path.splitext(base_name)
    return name, ext


def is_valid_image_file(file_path: str) -> bool:
    """Check if file is a valid image file"""
    if not os.path.exists(file_path):
        return False
    
    _, ext = os.path.splitext(file_path)
    return any(ext.lower() in pattern.replace('*', '') for pattern in AppConfig.SUPPORTED_FORMATS)
