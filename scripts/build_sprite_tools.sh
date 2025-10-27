#!/bin/bash
# Build Sprite Tools Suite executable using Docker

set -e

echo "Building Sprite Tools Suite executable..."
echo "=========================================="

# Build the Docker image if needed
docker-compose -f wine.yml build

# Run the build process
# Build with both source and output directories writable
docker run --rm -v "$(pwd)/tools:/source" --entrypoint="/app/build-scripts/build_exe.sh" wine-builder-test "combined_sprite_tools.py" "Godot_Sprite_Tools" ""

echo "=========================================="
echo "Build complete!"
echo "Check ./dist/ for your executable"