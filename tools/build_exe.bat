@echo off
echo ========================================
echo   Building Godot Sprite Tools Suite .exe
echo ========================================
echo.
cd /d "%~dp0"

REM Try to find a Python with PyInstaller
set PYINSTALLER_FOUND=0
set PYTHON_EXE=

REM First try the system Python
if exist "C:\Python313\python.exe" (
    echo Testing C:\Python313\python.exe for PyInstaller...
    "C:\Python313\python.exe" -m pyinstaller --version >nul 2>&1
    if not errorlevel 1 (
        set PYINSTALLER_FOUND=1
        set PYTHON_EXE=C:\Python313\python.exe
        echo ✓ PyInstaller found in C:\Python313\
    )
)

REM Try other common Python locations
if !PYINSTALLER_FOUND!==0 (
    echo Testing AppData Python...
    if exist "%APPDATA%\..\Local\Programs\Python\Python313\python.exe" (
        "%APPDATA%\..\Local\Programs\Python\Python313\python.exe" -m pyinstaller --version >nul 2>&1
        if not errorlevel 1 (
            set PYINSTALLER_FOUND=1
            set PYTHON_EXE=%APPDATA%\..\Local\Programs\Python\Python313\python.exe
            echo ✓ PyInstaller found in Local Programs
        )
    )
)

REM Try the AppData location
if !PYINSTALLER_FOUND!==0 (
    if exist "%APPDATA%\Python\Python313\python.exe" (
        "%APPDATA%\Python\Python313\python.exe" -m pyinstaller --version >nul 2>&1
        if not errorlevel 1 (
            set PYINSTALLER_FOUND=1
            set PYTHON_EXE=%APPDATA%\Python\Python313\python.exe
            echo ✓ PyInstaller found in AppData
        )
    )
)

REM Try PATH Python
if !PYINSTALLER_FOUND!==0 (
    where python >nul 2>&1
    if not errorlevel 1 (
        python -m pyinstaller --version >nul 2>&1
        if not errorlevel 1 (
            set PYINSTALLER_FOUND=1
            set PYTHON_EXE=python
            echo ✓ PyInstaller found in PATH
        )
    )
)

REM If still not found, try to install
if !PYINSTALLER_FOUND!==0 (
    echo PyInstaller not found in any Python installation.
    echo Installing PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller!
        echo Try these solutions:
        echo 1. Run as administrator
        echo 2. Install PyInstaller manually to the correct Python: pip install pyinstaller
        echo 3. Or try: pyinstaller --version (if pyinstaller is in PATH)
        pause
        exit /b 1
    )
    echo PyInstaller installed. Retrying...
    goto :retry_python_search
)

:retry_python_search
REM After successful install, search for Python with PyInstaller again
call :find_python

if !PYINSTALLER_FOUND!==0 (
    echo ERROR: Cannot find Python with PyInstaller!
    echo Please ensure PyInstaller is installed to your Python environment.
    pause
    exit /b 1
)

echo Using Python: !PYTHON_EXE!
echo.

:find_python
 REM Internal function to find Python
 goto :eof

REM Install Pillow and tkinter checks
echo Checking/installing dependencies...

!PYTHON_EXE! -c "import PIL" >nul 2>&1
if errorlevel 1 (
    echo Installing Pillow...
    !PYTHON_EXE! -m pip install pillow
    if errorlevel 1 (
        echo ERROR: Failed to install Pillow!
        pause
        exit /b 1
    )
)

!PYTHON_EXE! -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo ERROR: tkinter not available!
    echo Your Python installation needs tkinter support.
    echo Please install Python with tkinter/TCL support.
    pause
    exit /b 1
)

echo ✓ All dependencies ready
echo.

REM Verify our script exists
if not exist "combined_sprite_tools.py" (
    echo ERROR: combined_sprite_tools.py not found!
    echo Please run this script from the same directory as the Python file.
    pause
    exit /b 1
)

echo Building .exe file with PyInstaller...
echo This may take several minutes...
echo.

REM Clear any existing build/dist directories
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

REM Build with PyInstaller - include tkinter and PIL
!PYTHON_EXE! -m pyinstaller --onefile --windowed ^
    --name "Godot_Sprite_Tools" ^
    --hidden-import="tkinter" ^
    --hidden-import="PIL" ^
    --hidden-import="PIL.Image" ^
    --hidden-import="PIL.ImageTk" ^
    combined_sprite_tools.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    echo.
    echo Troubleshooting:
    echo 1. Try running as administrator
    echo 2. Install PyInstaller manually: pip install pyinstaller
    echo 3. Make sure you have tkinter (Python with GUI support)
    echo 4. Try without --windowed: python -m pyinstaller --onefile --name "Godot_Sprite_Tools" combined_sprite_tools.py
    pause
    exit /b 1
)

echo.
echo ====================================
echo         BUILD SUCCESSFUL!
echo ====================================
echo.
echo Your executable is located at:
echo    %cd%\dist\Godot_Sprite_Tools.exe
echo.
echo You can copy this single .exe file to any Windows machine.
echo No Python or dependencies required to run the .exe!
echo.
pause