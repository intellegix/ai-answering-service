@echo off
echo AI Answering Service - GitHub CLI Deployment
echo Austin Kidwell | ASR Inc / Intellegix
echo ================================================

echo.
echo Checking GitHub CLI...
gh --version
if %errorlevel% neq 0 (
    echo Error: GitHub CLI not found. Please install from: https://cli.github.com/
    pause
    exit /b 1
)

echo.
echo Initializing Git repository...
git init
if %errorlevel% neq 0 (
    echo Error: Git initialization failed
    pause
    exit /b 1
)

echo.
echo Adding all files...
git add .
if %errorlevel% neq 0 (
    echo Error: Failed to add files
    pause
    exit /b 1
)

echo.
echo Creating initial commit...
git commit -m "Initial commit: Complete AI Answering Service implementation

- Flask backend with Claude + Twilio integration
- Node.js conversation relay with OpenAI TTS
- React dashboard with mobile-responsive design
- Render deployment configuration
- Complete documentation and testing guides
"
if %errorlevel% neq 0 (
    echo Error: Commit failed
    pause
    exit /b 1
)

echo.
echo Setting main branch...
git branch -M main
if %errorlevel% neq 0 (
    echo Error: Failed to set main branch
    pause
    exit /b 1
)

echo.
echo Adding remote origin...
git remote add origin https://github.com/intellegix/ai-answering-service.git
if %errorlevel% neq 0 (
    echo Warning: Remote might already exist, continuing...
)

echo.
echo Pushing to GitHub...
git push -u origin main
if %errorlevel% neq 0 (
    echo Error: Push to GitHub failed
    echo Please check your GitHub authentication
    pause
    exit /b 1
)

echo.
echo ================================================
echo SUCCESS! AI Answering Service uploaded to GitHub
echo ================================================
echo.
echo Repository: https://github.com/intellegix/ai-answering-service
echo.
echo Next Steps:
echo 1. Return to Render Dashboard
echo 2. Search for 'ai-answering-service' in Blueprint
echo 3. Deploy all services automatically
echo 4. Configure API keys in environment variables
echo.
echo Press any key to open GitHub repository...
pause
start https://github.com/intellegix/ai-answering-service
echo.
echo Press any key to open Render Blueprint...
pause
start https://dashboard.render.com/select-repo?type=blueprint
echo.
echo Deployment script complete!
pause