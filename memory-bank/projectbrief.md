# YouTube Downloader & Transcription Suite - Project Brief

## Project Overview
A comprehensive Python-based toolkit for downloading YouTube content and transcribing audio files. The suite provides both standalone scripts and an MCP (Model Context Protocol) server implementation for integration with AI assistants.

## Core Purpose
Enable users to:
1. Download YouTube videos in MP4 format with quality selection
2. Extract audio from YouTube videos as MP3 files
3. Transcribe audio content using AssemblyAI API
4. Access functionality through command-line tools or MCP protocol

## Key Requirements

### Functional Requirements
- **Video Download**: Support multiple quality options (360p to 4K/best)
- **Audio Extraction**: Support multiple bitrates (128-320 kbps)
- **Transcription**: Multiple output formats (text, SRT, paragraphs, sentences, JSON)
- **Caching**: 7-day cache to avoid redundant downloads
- **File Access**: Secure, time-limited URLs for downloaded content
- **MCP Integration**: Full Model Context Protocol server implementation

### Technical Requirements
- Python 3.6+ compatibility
- Cross-platform support (Windows, macOS, Linux)
- Docker containerization for MCP server
- JWT-based authentication for file access
- Asynchronous operation support

## Target Users
1. **Content Creators**: Need to download and transcribe YouTube content
2. **Researchers**: Require transcripts for analysis
3. **Developers**: Want to integrate YouTube functionality into applications
4. **AI Assistants**: Access YouTube content through MCP protocol

## Success Criteria
- Reliable downloading with error handling
- High-quality transcription accuracy
- Fast performance with caching
- Secure file access with time limits
- Easy deployment via Docker
- Clean, maintainable codebase

## Constraints
- Respect YouTube Terms of Service
- Require AssemblyAI API key for transcription
- 15-minute expiry for file access tokens
- 7-day cache retention policy
