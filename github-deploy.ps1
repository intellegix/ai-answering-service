# AI Answering Service - GitHub CLI Deployment
# Austin Kidwell | ASR Inc / Intellegix

Write-Host "🚀 AI Answering Service - GitHub CLI Deployment" -ForegroundColor Cyan
Write-Host "Austin Kidwell | ASR Inc / Intellegix" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan

# Check if we're in the right directory
Write-Host "`n📁 Checking project structure..." -ForegroundColor Yellow

$requiredFiles = @(
    "render.yaml",
    "README.md",
    "backend\app.py",
    "frontend\src\App.jsx"
)

$missingFiles = @()
foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host "❌ Missing required files:" -ForegroundColor Red
    foreach ($file in $missingFiles) {
        Write-Host "   - $file" -ForegroundColor Red
    }
    Write-Host "`nPlease ensure you're running this script from the project root directory." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ All required files found" -ForegroundColor Green

# Check GitHub CLI
Write-Host "`n🔧 Checking GitHub CLI..." -ForegroundColor Yellow
try {
    $ghVersion = gh --version
    Write-Host "✅ GitHub CLI found: $($ghVersion[0])" -ForegroundColor Green
} catch {
    Write-Host "❌ GitHub CLI not found. Please install from: https://cli.github.com/" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Git
Write-Host "`n🔧 Checking Git..." -ForegroundColor Yellow
try {
    $gitVersion = git --version
    Write-Host "✅ Git found: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Git not found. Please install Git first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Initialize Git repository if not already done
Write-Host "`n📦 Initializing Git repository..." -ForegroundColor Yellow
if (-not (Test-Path ".git")) {
    git init
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Git repository initialized" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to initialize Git repository" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✅ Git repository already exists" -ForegroundColor Green
}

# Configure Git user if needed
Write-Host "`n👤 Checking Git configuration..." -ForegroundColor Yellow
$gitName = git config user.name
$gitEmail = git config user.email

if (-not $gitName -or -not $gitEmail) {
    Write-Host "⚠️ Git user not configured" -ForegroundColor Yellow

    if (-not $gitName) {
        git config user.name "Austin Kidwell"
        Write-Host "✅ Set Git username: Austin Kidwell" -ForegroundColor Green
    }

    if (-not $gitEmail) {
        $email = Read-Host "Enter your Git email address"
        git config user.email $email
        Write-Host "✅ Set Git email: $email" -ForegroundColor Green
    }
} else {
    Write-Host "✅ Git configured: $gitName ($gitEmail)" -ForegroundColor Green
}

# Add all files
Write-Host "`n📁 Adding files to Git..." -ForegroundColor Yellow
git add .
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ All files added to Git" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to add files to Git" -ForegroundColor Red
    exit 1
}

# Create commit
Write-Host "`n💾 Creating commit..." -ForegroundColor Yellow
$commitMessage = @"
Initial commit: Complete AI Answering Service implementation

🎯 Features implemented:
- Flask backend with Claude 3.5 Sonnet integration
- Node.js conversation relay with OpenAI TTS
- React dashboard with mobile-responsive design
- Twilio voice integration with webhooks
- PostgreSQL database models and API endpoints
- Render.com deployment configuration
- Complete documentation and testing guides

🏗️ Architecture:
- Backend: Flask + SQLAlchemy + PostgreSQL
- AI: Claude API + OpenAI TTS + Twilio Voice
- Frontend: React + Modern CSS (mobile-first)
- Deployment: Render.com with auto-scaling

📊 Business ready:
- Professional AI secretary for ASR Inc / Intellegix
- 24/7 phone coverage with intelligent responses
- Real-time call management dashboard
- Cost-effective operation (~$50-85/month)

Built with Claude Code following Austin's coding standards.
"@

git commit -m $commitMessage
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Commit created successfully" -ForegroundColor Green
} else {
    # Check if there are changes to commit
    $status = git status --porcelain
    if (-not $status) {
        Write-Host "✅ No changes to commit (repository up to date)" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to create commit" -ForegroundColor Red
        exit 1
    }
}

# Set main branch
Write-Host "`n🌿 Setting main branch..." -ForegroundColor Yellow
git branch -M main
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Main branch set" -ForegroundColor Green
} else {
    Write-Host "⚠️ Branch already set to main" -ForegroundColor Yellow
}

# Add remote origin
Write-Host "`n🔗 Adding remote origin..." -ForegroundColor Yellow
$repoUrl = "https://github.com/intellegix/ai-answering-service.git"

# Remove existing remote if it exists
git remote remove origin 2>$null

git remote add origin $repoUrl
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Remote origin added: $repoUrl" -ForegroundColor Green
} else {
    Write-Host "⚠️ Remote origin might already exist" -ForegroundColor Yellow
}

# Push to GitHub
Write-Host "`n🚀 Pushing to GitHub..." -ForegroundColor Yellow
Write-Host "Repository: https://github.com/intellegix/ai-answering-service" -ForegroundColor Cyan

git push -u origin main
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Successfully pushed to GitHub!" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to push to GitHub" -ForegroundColor Red
    Write-Host "This might be due to authentication issues." -ForegroundColor Yellow
    Write-Host "Please ensure you're logged in with: gh auth login" -ForegroundColor Yellow
    exit 1
}

# Success message
Write-Host "`n🎉 DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 GitHub Repository: https://github.com/intellegix/ai-answering-service" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Yellow
Write-Host "1. ✅ Code uploaded to GitHub successfully"
Write-Host "2. 🔄 Return to Render Dashboard Blueprint"
Write-Host "3. 🔍 Search for 'ai-answering-service' repository"
Write-Host "4. 🚀 Deploy all services automatically"
Write-Host "5. 🔑 Configure API keys in environment variables"
Write-Host "6. 📞 Set up Twilio webhooks"
Write-Host "7. ✅ Test your AI answering service!"
Write-Host ""

# Open GitHub repository
$openGitHub = Read-Host "Open GitHub repository in browser? (y/N)"
if ($openGitHub -eq "y" -or $openGitHub -eq "Y") {
    Start-Process "https://github.com/intellegix/ai-answering-service"
    Write-Host "✅ GitHub repository opened" -ForegroundColor Green
}

# Open Render Blueprint
$openRender = Read-Host "Open Render Blueprint deployment? (y/N)"
if ($openRender -eq "y" -or $openRender -eq "Y") {
    Start-Process "https://dashboard.render.com/select-repo?type=blueprint"
    Write-Host "✅ Render Blueprint opened" -ForegroundColor Green
}

Write-Host ""
Write-Host "🎯 Ready for Render deployment!" -ForegroundColor Green
Write-Host "Your AI Answering Service is now on GitHub and ready to deploy." -ForegroundColor Cyan

Read-Host "Press Enter to exit"