#!/bin/bash
# ==============================================================================
# AWS EC2 Cloud-Init User Data Script
# Automatically installs Docker and runs the CloudPulse Containerized Microservice
# ==============================================================================

set -e
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1

echo "============================================="
echo "Starting CloudPulse EC2 Automated Provisioning"
echo "============================================="

# 1. Update OS packages
apt-get update -y
apt-get install -y apt-transport-https ca-certificates curl software-properties-common git

# 2. Install Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io
systemctl enable docker
systemctl start docker

# 3. Add ubuntu user to docker group
usermod -aG docker ubuntu

# 4. Clone repository or run application
APP_DIR="/opt/cloudpulse"
mkdir -p $APP_DIR
cd /opt

# Fetch instance metadata for unique node ID
TOKEN=`curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600" 2>/dev/null`
INSTANCE_ID=`curl -H "X-aws-ec2-metadata-token: $TOKEN" -s http://169.254.169.254/latest/meta-data/instance-id 2>/dev/null || echo "aws-ec2-demo-node"`

# 5. Clone repository code (replace with user repository if applicable)
if [ ! -d "$APP_DIR/.git" ]; then
    git clone https://github.com/REPLACE_WITH_YOUR_GITHUB_USERNAME/cloudpulse-microservice.git $APP_DIR || true
fi

cd $APP_DIR

if [ -f "Dockerfile" ]; then
    echo "Building container from cloned repo..."
    docker build -t cloudpulse-app .
    docker run -d --name cloudpulse-live \
        --restart always \
        -p 80:8000 \
        -e INSTANCE_ID="$INSTANCE_ID" \
        -e ENVIRONMENT="aws-ec2" \
        cloudpulse-app
else
    echo "Running fallback container image..."
    docker run -d --name cloudpulse-live \
        --restart always \
        -p 80:80 \
        nginx:alpine
fi

echo "============================================="
echo "CloudPulse Microservice is active on Port 80!"
echo "============================================="
