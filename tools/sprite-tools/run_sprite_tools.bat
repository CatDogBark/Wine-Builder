@echo off
echo ========================================
echo   Sprite Tools Suite Launcher
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please make sure Python is installed and in your PATH.
    echo.
    pause
    exit /b 1
)

REM Check if required modules are available
echo Checking dependencies...
python -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo ERROR: tkinter module not found!
    echo Please install tkinter or ensure it's included in your Python installation.
    echo.
    pause
    exit /b 1
)

python -c "from PIL import Image" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Pillow (PIL) module not found!
    echo Run: pip install pillow
    echo.
    pause
    exit /b 1
)

echo Starting Sprite Tools Suite...
echo Press Ctrl+C to exit the application
echo.

REM Run the combined tools (we're already in the sprite-tools directory)
python combined_sprite_tools.py

REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo An error occurred! Check the error message above.
    echo.
    pause
)