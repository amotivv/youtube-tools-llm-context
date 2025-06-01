# Use Python 3.11 slim image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/cache /tmp/youtube-mcp

# Expose port for HTTP MCP server and file server
EXPOSE 8080

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV CACHE_DIR=/app/cache
ENV TEMP_DIR=/tmp/youtube-mcp
ENV BASE_URL=http://localhost:8080

# Run the server in HTTP mode for Docker deployments
CMD ["python", "server.py", "--http"]
