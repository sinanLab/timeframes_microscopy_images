@echo off
echo ============================================
echo  Microscopy Image Analyzer - Build Script
echo ============================================
echo.

REM Change to the directory containing this script
cd /d "%~dp0"

echo Step 1: Installing required packages...
pip install pillow numpy imageio pyinstaller
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to install packages
    pause
    exit /b 1
)

echo.
echo Step 2: Creating executable...
pyinstaller --name="MicroscopyImageAnalyzer" ^
    --onefile ^
    --windowed ^
    --add-data "config;config" ^
    --add-data "src;src" ^
    --add-data "import;import" ^
    --add-data "export;export" ^
    --add-data "README.md;." ^
    --hidden-import="PIL._tkinter_finder" ^
    --hidden-import="numpy" ^
    --hidden-import="imageio" ^
    --hidden-import="tkinter" ^
    --hidden-import="tkinter.ttk" ^
    --hidden-import="tkinter.filedialog" ^
    --hidden-import="tkinter.messagebox" ^
    main_exe.py

if %ERRORLEVEL% neq 0 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo Step 3: Creating portable package...
if not exist "dist\MicroscopyImageAnalyzer_Portable" mkdir "dist\MicroscopyImageAnalyzer_Portable"

copy "dist\MicroscopyImageAnalyzer.exe" "dist\MicroscopyImageAnalyzer_Portable\"
xcopy "import" "dist\MicroscopyImageAnalyzer_Portable\import\" /E /I /Y
xcopy "export" "dist\MicroscopyImageAnalyzer_Portable\export\" /E /I /Y
copy "README.md" "dist\MicroscopyImageAnalyzer_Portable\"
copy "requirements.txt" "dist\MicroscopyImageAnalyzer_Portable\"

REM Create run script
echo @echo off > "dist\MicroscopyImageAnalyzer_Portable\run_analyzer.bat"
echo echo Starting Microscopy Image Analyzer... >> "dist\MicroscopyImageAnalyzer_Portable\run_analyzer.bat"
echo MicroscopyImageAnalyzer.exe >> "dist\MicroscopyImageAnalyzer_Portable\run_analyzer.bat"
echo pause >> "dist\MicroscopyImageAnalyzer_Portable\run_analyzer.bat"

echo.
echo ============================================
echo  BUILD SUCCESSFUL!
echo ============================================
echo.
echo Your executable is ready in: dist\MicroscopyImageAnalyzer.exe
echo Portable package is in: dist\MicroscopyImageAnalyzer_Portable\
echo.
echo To run: Double-click MicroscopyImageAnalyzer.exe
echo.
pause
