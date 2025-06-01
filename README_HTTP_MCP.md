# YouTube MCP HTTP Server - Remote Deployment Guide

This guide is for deploying the YouTube MCP Server as a remote HTTP service that can be accessed by any MCP-compatible client over the internet.

## When to Use This Guide

- You want to host the MCP server on a remote server (VPS, cloud, etc.)
- Multiple users need to access the same MCP server
- You're building a service that integrates with the MCP protocol
- You need programmatic access via HTTP API

## Key Features

- **Full HTTP MCP Implementation**: Complete MCP protocol over HTTP
- **Remote accessible**: Can be hosted anywhere and accessed over the internet
- **Stateless**: Each request is independent (uses JSON-RPC 2.0)
- **Optional authentication**: Supports API key authentication via Bearer tokens
- **Same tools as local version**: All YouTube download/transcribe features

## Quick Start

1. **Build and run with Docker Compose:**
```bash
docker-compose up -d
```

2. **Test the server:**
```bash
python test_mcp_http.py
```

## MCP HTTP Endpoints

### Base URL
- Default: `http://localhost:8080`
- Configure via `BASE_URL` environment variable

### Endpoints

#### 1. Initialize Session
```
POST /mcp/initialize
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "method": "initialize",
  "params": {
    "clientInfo": {
      "name": "your-client",
      "version": "1.0"
    }
  },
  "id": 1
}
```

#### 2. List Tools
```
POST /mcp/list_tools
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "params": {},
  "id": 2
}
```

#### 3. Call Tool
```
POST /mcp/call_tool
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "youtube_download_video",
    "arguments": {
      "url": "https://youtube.com/watch?v=VIDEO_ID",
      "quality": "720"
    }
  },
  "id": 3
}
```

#### 4. Health Check
```
GET /mcp/health
```

## Authentication

To enable API key authentication:

1. Set the `MCP_API_KEY` environment variable:
```bash
MCP_API_KEY=your-secret-api-key
```

2. Include the API key in requests:
```
Authorization: Bearer your-secret-api-key
```

## Environment Variables

- `BASE_URL`: Public URL for file access (default: `http://localhost:8080`)
- `MCP_API_KEY`: Optional API key for authentication
- `ASSEMBLYAI_API_KEY`: AssemblyAI API key for transcription
- `JWT_SECRET`: Secret for JWT tokens (auto-generated if not set)
- `CACHE_DIR`: Cache directory path (default: `/app/cache`)
- `TEMP_DIR`: Temporary files directory (default: `/tmp/youtube-mcp`)

## Client Integration Example

### Python Client
```python
import requests
import json

class YouTubeMCPClient:
    def __init__(self, base_url, api_key=None):
        self.base_url = base_url
        self.headers = {}
        if api_key:
            self.headers['Authorization'] = f'Bearer {api_key}'
        self.session_id = None
        self._initialize()
    
    def _initialize(self):
        response = requests.post(
            f"{self.base_url}/mcp/initialize",
            json={
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {"clientInfo": {"name": "python-client", "version": "1.0"}},
                "id": 1
            },
            headers=self.headers
        )
        result = response.json()
        self.session_id = result['result']['sessionId']
    
    def download_video(self, url, quality='best'):
        response = requests.post(
            f"{self.base_url}/mcp/call_tool",
            json={
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "youtube_download_video",
                    "arguments": {"url": url, "quality": quality}
                },
                "id": 2
            },
            headers=self.headers
        )
        result = response.json()
        return json.loads(result['result']['content'][0]['text'])

# Usage
client = YouTubeMCPClient('http://your-server:8080', api_key='your-api-key')
result = client.download_video('https://youtube.com/watch?v=VIDEO_ID')
print(f"Download URL: {result['url']}")
```

### JavaScript/TypeScript Client
```javascript
class YouTubeMCPClient {
  constructor(baseUrl, apiKey) {
    this.baseUrl = baseUrl;
    this.headers = {
      'Content-Type': 'application/json'
    };
    if (apiKey) {
      this.headers['Authorization'] = `Bearer ${apiKey}`;
    }
  }

  async initialize() {
    const response = await fetch(`${this.baseUrl}/mcp/initialize`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify({
        jsonrpc: '2.0',
        method: 'initialize',
        params: { clientInfo: { name: 'js-client', version: '1.0' } },
        id: 1
      })
    });
    const result = await response.json();
    this.sessionId = result.result.sessionId;
  }

  async downloadVideo(url, quality = 'best') {
    const response = await fetch(`${this.baseUrl}/mcp/call_tool`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify({
        jsonrpc: '2.0',
        method: 'tools/call',
        params: {
          name: 'youtube_download_video',
          arguments: { url, quality }
        },
        id: 2
      })
    });
    const result = await response.json();
    return JSON.parse(result.result.content[0].text);
  }
}
```

## Deployment

### Production Deployment

1. **Update .env for production:**
```env
BASE_URL=https://your-domain.com
MCP_API_KEY=strong-random-api-key
JWT_SECRET=strong-random-secret
ASSEMBLYAI_API_KEY=your-assemblyai-key
```

2. **Use a reverse proxy (nginx example):**
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
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

3. **Run with Docker Compose:**
```bash
docker-compose up -d
```

## Security Considerations

1. **Always use HTTPS in production**
2. **Set a strong MCP_API_KEY**
3. **Use a strong JWT_SECRET**
4. **Consider rate limiting**
5. **Monitor server logs**
6. **Keep dependencies updated**

## Monitoring

Check server health:
```bash
curl http://localhost:8080/health
curl http://localhost:8080/mcp/health
```

View logs:
```bash
docker-compose logs -f
```

## Troubleshooting

1. **Server won't start**: Check if port 8080 is available
2. **Authentication errors**: Verify MCP_API_KEY matches
3. **Download failures**: Check YouTube URL and ffmpeg installation
4. **Transcription errors**: Verify AssemblyAI API key

## Architecture Overview

```
┌─────────────────┐         ┌──────────────────────┐
│ Remote Client   │ HTTP    │ YouTube MCP Server   │
│ (Any MCP app)   │────────▶│ - Downloads videos   │
└─────────────────┘         │ - Serves files       │
                            │ - Handles MCP calls  │
                            └──────────────────────┘
```

## Differences from Claude Desktop Setup

- **Claude Desktop**: Uses STDIO for MCP + separate HTTP for files
- **This Guide**: Single HTTP server handles both MCP protocol and file serving
- **Use Case**: Remote deployment for multiple clients vs local Claude integration
