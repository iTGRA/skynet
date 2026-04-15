#!/bin/bash
set -e

echo "=== Skynet Deployment Script for Rocky Linux ==="

# Step 1: System update and base dependencies
echo "[1/5] Updating system and installing base packages..."
dnf update -y
dnf install -y python3 python3-pip python3-venv nginx git curl wget

# Step 2: Python virtual environment
echo "[2/5] Creating Python virtual environment..."
PROJECT_DIR="/opt/mcpserver"
VENV_DIR="$PROJECT_DIR/venv"
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
[ -f "$PROJECT_DIR/requirements.txt" ] && pip install -r "$PROJECT_DIR/requirements.txt"
echo "Virtual environment created at $VENV_DIR"

# Step 3: Nginx configuration
echo "[3/5] Configuring Nginx..."
cat > /etc/nginx/conf.d/mcpserver.conf << 'NGINX'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location /sse {
        proxy_pass http://127.0.0.1:8000/sse;
        proxy_set_header Host $host;
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header X-Accel-Buffering no;
    }
}
NGINX
systemctl enable nginx
systemctl restart nginx
echo "Nginx configured and restarted"

# Step 4: Systemd unit for MCP server
echo "[4/5] Creating systemd service unit..."
cat > /etc/systemd/system/mcpserver.service << 'UNIT'
[Unit]
Description=Skynet MCP Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/mcpserver
EnvironmentFile=-/opt/mcpserver/.env
ExecStart=/opt/mcpserver/venv/bin/python /opt/mcpserver/main.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload
systemctl enable mcpserver
echo "Systemd unit created and enabled"

# Step 5: Done
echo "[5/5] Deployment complete! Run 'systemctl start mcpserver' to launch."
echo "=== Skynet is ready to rise. ==="
