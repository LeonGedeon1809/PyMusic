import pygame
from pygame import mixer
import time
import os
import yt_dlp
import subprocess  # FFmpeg for conversion

pygame.init()
pygame.mixer.init()

playlist = []
current_track = 0

def download_music(url, download_folder="downloads"):
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

def convert_webm_to_mp3(webm_file, output_folder="downloads"):
    # Generating the otput mp3 name
    mp3_file = os.path.splitext(webm_file)[0] + ".mp3"
    mp3_path = os.path.join(output_folder, mp3_file)

    # Using FFpmeg for converting webm to MP3
    command = [
        "ffmpeg", "-i", webm_file,  # Input webm file
        "-vn",  # Nepoužívaj video
        "-acodec", "libmp3lame",  # Use codec MP3
        "-ac", "2",  # Stereo sound
        "-ar", "44100",  # 44.1 kHz
        "-ab", "192k",  # 192 kbps
        mp3_path  # output MP3 file
    ]
    
    try:
        subprocess.run(command, check=True)
        print(f"Converted MP4 to MP3: {mp3_path}")
        return mp3_path
    except subprocess.CalledProcessError as e:
        print(f"Error converting file: {e}")
        return None

def show_help():
    print("commands: music")
    print("music: play, pause, resume, skip")

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
        else:
            print("No music files found.")
    else:
        print("Folder or URL not found.")

# Playing, pausing, and skipping music
while True:
    player = input("Enter command: ")
    if player == "play":
        pygame.mixer.music.play()
    elif player == "pause":
        pygame.mixer.music.pause()
    elif player == "unpause":
        pygame.mixer.music.unpause()
    elif player == "skip":
        if playlist:
            current_track = (current_track + 1) % len(playlist)
            pygame.mixer.music.load(playlist[current_track])
            pygame.mixer.music.play()
            print(f"Skipped to: {playlist[current_track]}")
        else:
            print("No loaded tracks to skip.")
    elif player == "quit":
        pygame.mixer.music.stop()
        print("Music player closed.")
        break