#!/bin/bash
# Docker entrypoint script to properly handle environment variable expansion

# Echo the values for debugging
env | grep -E "(PYTHON_SCRIPT|EXECUTABLE_NAME|EXTRA_PYINSTALLER_ARGS)" || echo "No env vars found"

echo "PYTHON_SCRIPT: '$PYTHON_SCRIPT'"
echo "EXECUTABLE_NAME: '$EXECUTABLE_NAME'"
echo "EXTRA_PYINSTALLER_ARGS: '$EXTRA_PYINSTALLER_ARGS'"
echo "ARGS: $@"

# Use env vars or defaults
PYTHON_SCRIPT=${PYTHON_SCRIPT:-"main.py"}
EXECUTABLE_NAME=${EXECUTABLE_NAME:-"tool"}
EXTRA_PYINSTALLER_ARGS=${EXTRA_PYINSTALLER_ARGS:-""}

echo "Using: PYTHON_SCRIPT='$PYTHON_SCRIPT' EXECUTABLE_NAME='$EXECUTABLE_NAME' ARGS='$EXTRA_PYINSTALLER_ARGS'"

# Call the build script with proper variable expansion
exec /app/build-scripts/build_exe.sh "$PYTHON_SCRIPT" "$EXECUTABLE_NAME" "$EXTRA_PYINSTALLER_ARGS"