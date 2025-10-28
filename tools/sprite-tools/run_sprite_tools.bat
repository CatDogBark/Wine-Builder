@echo off
echo ========================================
echo   Sprite Tools Suite Launcher
echo ========================================
echo.

echo STEP 1: Check if Python is available...
python --version
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    pause
    exit /b 1
)
echo Python OK!
pause
echo.

echo STEP 2: Check if tkinter works...
python -c "import tkinter; print('tkinter OK!')"
if errorlevel 1 (
    echo ERROR: tkinter import failed
    pause
    exit /b 1
)
pause
echo.

echo STEP 3: Check if Pillow (PIL) works...
python -c "from PIL import Image; print('PIL OK!')"
if errorlevel 1 (
    echo ERROR: PIL import failed
    pause
    exit /b 1
)
pause
echo.

echo STEP 4: Launch the Sprite Tools Suite...
echo The GUI should open in a new window.
echo If it doesn't appear, check for error messages.
echo.
python combined_sprite_tools.py

echo.
echo Application closed.
echo If you saw errors above, that's the issue.
pause