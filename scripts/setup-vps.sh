#!/bin/bash

# VPS Setup Script
# Run this script to install Docker and Git on the VPS

echo "========================================="
echo "VPS Setup Script"
echo "========================================="
echo ""
echo "This script will install Docker and Git on your VPS"
echo ""
echo "VPS Details:"
echo "  Host: 205.209.121.94"
echo "  User: root"
echo "  Port: 22"
echo ""
echo "You will be prompted for the password: x93Zoquy&BTJQ0"
echo ""
read -p "Press Enter to continue..."

# SSH into VPS and run setup commands
ssh -p 22 root@205.209.121.94 << 'ENDSSH'
echo "========================================="
echo "Installing Docker..."
echo "========================================="

# Check if Docker is already installed
if command -v docker &> /dev/null; then
    echo "✓ Docker is already installed"
    docker --version
else
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    echo "✓ Docker installed successfully"
    docker --version
fi

echo ""
echo "========================================="
echo "Installing Git..."
echo "========================================="

# Check if Git is already installed
if command -v git &> /dev/null; then
    echo "✓ Git is already installed"
    git --version
else
    echo "Installing Git..."
    apt-get update
    apt-get install -y git
    echo "✓ Git installed successfully"
    git --version
fi

echo ""
echo "========================================="
echo "Creating application directory..."
echo "========================================="

mkdir -p /root/telegram-signal-copy-bot
echo "✓ Created /root/telegram-signal-copy-bot"

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Configure GitHub Secrets (run ./setup-secrets.sh for details)"
echo "2. Commit and push your code to GitHub"
echo "3. The GitHub Action will automatically deploy to VPS"
echo ""
ENDSSH

echo ""
echo "========================================="
echo "VPS Setup Complete!"
echo "========================================="
