# 🎬 YouTube Downloader & Transcription Suite

A comprehensive collection of Python scripts for downloading YouTube content and transcribing audio files. Download videos, extract audio, and generate accurate transcriptions with timestamps, all in one powerful toolkit.

![Python](https://img.shields.io/badge/python-3.6+-blue.svg)
![yt-dlp](https://img.shields.io/badge/yt--dlp-latest-green.svg)
![AssemblyAI](https://img.shields.io/badge/AssemblyAI-API-orange.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

## 📋 Table of Contents

- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Scripts Overview](#-scripts-overview)
- [Usage Examples](#-usage-examples)
- [Advanced Options](#-advanced-options)
- [Transcription Workflow](#-transcription-workflow)
- [Troubleshooting](#-troubleshooting)
- [Technical Details](#-technical-details)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

- **🎵 Audio Downloads**: Extract high-quality MP3 audio from YouTube videos
- **🎥 Video Downloads**: Download videos in MP4 format with customizable quality
- **📦 Combined Tool**: All-in-one solution for both video and audio downloads
- **🎙️ Audio Transcription**: Convert speech to text using AssemblyAI
- **📝 Multiple Output Formats**: Transcripts, subtitles (SRT), paragraphs, sentences, and JSON
- **⚡ Fast & Reliable**: Built on yt-dlp for robust performance
- **🎯 Quality Control**: Choose your preferred video resolution and audio bitrate
- **📁 Flexible Output**: Specify custom download directories
- **🛡️ Error Handling**: Graceful error messages and recovery
- **📊 Progress Tracking**: Real-time download and transcription progress

## 🔧 Prerequisites

### Required

- **Python 3.6+**: Ensure you have Python installed
  ```bash
  python --version
  ```

- **yt-dlp**: The core downloading engine
  ```bash
  pip install yt-dlp
  ```

- **requests**: For API calls (required for transcription)
  ```bash
  pip install requests
  ```

- **python-dotenv**: For environment variable management
  ```bash
  pip install python-dotenv
  ```

### Recommended

- **FFmpeg**: For audio extraction and format conversion
  
  **Windows:**
  - Download from [ffmpeg.org](https://ffmpeg.org/download.html)
  - Add to PATH or place in script directory
  
  **macOS:**
  ```bash
  brew install ffmpeg
  ```
  
  **Linux (Ubuntu/Debian):**
  ```bash
  sudo apt update
  sudo apt install ffmpeg
  ```
  
  **Linux (Fedora/RHEL):**
  ```bash
  sudo dnf install ffmpeg
  ```

## 📥 Installation

1. **Clone or download the scripts:**
   ```bash
   git clone https://github.com/yourusername/youtube-downloader-suite.git
   cd youtube-downloader-suite
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   Or manually:
   ```bash
   pip install yt-dlp
   ```

3. **Make scripts executable (Linux/macOS):**
   ```bash
   chmod +x youtube_*.py
   ```

## 📚 Scripts Overview

### 1. `youtube_mp3_downloader.py` - Audio Specialist

Dedicated audio extraction tool that converts YouTube videos to MP3 format.

**Key Features:**
- Extracts best available audio quality
- Configurable bitrate (128-320 kbps)
- Automatic metadata preservation
- Minimal file size with maximum quality

### 2. `youtube_mp4_downloader.py` - Video Specialist  

Focused video downloader optimized for MP4 format compatibility.

**Key Features:**
- Smart format selection (best video + audio combination)
- Resolution options (360p to 4K)
- Hardware acceleration support
- Automatic format conversion to MP4

### 3. `youtube_combined_downloader.py` - Universal Tool

The Swiss Army knife of YouTube downloading - handles everything in one script.

**Key Features:**
- Three modes: video-only, audio-only, or both
- All features from specialized scripts
- Unified command-line interface
- Batch processing capabilities

### 4. `audio_transcriber.py` - Transcription Tool

Powerful transcription tool using AssemblyAI API for converting audio to text.

**Key Features:**
- High-accuracy speech-to-text conversion
- Multiple output formats (text, SRT, paragraphs, sentences, JSON)
- Speaker diarization (identify different speakers)
- Timestamp preservation for all formats
- Perfect integration with downloaded YouTube audio

## 🚀 Usage Examples

### Basic Usage

#### Audio Download (MP3)
```bash
# Using the specialized audio script
python youtube_mp3_downloader.py https://www.youtube.com/watch?v=dQw4w9WgXcQ

# Specify output directory
python youtube_mp3_downloader.py https://www.youtube.com/watch?v=dQw4w9WgXcQ -o ~/Music
```

#### Video Download (MP4)
```bash
# Using the specialized video script
python youtube_mp4_downloader.py https://www.youtube.com/watch?v=dQw4w9WgXcQ

# Specify output directory
python youtube_mp4_downloader.py https://www.youtube.com/watch?v=dQw4w9WgXcQ ~/Videos
```

#### Combined Downloader
```bash
# Download video only
python youtube_combined_downloader.py -v https://www.youtube.com/watch?v=dQw4w9WgXcQ

# Download audio only
python youtube_combined_downloader.py -a https://www.youtube.com/watch?v=dQw4w9WgXcQ

# Download both video and audio
python youtube_combined_downloader.py -b https://www.youtube.com/watch?v=dQw4w9WgXcQ

# With quality options
python youtube_combined_downloader.py -v URL --vq 1080  # 1080p video
python youtube_combined_downloader.py -a URL --aq 320   # 320kbps audio
python youtube_combined_downloader.py -b URL --vq 720 --aq 256  # Custom qualities for both
```

#### Audio Transcription
```bash
# Basic transcription
python audio_transcriber.py audio.mp3 --api-key YOUR_API_KEY

# Using environment variable for API key
export ASSEMBLYAI_API_KEY=YOUR_API_KEY
python audio_transcriber.py audio.mp3

# Save all transcript formats
python audio_transcriber.py audio.mp3 --all-formats

# Generate subtitles only
python audio_transcriber.py audio.mp3 --srt

# Transcribe with speaker identification
python audio_transcriber.py podcast.mp3 --speaker-labels --paragraphs

# Multiple specific formats
python audio_transcriber.py audio.mp3 --paragraphs --sentences --srt
```

### Advanced Examples

```bash
# Download playlist (audio only)
python youtube_mp3_downloader.py "https://www.youtube.com/playlist?list=PLAYLIST_ID" -o ~/Music/Playlist

# Download with custom filename template (combined downloader)
python youtube_combined_downloader.py -v URL -o ~/Videos --template "%(upload_date)s-%(title)s"

# Download age-restricted content (requires cookies)
python youtube_mp4_downloader.py URL --cookies youtube_cookies.txt

# Complete workflow: Download and transcribe
python youtube_combined_downloader.py -a URL && python audio_transcriber.py *.mp3 --all-formats
```

## 🎯 Transcription Workflow

### Complete YouTube to Text Pipeline

1. **Download audio from YouTube:**
   ```bash
   python youtube_mp3_downloader.py https://youtube.com/watch?v=VIDEO_ID
   ```

2. **Transcribe the audio:**
   ```bash
   python audio_transcriber.py "Video_Title.mp3" --all-formats
   ```

3. **Or do it in one command:**
   ```bash
   # Download audio and transcribe with subtitles
   python youtube_combined_downloader.py -a URL && \
   python audio_transcriber.py *.mp3 --srt --paragraphs
   ```

### Transcription Output Formats

- **Full Text** (`_transcript_*.txt`): Complete transcription with metadata
- **JSON** (`_transcript_*.json`): Full API response with all details
- **Paragraphs** (`_paragraphs_*.txt`): Natural paragraph breaks with timestamps
- **Sentences** (`_sentences_*.txt`): Individual sentences with timing
- **SRT Subtitles** (`_subtitles_*.srt`): Standard subtitle format for videos

### Setting Up AssemblyAI

1. **Get API Key**: Sign up at [AssemblyAI](https://www.assemblyai.com)
2. **Set Environment Variable**: 
   ```bash
   # Add to .env file
   echo "ASSEMBLYAI_API_KEY=your_api_key_here" >> .env
   
   # Or export directly
   export ASSEMBLYAI_API_KEY=your_api_key_here
   ```

## ⚙️ Advanced Options

### Quality Settings

#### Video Quality Options
- `best`: Highest available quality (default)
- `1080`: 1080p (Full HD)
- `720`: 720p (HD)
- `480`: 480p (SD)
- `360`: 360p (Mobile)

#### Audio Quality Options
- `320`: 320 kbps (Studio quality)
- `256`: 256 kbps (High quality)
- `192`: 192 kbps (Standard quality) - default
- `128`: 128 kbps (Acceptable quality)

### Command-Line Arguments

```bash
# Combined downloader full options
usage: youtube_combined_downloader.py [-h] [-v | -a | -b] [-o OUTPUT] 
                                     [--vq {best,1080,720,480,360}]
                                     [--aq {320,256,192,128}]
                                     url

positional arguments:
  url                   YouTube video URL

optional arguments:
  -h, --help           show this help message and exit
  -v, --video          Download video only (MP4)
  -a, --audio          Download audio only (MP3)
  -b, --both           Download both video and audio
  -o OUTPUT            Output directory (default: current directory)
  --vq {VIDEO_QUALITY} Video quality (default: best)
  --aq {AUDIO_QUALITY} Audio quality in kbps (default: 192)
```

## 🔍 Technical Details

### Architecture

```
┌─────────────────────┐
│   User Interface    │
│  (Command Line)     │
└──────────┬──────────┘
           │
┌──────────┴──────────┐      ┌─────────────────────┐
│   Script Layer      │      │  Audio Transcriber  │
│  (Python Scripts)   │      │  (AssemblyAI API)   │
└──────────┬──────────┘      └──────────┬───────────┘
           │                             │
┌──────────┴──────────┐      ┌──────────┴───────────┐
│     yt-dlp API      │      │   AssemblyAI Cloud   │
│  (Core Downloader)  │      │  (Speech-to-Text)    │
└──────────┬──────────┘      └──────────────────────┘
           │
┌──────────┴──────────┐
│  YouTube Extractor  │
│   (Data Fetching)   │
└──────────┬──────────┘
           │
┌──────────┴──────────┐
│   FFmpeg (Optional) │
│ (Format Conversion) │
└─────────────────────┘
```

### Download Process

1. **URL Validation**: Verify YouTube URL format
2. **Metadata Extraction**: Fetch video information without downloading
3. **Format Selection**: Choose optimal format based on user preferences
4. **Download Stream**: Retrieve video/audio data
5. **Post-Processing**: Convert formats if necessary (using FFmpeg)
6. **File Output**: Save with sanitized filename to specified directory

### Format Selection Algorithm

For **video downloads**:
```python
# Preference order:
1. MP4 video + M4A audio (direct merge to MP4)
2. Best video + best audio (convert to MP4)
3. Best available pre-merged MP4
```

For **audio downloads**:
```python
# Preference order:
1. Best audio-only stream
2. Best quality from video (extract audio)
3. Convert to MP3 at specified bitrate
```

### Transcription Process

For **audio transcription**:
```python
# Process flow:
1. Upload audio file to AssemblyAI
2. Submit transcription job with configuration
3. Poll for completion status
4. Retrieve transcript in requested formats
5. Save with appropriate timestamps and structure
```

## 🐛 Troubleshooting

### Common Issues

**1. "yt-dlp is not installed"**
```bash
pip install --upgrade yt-dlp
```

**2. "FFmpeg not found" (for audio downloads)**
- Install FFmpeg following the prerequisites section
- Ensure FFmpeg is in your system PATH

**3. "HTTP Error 403: Forbidden"**
- Video might be geo-restricted or private
- Try updating yt-dlp: `pip install --upgrade yt-dlp`

**4. "Unable to extract video data"**
- YouTube might have changed their API
- Update yt-dlp to the latest version

**5. Slow downloads**
- Check your internet connection
- YouTube might be throttling - try again later
- Use `--throttled-rate` option if available

**6. "AssemblyAI API key is required"**
- Ensure you have `python-dotenv` installed: `pip install python-dotenv`
- Check your `.env` file has: `ASSEMBLYAI_API_KEY=your_key_here`
- Or export directly: `export ASSEMBLYAI_API_KEY=your_key`

**7. Transcription errors**
- Verify your API key is valid
- Check you have remaining credits on AssemblyAI
- Ensure audio file is not corrupted
- Supported formats: MP3, WAV, M4A, and most audio formats

### Debug Mode

Add verbose output for troubleshooting:
```bash
# Modify the script to add debug flag
python youtube_combined_downloader.py -v URL --debug
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Add docstrings to all functions
- Include type hints where applicable
- Write unit tests for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

These tools are for educational purposes and personal use only. Please respect copyright laws and YouTube's Terms of Service. Always ensure you have the right to download and use the content. Transcription services require an AssemblyAI API key and may incur costs based on usage.

## 🙏 Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - The amazing core that powers these scripts
- [FFmpeg](https://ffmpeg.org/) - For media processing capabilities
- [AssemblyAI](https://www.assemblyai.com/) - For powerful speech-to-text API
- The open-source community for continuous improvements

---

<p align="center">
Made with ❤️ by the open-source community
</p>

<p align="center">
<a href="#-youtube-downloader-suite">⬆ Back to Top</a>
</p>
