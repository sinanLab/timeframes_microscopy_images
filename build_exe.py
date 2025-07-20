#!/usr/bin/env python3
"""
Build script for creating executable from Microscopy Image Analyzer
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def create_spec_file():
    """Create PyInstaller spec file"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config', 'config'),
        ('src', 'src'),
        ('import', 'import'),
        ('export', 'export'),
        ('README.md', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'PIL._tkinter_finder',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'numpy',
        'imageio',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MicroscopyImageAnalyzer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
    version='version_info.txt' if os.path.exists('version_info.txt') else None,
)
'''
    
    with open('microscopy_analyzer.spec', 'w') as f:
        f.write(spec_content)
    print("Created microscopy_analyzer.spec")

def create_version_info():
    """Create version info file for Windows exe"""
    version_info = '''# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(2,0,0,0),
    prodvers=(2,0,0,0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Microscopy Analysis Team'),
        StringStruct(u'FileDescription', u'Microscopy Image Analyzer'),
        StringStruct(u'FileVersion', u'2.0.0'),
        StringStruct(u'InternalName', u'MicroscopyImageAnalyzer'),
        StringStruct(u'LegalCopyright', u'Copyright (c) 2025'),
        StringStruct(u'OriginalFilename', u'MicroscopyImageAnalyzer.exe'),
        StringStruct(u'ProductName', u'Microscopy Image Analyzer'),
        StringStruct(u'ProductVersion', u'2.0.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
    
    with open('version_info.txt', 'w') as f:
        f.write(version_info)
    print("Created version_info.txt")

def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    try:
        import PyInstaller
        print("PyInstaller is already installed")
        return True
    except ImportError:
        print("Installing PyInstaller...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
            print("PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("Failed to install PyInstaller")
            return False

def ensure_dependencies():
    """Ensure all required dependencies are installed"""
    dependencies = ['pillow', 'numpy', 'imageio', 'pyinstaller']
    
    print("Checking dependencies...")
    missing = []
    
    for dep in dependencies:
        try:
            if dep == 'pillow':
                import PIL
            elif dep == 'numpy':
                import numpy
            elif dep == 'imageio':
                import imageio
            elif dep == 'pyinstaller':
                import PyInstaller
            print(f"✓ {dep} is installed")
        except ImportError:
            missing.append(dep)
            print(f"✗ {dep} is missing")
    
    if missing:
        print(f"\\nInstalling missing dependencies: {', '.join(missing)}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing)
            print("All dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("Failed to install dependencies")
            return False
    
    print("All dependencies are satisfied")
    return True

def build_executable():
    """Build the executable using PyInstaller"""
    print("\\nBuilding executable...")
    
    # Clean previous builds
    if os.path.exists('build'):
        shutil.rmtree('build')
        print("Cleaned build directory")
    
    if os.path.exists('dist'):
        shutil.rmtree('dist')
        print("Cleaned dist directory")
    
    # Build using spec file
    try:
        cmd = [sys.executable, '-m', 'PyInstaller', '--clean', 'microscopy_analyzer.spec']
        subprocess.check_call(cmd)
        print("\\n✓ Executable built successfully!")
        print("✓ Find the executable in the 'dist' folder")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\\n✗ Build failed: {e}")
        return False

def create_portable_package():
    """Create a portable package with the executable"""
    dist_path = Path('dist')
    if not dist_path.exists():
        print("No dist folder found. Build first.")
        return False
    
    # Create portable package folder
    package_name = 'MicroscopyImageAnalyzer_Portable'
    package_path = dist_path / package_name
    
    if package_path.exists():
        shutil.rmtree(package_path)
    
    package_path.mkdir()
    
    # Copy executable
    exe_path = dist_path / 'MicroscopyImageAnalyzer.exe'
    if exe_path.exists():
        shutil.copy2(exe_path, package_path)
        print(f"✓ Copied executable to {package_path}")
    else:
        print("✗ Executable not found")
        return False
    
    # Copy sample data folders
    for folder in ['import', 'export']:
        src_folder = Path(folder)
        if src_folder.exists():
            shutil.copytree(src_folder, package_path / folder)
            print(f"✓ Copied {folder} folder")
    
    # Copy documentation
    for file in ['README.md', 'requirements.txt']:
        src_file = Path(file)
        if src_file.exists():
            shutil.copy2(src_file, package_path)
            print(f"✓ Copied {file}")
    
    # Create run script
    run_script = package_path / 'run_analyzer.bat'
    with open(run_script, 'w') as f:
        f.write('@echo off\\n')
        f.write('echo Starting Microscopy Image Analyzer...\\n')
        f.write('MicroscopyImageAnalyzer.exe\\n')
        f.write('pause\\n')
    
    print(f"\\n✓ Portable package created: {package_path}")
    return True

def main():
    """Main build process"""
    print("=== Microscopy Image Analyzer - Build Script ===\\n")
    
    # Change to project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Step 1: Check dependencies
    if not ensure_dependencies():
        print("\\n✗ Failed to install dependencies. Please install manually:")
        print("pip install pillow numpy imageio pyinstaller")
        return False
    
    # Step 2: Create build files
    create_spec_file()
    create_version_info()
    
    # Step 3: Build executable
    if not build_executable():
        return False
    
    # Step 4: Create portable package
    create_portable_package()
    
    print("\\n=== Build Complete ===")
    print("Your executable is ready in the 'dist' folder!")
    print("Run 'MicroscopyImageAnalyzer.exe' to start the application.")
    
    return True

if __name__ == "__main__":
    success = main()
    input("\\nPress Enter to exit...")
    sys.exit(0 if success else 1)
