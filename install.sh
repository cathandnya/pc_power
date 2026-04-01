#!/bin/bash
set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$REPO_DIR/.venv"

echo "=== Front Panel Bridge ==="

# Install system dependencies
echo "Installing system packages..."
sudo apt-get update -qq
sudo apt-get install -y -qq python3-venv python3-pip

# Create venv and install packages
echo "Setting up Python virtual environment..."
python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install -r "$REPO_DIR/requirements.txt"

# Install systemd service
echo "Installing systemd service..."
sudo cp "$REPO_DIR/fp-bridge.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable fp-bridge
sudo systemctl restart fp-bridge

echo "Done! Access http://$(hostname -I | awk '{print $1}'):8080"
