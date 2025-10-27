# Multi-stage Wine-based Windows executable builder
FROM ubuntu:20.04 AS base

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install Wine and dependencies
RUN dpkg --add-architecture i386 && apt-get -qq update && apt-get -qq -y install \
    wine \
    wine32 \
    wine64 \
    libwine \
    libwine:i386 \
    fonts-wine \
    xvfb \
    cabextract \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN apt-get -qq update && apt-get -qq -y install \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Set up Wine environment
ENV WINEPREFIX=/root/.wine
ENV WINEARCH=win32
ENV WINEDEBUG=fixme-all
RUN wineboot --init

# Install Python 3.12 embeddable in Wine for PyInstaller (simpler approach)
RUN apt-get -qq update && apt-get -qq -y install wget unzip cabextract p7zip-full \
    && rm -rf /var/lib/apt/lists/*

# Download and extract Python 3.12 embeddable to Wine
RUN cd /tmp \
    && wget -O python312.zip https://www.python.org/ftp/python/3.12.7/python-3.12.7-embed-win32.zip \
    && mkdir -p $WINEPREFIX/drive_c/Python312 \
    && cd $WINEPREFIX/drive_c/Python312 \
    && unzip /tmp/python312.zip \
    && sed -i 's|# Lib/site-packages|Lib/site-packages|' python312._pth \
    && echo "import site" >> python312._pth \
    && echo "uncommented Lib/site-packages in python312._pth" \
    && rm /tmp/python312.zip

# Don't create fake tkinter module - let PyInstaller handle tkinter properly
# PyInstaller will reference tkinter at runtime when the executable runs on target systems

# Install PyInstaller by extracting cached wheels offline
COPY pyinstaller_cache /tmp/pyinstaller_cache/
RUN mkdir -p $WINEPREFIX/drive_c/Python312/Lib/site-packages && \
    for whl in /tmp/pyinstaller_cache/*.whl; do \
        if unzip -l "$whl" >/dev/null 2>&1; then \
            unzip "$whl" -d $WINEPREFIX/drive_c/Python312/Lib/site-packages/ || true; \
        fi; \
    done

# Install common dependencies that tools might need
RUN python3 -m pip install pillow pywin32-ctypes

# Test tkinter installation (non-fatal)
RUN xvfb-run wine C:\\Python312\\python.exe -c "import tkinter; print('Tkinter installed successfully')" || echo "Warning: Tkinter not available in Wine environment. Executable will require tkinter on target system."

FROM base AS builder

# Set working directory
WORKDIR /app

# Copy build scripts
COPY build-scripts/ /app/build-scripts/

# Make build script executable
RUN chmod +x /app/build-scripts/*.sh

# Volume mount point for source (output goes to source directory)
VOLUME ["/source"]

# Default entrypoint
ENTRYPOINT ["/app/build-scripts/build_exe.sh"]