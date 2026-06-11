# PyMusic Build Scripts

This directory contains scripts for building PyMusic for different platforms.

## Windows (.exe) Build

To build a standalone Windows executable:

1. Install Python 3.x on Windows
2. Install required dependencies:
   ```bash
   pip install pyinstaller pygame yt_dlp
   ```
3. Run the build script:
   ```bash
   python build/windows_build.py
   ```
4. The executable will be created in `dist/PyMusic.exe`

**Note**: The target machine will need FFmpeg installed and in PATH to use the YouTube download feature.

## Linux (AppImage) Build

To create a Linux AppImage:

1. Install required dependencies:
   ```bash
   # Ubuntu/Debian
   sudo apt install python3-pip python3-venv patchelf libfuse2
   
   # Fedora
   sudo dnf install python3 python3-venv patchelf fuse
   
   # Arch
   sudo pacman -S python python-venv patchelf fuse
   ```
2. Make the build script executable:
   ```bash
   chmod +x build/linux_build.sh
   ```
3. Run the build script:
   ```bash
   ./build/linux_build.sh
   ```
4. The AppImage will be created in the current directory (look for `PyMusic-*.AppImage`)

**Note**: The AppImage includes a basic set of dependencies, but users will still need FFmpeg installed on their system to use the YouTube download feature. The AppImage will check for FFmpeg at runtime and provide installation instructions if missing.

## Dependencies

Both builds require:
- Python 3.x
- pygame
- yt_dlp
- FFmpeg (separately installed, not bundled due to licensing)

The Windows build bundles the Python interpreter and required Python packages into a single executable using PyInstaller.
The Linux AppImage bundles a minimal Python environment with the application and dependencies.

## Testing

After building, test the executable/AppImage on a clean system to ensure all dependencies are properly included.
