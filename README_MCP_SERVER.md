# YouTube MCP Server

A Model Context Protocol (MCP) server that provides YouTube downloading and transcription capabilities to LLMs. Download videos, extract audio, and generate transcripts with temporary URL access.

## Features

- 🎥 **Video Download**: Download YouTube videos in MP4 format with quality selection
- 🎵 **Audio Extraction**: Extract audio in MP3 format with bitrate options
- 📝 **Transcription**: Transcribe audio using AssemblyAI API
- 🔗 **Temporary URLs**: Secure, time-limited URLs (15 minutes) for file access
- 💾 **Smart Caching**: 7-day cache to avoid re-downloading
- 📂 **Cache Management**: List and access cached files via tools and resources
- 🔌 **MCP Resources**: Direct access to cached content via resource URIs
- 📋 **MCP Prompts**: Pre-built workflows for common YouTube tasks
- 🐳 **Docker Ready**: Run isolated in Docker with volume persistence
- 🔧 **MCP Compliant**: Full Model Context Protocol implementation with tools, resources, and prompts

## Quick Start

### Using Docker Compose (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/amotivv/youtube-mcp-server.git
cd youtube-mcp-server
```

2. Create `.env` file:
```bash
# Optional: Add your AssemblyAI API key for transcription
ASSEMBLYAI_API_KEY=your_api_key_here
BASE_URL=http://your-server-ip:8080
JWT_SECRET=your-secret-key-here
```

3. Build and run:
```bash
docker-compose up -d
```

### Manual Docker Build

```bash
# Build the image
docker build -t youtube-mcp-server .

# Run the container
docker run -d \
  --name youtube-mcp \
  -p 8080:8080 \
  -p 5000:5000 \
  -v $(pwd)/cache:/app/cache \
  -e ASSEMBLYAI_API_KEY=$ASSEMBLYAI_API_KEY \
  youtube-mcp-server
```

## MCP Tools

### 5. `youtube_list_cache`
List all cached YouTube files with resource URIs.

**Parameters:** None

**Returns:**
```json
{
  "success": true,
  "cache_dir": "/app/cache",
  "total_files": 3,
  "files": [
    {
      "filename": "abc123.mp3",
      "cache_key": "abc123",
      "type": "audio",
      "size": 4194304,
      "size_mb": 4.0,
      "modified": "2024-12-28T10:00:00",
      "resource_uri": "youtube://cache/audio/abc123"
    }
  ],
  "note": "You can access these files using the resource URIs listed"
}
```

## Original MCP Tools

### 1. `youtube_download_video`
Download YouTube videos in MP4 format.

**Parameters:**
- `url` (string, required): YouTube video URL
- `quality` (string, optional): Video quality - "best", "1080", "720", "480", "360" (default: "best")

**Returns:**
```json
{
  "success": true,
  "file_path": "/app/cache/video_hash.mp4",
  "url": "http://localhost:8080/files/jwt_token",
  "title": "Video Title",
  "duration": 180,
  "size": 52428800,
  "cached": false,
  "expires_at": "2024-12-28T10:30:00"
}
```

### 2. `youtube_download_audio`
Extract audio from YouTube videos in MP3 format.

**Parameters:**
- `url` (string, required): YouTube video URL
- `quality` (string, optional): Audio bitrate - "320", "256", "192", "128" (default: "192")

**Returns:**
```json
{
  "success": true,
  "file_path": "/app/cache/audio_hash.mp3",
  "url": "http://localhost:8080/files/jwt_token",
  "title": "Video Title",
  "duration": 180,
  "size": 4194304,
  "cached": false,
  "expires_at": "2024-12-28T10:30:00"
}
```

### 3. `youtube_transcribe`
Download audio and transcribe using AssemblyAI.

**Parameters:**
- `url` (string, required): YouTube video URL
- `assemblyai_key` (string, optional): AssemblyAI API key (uses environment variable if not provided)

**Returns:**
```json
{
  "audio": {
    "success": true,
    "file_path": "/app/cache/audio_hash.mp3",
    "url": "http://localhost:8080/files/jwt_token_audio"
  },
  "transcript": {
    "success": true,
    "text": "Full transcription text...",
    "transcript_url": "http://localhost:8080/files/jwt_token_transcript",
    "duration": 180,
    "confidence": 0.95,
    "expires_at": "2024-12-28T10:30:00"
  }
}
```

### 4. `youtube_get_info`
Get metadata about a YouTube video without downloading.

**Parameters:**
- `url` (string, required): YouTube video URL

**Returns:**
```json
{
  "title": "Video Title",
  "description": "Video description...",
  "duration": 180,
  "uploader": "Channel Name",
  "upload_date": "20241225",
  "view_count": 1000000,
  "like_count": 50000,
  "thumbnail": "https://i.ytimg.com/...",
  "formats": 22,
  "subtitles": ["en", "es", "fr"]
}
```

## MCP Resources

The server exposes cached content through MCP resources:

### Available Resources

1. **`youtube://cache/list`** - List all cached files
   - Returns JSON with all cached files information
   - MIME type: `application/json`

2. **`youtube://cache/audio/{cache_key}`** - Access cached audio files
   - Returns base64-encoded MP3 audio data
   - MIME type: `audio/mpeg`

3. **`youtube://cache/transcript/{cache_key}`** - Access cached transcripts
   - Returns JSON transcript data from AssemblyAI
   - MIME type: `application/json`

### Using Resources in Claude

```
"Read the youtube://cache/list resource"
"Access the transcript at youtube://cache/transcript/abc123"
```

## MCP Prompts

Pre-built workflows for common YouTube tasks:

### 1. `youtube-quick-summary`
Get a quick summary of a YouTube video.

**Arguments:**
- `url` (required): YouTube video URL

**Example:** "Use the youtube-quick-summary prompt for https://youtube.com/watch?v=VIDEO_ID"

### 2. `youtube-to-notes`
Convert YouTube video to structured notes.

**Arguments:**
- `url` (required): YouTube video URL
- `style` (optional): "bullet", "outline", or "markdown"

**Example:** "Use the youtube-to-notes prompt with style=markdown for [URL]"

### 3. `youtube-extract-quotes`
Extract key quotes from a YouTube video.

**Arguments:**
- `url` (required): YouTube video URL
- `topic` (optional): Specific topic to focus on

**Example:** "Use the youtube-extract-quotes prompt focusing on AI for [URL]"

### 4. `youtube-to-blog`
Transform YouTube video into a blog post.

**Arguments:**
- `url` (required): YouTube video URL
- `tone` (optional): "professional", "casual", or "technical"

**Example:** "Use the youtube-to-blog prompt with casual tone for [URL]"

## Client Configuration

### For Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "youtube": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "--network", "host",
        "-v", "/path/to/cache:/app/cache",
        "-e", "BASE_URL=http://localhost:8080",
        "-e", "ASSEMBLYAI_API_KEY=${ASSEMBLYAI_API_KEY}",
        "-e", "JWT_SECRET=your-secret-key-here",
        "youtube-download-youtube-mcp"
      ]
    }
  }
}
```

### For Custom MCP Clients

```python
from mcp import ClientSession
from mcp.client.stdio import stdio_client

async def connect_youtube_mcp():
    server_params = StdioServerParameters(
        command="docker",
        args=[
            "run", "--rm", "-i",
            "--network", "host",
            "-v", f"{Path.home()}/.youtube-mcp/cache:/app/cache",
            "-e", "BASE_URL=http://localhost:8080",
            "youtube-mcp-server"
        ]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            
            # Download a video
            result = await session.call_tool(
                "youtube_download_video",
                {"url": "https://youtube.com/watch?v=VIDEO_ID"}
            )
```

## Architecture

```
┌─────────────────┐     ┌──────────────────┐
│   LLM Client    │────▶│  MCP Interface   │
│  (Claude, etc)  │     │  (stdio/HTTP)    │
└─────────────────┘     └──────────────────┘
                               │
                        ┌──────▼───────────┐
                        │  YouTube MCP     │
                        │    Server        │
                        └──────┬───────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
         ┌──────▼──────┐ ┌────▼─────┐ ┌─────▼──────┐
         │   yt-dlp    │ │ Assembly │ │ File Server│
         │  (Download) │ │    AI    │ │  (URLs)    │
         └─────────────┘ └──────────┘ └────────────┘
```

## Storage & Caching

- **Cache Directory**: `/app/cache` (persistent volume)
- **Cache Duration**: 7 days (automatic cleanup)
- **File Naming**: MD5 hash of `url_format_quality`
- **Token Duration**: 15 minutes (JWT with expiry)

## Security Considerations

1. **No Authentication**: This server has no auth - secure your deployment
2. **JWT Tokens**: Time-limited access tokens for files
3. **File Access**: Only cached files are accessible via tokens
4. **API Keys**: Store AssemblyAI keys securely in environment

## Environment Variables

- `CACHE_DIR`: Cache directory path (default: `/app/cache`)
- `TEMP_DIR`: Temporary files directory (default: `/tmp/youtube-mcp`)
- `BASE_URL`: Public URL for file access (default: `http://localhost:8080`)
- `JWT_SECRET`: Secret for JWT tokens (auto-generated if not set)
- `ASSEMBLYAI_API_KEY`: AssemblyAI API key for transcription (optional)

## Troubleshooting

### JWT Token Issues
If download links return "File not found or token expired":
1. Ensure JWT_SECRET is set consistently in both `.env` and `mcp_server_config.json`
2. Restart Claude Desktop after configuration changes
3. Request new download links (old tokens won't work with new secrets)

### Port Conflicts
If ports 8080 or 5000 are in use:
```yaml
# docker-compose.yml
ports:
  - "8081:8080"  # Change external port
  - "5001:5000"
```

### Cache Permissions
```bash
# Fix cache directory permissions
sudo chown -R 1000:1000 ./cache
```

### Download Failures
- Check YouTube URL is valid
- Verify ffmpeg is installed in container
- Check disk space for cache directory

## Development

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python server.py
```

### Adding New Tools
1. Add tool definition in `list_tools()`
2. Implement handler in `call_tool()`
3. Update README documentation

## License

MIT License - See LICENSE file for details

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## Credits

- Built with [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- YouTube downloads via [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- Transcription by [AssemblyAI](https://www.assemblyai.com/)
