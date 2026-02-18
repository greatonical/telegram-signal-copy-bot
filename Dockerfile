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

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

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
