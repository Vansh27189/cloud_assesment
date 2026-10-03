# ==============================================================================
# CloudPulse Microservice - AWS Deployment Automation (PowerShell)
# ==============================================================================

param(
    [string]$Region = "us-east-1",
    [string]$RepositoryName = "cloudpulse-microservice",
    [string]$InstanceType = "t2.micro"
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "CloudPulse Microservice - AWS Deployment" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. Verify AWS CLI
try {
    $callerIdentity = aws sts get-caller-identity | ConvertFrom-Json
    Write-Host "Authenticated as AWS Account: $($callerIdentity.Account)" -ForegroundColor Green
} catch {
    Write-Host "AWS CLI is not configured or authenticated." -ForegroundColor Red
    Write-Host "Please run 'aws configure' and enter your AWS Access Key, Secret Key, and Region." -ForegroundColor Yellow
    exit 1
}

$accountId = $callerIdentity.Account

# 2. Ensure ECR repository exists
Write-Host "Checking Amazon ECR repository: $RepositoryName..." -ForegroundColor Cyan
$repoCheck = aws ecr describe-repositories --repository-names $RepositoryName --region $Region 2>$null
if (-not $repoCheck) {
    Write-Host "Creating Amazon ECR repository: $RepositoryName..." -ForegroundColor Yellow
    aws ecr create-repository --repository-name $RepositoryName --region $Region
}

# 3. Log in to Amazon ECR
Write-Host "Logging in to Amazon ECR..." -ForegroundColor Cyan
$ecrUri = "$accountId.dkr.ecr.$Region.amazonaws.com"
aws ecr get-login-password --region $Region | docker login --username AWS --password-stdin $ecrUri

# 4. Build and Tag Docker Image
Write-Host "Building Docker image..." -ForegroundColor Cyan
docker build -t $RepositoryName .
docker tag "$RepositoryName`:latest" "$ecrUri/$RepositoryName`:latest"

# 5. Push to Amazon ECR
Write-Host "Pushing image to Amazon ECR ($ecrUri/$RepositoryName:latest)..." -ForegroundColor Cyan
docker push "$ecrUri/$RepositoryName`:latest"
Write-Host "ECR Push complete!" -ForegroundColor Green

Write-Host "`nNext Step: Run on EC2 or ECS with container image:" -ForegroundColor Yellow
Write-Host "$ecrUri/$RepositoryName`:latest" -ForegroundColor White
