#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# ec2-setup.sh — Run this ONCE on a fresh Amazon Linux 2023 / Ubuntu EC2.
# Usage: chmod +x ec2-setup.sh && sudo ./ec2-setup.sh
# ─────────────────────────────────────────────────────────────────────────────

set -e

echo "==> Updating system packages..."
if command -v apt-get &>/dev/null; then
    apt-get update -y && apt-get upgrade -y
    # Ubuntu / Debian
    apt-get install -y docker.io curl
    systemctl enable docker
    systemctl start docker
    usermod -aG docker ubuntu
else
    # Amazon Linux 2023
    dnf update -y
    dnf install -y docker curl
    systemctl enable docker
    systemctl start docker
    usermod -aG docker ec2-user
fi

echo "==> Installing Docker Compose plugin..."
mkdir -p /usr/local/lib/docker/cli-plugins
curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 \
     -o /usr/local/lib/docker/cli-plugins/docker-compose
chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

echo ""
echo "✅  Done! Docker version: $(docker --version)"
echo "✅  Log out and back in so group changes take effect."
