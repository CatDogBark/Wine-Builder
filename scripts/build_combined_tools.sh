#!/bin/bash
# Build the unified Combined Sprite Tools executable

set -e

echo "Building Combined Sprite Tools Suite..."
echo "========================================"

# Use the build_tool.sh script with specific parameters for combined tools
./scripts/build_tool.sh "Combined Sprite Tools" "combined_sprite_tools.py" "Combined_Sprite_Tools" "--icon=icon.ico --hidden-import=PIL --hidden-import=PIL.Image --hidden-import=PIL.ImageTk"

echo "========================================"
echo "Combined Sprite Tools build complete!"
echo "Executable: ./dist/Combined_Sprite_Tools.exe"
echo "========================================"