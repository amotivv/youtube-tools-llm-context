# Active Context - YouTube Downloader & Transcription Suite

## Current State (May 31, 2025)

### Project Status
- **Phase**: Feature enhancement and documentation update
- **Codebase**: Enhanced with MCP Resources and Prompts
- **Documentation**: Updated with new features
- **Deployment**: Docker deployment tested and working

### Recent Activities
1. Implemented MCP Resources feature for cached content access
2. Added MCP Prompts for workflow automation
3. Added youtube_list_cache tool for easier cache discovery
4. Fixed JWT token synchronization between STDIO and HTTP modes
5. Updated all documentation with new features
6. Tested full integration with Claude Desktop

### Active Components

#### Standalone Scripts (Working)
- `youtube_mp3_downloader.py` - Audio extraction tool
- `youtube_mp4_downloader.py` - Video download tool
- `youtube_combined_downloader.py` - Universal downloader
- `audio_transcriber.py` - AssemblyAI transcription tool

#### MCP Server (Enhanced & Working)
- `server.py` - Full MCP implementation with:
  - JWT-based file serving on port 8080
  - MCP protocol on stdio
  - **5 tools**: download_video, download_audio, transcribe, get_info, list_cache
  - **MCP Resources**: youtube://cache/list, youtube://cache/audio/{key}, youtube://cache/transcript/{key}
  - **MCP Prompts**: youtube-quick-summary, youtube-to-notes, youtube-extract-quotes, youtube-to-blog
  - Cache management system with 7-day retention
  - Health check endpoint
  - Fixed JWT secret synchronization

#### Infrastructure (Configured)
- Docker setup with Dockerfile and docker-compose.yml
- Requirements.txt with all dependencies
- Cache directory for 7-day retention
- Environment variable configuration
- MCP configuration for Claude Desktop

### Current Focus Areas

1. **Documentation Completion**
   - Updated all README files with new features
   - Documented Resources and Prompts
   - Added troubleshooting for JWT issues

2. **Key Features Verified**
   - Multi-format download support
   - Quality selection for audio/video
   - Transcription with multiple output formats
   - MCP integration for AI assistants
   - JWT-based secure file access
   - Automatic cache management
   - **NEW: Resource-based cache access**
   - **NEW: Prompt-based workflows**
   - **NEW: Cache listing tool**

### Next Steps

1. **Documentation Updates**
   - ✅ README.md - Updated with new features
   - ✅ README_MCP_SERVER.md - Updated with Resources and Prompts
   - ✅ activeContext.md - Updated
   - ⏳ progress.md - Update next
   - ⏳ systemPatterns.md - Add new patterns
   - ⏳ techContext.md - Update with new capabilities

2. **Potential Enhancements**
   - Add cache cleanup tool
   - Add batch processing for multiple URLs
   - Implement progress callbacks for MCP
   - Add subtitle download support
   - Create web UI for non-technical users
   - Add more transcription services

### Important Decisions Made

1. **Architecture**: Modular design with separate scripts for flexibility
2. **Security**: JWT tokens for time-limited file access
3. **Performance**: 7-day cache to balance storage and convenience
4. **Integration**: MCP server for AI assistant compatibility
5. **Quality**: Multiple quality options for different use cases
6. **Resources**: Direct cache access via MCP resource URIs
7. **Prompts**: Pre-built workflows for common tasks

### Known Considerations

1. **Dependencies**
   - FFmpeg must be installed separately
   - AssemblyAI API key required for transcription
   - Docker recommended for MCP deployment

2. **Limitations**
   - 15-minute token expiry for security
   - Single concurrent download per video (prevents duplicates)
   - Cache cleanup runs hourly

3. **Configuration**
   - Environment variables for sensitive data
   - Quality settings customizable per request
   - Base URL must be configured for remote access
   - **JWT_SECRET must match between MCP and HTTP server**
   - Cache directory must be consistent across containers

### Active Questions/Decisions

1. Should we add a cache cleanup tool? (User requested)
2. Is 15-minute token expiry appropriate for all use cases?
3. Should cache duration be configurable?
4. Need for additional transcription service support?

### Development Environment

- **Current Directory**: `/Users/jason/Projects/youtube-download`
- **Python Environment**: System Python with pip packages
- **Docker**: Images built and tested
- **Claude Desktop**: Configured and working

### Integration Points

1. **MCP Clients**: Can connect via stdio protocol
2. **HTTP API**: File access via port 8080
3. **Command Line**: Direct script execution
4. **Docker**: Full containerized deployment
5. **Resources**: Direct cache access via URIs
6. **Prompts**: Workflow automation

### Recent Issues Resolved

1. **JWT Token Mismatch**: Fixed by ensuring JWT_SECRET is consistent between containers
2. **Resource Access**: Implemented proper MCP resource response format
3. **Cache Discovery**: Added youtube_list_cache tool for easier access
4. **Docker Image Naming**: Corrected to use hyphens instead of underscores

This context represents the enhanced state after implementing MCP Resources and Prompts features. The system is fully functional with improved AI assistant integration capabilities.
