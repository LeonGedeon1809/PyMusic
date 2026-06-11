#!/usr/bin/env python3
"""
Windows build script for PyMusic using PyInstaller
Run this script on Windows to create a standalone .exe executable
"""

import os
import sys
import subprocess
import shutil

def main():
    print("Building PyMusic for Windows using PyInstaller...")
    
    # Ensure we're in the right directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    os.chdir(project_dir)
    
    # Check if PyInstaller is available
    try:
        import PyInstaller
        print(f"Using PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Clean previous builds
    build_dirs = ["build", "dist"]
    for dir_name in build_dirs:
        if os.path.exists(dir_name):
            print(f"Removing {dir_name}...")
            shutil.rmtree(dir_name)
    
    # PyInstaller command
    pyinstaller_cmd = [
        "pyinstaller",
        "--onefile",  # Create a single executable file
        "--windowed",  # No console window (GUI app)
        "--name=PyMusic",  # Executable name
        "--icon=Py.ico",  # Icon file
        "--add-data=_internal;_internal",  # Include internal dependencies
        "PyMusic.py"
    ]
    
    print("Running PyInstaller...")
    print(" ".join(pyinstaller_cmd))
    
    try:
        subprocess.check_call(pyinstaller_cmd)
        print("\nBuild successful!")
        print("Executable created: dist/PyMusic.exe")
        print("\nTo distribute:")
        print("1. Copy dist/PyMusic.exe to target Windows machine")
        print("2. Ensure FFmpeg is installed and in PATH on target machine")
        print("3. The executable will create a .pymusic folder in the user's home directory for settings")
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed with error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
