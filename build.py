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
    
    path = Path(path)
    for attempt in range(5):  # Increased retries
        try:
            if path.is_file():
                path.unlink()
            else:
                shutil.rmtree(path, ignore_errors=True)
            print(f"✅ Cleaned {path}")
            return True
        except PermissionError:
            if attempt < 4:  # Increased wait time
                print(f"⚠️ {path} locked, waiting...")
                time.sleep(5)  # Longer wait time
            else:
                print(f"⚠️ Skipping {path} (locked by system)")
                return False
        except OSError as e:
            if attempt < 4:
                print(f"⚠️ {path} access error, retrying... ({e})")
                time.sleep(5)
            else:
                print(f"⚠️ Failed to remove {path}: {e}")
                return False

def main():
    """Simple build process"""
    
    print("🔬 MICROSCOPY IMAGE ANALYZER - SIMPLE BUILD")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("👨‍🔬 Author: Muhammad Sinan")
    print("="*50)
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Clean previous builds
    print("\n🧹 Cleaning previous builds...")
    safe_remove_dir('build')
    safe_remove_dir('dist')
    for file in Path('.').glob('*.spec'):
        try:
            file.unlink()
            print(f"✅ Removed {file}")
        except OSError as e:
            print(f"⚠️ Could not remove {file}: {e}")

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
    
    # Prepare PyInstaller command
    app_name = "MicroscopyImageAnalyzer"
    main_script = "main.py"
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        f"--name={app_name}",
        "--onefile",  # Create a single executable
        "--windowed",  # Don't show console window
        "--clean",    # Clean PyInstaller cache
        "--noconfirm",  # Replace output directory without asking
        "--add-data", "config;config",
        "--add-data", "src;src",
        "--hidden-import", "tkinter",
        "--hidden-import", "tkinter.ttk",
        "--hidden-import", "tkinter.filedialog",
        "--hidden-import", "tkinter.messagebox",
        "--hidden-import", "PIL._tkinter_finder",  # Required for Pillow
        "--hidden-import", "imageio",
        "--hidden-import", "imageio.plugins",
        "--hidden-import", "imageio.plugins.ffmpeg",
        "--hidden-import", "imageio_ffmpeg",
        "--hidden-import", "imageio_ffmpeg._utils",
        "--collect-submodules", "imageio",
        "--collect-submodules", "numpy",
        main_script
    ]
    
    # Check for assets directory
    assets_path = Path("src/gui/assets")
    if assets_path.exists():
        cmd.extend(["--add-data", f"{assets_path};src/gui/assets"])
        # Check for icon file
        icon_file = assets_path / "icon.ico"
        if icon_file.exists():
            cmd.extend(["--icon", str(icon_file)])
    
    print("\n🛠️ Building executable...")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        exe_path = project_dir / "dist" / f"{app_name}.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / 1024 / 1024
            print("\n✅ Build completed successfully!")
            print(f"📦 Executable: {exe_path}")
            print(f"💾 Size: {size_mb:.1f} MB")
            print(f"\n▶️ Run with: {exe_path}")
            return True
        else:
            print("\n❌ Build completed but executable not found")
            return False
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed with error: {e}")
        if hasattr(e, 'output') and e.output:
            print("Build output:")
            print(e.output)
        if hasattr(e, 'stderr') and e.stderr:
            print("Error output:")
            print(e.stderr)
        return False
    except OSError as e:
        print(f"\n❌ System error during build: {e}")
        return False

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
