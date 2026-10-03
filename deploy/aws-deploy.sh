#!/usr/bin/env bash
# ==============================================================================
# CloudPulse Microservice - AWS Deployment Automation (Bash)
# ==============================================================================

set -e

REGION="${AWS_REGION:-us-east-1}"
REPOSITORY_NAME="cloudpulse-microservice"

echo "=========================================="
echo "CloudPulse Microservice - AWS Deployment"
echo "=========================================="

# Check AWS CLI authentication
ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
if [ -z "$ACCOUNT_ID" ]; then
    echo "Error: AWS CLI not authenticated. Run 'aws configure' first."
    exit 1
fi

echo "Authenticated with AWS Account: $ACCOUNT_ID (Region: $REGION)"

# Create ECR repository if missing
aws ecr describe-repositories --repository-names "$REPOSITORY_NAME" --region "$REGION" >/dev/null 2>&1 || \
aws ecr create-repository --repository-name "$REPOSITORY_NAME" --region "$REGION"

# Authenticate Docker to ECR
ECR_URI="$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"
aws ecr get-login-password --region "$REGION" | docker login --username AWS --password-stdin "$ECR_URI"

# Build, tag and push
echo "Building Docker container image..."
docker build -t "$REPOSITORY_NAME" .
docker tag "$REPOSITORY_NAME:latest" "$ECR_URI/$REPOSITORY_NAME:latest"

echo "Pushing Docker image to Amazon ECR..."
docker push "$ECR_URI/$REPOSITORY_NAME:latest"

echo "=========================================="
echo "Successfully pushed to ECR: $ECR_URI/$REPOSITORY_NAME:latest"
echo "=========================================="
