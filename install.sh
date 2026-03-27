#!/bin/bash
set -e

APP_DIR="/opt/pc-power"

echo "=== Front Panel Bridge ==="

# Install dependencies
echo "Installing Python packages..."
pip3 install -r requirements.txt

# Copy app
echo "Copying files to $APP_DIR..."
sudo mkdir -p "$APP_DIR"
sudo cp -r app web requirements.txt "$APP_DIR/"

# Install systemd service
echo "Installing systemd service..."
sudo cp pc-power.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable pc-power
sudo systemctl restart pc-power

echo "Done! Access http://$(hostname -I | awk '{print $1}'):8080"
