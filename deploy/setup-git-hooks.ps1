# ==============================================================================
# Setup Local Git Pre-Push Hooks
# ==============================================================================

Write-Host "Configuring local Git hooks directory..." -ForegroundColor Cyan

# Set Git to look for hooks in .githooks directory
git config core.hooksPath .githooks

Write-Host "Local Git pre-push hook activated successfully!" -ForegroundColor Green
Write-Host "Any future 'git push' will automatically run pytest and block pushing if tests fail." -ForegroundColor Yellow
