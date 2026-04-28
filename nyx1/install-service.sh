#!/bin/bash
# Install NYX backend as a systemd service
# Run with: sudo ./install-service.sh

set -e

SERVICE_NAME="nyx-backend"
SERVICE_FILE="nyx-backend.service"
SYSTEMD_DIR="/etc/systemd/system"
PROJECT_DIR="/mnt/c/Users/rudra/Desktop/project/hermes/nyx1"

echo "=== NYX Backend Systemd Service Installer ==="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root: sudo ./install-service.sh"
    exit 1
fi

# Check if systemd is available
if ! command -v systemctl &> /dev/null; then
    echo "ERROR: systemctl not found. This system doesn't use systemd."
    exit 1
fi

# Copy service file
echo "Copying service file to $SYSTEMD_DIR..."
cp "$PROJECT_DIR/$SERVICE_FILE" "$SYSTEMD_DIR/"

# Reload systemd
echo "Reloading systemd..."
systemctl daemon-reload

# Enable service (start on boot)
echo "Enabling $SERVICE_NAME service..."
systemctl enable "$SERVICE_NAME"

# Start service now
echo "Starting $SERVICE_NAME service..."
systemctl start "$SERVICE_NAME"

# Check status
sleep 2
echo ""
echo "=== Service Status ==="
systemctl status "$SERVICE_NAME" --no-pager

echo ""
echo "=== Done ==="
echo "Commands you can use:"
echo "  sudo systemctl status $SERVICE_NAME   # Check status"
echo "  sudo systemctl stop $SERVICE_NAME     # Stop"
echo "  sudo systemctl start $SERVICE_NAME    # Start"
echo "  sudo systemctl restart $SERVICE_NAME  # Restart"
echo "  sudo journalctl -u $SERVICE_NAME -f   # View logs"
