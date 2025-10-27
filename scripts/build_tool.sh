#!/bin/bash
# Generic tool builder using Docker
# Usage: ./build_tool.sh <tool_name> [python_script] [executable_name] [extra_args]

set -e

TOOL_NAME=${1:-"unknown"}
EXECUTABLE_NAME=${3:-"${TOOL_NAME}"}
EXTRA_ARGS=${4:-""}

# Determine PYTHON_SCRIPT based on TOOL_NAME or provided arg
if [ -n "$2" ]; then
  PYTHON_SCRIPT="$2"
else
  case "$TOOL_NAME" in
    "spriteframe-sizer") PYTHON_SCRIPT="spriteframe-sizer/sprite_frame_sizer.py" ;;
    "spritesheet-combiner") PYTHON_SCRIPT="spritesheet-combiner/spritesheet_combiner.py" ;;
    "spritesheet-id") PYTHON_SCRIPT="spritesheet-id/spritesheet_analyzer.py" ;;
    "editor") PYTHON_SCRIPT="editor/sprite_frame_editor.py" ;;
    *) PYTHON_SCRIPT="main.py" ;;  # fallback
  esac
fi

echo "Building $TOOL_NAME executable..."
echo "=================================="
echo "Tool: $TOOL_NAME"
echo "Script: $PYTHON_SCRIPT"
echo "Executable: $EXECUTABLE_NAME.exe"
echo "Extra Args: $EXTRA_ARGS"
echo ""

# Build the Docker image if needed
docker-compose -f wine.yml build

# Run the build process with custom parameters
export PYTHON_SCRIPT="$PYTHON_SCRIPT"
export EXECUTABLE_NAME="$EXECUTABLE_NAME"
export EXTRA_PYINSTALLER_ARGS="$EXTRA_ARGS"
docker-compose -f wine.yml up

echo "=================================="
echo "Build complete!"
echo "Check ./dist/ for your executable"