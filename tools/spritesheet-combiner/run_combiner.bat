@echo off
echo ========================================
echo   Godot Spritesheet Combiner
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python from https://www.python.org/
    echo.
    pause
    exit /b 1
)

REM Check if PIL/Pillow is installed
python -c "import PIL" >nul 2>&1
if errorlevel 1 (
    echo Installing required package: Pillow...
    echo.
    pip install pillow
    echo.
)

REM Run the script
echo Starting Spritesheet Combiner...
echo.
python spritesheet_combiner.py

REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo An error occurred!
    pause
)