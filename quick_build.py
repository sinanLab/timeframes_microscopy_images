"""
Quick build script - automatically handles everything
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{'='*50}")
    print(f"{description}")
    print(f"{'='*50}")
    
    try:
        if isinstance(cmd, str):
            result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        else:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        if result.stdout:
            print(result.stdout)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False

def main():
    """Main build process"""
    print("Building Microscopy Image Analyzer executable...")
    
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    # Step 1: Install dependencies
    deps = ["pillow", "numpy", "imageio", "pyinstaller"]
    for dep in deps:
        if not run_command([sys.executable, "-m", "pip", "install", dep], f"Installing {dep}"):
            print(f"Failed to install {dep}. Please install manually:")
            print(f"pip install {dep}")
            return False
    
    # Step 2: Clean previous builds
    for folder in ["build", "dist"]:
        if Path(folder).exists():
            import shutil
            shutil.rmtree(folder)
            print(f"Cleaned {folder} directory")
    
    # Step 3: Build executable
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=MicroscopyImageAnalyzer",
        "--onefile",
        "--windowed",
        "--add-data=config;config",
        "--add-data=src;src", 
        "--add-data=import;import",
        "--add-data=export;export",
        "--add-data=README.md;.",
        "--hidden-import=PIL._tkinter_finder",
        "--hidden-import=numpy",
        "--hidden-import=imageio", 
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.ttk",
        "--hidden-import=tkinter.filedialog",
        "--hidden-import=tkinter.messagebox",
        "main_exe.py"
    ]
    
    if not run_command(cmd, "Building executable with PyInstaller"):
        return False
    
    # Step 4: Verify executable exists
    exe_path = Path("dist/MicroscopyImageAnalyzer.exe")
    if not exe_path.exists():
        print("✗ Executable not found after build")
        return False
    
    print(f"\n{'='*60}")
    print("BUILD SUCCESSFUL! 🎉")
    print(f"{'='*60}")
    print(f"Executable location: {exe_path.absolute()}")
    print(f"File size: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
    print("\nTo run: Double-click MicroscopyImageAnalyzer.exe")
    
    return True

if __name__ == "__main__":
    success = main()
    input("\nPress Enter to exit...")
    sys.exit(0 if success else 1)
