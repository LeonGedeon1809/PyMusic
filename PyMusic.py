import pygame
from pygame import mixer
import time
import os
import yt_dlp
import subprocess  # FFmpeg for conversion
import json
import sys

# Configuration management
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".pymusic")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

DEFAULT_CONFIG = {
    "download_folder": "downloads",
    "audio_quality": "192k",
    "audio_sample_rate": "44100",
    "audio_channels": "2",
    "volume": 0.7,
    "notifications": True
}

# Initialize pygame and load configuration
pygame.init()
pygame.mixer.init()
config = load_config()

def load_config():
    """Load configuration from file, creating default if not exists"""
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                # Merge with defaults to ensure all keys exist
                for key in DEFAULT_CONFIG:
                    if key not in config:
                        config[key] = DEFAULT_CONFIG[key]
                return config
        except (json.JSONDecodeError, IOError):
            print("Warning: Could not load config file, using defaults")
            return DEFAULT_CONFIG.copy()
    else:
        # Create default config file
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

def save_config(config):
    """Save configuration to file"""
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except IOError as e:
        print(f"Error saving config: {e}")
        return False

def show_options(config):
    """Display current configuration"""
    print("\nCurrent PyMusic Settings:")
    print("=" * 40)
    for key, value in config.items():
        print(f"{key}: {value}")
    print("=" * 40)
    print("Use 'options set <key> <value>' to change a setting")
    print("Use 'options reset' to restore defaults\n")

def set_option(config, key, value):
    """Set a configuration option"""
    if key not in DEFAULT_CONFIG:
        print(f"Error: Unknown setting '{key}'")
        print(f"Available settings: {', '.join(DEFAULT_CONFIG.keys())}")
        return config

    # Try to convert value to appropriate type
    try:
        # Try integer first
        if value.isdigit():
            value = int(value)
        # Try float
        elif '.' in value and all(c.isdigit() or c == '.' for c in value):
            value = float(value)
        # Try boolean
        elif value.lower() in ['true', 'false']:
            value = value.lower() == 'true'
        # Otherwise keep as string
    except AttributeError:
        pass  # value is not a string

    config[key] = value
    if save_config(config):
        print(f"Setting '{key}' updated to '{value}'")
    else:
        print(f"Warning: Setting updated in memory but failed to save to disk")

    return config

def reset_options():
    """Reset configuration to defaults"""
    if save_config(DEFAULT_CONFIG):
        print("All settings reset to defaults")
        return DEFAULT_CONFIG.copy()
    else:
        print("Error: Failed to reset settings")
        return load_config()  # Return current config on failure

def download_music(url, download_folder=None):
    # Use config download folder if not specified
    if download_folder is None:
        download_folder = config["download_folder"]

    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    ydl_opts = {
        'format': 'bestaudio/best',  # Downloads the best format
        'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
        'noplaylist': True,  # Does not download in playlists
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info_dict)
            print(f"Downloaded video: {filename}")
            return filename
    except Exception as e:
        print(f"Error downloading music: {e}")
        return None

def convert_webm_to_mp3(webm_file, output_folder=None):
    # Use config download folder if not specified
    if output_folder is None:
        output_folder = config["download_folder"]

    # Generating the output mp3 name
    mp3_file = os.path.splitext(webm_file)[0] + ".mp3"
    mp3_path = os.path.join(output_folder, mp3_file)

    # Using FFmpeg for converting webm to MP3
    # Check if ffmpeg is available
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: FFmpeg not found. Please install FFmpeg and ensure it's in your PATH.")
        print("On Ubuntu/Debian: sudo apt install ffmpeg")
        print("On macOS: brew install ffmpeg")
        print("On Windows: download from https://ffmpeg.org/download.html")
        return None

    command = [
        "ffmpeg", "-i", webm_file,  # Input webm file
        "-vn",  # No video
        "-acodec", "libmp3lame",  # Use codec MP3
        "-ac", config["audio_channels"],  # Stereo sound
        "-ar", config["audio_sample_rate"],  # Audio sample rate
        "-ab", config["audio_quality"],  # Audio bitrate
        mp3_path  # output MP3 file
    ]

    try:
        subprocess.run(command, check=True, capture_output=True)
        print(f"Converted WEBM to MP3: {mp3_path}")
        return mp3_path
    except subprocess.CalledProcessError as e:
        print(f"Error converting file: {e}")
        if e.stderr:
            print(f"FFmpeg error: {e.stderr.decode() if isinstance(e.stderr, bytes) else e.stderr}")
        return None
    except FileNotFoundError:
        print("Error: FFmpeg not found. Please install FFmpeg and ensure it's in your PATH.")
        return None

def show_help():
    print("commands: music, options, help")
    print("music: play, pause, resume, skip")
    print("options: show/set/reset - Manage PyMusic settings")
    print("help: show this help message")

master = input("Enter command: ")
if master == "help":
    while True:
        help_page = input("Enter help command: ")
        if help_page == "help":
            show_help()
        elif help_page == "help music":
            print("music: enter folder than: play, pause, resume, skip")
        elif help_page == "help download":
            print("To download music, enter a YouTube URL after the music command")
        elif help_page == "help options":
            print("options: show - Display current settings")
            print("         options set <key> <value> - Change a setting")
            print("         options reset - Reset all settings to defaults")
            print("         Available settings: download_folder, audio_quality, audio_sample_rate, audio_channels, volume, notifications")

# Loading music
if master == "music":
    load = input("Enter music folder or YouTube URL: ")
    if load.startswith("http"):
        # If URL, download music and convert it
        downloaded_file = download_music(load)
        if downloaded_file:
            mp3_file = convert_webm_to_mp3(downloaded_file)
            if mp3_file:
                pygame.mixer.music.load(mp3_file)
    elif os.path.exists(load):
        # If folder, load local music
        playlist = [os.path.join(load, f) for f in os.listdir(load) if f.endswith(".mp3")]
        if playlist:
            pygame.mixer.music.load(playlist[current_track])
            # Set volume from config
            pygame.mixer.music.set_volume(config["volume"])
        else:
            print("No music files found.")
    else:
        print("Folder or URL not found.")
elif master == "options":
    # Handle options command
    option_input = input("Enter options command (show/set/reset): ").strip()
    if option_input == "show":
        show_options(config)
    elif option_input.startswith("set "):
        parts = option_input[4:].split(maxsplit=1)
        if len(parts) == 2:
            key, value = parts
            config = set_option(config, key, value)
        else:
            print("Usage: options set <key> <value>")
    elif option_input == "reset":
        config = reset_options()
    else:
        print("Available options commands: show, set <key> <value>, reset")

# Playing, pausing, and skipping music
while True:
    player = input("Enter command: ")
    if player == "play":
        pygame.mixer.music.play()
        # Ensure volume is set from config
        pygame.mixer.music.set_volume(config["volume"])
    elif player == "pause":
        pygame.mixer.music.pause()
    elif player == "unpause":
        pygame.mixer.music.unpause()
    elif player == "skip":
        if playlist:
            current_track = (current_track + 1) % len(playlist)
            pygame.mixer.music.load(playlist[current_track])
            pygame.mixer.music.set_volume(config["volume"])
            pygame.mixer.music.play()
            print(f"Skipped to: {playlist[current_track]}")
        else:
            print("No loaded tracks to skip.")
    elif player == "quit":
        pygame.mixer.music.stop()
        print("Music player closed.")
        break
