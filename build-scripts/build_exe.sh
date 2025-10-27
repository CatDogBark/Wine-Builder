#!/bin/bash
# Updated: 2025-10-26
set -e

# Generic Wine + PyInstaller executable builder
# Usage: build_exe.sh <python_script> <executable_name> [extra_pyinstaller_args]

PYTHON_SCRIPT=${1:-"main.py"}
EXECUTABLE_NAME=${2:-"tool"}
EXTRA_ARGS=${3:-""}

echo "=========================================="
echo "  Wine Executable Builder"
echo "=========================================="
echo "Python Script: $PYTHON_SCRIPT"
echo "Executable Name: $EXECUTABLE_NAME"
echo "Extra Args: $EXTRA_ARGS"
echo ""

# Install Python dependencies if requirements.txt exists
if [ -f /source/requirements.txt ]; then
  echo "Installing Python dependencies..."
  python3 -m pip install -r /source/requirements.txt
fi

# Verify source file exists
if [ ! -f "/source/$PYTHON_SCRIPT" ]; then
    echo "ERROR: Source file /source/$PYTHON_SCRIPT not found!"
    echo "Available files in /source:"
    ls -la /source/
    exit 1
fi

# PyInstaller is pre-installed in Docker container
echo "PyInstaller pre-installed in Wine environment..."

# Create Windows build script in /app (writable location)
BUILD_SCRIPT="/app/build_in_wine.bat"
cat > "$BUILD_SCRIPT" << EOF
@echo off
echo ========================================
echo   Windows Executable Build
echo ========================================
echo.

REM Add Python 3.12 embeddable to PATH
set PATH=C:\Python312;%PATH%
echo Added Python 3.12 to PATH: %PATH%

REM Verify Python installation in Wine
python --version
if errorlevel 1 (
    echo ERROR: Python not found in Wine environment!
    echo Current directory: %cd%
    echo Python path should be: C:\Python312\python.exe
    dir C:\Python312\python.exe > nul 2>&1
    if errorlevel 1 (
        echo Python executable not found in expected location
        exit /b 1
    )
    exit /b 1
)

REM Set PYTHONPATH for site-packages
set PYTHONPATH=C:\Python312\Lib\site-packages;%PYTHONPATH%
echo Set PYTHONPATH to include site-packages: %PYTHONPATH%

REM Check if PyInstaller is available
python -c "import site; import PyInstaller" > nul 2>&1
if errorlevel 1 (
    echo WARNING: PyInstaller not found, checking installation...
    echo Python path with site:
    python -c "import site; import sys; [print(p) for p in sys.path]"
    echo Current dir files:
    dir
    echo PyInstaller not available - this may cause build failures!
    echo Continuing anyway...
)

REM Clear previous builds
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

echo Building executable: $EXECUTABLE_NAME
echo.

REM Build the executable using pyinstaller module with GUI support
REM Optimized for AV compatibility and proper bundling
REM Include tkinter as runtime dependency (resolved from target Windows system)
python -m PyInstaller --onefile --windowed --clean --noupx --name=$EXECUTABLE_NAME --collect-all PIL --hidden-import=PIL.Image --hidden-import=PIL.ImageTk --hidden-import=tkinter $EXTRA_ARGS $PYTHON_SCRIPT

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    echo.
    pause
    exit /b 1
)

echo.
echo ====================================
echo         BUILD SUCCESSFUL!
echo ====================================
echo.
EOF

echo "Created Windows build script in /app"

# Copy source files and build script to Wine environment
echo "Copying source files to Wine environment..."
cp "/source/$PYTHON_SCRIPT" "$WINEPREFIX/drive_c/"
cp -r "/source/tools/" "$WINEPREFIX/drive_c/" || true
cp "/app/build_in_wine.bat" "$WINEPREFIX/drive_c/"

# Copy requirements.txt if it exists
if [ -f "/source/tools/requirements.txt" ]; then
    cp "/source/tools/requirements.txt" "$WINEPREFIX/drive_c/"
fi

# Copy icon if specified in extra args
if [[ "$EXTRA_ARGS" == *"--icon"* ]]; then
    icon_path=$(echo "$EXTRA_ARGS" | sed -n 's/.*--icon=\([^[:space:]]*\).*/\1/p')
    if [ -f "/source/$icon_path" ]; then
        cp "/source/$icon_path" "$WINEPREFIX/drive_c/"
        echo "Icon file copied to Wine environment"
    else
        echo "Warning: Icon file $icon_path not found, build will continue without icon"
        # Remove --icon from args if file not found
        EXTRA_ARGS=$(echo "$EXTRA_ARGS" | sed 's/--icon=[^[:space:]]*//g' | tr -s ' ')
    fi
fi

# Run build in Wine environment
echo "Running build in Wine environment..."
echo "(This may take several minutes...)"
echo ""

# Initialize Wine environment if needed
wineboot --init || true

# Change to C: drive and run the Windows batch file through Wine
cd "$WINEPREFIX/drive_c"
xvfb-run -a wine cmd /c "C:\\build_in_wine.bat"

# Check if build succeeded
if [ ! -f "$WINEPREFIX/drive_c/dist/${EXECUTABLE_NAME}.exe" ]; then
    echo "ERROR: Build failed - executable not created!"
    echo "Checking Wine C: drive contents:"
    ls -la "$WINEPREFIX/drive_c/" 2>/dev/null || echo "Wine directory not accessible"
    echo "Checking dist directory:"
    ls -la "$WINEPREFIX/drive_c/dist/" 2>/dev/null || echo "Dist directory not found"
    exit 1
fi

# Copy the built executable to source directory
echo "Copying executable to source directory..."
cp "$WINEPREFIX/drive_c/dist/${EXECUTABLE_NAME}.exe" "/source/"
ls -la "/source/"

echo ""
echo "=========================================="
echo "  Build Complete!"
echo "=========================================="
echo "Executable: /source/${EXECUTABLE_NAME}.exe"
echo "=========================================="