#!/usr/bin/env python3
"""
YouTube Video Downloader Script
Downloads YouTube videos in MP4 format using yt-dlp
"""

import sys
import os
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    print("Error: yt-dlp is not installed.")
    print("Please install it using: pip install yt-dlp")
    sys.exit(1)

def download_youtube_video(url, output_path=None):
    """
    Download a YouTube video in MP4 format
    
    Args:
        url (str): YouTube video URL
        output_path (str, optional): Output directory path. Defaults to current directory.
    """
    # Set output directory
    if output_path is None:
        output_path = os.getcwd()
    else:
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)
    
    # Configure yt-dlp options
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',  # Prefer MP4
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),  # Output filename template
        'merge_output_format': 'mp4',  # Ensure output is MP4
        'quiet': False,  # Show download progress
        'no_warnings': False,
        'extract_flat': False,
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',  # Convert to MP4 if needed
        }],
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Accept-Encoding': 'gzip,deflate',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Downloading video from: {url}")
            print(f"Output directory: {output_path}")
            print("-" * 50)
            
            # Extract video info first (optional, for displaying title)
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'Unknown')
            print(f"Video title: {video_title}")
            print("-" * 50)
            
            # Download the video
            ydl.download([url])
            
            print("\n✅ Download completed successfully!")
            
    except yt_dlp.utils.DownloadError as e:
        print(f"\n❌ Download error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)

def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) < 2:
        print("Usage: python youtube_downloader.py <YouTube_URL> [output_directory]")
        print("Example: python youtube_downloader.py https://www.youtube.com/watch?v=VIDEO_ID")
        print("Example: python youtube_downloader.py https://www.youtube.com/watch?v=VIDEO_ID ~/Downloads")
        sys.exit(1)
    
    url = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Basic URL validation
    if not url.startswith(('http://', 'https://')):
        print("Error: Please provide a valid URL starting with http:// or https://")
        sys.exit(1)
    
    if 'youtube.com/watch' not in url and 'youtu.be/' not in url:
        print("Warning: This doesn't appear to be a YouTube URL. Attempting download anyway...")
    
    download_youtube_video(url, output_path)

if __name__ == "__main__":
    main()
