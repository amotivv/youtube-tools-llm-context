#!/usr/bin/env python3
"""
YouTube Media Downloader
A comprehensive tool for downloading YouTube videos (MP4) and audio (MP3)
"""

import sys
import os
import argparse
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    print("Error: yt-dlp is not installed.")
    print("Please install it using: pip install yt-dlp")
    sys.exit(1)

def download_video(url, output_dir=None, quality='best'):
    """
    Download a YouTube video in MP4 format
    
    Args:
        url (str): YouTube video URL
        output_dir (str, optional): Output directory path
        quality (str): Video quality (best, 1080, 720, 480, 360)
    
    Returns:
        str: Path to the downloaded video file
    """
    # Set output directory
    if output_dir is None:
        output_dir = os.getcwd()
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure quality format string
    if quality == 'best':
        format_str = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
    else:
        format_str = f'bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/best[height<={quality}][ext=mp4]/best'
    
    # Configure yt-dlp options
    ydl_opts = {
        'format': format_str,
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'quiet': False,
        'no_warnings': False,
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Downloading video from: {url}")
            print(f"Quality: {quality}")
            print(f"Output directory: {output_dir}")
            print("-" * 50)
            
            # Extract and download
            info = ydl.extract_info(url, download=True)
            video_title = info.get('title', 'Unknown')
            video_file = os.path.join(output_dir, f"{video_title}.mp4")
            
            print(f"\n✅ Video downloaded successfully!")
            print(f"File: {video_file}")
            return video_file
            
    except Exception as e:
        print(f"\n❌ Error downloading video: {str(e)}")
        return None

def download_audio(url, output_dir=None, quality='192'):
    """
    Download audio from a YouTube video and save as MP3
    
    Args:
        url (str): YouTube video URL
        output_dir (str, optional): Directory to save the downloaded audio
        quality (str): Audio bitrate (320, 256, 192, 128)
    
    Returns:
        str: Path to the downloaded MP3 file
    """
    # Set output directory
    if output_dir is None:
        output_dir = os.getcwd()
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure yt-dlp options
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': quality,
        }],
        'quiet': False,
        'no_warnings': False
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Downloading audio from: {url}")
            print(f"Audio quality: {quality}kbps")
            print(f"Output directory: {output_dir}")
            print("-" * 50)
            
            # Extract and download
            info = ydl.extract_info(url, download=True)
            audio_title = info.get('title', 'Unknown')
            mp3_file = os.path.join(output_dir, f"{audio_title}.mp3")
            
            print(f"\n✅ Audio downloaded successfully!")
            print(f"File: {mp3_file}")
            return mp3_file
            
    except Exception as e:
        print(f"\n❌ Error downloading audio: {str(e)}")
        return None

def download_both(url, output_dir=None, video_quality='best', audio_quality='192'):
    """
    Download both video and audio from a YouTube video
    
    Args:
        url (str): YouTube video URL
        output_dir (str, optional): Output directory path
        video_quality (str): Video quality
        audio_quality (str): Audio bitrate
    
    Returns:
        tuple: (video_path, audio_path)
    """
    print("📥 Downloading both video and audio...\n")
    
    # Download video
    print("🎬 Step 1/2: Downloading video")
    video_path = download_video(url, output_dir, video_quality)
    
    if video_path:
        print("\n🎵 Step 2/2: Downloading audio")
        audio_path = download_audio(url, output_dir, audio_quality)
        
        if audio_path:
            print("\n✅ Both video and audio downloaded successfully!")
            return video_path, audio_path
    
    return None, None

def main():
    parser = argparse.ArgumentParser(
        description='YouTube Media Downloader - Download videos (MP4) and/or audio (MP3)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Download video only:
    %(prog)s -v https://youtube.com/watch?v=VIDEO_ID
    %(prog)s -v https://youtube.com/watch?v=VIDEO_ID -o ~/Downloads
    %(prog)s -v https://youtube.com/watch?v=VIDEO_ID --vq 720
  
  Download audio only:
    %(prog)s -a https://youtube.com/watch?v=VIDEO_ID
    %(prog)s -a https://youtube.com/watch?v=VIDEO_ID -o ~/Music
    %(prog)s -a https://youtube.com/watch?v=VIDEO_ID --aq 320
  
  Download both:
    %(prog)s -b https://youtube.com/watch?v=VIDEO_ID
    %(prog)s -b https://youtube.com/watch?v=VIDEO_ID -o ~/Media --vq 1080 --aq 320
        """
    )
    
    # URL argument
    parser.add_argument('url', help='YouTube video URL')
    
    # Mode selection (mutually exclusive group)
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('-v', '--video', action='store_true', 
                           help='Download video only (MP4)')
    mode_group.add_argument('-a', '--audio', action='store_true', 
                           help='Download audio only (MP3)')
    mode_group.add_argument('-b', '--both', action='store_true', 
                           help='Download both video and audio')
    
    # Output options
    parser.add_argument('-o', '--output', type=str, 
                       help='Output directory (default: current directory)')
    
    # Quality options
    parser.add_argument('--vq', '--video-quality', dest='video_quality',
                       choices=['best', '1080', '720', '480', '360'],
                       default='best',
                       help='Video quality (default: best)')
    parser.add_argument('--aq', '--audio-quality', dest='audio_quality',
                       choices=['320', '256', '192', '128'],
                       default='192',
                       help='Audio quality in kbps (default: 192)')
    
    args = parser.parse_args()
    
    # Validate URL
    if not args.url.startswith(('http://', 'https://')):
        print("Error: Please provide a valid URL starting with http:// or https://")
        sys.exit(1)
    
    if 'youtube.com/watch' not in args.url and 'youtu.be/' not in args.url:
        print("Warning: This doesn't appear to be a YouTube URL. Attempting download anyway...")
    
    # Execute based on mode
    print(f"🚀 YouTube Media Downloader\n")
    
    if args.video:
        download_video(args.url, args.output, args.video_quality)
    elif args.audio:
        download_audio(args.url, args.output, args.audio_quality)
    elif args.both:
        download_both(args.url, args.output, args.video_quality, args.audio_quality)

if __name__ == "__main__":
    main()
