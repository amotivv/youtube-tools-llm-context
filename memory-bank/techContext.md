# Technical Context - YouTube Downloader & Transcription Suite

## Technology Stack

### Core Dependencies
- **Python 3.6+**: Primary programming language
- **yt-dlp (>=2024.1.0)**: YouTube downloading engine
- **FFmpeg**: Media processing and format conversion
- **requests (>=2.31.0)**: HTTP client for API calls
- **python-dotenv (>=1.0.0)**: Environment variable management

### MCP Server Dependencies
- **mcp (>=0.1.0)**: Model Context Protocol SDK with tools, resources, and prompts
- **aiohttp (>=3.9.0)**: Async HTTP server for file serving
- **aiohttp-cors (>=0.7.0)**: CORS support for web access
- **PyJWT (>=2.8.0)**: JWT token generation and validation
- **asyncio (>=3.4.3)**: Asynchronous programming support

### External Services
- **AssemblyAI API**: Speech-to-text transcription service
- **YouTube**: Content source (via yt-dlp)

## Development Environment

### System Requirements
- Python 3.6 or higher
- FFmpeg installed and in PATH
- Internet connection for downloads
- AssemblyAI API key (for transcription)

### Platform Support
- **Windows**: Full support with Windows-specific paths
- **macOS**: Full support with Homebrew FFmpeg
- **Linux**: Full support with package manager FFmpeg

### Docker Environment
- Base image: Python 3.x
- Exposed ports: 8080 (file server), 5000 (MCP)
- Volume mounts: `/app/cache` for persistent storage
- Environment variables configuration

## Architecture Overview

### Component Structure
```
youtube-download/
├── youtube_mp3_downloader.py    # Audio-only downloader
├── youtube_mp4_downloader.py    # Video-only downloader
├── youtube_combined_downloader.py # Universal downloader
├── audio_transcriber.py         # Transcription tool
├── server.py                    # MCP server implementation
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Container definition
├── docker-compose.yml          # Container orchestration
└── cache/                      # Download cache directory
```

### Data Flow
1. **Download Flow**: URL → yt-dlp → FFmpeg → Local File
2. **Transcription Flow**: Audio File → AssemblyAI Upload → Processing → Results
3. **MCP Tool Flow**: Client Request → Server Handler → Tool Execution → JWT URL Response
4. **MCP Resource Flow**: Resource URI → Content Loader → Format Response → Return to Client
5. **MCP Prompt Flow**: Prompt Request → Template Engine → Parameterized Instructions → Client Execution

## Key Technical Decisions

### 1. yt-dlp over youtube-dl
- More active development
- Better YouTube compatibility
- Improved error handling
- Faster downloads

### 2. JWT for File Access
- Time-limited access (15 minutes)
- No database required
- Stateless authentication
- Secure file serving

### 3. Asynchronous MCP Server
- Non-blocking operations
- Concurrent request handling
- Better resource utilization
- Scalable architecture
- Full MCP protocol support (tools, resources, prompts)

### 4. 7-Day Cache Policy
- Balance between storage and convenience
- Automatic cleanup process
- MD5-based cache keys
- Prevents redundant downloads

### 5. Docker Containerization
- Consistent environment
- Easy deployment
- Isolated dependencies
- Volume persistence

## Configuration Management

### Environment Variables
- `ASSEMBLYAI_API_KEY`: API key for transcription
- `CACHE_DIR`: Cache directory path (default: `/app/cache`)
- `TEMP_DIR`: Temporary files directory (default: `/tmp/youtube-mcp`)
- `BASE_URL`: Public URL for file access (default: `http://localhost:8080`)
- `JWT_SECRET`: Secret for JWT tokens (must be consistent across containers)

### Quality Settings
- **Video**: best, 1080p, 720p, 480p, 360p
- **Audio**: 320kbps, 256kbps, 192kbps, 128kbps

## Security Considerations

### File Access Security
- JWT tokens with expiration
- No direct file system access
- Token verification on each request
- Isolated cache directory

### API Key Management
- Environment variable storage
- Optional .env file support
- No hardcoded credentials
- Per-request key override option

## Performance Optimizations

### Caching Strategy
- MD5 hash-based file naming
- 7-day retention policy
- Cache hit detection
- Automatic cleanup task

### Download Optimization
- Format pre-selection
- Direct MP4 preference
- Parallel processing support
- Progress tracking

### Transcription Efficiency
- Async polling for results
- Batch processing ready
- Result caching in JSON
- Multiple format generation

## MCP Protocol Implementation

### Tools (5 available)
1. `youtube_download_video` - Download videos with quality selection
2. `youtube_download_audio` - Extract audio with bitrate options
3. `youtube_transcribe` - Download and transcribe in one operation
4. `youtube_get_info` - Get video metadata without downloading
5. `youtube_list_cache` - List cached files with resource URIs

### Resources (Dynamic)
- `youtube://cache/list` - JSON list of all cached files
- `youtube://cache/audio/{cache_key}` - Base64-encoded audio data
- `youtube://cache/transcript/{cache_key}` - JSON transcript data

### Prompts (4 workflows)
1. `youtube-quick-summary` - Automated video summarization
2. `youtube-to-notes` - Convert videos to structured notes
3. `youtube-extract-quotes` - Extract notable quotes
4. `youtube-to-blog` - Transform videos into blog posts

### JWT Token Synchronization
- Shared secret between STDIO and HTTP modes
- Consistent token generation and validation
- 15-minute expiration for security
- Base64 URL-safe encoding
