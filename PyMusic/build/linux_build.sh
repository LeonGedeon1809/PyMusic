#!/bin/bash
# Linux AppImage build script for PyMusic
# Run this script on Linux to create an AppImage

set -e  # Exit on any error

echo "Building PyMusic for Linux as AppImage..."

# Ensure we're in the right directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( dirname "$SCRIPT_DIR" )"
cd "$PROJECT_DIR"

# Check for required tools
command -v python3 >/dev/null 2>&1 || { echo "Error: python3 required but not installed."; exit 1; }
command -v patchelf >/dev/null 2>&1 || { echo "Error: patchelf required but not installed."; exit 1; }

# Clean previous builds
rm -rf build dist AppDir
mkdir -p build dist AppDir/usr/bin AppDir/usr/lib

echo "Creating virtual environment and installing dependencies..."
python3 -m venv build/venv
source build/venv/bin/activate

# Install dependencies
pip install pygame yt_dlp

# Create the application directory structure
mkdir -p AppDir/usr/share/applications
mkdir -p AppDir/usr/share/pixmaps
mkdir -p AppDir/usr/share/icons/hicolor/256x256/apps

# Copy the main script and dependencies
cp PyMusic.py AppDir/usr/bin/
cp Py.ico AppDir/usr/share/pixmaps/pymusic.ico 2>/dev/null || true
cp Py.ico AppDir/usr/share/icons/hicolor/256x256/apps/pymusic.png 2>/dev/null || true

# Create a desktop file
cat > AppDir/usr/share/applications/pymusic.desktop << EOF
[Desktop Entry]
Name=PyMusic
Comment=Command-line music player with YouTube support
Exec=pymusic
Icon=pymusic
Terminal=true
Type=Application
Categories=AudioVideo;Player;Audio;
