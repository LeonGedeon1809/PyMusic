# PyMusic
Tired of GUI? You can use this lightweight music player completely 
coded in python. Controlled only using commands. It's simple
and functional without the luxury of GUI - pure CLI.
## Usage
Main command: `music`

You basically just type `music` to the terminal or whatever
when it asks you about folder name you just type out your 
playlist name (default: `music`)
or a YouTube URL then the player loads it.

### After loading
You can control it with the following commands:

- `play` - Start/resume playback
- `pause` - Pause playback
- `unpause` - Resume playback (same as play when paused)
- `skip` - Skip to next track in playlist
- `quit` - Exit the music player

### Options Command
Manage PyMusic settings with the `options` command:
- `options show` - Display current settings
- `options set <key> <value>` - Change a setting (e.g., `options set volume 0.5`)
- `options reset` - Reset all settings to defaults

Available settings:
- `download_folder`: Folder for downloaded music (default: "downloads")
- `audio_quality`: Audio bitrate for conversion (default: "192k")
- `audio_sample_rate`: Audio sample rate (default: "44100")
- `audio_channels`: Number of audio channels (default: "2")
- `volume`: Playback volume (0.0 to 1.0, default: 0.7)
- `notifications`: Enable/disable informational messages (default: true)

## Dependencies
- **Pygame** - For playing music
- **yt_dlp** - For downloading from YouTube
- **FFmpeg** - For converting downloaded audio to MP3 (required for YouTube feature)

Install Python dependencies with pip:
```bash
pip install pygame yt_dlp
```

**Important**: FFmpeg must be installed separately and available in your system PATH.
- Ubuntu/Debian: `sudo apt install ffmpeg`
- macOS: `brew install ffmpeg`
- Windows: Download from https://ffmpeg.org/download.html and add to PATH

## Features
- Play local MP3 files from a folder
- Download audio from YouTube URLs and automatically convert to MP3
- Persistent settings via configuration file (~/.pymusic/config.json)
- Cross-platform support (Windows .exe and Linux AppImage builds available)
- Simple CLI interface with helpful error messages

## Building Distributable Versions
See the `build/` directory for scripts to create:
- Windows standalone executable (.exe) using PyInstaller
- Linux AppImage for portable distribution

## Notes
- The downloader downloads audio in WebM format which is then converted to MP3 using FFmpeg.
- If FFmpeg is not installed or not in PATH, the player will show clear installation instructions.
- Local music playback works without FFmpeg (only YouTube download/conversion requires it).
- Settings are saved between sessions in `~/.pymusic/config.json`.
