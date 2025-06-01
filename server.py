#!/usr/bin/env python3
"""
YouTube MCP Server - Dual Mode (STDIO/HTTP)
Supports both local Claude Desktop (stdio) and remote HTTP access
"""

import os
import sys
import json
import hashlib
import asyncio
import logging
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List
from urllib.parse import quote
import secrets
import time
import uuid

import yt_dlp
import requests
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource, Resource, Prompt, PromptArgument, PromptMessage
from aiohttp import web
import aiohttp_cors
import jwt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YouTubeMCPServer:
    """MCP Server for YouTube operations - supports both STDIO and HTTP modes"""
    
    def __init__(self, mode='stdio'):
        self.mode = mode
        self.cache_dir = Path(os.environ.get('CACHE_DIR', '/app/cache'))
        self.temp_dir = Path(os.environ.get('TEMP_DIR', '/tmp/youtube-mcp'))
        self.base_url = os.environ.get('BASE_URL', 'http://localhost:8080')
        self.jwt_secret = os.environ.get('JWT_SECRET', secrets.token_urlsafe(32))
        self.assemblyai_key = os.environ.get('ASSEMBLYAI_API_KEY', None)
        
        # Create directories
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Download tracking
        self.active_downloads = {}
        
        if mode == 'stdio':
            # STDIO mode - for Claude Desktop
            self.server = Server("youtube-mcp-server")
            self.setup_stdio_handlers()
        else:
            # HTTP mode - for remote access
            self.api_key = os.environ.get('MCP_API_KEY', None)
            self.web_app = web.Application()
            self.sessions = {}
            self.setup_http_routes()
    
    def setup_stdio_handlers(self):
        """Setup MCP protocol handlers for STDIO mode"""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available tools"""
            return self._get_tools_list()
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls"""
            result = await self._execute_tool(name, arguments)
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            """List available resources"""
            return await self._list_resources()
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> List[Dict[str, Any]]:
            """Read a resource by URI"""
            return await self._read_resource(uri)
        
        @self.server.list_prompts()
        async def list_prompts() -> List[Prompt]:
            """List available prompts"""
            return self._get_prompts_list()
        
        @self.server.get_prompt()
        async def get_prompt(name: str, arguments: Optional[Dict[str, str]] = None) -> List[PromptMessage]:
            """Get a specific prompt"""
            return await self._get_prompt(name, arguments)
    
    def setup_http_routes(self):
        """Setup HTTP routes for HTTP mode"""
        cors = aiohttp_cors.setup(self.web_app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods=["GET", "POST", "OPTIONS"]
            )
        })
        
        # File serving routes
        file_route = self.web_app.router.add_route('GET', '/files/{token}', self.serve_file)
        cors.add(file_route)
        
        # Health check route
        health_route = self.web_app.router.add_get('/health', self.health_check)
        cors.add(health_route)
        
        # MCP HTTP endpoints
        mcp_routes = [
            ('POST', '/mcp/initialize', self.mcp_initialize),
            ('POST', '/mcp/list_tools', self.mcp_list_tools),
            ('POST', '/mcp/call_tool', self.mcp_call_tool),
            ('GET', '/mcp/health', self.mcp_health),
        ]
        
        for method, path, handler in mcp_routes:
            route = self.web_app.router.add_route(method, path, handler)
            cors.add(route)
    
    def _get_tools_list(self):
        """Get the list of available tools"""
        return [
            Tool(
                name="youtube_download_video",
                description="Download a YouTube video in MP4 format",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "YouTube video URL"
                        },
                        "quality": {
                            "type": "string",
                            "description": "Video quality (best, 1080, 720, 480, 360)",
                            "default": "best"
                        }
                    },
                    "required": ["url"]
                }
            ),
            Tool(
                name="youtube_download_audio",
                description="Download audio from YouTube video in MP3 format",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "YouTube video URL"
                        },
                        "quality": {
                            "type": "string",
                            "description": "Audio bitrate (320, 256, 192, 128)",
                            "default": "192"
                        }
                    },
                    "required": ["url"]
                }
            ),
            Tool(
                name="youtube_transcribe",
                description="Download and transcribe YouTube video audio",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "YouTube video URL"
                        },
                        "assemblyai_key": {
                            "type": "string",
                            "description": "AssemblyAI API key (optional if set in environment)"
                        }
                    },
                    "required": ["url"]
                }
            ),
            Tool(
                name="youtube_get_info",
                description="Get metadata about a YouTube video",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "YouTube video URL"
                        }
                    },
                    "required": ["url"]
                }
            ),
            Tool(
                name="youtube_list_cache",
                description="List all cached YouTube files. Use this to see what videos/audio/transcripts are already downloaded. You can also access cached files via resources: youtube://cache/list",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            )
        ]
    
    async def _execute_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool and return the result"""
        if name == "youtube_download_video":
            return await self.download_youtube(
                arguments['url'],
                format_type='video',
                quality=arguments.get('quality', 'best')
            )
        elif name == "youtube_download_audio":
            return await self.download_youtube(
                arguments['url'],
                format_type='audio',
                quality=arguments.get('quality', '192')
            )
        elif name == "youtube_transcribe":
            # First download audio
            audio_result = await self.download_youtube(
                arguments['url'],
                format_type='audio',
                quality='192'
            )
            
            if not audio_result['success']:
                return audio_result
            
            # Then transcribe
            transcript_result = await self.transcribe_audio(
                audio_result['file_path'],
                arguments.get('assemblyai_key')
            )
            
            # Combine results
            return {
                'audio': audio_result,
                'transcript': transcript_result
            }
        elif name == "youtube_get_info":
            return await self.get_video_info(arguments['url'])
        elif name == "youtube_list_cache":
            # List all cached files
            cache_files = []
            try:
                for file in self.cache_dir.iterdir():
                    if file.is_file():
                        stat = file.stat()
                        cache_files.append({
                            'filename': file.name,
                            'cache_key': file.stem,
                            'type': 'audio' if file.suffix == '.mp3' else 'video' if file.suffix == '.mp4' else 'transcript',
                            'size': stat.st_size,
                            'size_mb': round(stat.st_size / (1024 * 1024), 2),
                            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            'resource_uri': f"youtube://cache/{'audio' if file.suffix == '.mp3' else 'transcript'}/{file.stem}" if file.suffix in ['.mp3', '.json'] else None
                        })
                
                return {
                    'success': True,
                    'cache_dir': str(self.cache_dir),
                    'total_files': len(cache_files),
                    'files': cache_files,
                    'note': 'You can access these files using the resource URIs listed'
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e)
                }
        else:
            return {'error': f'Unknown tool: {name}'}
    
    def _get_prompts_list(self) -> List[Prompt]:
        """Get the list of available prompts"""
        return [
            Prompt(
                name="youtube-quick-summary",
                description="Get a quick summary of a YouTube video",
                arguments=[
                    PromptArgument(
                        name="url",
                        description="YouTube video URL",
                        required=True
                    )
                ]
            ),
            Prompt(
                name="youtube-to-notes",
                description="Convert YouTube video to structured notes",
                arguments=[
                    PromptArgument(
                        name="url",
                        description="YouTube video URL",
                        required=True
                    ),
                    PromptArgument(
                        name="style",
                        description="Note style: bullet, outline, or markdown",
                        required=False
                    )
                ]
            ),
            Prompt(
                name="youtube-extract-quotes",
                description="Extract key quotes from a YouTube video",
                arguments=[
                    PromptArgument(
                        name="url",
                        description="YouTube video URL",
                        required=True
                    ),
                    PromptArgument(
                        name="topic",
                        description="Specific topic to focus on (optional)",
                        required=False
                    )
                ]
            ),
            Prompt(
                name="youtube-to-blog",
                description="Convert YouTube video to blog post",
                arguments=[
                    PromptArgument(
                        name="url",
                        description="YouTube video URL",
                        required=True
                    ),
                    PromptArgument(
                        name="tone",
                        description="Blog tone: professional, casual, or technical",
                        required=False
                    )
                ]
            )
        ]
    
    async def _get_prompt(self, name: str, arguments: Optional[Dict[str, str]] = None) -> List[PromptMessage]:
        """Get a specific prompt with arguments"""
        if name == "youtube-quick-summary":
            url = arguments.get('url') if arguments else ''
            return [
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"Please provide a quick summary of this YouTube video: {url}\n\n"
                             f"First, use the youtube_transcribe tool to get the transcript, "
                             f"then provide a concise summary covering the main points."
                    )
                )
            ]
        
        elif name == "youtube-to-notes":
            url = arguments.get('url', '') if arguments else ''
            style = arguments.get('style', 'bullet') if arguments else 'bullet'
            style_instructions = {
                'bullet': "Use bullet points with main topics and sub-points",
                'outline': "Use a numbered outline format with hierarchical structure",
                'markdown': "Use markdown formatting with headers, lists, and emphasis"
            }
            return [
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"Convert this YouTube video into structured notes: {url}\n\n"
                             f"Instructions:\n"
                             f"1. First, use youtube_transcribe to get the transcript\n"
                             f"2. Create organized notes using this style: {style_instructions.get(style, style_instructions['bullet'])}\n"
                             f"3. Include key concepts, main points, and important details\n"
                             f"4. Add timestamps for major sections"
                    )
                )
            ]
        
        elif name == "youtube-extract-quotes":
            url = arguments.get('url', '') if arguments else ''
            topic = arguments.get('topic', '') if arguments else ''
            topic_instruction = f" focusing on {topic}" if topic else ""
            return [
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"Extract notable quotes from this YouTube video{topic_instruction}: {url}\n\n"
                             f"Instructions:\n"
                             f"1. Use youtube_transcribe to get the full transcript\n"
                             f"2. Identify the most impactful, insightful, or memorable quotes\n"
                             f"3. For each quote, provide:\n"
                             f"   - The exact quote\n"
                             f"   - The timestamp\n"
                             f"   - Brief context about why it's significant\n"
                             f"4. Organize quotes thematically if possible"
                    )
                )
            ]
        
        elif name == "youtube-to-blog":
            url = arguments.get('url', '') if arguments else ''
            tone = arguments.get('tone', 'professional') if arguments else 'professional'
            tone_instructions = {
                'professional': "formal, authoritative, and well-researched",
                'casual': "conversational, friendly, and accessible",
                'technical': "detailed, precise, and industry-focused"
            }
            return [
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"Transform this YouTube video into a blog post: {url}\n\n"
                             f"Blog Requirements:\n"
                             f"1. First, use youtube_transcribe to get the transcript\n"
                             f"2. Write in a {tone_instructions.get(tone, tone_instructions['professional'])} tone\n"
                             f"3. Structure:\n"
                             f"   - Engaging introduction that hooks the reader\n"
                             f"   - Clear sections with descriptive headings\n"
                             f"   - Key takeaways or insights from the video\n"
                             f"   - Relevant quotes with attribution\n"
                             f"   - Compelling conclusion with call-to-action\n"
                             f"4. Make it SEO-friendly with natural keyword usage\n"
                             f"5. Length: 800-1200 words\n"
                             f"6. Include a note crediting the original video"
                    )
                )
            ]
        
        else:
            raise ValueError(f"Unknown prompt: {name}")
    
    async def _list_resources(self) -> List[Resource]:
        """List available resources"""
        resources = [
            Resource(
                uri="youtube://cache/list",
                name="Cached Files List",
                description="List all cached YouTube downloads",
                mimeType="application/json"
            )
        ]
        
        # Add individual cached files as resources
        try:
            for file in self.cache_dir.iterdir():
                if file.is_file() and file.suffix in ['.mp3', '.json']:
                    cache_key = file.stem
                    if file.suffix == '.mp3':
                        resources.append(Resource(
                            uri=f"youtube://cache/audio/{cache_key}",
                            name=f"Audio: {cache_key}",
                            description="Cached audio file",
                            mimeType="audio/mpeg"
                        ))
                    elif file.suffix == '.json':
                        resources.append(Resource(
                            uri=f"youtube://cache/transcript/{cache_key}",
                            name=f"Transcript: {cache_key}",
                            description="Cached transcript",
                            mimeType="application/json"
                        ))
        except Exception as e:
            logger.error(f"Error listing cache files: {e}")
        
        return resources
    
    async def _read_resource(self, uri: str) -> List[Dict[str, Any]]:
        """Read a resource by URI - returns contents array per MCP spec"""
        if uri == "youtube://cache/list":
            # Return list of all cached files
            cache_info = []
            for file in self.cache_dir.iterdir():
                if file.is_file():
                    stat = file.stat()
                    cache_info.append({
                        'filename': file.name,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'type': 'audio' if file.suffix == '.mp3' else 'video' if file.suffix == '.mp4' else 'transcript'
                    })
            
            return [{
                'uri': uri,
                'mimeType': 'application/json',
                'text': json.dumps(cache_info, indent=2)
            }]
        
        elif uri.startswith("youtube://cache/audio/"):
            # Extract cache key from URI
            cache_key = uri.replace("youtube://cache/audio/", "")
            audio_file = self.cache_dir / f"{cache_key}.mp3"
            
            if audio_file.exists():
                # Read file and return as base64
                import base64
                with open(audio_file, 'rb') as f:
                    content = base64.b64encode(f.read()).decode('utf-8')
                
                return [{
                    'uri': uri,
                    'mimeType': 'audio/mpeg',
                    'blob': content
                }]
            else:
                raise ValueError(f"Audio file not found: {cache_key}")
        
        elif uri.startswith("youtube://cache/transcript/"):
            # Extract cache key from URI
            cache_key = uri.replace("youtube://cache/transcript/", "")
            transcript_file = self.cache_dir / f"{cache_key}.json"
            
            if transcript_file.exists():
                with open(transcript_file, 'r') as f:
                    content = f.read()
                
                return [{
                    'uri': uri,
                    'mimeType': 'application/json',
                    'text': content
                }]
            else:
                raise ValueError(f"Transcript file not found: {cache_key}")
        
        else:
            raise ValueError(f"Unknown resource URI: {uri}")
    
    # HTTP mode methods
    async def check_auth(self, request):
        """Check API key authentication if enabled"""
        if not self.api_key:
            return True
        
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            return token == self.api_key
        return False
    
    async def mcp_health(self, request):
        """MCP health check endpoint"""
        return web.json_response({
            'status': 'healthy',
            'protocol': 'mcp',
            'version': '1.0',
            'server': 'youtube-mcp-server',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def mcp_initialize(self, request):
        """Initialize MCP session"""
        if not await self.check_auth(request):
            return web.json_response({'error': 'Unauthorized'}, status=401)
        
        try:
            data = await request.json()
            session_id = str(uuid.uuid4())
            
            self.sessions[session_id] = {
                'created_at': datetime.utcnow().isoformat(),
                'client_info': data.get('clientInfo', {})
            }
            
            response = {
                'jsonrpc': '2.0',
                'result': {
                    'protocolVersion': '1.0',
                    'serverInfo': {
                        'name': 'youtube-mcp-server',
                        'version': '1.0.0'
                    },
                    'capabilities': {
                        'tools': True,
                        'resources': True,
                        'prompts': True
                    },
                    'sessionId': session_id
                },
                'id': data.get('id', 1)
            }
            
            return web.json_response(response)
            
        except Exception as e:
            logger.error(f"Initialize error: {str(e)}")
            return web.json_response({
                'jsonrpc': '2.0',
                'error': {
                    'code': -32603,
                    'message': 'Internal error',
                    'data': str(e)
                },
                'id': data.get('id', 1) if 'data' in locals() else 1
            })
    
    async def mcp_list_tools(self, request):
        """List available MCP tools"""
        if not await self.check_auth(request):
            return web.json_response({'error': 'Unauthorized'}, status=401)
        
        try:
            data = await request.json()
            
            # Convert Tool objects to dicts for JSON serialization
            tools = []
            for tool in self._get_tools_list():
                tools.append({
                    'name': tool.name,
                    'description': tool.description,
                    'inputSchema': tool.inputSchema
                })
            
            response = {
                'jsonrpc': '2.0',
                'result': {
                    'tools': tools
                },
                'id': data.get('id', 1)
            }
            
            return web.json_response(response)
            
        except Exception as e:
            logger.error(f"List tools error: {str(e)}")
            return web.json_response({
                'jsonrpc': '2.0',
                'error': {
                    'code': -32603,
                    'message': 'Internal error',
                    'data': str(e)
                },
                'id': data.get('id', 1) if 'data' in locals() else 1
            })
    
    async def mcp_call_tool(self, request):
        """Execute an MCP tool"""
        if not await self.check_auth(request):
            return web.json_response({'error': 'Unauthorized'}, status=401)
        
        try:
            data = await request.json()
            params = data.get('params', {})
            tool_name = params.get('name')
            arguments = params.get('arguments', {})
            
            # Execute the tool
            result = await self._execute_tool(tool_name, arguments)
            
            response = {
                'jsonrpc': '2.0',
                'result': {
                    'content': [
                        {
                            'type': 'text',
                            'text': json.dumps(result, indent=2)
                        }
                    ]
                },
                'id': data.get('id', 1)
            }
            
            return web.json_response(response)
            
        except Exception as e:
            logger.error(f"Call tool error: {str(e)}")
            return web.json_response({
                'jsonrpc': '2.0',
                'error': {
                    'code': -32603,
                    'message': 'Internal error',
                    'data': str(e)
                },
                'id': data.get('id', 1) if 'data' in locals() else 1
            })
    
    async def health_check(self, request):
        """Health check endpoint"""
        return web.json_response({
            'status': 'healthy',
            'service': 'youtube-mcp-server',
            'mode': self.mode,
            'timestamp': datetime.utcnow().isoformat(),
            'cache_dir': str(self.cache_dir),
            'file_server_url': self.base_url,
            'cache_exists': self.cache_dir.exists(),
            'active_downloads': len(self.active_downloads),
            'mcp_enabled': True,
            'mcp_sessions': len(self.sessions) if hasattr(self, 'sessions') else 0
        })
    
    async def serve_file(self, request):
        """Serve file with token verification"""
        token = request.match_info['token']
        file_path = self.verify_token(token)
        
        if not file_path or not Path(file_path).exists():
            return web.Response(text="File not found or token expired", status=404)
        
        return web.FileResponse(file_path)
    
    # Shared methods for both modes
    def generate_token(self, file_path: str, duration_minutes: int = 15) -> str:
        """Generate a time-limited JWT token for file access"""
        expiry = datetime.utcnow() + timedelta(minutes=duration_minutes)
        payload = {
            'file_path': file_path,
            'exp': expiry
        }
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')
    
    def verify_token(self, token: str) -> Optional[str]:
        """Verify JWT token and return file path if valid"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            return payload.get('file_path')
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None
    
    def get_cache_key(self, url: str, format_type: str, quality: str = 'best') -> str:
        """Generate cache key for a download"""
        key_string = f"{url}_{format_type}_{quality}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def check_cache(self, cache_key: str) -> Optional[Path]:
        """Check if file exists in cache"""
        for ext in ['.mp4', '.mp3', '.json']:
            cached_file = self.cache_dir / f"{cache_key}{ext}"
            if cached_file.exists():
                # Check if file is not too old (7 days)
                age = time.time() - cached_file.stat().st_mtime
                if age < 7 * 24 * 3600:  # 7 days
                    return cached_file
        return None
    
    async def download_youtube(self, url: str, format_type: str = 'video', 
                              quality: str = 'best') -> Dict[str, Any]:
        """Download YouTube content"""
        cache_key = self.get_cache_key(url, format_type, quality)
        
        # Check cache first
        cached_file = self.check_cache(cache_key)
        if cached_file:
            logger.info(f"Using cached file: {cached_file}")
            token = self.generate_token(str(cached_file))
            return {
                'success': True,
                'file_path': str(cached_file),
                'url': f"{self.base_url}/files/{token}",
                'cached': True,
                'expires_at': (datetime.utcnow() + timedelta(minutes=15)).isoformat()
            }
        
        # Track active downloads
        if cache_key in self.active_downloads:
            return {
                'success': False,
                'error': 'Download already in progress for this video'
            }
        
        self.active_downloads[cache_key] = True
        
        try:
            # Configure yt-dlp options
            if format_type == 'audio':
                ext = 'mp3'
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': str(self.cache_dir / f'{cache_key}.%(ext)s'),
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192' if quality == 'best' else quality,
                    }],
                    'quiet': True,
                    'no_warnings': True,
                    'no_progress': True,
                    'logger': type('', (), {'debug': lambda *a: None, 'warning': lambda *a: None, 'error': lambda *a: None})()
                }
            else:  # video
                ext = 'mp4'
                if quality == 'best':
                    format_str = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
                else:
                    format_str = f'bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/best[height<={quality}][ext=mp4]/best'
                
                ydl_opts = {
                    'format': format_str,
                    'outtmpl': str(self.cache_dir / f'{cache_key}.%(ext)s'),
                    'merge_output_format': 'mp4',
                    'quiet': True,
                    'no_warnings': True,
                    'no_progress': True,
                    'logger': type('', (), {'debug': lambda *a: None, 'warning': lambda *a: None, 'error': lambda *a: None})()
                }
            
            # Download
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'Unknown')
                duration = info.get('duration', 0)
            
            # Find the downloaded file
            output_file = self.cache_dir / f"{cache_key}.{ext}"
            if not output_file.exists():
                # Try to find it with yt-dlp's naming
                for file in self.cache_dir.glob(f"{cache_key}.*"):
                    if file.suffix in ['.mp3', '.mp4']:
                        output_file = file
                        break
            
            if not output_file.exists():
                raise FileNotFoundError("Downloaded file not found")
            
            # Generate temporary URL
            token = self.generate_token(str(output_file))
            
            return {
                'success': True,
                'file_path': str(output_file),
                'url': f"{self.base_url}/files/{token}",
                'title': title,
                'duration': duration,
                'size': output_file.stat().st_size,
                'cached': False,
                'expires_at': (datetime.utcnow() + timedelta(minutes=15)).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Download error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            del self.active_downloads[cache_key]
    
    async def transcribe_audio(self, audio_path: str, assemblyai_key: Optional[str] = None) -> Dict[str, Any]:
        """Transcribe audio using AssemblyAI"""
        api_key = assemblyai_key or self.assemblyai_key
        if not api_key:
            return {
                'success': False,
                'error': 'AssemblyAI API key not provided'
            }
        
        try:
            headers = {
                'authorization': api_key,
                'content-type': 'application/json'
            }
            
            # Upload file
            with open(audio_path, 'rb') as f:
                response = requests.post(
                    'https://api.assemblyai.com/v2/upload',
                    headers=headers,
                    data=f
                )
            
            if response.status_code != 200:
                raise Exception(f"Upload failed: {response.text}")
            
            upload_url = response.json()['upload_url']
            
            # Start transcription
            data = {
                'audio_url': upload_url,
                'speech_model': 'best'
            }
            
            response = requests.post(
                'https://api.assemblyai.com/v2/transcript',
                json=data,
                headers=headers
            )
            
            if response.status_code != 200:
                raise Exception(f"Transcription request failed: {response.text}")
            
            transcript_id = response.json()['id']
            
            # Poll for completion
            while True:
                response = requests.get(
                    f'https://api.assemblyai.com/v2/transcript/{transcript_id}',
                    headers=headers
                )
                result = response.json()
                
                if result['status'] == 'completed':
                    # Save transcript
                    transcript_path = Path(audio_path).with_suffix('.json')
                    with open(transcript_path, 'w') as f:
                        json.dump(result, f, indent=2)
                    
                    # Generate URL for transcript
                    token = self.generate_token(str(transcript_path))
                    
                    return {
                        'success': True,
                        'text': result['text'],
                        'transcript_url': f"{self.base_url}/files/{token}",
                        'duration': result.get('audio_duration', 0),
                        'confidence': result.get('confidence', 0),
                        'expires_at': (datetime.utcnow() + timedelta(minutes=15)).isoformat()
                    }
                    
                elif result['status'] == 'error':
                    raise Exception(f"Transcription failed: {result.get('error', 'Unknown error')}")
                
                await asyncio.sleep(3)
                
        except Exception as e:
            logger.error(f"Transcription error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_video_info(self, url: str) -> Dict[str, Any]:
        """Get video metadata"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'no_progress': True,
                'logger': type('', (), {'debug': lambda *a: None, 'warning': lambda *a: None, 'error': lambda *a: None})()
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Extract relevant metadata
                metadata = {
                    'title': info.get('title'),
                    'description': info.get('description'),
                    'duration': info.get('duration'),
                    'uploader': info.get('uploader'),
                    'upload_date': info.get('upload_date'),
                    'view_count': info.get('view_count'),
                    'like_count': info.get('like_count'),
                    'thumbnail': info.get('thumbnail'),
                    'formats': len(info.get('formats', [])),
                    'subtitles': list(info.get('subtitles', {}).keys())
                }
                
                return metadata
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def cleanup_expired_files(self):
        """Cleanup old files from cache"""
        while True:
            try:
                now = time.time()
                for file in self.cache_dir.iterdir():
                    if file.is_file():
                        age = now - file.stat().st_mtime
                        if age > 7 * 24 * 3600:  # 7 days
                            file.unlink()
                            logger.info(f"Deleted old file: {file}")
            except Exception as e:
                logger.error(f"Cleanup error: {e}")
            
            # Run cleanup every hour
            await asyncio.sleep(3600)
    
    async def run_stdio(self):
        """Run the MCP server in STDIO mode"""
        logger.info("Starting YouTube MCP Server in STDIO mode (for Claude Desktop)")
        
        # Start cleanup task
        asyncio.create_task(self.cleanup_expired_files())
        
        # Run MCP server
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )
    
    async def run_http(self):
        """Run the MCP server in HTTP mode"""
        # Start cleanup task
        asyncio.create_task(self.cleanup_expired_files())
        
        # Start web server
        runner = web.AppRunner(self.web_app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 8080)
        await site.start()
        
        logger.info(f"YouTube MCP Server started in HTTP mode on {self.base_url}")
        logger.info(f"File server: {self.base_url}/files/{{token}}")
        logger.info(f"MCP endpoints: {self.base_url}/mcp/*")
        if hasattr(self, 'api_key') and self.api_key:
            logger.info("API key authentication enabled")
        else:
            logger.warning("API key authentication disabled - server is open to all requests")
        
        # Keep the server running
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            logger.info("Server shutting down...")

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='YouTube MCP Server - Dual Mode')
    parser.add_argument('--http', action='store_true', 
                       help='Run in HTTP mode (default: STDIO mode for Claude Desktop)')
    args = parser.parse_args()
    
    # Check environment variable as well
    http_mode = args.http or os.environ.get('HTTP_MODE', '').lower() in ['true', '1', 'yes']
    
    mode = 'http' if http_mode else 'stdio'
    server = YouTubeMCPServer(mode=mode)
    
    if mode == 'http':
        await server.run_http()
    else:
        await server.run_stdio()

if __name__ == "__main__":
    asyncio.run(main())
