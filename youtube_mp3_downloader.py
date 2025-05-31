#!/usr/bin/env python3

import os
import sys
import argparse
from pathlib import Path
import yt_dlp

def download_audio(url, output_dir=None):
    """
    Download audio from a YouTube video and save as MP3.
    
    Args:
        url (str): YouTube video URL
        output_dir (str, optional): Directory to save the downloaded audio
    
    Returns:
        str: Path to the downloaded MP3 file
    """
    try:
        # Set output directory
        if not output_dir:
            output_dir = os.getcwd()
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Configure yt-dlp options
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': False,
            'no_warnings': False
        }
        
        # Download the audio file
        print(f"Downloading audio from: {url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            mp3_file = os.path.join(output_dir, f"{info['title']}.mp3")
        
        print(f"Successfully downloaded: {os.path.basename(mp3_file)}")
        print(f"Saved to: {mp3_file}")
        
        return mp3_file
    
    except Exception as e:
        print(f"Error downloading video: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Download YouTube audio as MP3')
    parser.add_argument('url', help='YouTube video URL')
    parser.add_argument('-o', '--output', help='Output directory (optional)')
    
    args = parser.parse_args()
    
    download_audio(args.url, args.output)

if __name__ == "__main__":
    main()