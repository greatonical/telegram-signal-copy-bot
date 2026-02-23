FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install all pinned/versioned dependencies first (fully cacheable layer)
RUN pip install --no-cache-dir $(grep -v 'github.com' requirements.txt | tr '\n' ' ')

# Install Telethon from git HEAD — bust this cache on every deploy so we always
# get the latest commit (which may include new TL constructors Telegram added).
# Pass --build-arg CACHEBUST=$(date +%s) when building / deploying.
ARG CACHEBUST=1
RUN pip install --no-cache-dir git+https://codeberg.org/Lonami/Telethon.git

# Copy application code
COPY . .

# Create directories for sessions and logs
RUN mkdir -p sessions logs

# Set permissions
RUN chmod -R 755 /app

# Expose port for API
EXPOSE 8080

# Run both bot and API server
CMD ["python", "start.py"]
