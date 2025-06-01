# YouTube MCP Server - Deployment Options

This server can be deployed in two different configurations:

1. **Local Setup for Claude Desktop** - Uses STDIO for MCP protocol + HTTP for file serving
2. **Remote HTTP MCP Server** - Full HTTP-based MCP server for remote clients

## 🎯 Quick Start

### Option 1: Local Setup for Claude Desktop

This setup uses Docker to run both the MCP server (STDIO) and file server (HTTP):

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/youtube-mcp-server.git
cd youtube-mcp-server
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure Claude Desktop:**
Add to your Claude Desktop configuration file:
```json
{
  "mcpServers": {
    "youtube": {
      "command": "python",
      "args": ["/path/to/youtube-mcp-server/server.py"],
      "env": {
        "ASSEMBLYAI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

4. **Restart Claude Desktop** and the YouTube tools will be available!

### Option 2: Remote HTTP MCP Server

For hosting a full HTTP-based MCP server that remote clients can connect to:

1. **Using Docker (Recommended):**
```bash
# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f
```

2. **Manual deployment:**
```bash
# Run in HTTP mode
python server.py --http

# Or use environment variable
HTTP_MODE=true python server.py
```

## 🔧 Understanding the Architecture

### For Claude Desktop (Local)
```
Claude Desktop ←→ MCP Server (STDIO via Docker)
                           ↓
                   Downloads files
                           ↓
Your Browser ←→ HTTP File Server (:8080)
```

### For Remote HTTP MCP
```
Remote Client ←→ HTTP MCP Server (:8080)
                    (Full MCP over HTTP)
```

The server automatically detects which mode to run based on:
- **No flags**: STDIO mode for Claude Desktop
- **--http flag**: HTTP MCP server mode

## 📋 Configuration

### Environment Variables

Create a `.env` file:
```env
# Required for transcription
ASSEMBLYAI_API_KEY=your-assemblyai-api-key

# For HTTP mode
BASE_URL=http://localhost:8080
MCP_API_KEY=your-secure-api-key  # Optional, for authentication
JWT_SECRET=your-jwt-secret

# Cache settings
CACHE_DIR=/app/cache
TEMP_DIR=/tmp/youtube-mcp
```

### Mode Selection

The server automatically selects the mode based on:

1. **Command line argument**: `--http` flag
2. **Environment variable**: `HTTP_MODE=true`
3. **Default**: STDIO mode (for Claude Desktop)

```bash
# STDIO mode (default)
python server.py

# HTTP mode via flag
python server.py --http

# HTTP mode via environment
HTTP_MODE=true python server.py
```

## 🛠️ Available Tools

Both modes provide the same MCP tools:

### 1. youtube_download_video
Download YouTube videos in MP4 format.
```json
{
  "url": "https://youtube.com/watch?v=VIDEO_ID",
  "quality": "720"  // optional: best, 1080, 720, 480, 360
}
```

### 2. youtube_download_audio
Extract audio in MP3 format.
```json
{
  "url": "https://youtube.com/watch?v=VIDEO_ID",
  "quality": "192"  // optional: 320, 256, 192, 128
}
```

### 3. youtube_transcribe
Download and transcribe audio.
```json
{
  "url": "https://youtube.com/watch?v=VIDEO_ID",
  "assemblyai_key": "optional-if-in-env"
}
```

### 4. youtube_get_info
Get video metadata without downloading.
```json
{
  "url": "https://youtube.com/watch?v=VIDEO_ID"
}
```

## 🌐 HTTP Mode Details

### Endpoints

When running in HTTP mode, the server exposes:

- `GET /health` - General health check
- `GET /mcp/health` - MCP-specific health check
- `POST /mcp/initialize` - Initialize MCP session
- `POST /mcp/list_tools` - List available tools
- `POST /mcp/call_tool` - Execute a tool
- `GET /files/{token}` - Access downloaded files

### Authentication

To enable API key authentication in HTTP mode:

1. Set `MCP_API_KEY` environment variable
2. Include in requests: `Authorization: Bearer your-api-key`

### Example HTTP Client

```python
import requests
import json

# Initialize session
response = requests.post('http://localhost:8080/mcp/initialize', 
    json={
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {"clientInfo": {"name": "my-client", "version": "1.0"}},
        "id": 1
    },
    headers={'Authorization': 'Bearer your-api-key'}  # if auth enabled
)

# Call a tool
response = requests.post('http://localhost:8080/mcp/call_tool',
    json={
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "youtube_download_audio",
            "arguments": {
                "url": "https://youtube.com/watch?v=dQw4w9WgXcQ"
            }
        },
        "id": 2
    }
)

result = response.json()
download_url = json.loads(result['result']['content'][0]['text'])['url']
print(f"Download from: {download_url}")
```

## 🐳 Docker Deployment

The Docker setup automatically runs in HTTP mode:

```yaml
# docker-compose.yml
services:
  youtube-mcp:
    build: .
    container_name: youtube-mcp-server
    ports:
      - "8080:8080"
    environment:
      - HTTP_MODE=true  # Not required, Dockerfile sets --http
      - MCP_API_KEY=${MCP_API_KEY}
      - ASSEMBLYAI_API_KEY=${ASSEMBLYAI_API_KEY}
    volumes:
      - ./cache:/app/cache
```

## 🔒 Security Considerations

### For STDIO Mode
- Only accessible locally
- No network exposure
- Inherits Claude Desktop's security

### For HTTP Mode
- Use HTTPS in production (reverse proxy)
- Enable API key authentication
- Set strong JWT_SECRET
- Consider rate limiting
- Monitor access logs

## 📊 Monitoring

### Check server status:
```bash
# HTTP mode
curl http://localhost:8080/health
curl http://localhost:8080/mcp/health

# Docker logs
docker-compose logs -f
```

### Health response includes:
- Server mode (stdio/http)
- Cache status
- Active downloads
- Session count (HTTP mode)

## 🚀 Production Deployment

### 1. Update configuration:
```env
BASE_URL=https://your-domain.com
MCP_API_KEY=strong-random-key
JWT_SECRET=another-strong-key
```

### 2. Use reverse proxy (nginx):
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. Deploy with Docker:
```bash
docker-compose up -d
```

## 🔧 Troubleshooting

### STDIO Mode Issues
- **"No MCP tools available"**: Check Claude Desktop config path
- **"Server not responding"**: Ensure Python path is correct
- **"Import errors"**: Install all requirements

### HTTP Mode Issues
- **"Port already in use"**: Change port or stop conflicting service
- **"Authentication failed"**: Verify MCP_API_KEY matches
- **"CORS errors"**: Check client origin is allowed

### General Issues
- **"Download failed"**: Check YouTube URL and internet connection
- **"Transcription failed"**: Verify AssemblyAI API key
- **"Cache full"**: Old files are auto-cleaned after 7 days

## 📝 Development

### Testing locally:
```bash
# Test STDIO mode
python server.py

# Test HTTP mode
python server.py --http
python test_mcp_http.py  # Run test suite
```

### Adding new features:
1. Update `_get_tools_list()` for tool definitions
2. Update `_execute_tool()` for tool logic
3. Test in both modes
4. Update documentation

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Test both modes
4. Submit pull request

## 📄 License

MIT License - See LICENSE file

---

The dual-mode design ensures maximum flexibility: use STDIO mode for local Claude Desktop integration, or HTTP mode for building remote services and integrations.
