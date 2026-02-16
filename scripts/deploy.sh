#!/bin/bash

# Deployment script for Telegram Signal Copy Bot
# This script runs on the VPS to deploy the bot

set -e  # Exit on error

echo "========================================="
echo "Telegram Bot Deployment Script"
echo "========================================="

# Configuration
APP_DIR="/root/telegram-signal-copy-bot"
CONTAINER_NAME="telegram-bot"
IMAGE_NAME="telegram-bot:latest"

# Navigate to app directory
cd "$APP_DIR"

echo "✓ Working directory: $(pwd)"

# Create .env file from environment variable
if [ -n "$ENV_CONTENT" ]; then
    echo "✓ Creating .env file..."
    echo "$ENV_CONTENT" > .env
    chmod 600 .env
else
    echo "⚠ Warning: ENV_CONTENT not provided, using existing .env file"
fi

# Stop and remove existing container
echo "✓ Stopping existing container..."
docker stop "$CONTAINER_NAME" 2>/dev/null || true
docker rm "$CONTAINER_NAME" 2>/dev/null || true

# Build new Docker image
echo "✓ Building Docker image..."
docker build -t "$IMAGE_NAME" .

# Run new container with volume mounts for persistence
echo "✓ Starting new container..."
docker run -d \
    --name "$CONTAINER_NAME" \
    --restart unless-stopped \
    -v "$APP_DIR/sessions:/app/sessions" \
    -v "$APP_DIR/logs:/app/logs" \
    "$IMAGE_NAME"

# Wait for container to start
sleep 3

# Check container status
if docker ps | grep -q "$CONTAINER_NAME"; then
    echo "========================================="
    echo "✅ Deployment successful!"
    echo "========================================="
    echo "Container status:"
    docker ps | grep "$CONTAINER_NAME"
    echo ""
    echo "Recent logs:"
    docker logs --tail 20 "$CONTAINER_NAME"
else
    echo "========================================="
    echo "❌ Deployment failed!"
    echo "========================================="
    echo "Container logs:"
    docker logs "$CONTAINER_NAME"
    exit 1
fi

# Clean up old images
echo ""
echo "✓ Cleaning up old images..."
docker image prune -f

echo ""
echo "========================================="
echo "Deployment complete!"
echo "========================================="
