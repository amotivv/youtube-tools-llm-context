# System Patterns - YouTube Downloader & Transcription Suite

## Architecture Patterns

### 1. Modular Script Architecture
```
┌─────────────────────────────────────────────┐
│           Combined Downloader               │
│         (Orchestration Layer)               │
└─────────────┬───────────────┬───────────────┘
              │               │
    ┌─────────▼─────────┐ ┌──▼──────────────┐
    │   MP3 Downloader  │ │  MP4 Downloader │
    │  (Audio Module)   │ │ (Video Module)  │
    └───────────────────┘ └─────────────────┘
              │               │
              └───────┬───────┘
                      │
                ┌─────▼─────────┐
                │    yt-dlp     │
                │ (Core Engine) │
                └───────────────┘
```

### 2. MCP Server Architecture (Enhanced)
```
┌─────────────────┐     ┌──────────────────┐
│   LLM Client    │────▶│  MCP Protocol    │
│  (Claude, etc)  │     │  (stdio/JSON)    │
└─────────────────┘     └────────┬─────────┘
                                 │
                        ┌────────▼─────────┐
                        │  Request Router  │
                        │  (server.py)     │
                        └────────┬─────────┘
                                 │
    ┌────────────────────────────┼────────────────────────────┐
    │                            │                            │
┌───▼────┐  ┌──────────┐  ┌─────▼─────┐  ┌────────┐  ┌──────▼──────┐
│ Tools  │  │Resources │  │ Prompts   │  │Download│  │ File Server │
│Handler │  │ Handler  │  │ Handler   │  │Handler │  │  (aiohttp)  │
└───┬────┘  └────┬─────┘  └─────┬─────┘  └───┬────┘  └──────┬──────┘
    │            │               │             │               │
┌───▼────┐  ┌────▼─────┐  ┌─────▼─────┐  ┌───▼────┐  ┌──────▼──────┐
│ Cache  │  │ Resource │  │ Template  │  │Assembly│  │JWT Manager  │
│ System │  │  Access  │  │  Engine   │  │   AI   │  │             │
└────────┘  └──────────┘  └───────────┘  └────────┘  └─────────────┘
```

## Design Patterns

### 1. Command Pattern (CLI Tools)
Each downloader implements a command interface:
- Parse arguments
- Validate inputs
- Execute download
- Return results

```python
def main():
    parser = create_parser()
    args = parser.parse_args()
    validate_args(args)
    result = execute_command(args)
    display_result(result)
```

### 2. Factory Pattern (Format Selection)
Dynamic format selection based on user requirements:
```python
if format_type == 'audio':
    return create_audio_options(quality)
elif format_type == 'video':
    return create_video_options(quality)
```

### 3. Singleton Pattern (MCP Server)
Single server instance managing all connections:
```python
class YouTubeMCPServer:
    def __init__(self):
        self.server = Server("youtube-mcp-server")
        self.cache_dir = Path(...)
        self.setup_handlers()
```

### 4. Observer Pattern (Download Progress)
yt-dlp hooks for progress monitoring:
```python
ydl_opts = {
    'progress_hooks': [progress_callback],
    'quiet': False,
    'no_warnings': False
}
```

### 5. Strategy Pattern (Quality Selection)
Different strategies for quality configuration:
```python
quality_strategies = {
    'best': 'bestvideo+bestaudio/best',
    '1080': 'bestvideo[height<=1080]+bestaudio',
    '720': 'bestvideo[height<=720]+bestaudio'
}
```

## Data Flow Patterns

### 1. Cache-First Pattern
```
Request → Check Cache → Hit? → Return Cached
                ↓ Miss
            Download → Store in Cache → Return New
```

### 4. Resource Access Pattern
```
Resource URI → Parse URI → Identify Type → Load Content
                                              ↓
                                    Format Response → Return
```

### 5. Prompt Execution Pattern
```
Prompt Request → Load Template → Inject Parameters → Return Messages
                                                           ↓
                                              LLM Executes Instructions
```

### 2. Token-Based Access Pattern
```
File Request → Generate JWT → Include Expiry → Return URL
                                                    ↓
Client Access → Verify Token → Valid? → Serve File
                                  ↓ Invalid
                              Return 404
```

### 3. Async Polling Pattern (Transcription)
```
Submit Job → Get Job ID → Poll Status → Complete? → Get Results
                              ↑              ↓ No
                              └──── Wait ────┘
```

## Error Handling Patterns

### 1. Graceful Degradation
- Try best quality first
- Fall back to lower quality
- Use pre-merged formats as last resort

### 2. Retry with Backoff
- Network failures trigger retries
- Exponential backoff for rate limits
- Maximum retry count

### 3. Comprehensive Error Messages
```python
try:
    # Operation
except SpecificError as e:
    return {
        'success': False,
        'error': str(e),
        'error_type': 'specific',
        'suggestion': 'Try this instead...'
    }
```

## Security Patterns

### 1. Time-Limited Access
- JWT tokens expire after 15 minutes
- No permanent URLs exposed
- Automatic token validation

### 2. Input Sanitization
- URL validation before processing
- Filename sanitization for filesystem
- Path traversal prevention

### 3. Isolated Execution
- Docker containerization
- Limited filesystem access
- Environment variable isolation

## Performance Patterns

### 1. Lazy Loading
- Extract info without downloading first
- Download only when necessary
- Load dependencies on demand

### 2. Resource Pooling
- Reuse HTTP connections
- Connection pooling for API calls
- Efficient memory usage

### 3. Async Operations
- Non-blocking I/O for MCP server
- Concurrent request handling
- Async file operations

## Integration Patterns

### 1. Protocol Adapter (MCP)
- Translate MCP requests to internal calls
- Standardize responses
- Handle protocol-specific requirements

### 2. Service Layer
- Separate business logic from protocol
- Reusable components
- Clean interfaces

### 3. Repository Pattern (Cache)
- Abstract cache operations
- Consistent storage interface
- Easy to swap implementations

### 4. Resource URI Pattern
- Custom URI scheme: `youtube://cache/`
- Resource discovery via listing
- Direct content access
- MIME type preservation

### 5. Prompt Template Pattern
- Pre-defined workflows
- Parameterized instructions
- Guided user interactions
- Consistent task execution

## Scalability Patterns

### 1. Horizontal Scaling Ready
- Stateless server design
- Shared cache volume
- Load balancer compatible

### 2. Resource Management
- Automatic cache cleanup
- Download tracking
- Memory-efficient streaming

### 3. Monitoring Integration
- Health check endpoints
- Structured logging
- Performance metrics ready
