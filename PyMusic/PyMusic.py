import pygame
from pygame import mixer
import time
import os
import yt_dlp
import subprocess  # FFmpeg for conversion
import json

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
    converted = value
    try:
        if value.lower() in ['true', 'false']:
            converted = value.lower() == 'true'
        elif value.lstrip('-').isdigit():
            converted = int(value)
        else:
            try:
                converted = float(value)
            except ValueError:
                converted = value  # keep as string
    except AttributeError:
        pass  # value is not a string

    # Validate volume range
    if key == "volume":
        try:
            converted = max(0.0, min(1.0, float(converted)))
        except (TypeError, ValueError):
            print("Error: volume must be a number between 0.0 and 1.0")
            return config

    config[key] = converted
    if save_config(config):
        print(f"Setting '{key}' updated to '{converted}'")
    else:
        print("Warning: Setting updated in memory but failed to save to disk")
    return config


def reset_options():
    """Reset configuration to defaults"""
    if save_config(DEFAULT_CONFIG):
        print("All settings reset to defaults")
        return DEFAULT_CONFIG.copy()
    else:
        print("Error: Failed to reset settings")
        return load_config()  # Return current config on failure


def check_ffmpeg():
    """Check if FFmpeg is available on PATH"""
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: FFmpeg not found. Please install FFmpeg and ensure it's in your PATH.")
        print("On Ubuntu/Debian: sudo apt install ffmpeg")
        print("On macOS: brew install ffmpeg")
        print("On Windows: download from https://ffmpeg.org/download.html")
        return False


def download_music(url, config, download_folder=None):
    """Download audio from a URL using yt_dlp. Returns the downloaded filepath or None."""
    if download_folder is None:
        download_folder = config["download_folder"]

    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info_dict)
            print(f"Downloaded: {filename}")
            return filename
    except Exception as e:
        print(f"Error downloading music: {e}")
        return None


def convert_to_mp3(input_file, config):
    """Convert a downloaded audio file to MP3 using FFmpeg. Returns the mp3 path or None."""
    mp3_path = os.path.splitext(input_file)[0] + ".mp3"

    if not check_ffmpeg():
        return None

    command = [
        "ffmpeg", "-y",
        "-i", input_file,
        "-vn",
        "-acodec", "libmp3lame",
        "-ac", str(config["audio_channels"]),
        "-ar", str(config["audio_sample_rate"]),
        "-ab", str(config["audio_quality"]),
        mp3_path
    ]

    try:
        subprocess.run(command, check=True, capture_output=True)
        print(f"Converted to MP3: {mp3_path}")
        # Remove the original non-mp3 file to avoid clutter
        if os.path.exists(input_file) and input_file != mp3_path:
            try:
                os.remove(input_file)
            except OSError:
                pass
        return mp3_path
    except subprocess.CalledProcessError as e:
        print(f"Error converting file: {e}")
        if e.stderr:
            print(f"FFmpeg error: {e.stderr.decode() if isinstance(e.stderr, bytes) else e.stderr}")
        return None
    except FileNotFoundError:
        print("Error: FFmpeg not found. Please install FFmpeg and ensure it's in your PATH.")
        return None


def show_help(topic=None):
    if topic is None:
        print("commands: music, options, help, quit")
        print("music: load a folder or YouTube URL, then control with play/pause/unpause/skip")
        print("options: show/set/reset - manage PyMusic settings")
        print("help <topic>: show help for 'music', 'download', or 'options'")
        print("quit: exit the program")
    elif topic == "music":
        print("music: enter a folder name (default 'music') or a YouTube URL.")
        print("Then use: play, pause, unpause, skip, quit")
    elif topic == "download":
        print("To download music, enter a YouTube URL when prompted for the music folder.")
        print("The audio is downloaded and converted to MP3 automatically (requires FFmpeg).")
    elif topic == "options":
        print("options show                  - Display current settings")
        print("options set <key> <value>     - Change a setting")
        print("options reset                 - Reset all settings to defaults")
        print(f"Available settings: {', '.join(DEFAULT_CONFIG.keys())}")
    else:
        print(f"No help available for '{topic}'. Try: help music / help download / help options")


def load_playlist(folder):
    """Return a sorted list of mp3 files in a folder."""
    return sorted(
        os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(".mp3")
    )


def play_track(playlist, index, config):
    """Load and play the track at `index`, applying configured volume."""
    pygame.mixer.music.load(playlist[index])
    pygame.mixer.music.set_volume(float(config["volume"]))
    pygame.mixer.music.play()


def music_loop(config, playlist, current_track):
    """Inner command loop for controlling playback."""
    while True:
        player = input("Enter command: ").strip().lower()

        if player == "play":
            try:
                pygame.mixer.music.play()
                pygame.mixer.music.set_volume(float(config["volume"]))
            except pygame.error as e:
                print(f"Error: no track loaded ({e})")

        elif player == "pause":
            pygame.mixer.music.pause()

        elif player == "unpause":
            pygame.mixer.music.unpause()

        elif player == "skip":
            if playlist:
                current_track = (current_track + 1) % len(playlist)
                try:
                    play_track(playlist, current_track, config)
                    print(f"Skipped to: {playlist[current_track]}")
                except pygame.error as e:
                    print(f"Error loading track: {e}")
            else:
                print("No loaded tracks to skip.")

        elif player == "quit":
            pygame.mixer.music.stop()
            print("Music player closed.")
            break

        elif player == "help":
            show_help("music")

        else:
            print("Unknown command. Try: play, pause, unpause, skip, quit, help")


def main():
    pygame.init()
    pygame.mixer.init()
    config = load_config()

    playlist = []
    current_track = 0

    print("PyMusic - type 'help' for commands")

    while True:
        master = input("Enter command: ").strip().lower()

        if master == "help":
            help_page = input("Enter help command (or press Enter for general help): ").strip().lower()
            if help_page == "":
                show_help()
            elif help_page.startswith("help "):
                show_help(help_page[5:])
            else:
                show_help(help_page)

        elif master == "music":
            load = input("Enter music folder or YouTube URL (default: music): ").strip()
            if load == "":
                load = "music"

            if load.startswith("http://") or load.startswith("https://"):
                downloaded_file = download_music(load, config)
                if downloaded_file:
                    mp3_file = convert_to_mp3(downloaded_file, config)
                    if mp3_file:
                        playlist = [mp3_file]
                        current_track = 0
                        try:
                            play_track(playlist, current_track, config)
                            print("Track loaded. Use 'play' to start (or it may already be playing).")
                            music_loop(config, playlist, current_track)
                        except pygame.error as e:
                            print(f"Error loading track: {e}")
                    else:
                        print("Conversion failed; nothing loaded.")
                else:
                    print("Download failed; nothing loaded.")

            elif os.path.isdir(load):
                playlist = load_playlist(load)
                current_track = 0
                if playlist:
                    try:
                        play_track(playlist, current_track, config)
                        print(f"Loaded {len(playlist)} track(s). Now playing: {playlist[current_track]}")
                        music_loop(config, playlist, current_track)
                    except pygame.error as e:
                        print(f"Error loading track: {e}")
                else:
                    print("No MP3 files found in that folder.")

            else:
                print("Folder or URL not found.")

        elif master == "options":
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

        elif master == "quit":
            print("Goodbye.")
            break

        else:
            print("Unknown command. Type 'help' for a list of commands.")

    pygame.quit()


if __name__ == "__main__":
    main()
