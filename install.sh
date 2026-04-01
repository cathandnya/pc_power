#!/bin/bash
set -e

APP_DIR="/opt/fp-bridge"
VENV_DIR="$APP_DIR/.venv"

echo "=== Front Panel Bridge ==="

# Install system dependencies
echo "Installing system packages..."
sudo apt-get update -qq
sudo apt-get install -y -qq python3-venv python3-pip

# Copy app
echo "Copying files to $APP_DIR..."
sudo mkdir -p "$APP_DIR"
sudo cp -r app web requirements.txt "$APP_DIR/"

# Create venv and install packages
echo "Setting up Python virtual environment..."
sudo python3 -m venv "$VENV_DIR"
sudo "$VENV_DIR/bin/pip" install -r "$APP_DIR/requirements.txt"

# Install systemd service
echo "Installing systemd service..."
sudo cp fp-bridge.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable fp-bridge
sudo systemctl restart fp-bridge

echo "Done! Access http://$(hostname -I | awk '{print $1}'):8080"
