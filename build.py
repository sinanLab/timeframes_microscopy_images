"""
Simple Build Script for Microscopy Image Analyzer
Just builds the executable - no deployment complexity

Author: Muhammad Sinan
Institution: Polish Academy of Sciences
Version: 0.2.20.07.2

USAGE: python build.py
"""

import subprocess
import sys
import os
import shutil
import time
from pathlib import Path
from datetime import datetime

def safe_remove_dir(path):
    """Safely remove directory with retries"""
    if not Path(path).exists():
        return True
    
    for attempt in range(3):
        try:
            shutil.rmtree(path)
            print(f"✅ Cleaned {path}")
            return True
        except PermissionError:
            if attempt < 2:
                print(f"⚠️ {path} locked, waiting...")
                time.sleep(3)
            else:
                print(f"⚠️ Skipping {path} (locked by system)")
                return False
        except Exception as e:
            print(f"⚠️ Error cleaning {path}: {e}")
            return False

def main():
    """Simple build process"""
    
    print("🔬 MICROSCOPY IMAGE ANALYZER - SIMPLE BUILD")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"👨‍🔬 Author: Muhammad Sinan")
    print("="*50)
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Clean previous builds (skip if locked)
    print("🧹 Cleaning previous builds...")
    safe_remove_dir("build")
    safe_remove_dir("dist")
    
    # Remove spec files
    for spec_file in project_dir.glob("*.spec"):
        try:
            spec_file.unlink()
            print(f"✅ Removed {spec_file.name}")
        except:
            pass
    
    # Check PyInstaller
    print("\n📦 Checking PyInstaller...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "show", "pyinstaller"], 
                     check=True, capture_output=True)
        print("✅ PyInstaller found")
    except subprocess.CalledProcessError:
        print("❌ Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("✅ PyInstaller installed")
    
    # Build executable
    print("\n🔨 Building executable...")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=MicroscopyImageAnalyzer",
        "--onefile",
        "--windowed", 
        "--noconfirm",
        "--add-data=config;config",
        "--add-data=src;src",
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.ttk",
        "--hidden-import=tkinter.filedialog", 
        "--hidden-import=tkinter.messagebox",
        "--hidden-import=PIL._tkinter_finder",
        "main.py"
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build completed!")
    except subprocess.CalledProcessError as e:
        print("❌ Build failed!")
        print(f"Error: {e.stderr}")
        return False
    
    # Check result
    exe_path = project_dir / "dist" / "MicroscopyImageAnalyzer.exe"
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / 1024 / 1024
        print(f"\n🎉 SUCCESS!")
        print(f"📦 Executable: {exe_path}")
        print(f"💾 Size: {size_mb:.1f} MB")
        print(f"\n▶️ Run with: {exe_path}")
    else:
        print("❌ Executable not found!")
        return False
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ Build failed!")
    except KeyboardInterrupt:
        print("\n❌ Cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    input("\nPress Enter to exit...")
