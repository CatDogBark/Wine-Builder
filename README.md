# Wine Executable Builder

A Docker-based Windows executable builder using Wine and PyInstaller. Create stand-alone Windows .exe files from Python applications on Linux/macOS systems.

## Overview

This project provides a reusable environment for building Windows executables from Python tools using Wine (Windows emulation) + PyInstaller. Perfect for cross-platform development where you want to create Windows executables without running Windows.

## Current Tools

The following Python tools are included and can be built into Windows executables:

- **Combined Sprite Tools**: Unified GUI for all sprite processing tools
- **Sprite Frame Editor**: Interactive tool for editing spritesheets
- **Sprite Frame Sizer**: Resize frames to standard sizes (64x64, 128x128, 256x256)
- **Spritesheet Combiner**: Combine multiple animation spritesheets into one
- **Spritesheet Analyzer**: Analyze spritesheets to determine grid layouts

## Quick Start

### Build All Sprite Tools Suite
```bash
./scripts/build_sprite_tools.sh
```

### Build Individual Tools
```bash
# Build Sprite Frame Editor
docker-compose -f docker-compose.yml -f docker-compose.override.sprite-frame-editor.yml up

# Or use the generic builder
./scripts/build_tool.sh "Sprite Frame Editor" "editor/sprite_frame_editor.py" "Sprite_Frame_Editor"
```

## How It Works

1. **Docker Image**: Multi-stage build with Ubuntu + Wine + Python + PyInstaller
2. **Volume Mounting**: Source code and dependencies mounted into container
3. **Wine Environment**: Windows-compatible executables built using Wine emulation
4. **Output**: Windows .exe files copied to local `dist/` directory

## Project Structure

```
wine-builder/
├── Dockerfile                  # Multi-stage Wine + PyInstaller build
├── docker-compose.yml          # Main compose file with volumes/env vars
├── build-scripts/              # Build scripts run inside container
│   └── build_exe.sh           # Main build script for PyInstaller
├── scripts/                    # Helper scripts for building
│   ├── build_sprite_tools.sh  # Build the combined tools suite
│   └── build_tool.sh          # Generic tool builder
├── tools/                      # Your Python tools and scripts
│   ├── combined_sprite_tools.py
│   ├── requirements.txt       # Dependencies for sprite tools
│   └── editor/
│   └── spritesheet-combiner/
│   └── ...
├── dist/                       # Built executables output here
└── README.md
```

## For New Tools

### Method 1: Use the Generic Builder Script

```bash
# Build any Python script as Windows executable
./scripts/build_tool.sh "My New Tool" "path/to/my_script.py" "My_New_Tool" "--icon=my_icon.ico"
```

### Method 2: Create Custom Docker Compose Override

Create `docker-compose.override.mytool.yml`:
```yaml
version: '3.8'
services:
  wine-builder:
    environment:
      - PYTHON_SCRIPT=path/to/your_script.py
      - EXECUTABLE_NAME=My_New_Tool
      - EXTRA_PYINSTALLER_ARGS=--icon=my_icon.ico
```

Then build:
```bash
docker-compose -f docker-compose.yml -f docker-compose.override.mytool.yml up
```

### Method 3: Direct Docker Compose Commands

```bash
# Build once
docker-compose build

# Build your tool
PYTHON_SCRIPT="path/to/script.py" \
EXECUTABLE_NAME="ToolName" \
EXTRA_PYINSTALLER_ARGS="--hidden-import=mylib" \
docker-compose up
```

## Dependencies

### For Your Python Tools

Create a `tools/requirements.txt` file with your Python dependencies:

```
Pillow>=8.0.0
numpy>=1.20.0
requests>=2.25.0
```

The build system will automatically install these dependencies inside the Wine environment.

### System Requirements

- Docker
- Docker Compose
- Linux/macOS host system (no Windows required!)
- At least 4GB RAM recommended

## Build Process Details

1. **Base Image**: Ubuntu with Wine, Python, and PyInstaller
2. **Dependency Installation**: `pip install -r requirements.txt`
3. **Windows Environment Setup**: Wine configuration and initialization
4. **PyInstaller Build**: `--onefile --windowed` for GUI applications
5. **Executable Extraction**: Copy .exe to host `dist/` directory

## PyInstaller Options

The build system supports these PyInstaller arguments via `EXTRA_PYINSTALLER_ARGS`:

```bash
# GUI application (default)
--windowed

# Console application
--console

# Add icons
--icon=my_icon.ico

# Hidden imports for problematic modules
--hidden-import=problem_module
--hidden-import=tkinter

# Add data files
--add-data "data/*;data/"
```

## Troubleshooting

### Common Issues

1. **"Python not found in Wine"**
   - Docker image might need rebuild: `docker-compose build --no-cache`

2. **"Module not found" errors**
   - Add missing imports to `EXTRA_PYINSTALLER_ARGS`: `--hidden-import=missing_module`

3. **GUI not working**
   - X11 display issues: Add `DISPLAY` environment variables for GUI debugging

4. **Build hangs**
   - Wine initialization can be slow on first run. Wait 2-3 minutes.

### Debug Mode

For debugging Wine applications, uncomment the GUI section in `docker-compose.yml`:

```yaml
environment:
  - DISPLAY=$DISPLAY
devices:
  - /dev/dri:/dev/dri
volumes:
  - /tmp/.X11-unix:/tmp/.X11-unix:ro
network_mode: host
```

## Advanced Usage

### Custom Docker Image

Modify `Dockerfile` to add custom Python versions, system libraries, or Windows SDKs.

### Multiple Tool Builds

Create a `Makefile` or bash script to build multiple tools:

```bash
#!/bin/bash
# Build all tools
TOOLS=("sprite_editor editor/sprite_frame_editor.py Sprite_Frame_Editor"
       "sprite_sizer spriteframe-sizer/sprite_frame_sizer.py Sprite_Frame_Sizer"
       "sheet_combiner spritesheet-combiner/spritesheet_combiner.py Spritesheet_Combiner"
       "sheet_analyzer spritesheet-id/spritesheet_analyzer.py Spritesheet_Analyzer")

for tool in "${TOOLS[@]}"; do
    ./scripts/build_tool.sh $tool
done
```

### CI/CD Integration

Use in GitHub Actions, GitLab CI, or other pipelines:

```yaml
- name: Build Windows Executables
  run: |
    docker-compose build
    ./scripts/build_tool.sh "MyApp" "main.py" "MyApp"
```

## Contributing

1. Add your Python tool to the `tools/` directory
2. Create a `requirements.txt` with dependencies
3. Test the build: `./scripts/build_tool.sh "ToolName" "path/to/script.py" "ExecutableName"`
4. Create a docker-compose override file for your tool
5. Update this README with your new tool

## License

This project provides a build environment. Individual tools may have their own licenses.