#!/usr/bin/env python3
"""
Quick Deployment Script for AI Answering Service
Simplified Render deployment with GitHub autodeploy setup
Austin Kidwell | ASR Inc / Intellegix
"""

import os
import json
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description=""):
    """Run a shell command and handle errors."""
    print(f"🔄 {description}")
    print(f"Running: {cmd}")

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Error: {result.stderr}")
            return False, result.stderr
        if result.stdout:
            print(f"✅ Output: {result.stdout.strip()}")
        return True, result.stdout.strip()
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False, str(e)

def check_prerequisites():
    """Check if all prerequisites are installed."""
    print("🔍 Checking Prerequisites...")

    # Check Git
    success, _ = run_command("git --version", "Checking Git")
    if not success:
        print("❌ Git is required. Install from: https://git-scm.com/")
        return False

    # Check GitHub CLI (optional but recommended)
    success, _ = run_command("gh --version", "Checking GitHub CLI")
    if not success:
        print("💡 GitHub CLI not found (optional). Install from: https://cli.github.com/")

    # Check required Python packages
    try:
        import requests
        print("✅ Python requests library available")
    except ImportError:
        print("❌ Python requests library required. Install with: pip install requests")
        return False

    return True

def setup_git_repository():
    """Set up Git repository if not already done."""
    print("\n📦 Setting up Git Repository...")

    # Initialize git if needed
    if not Path(".git").exists():
        success, _ = run_command("git init", "Initializing Git repository")
        if not success:
            return False

    # Add all files
    success, _ = run_command("git add .", "Adding files to Git")
    if not success:
        return False

    # Create commit if there are changes
    success, output = run_command("git status --porcelain", "Checking for changes")
    if success and output.strip():
        success, _ = run_command('git commit -m "Initial commit: AI Answering Service"', "Creating commit")
        if not success:
            print("⚠️ Commit failed, but continuing...")

    return True

def get_github_info():
    """Get GitHub repository information."""
    print("\n🐙 GitHub Repository Setup")

    # Try to get existing remote
    success, output = run_command("git config --get remote.origin.url", "Checking existing remote")

    if success and "github.com" in output:
        print(f"✅ Found existing GitHub remote: {output}")
        # Parse owner/repo from URL
        repo_url = output.strip()
        if repo_url.endswith(".git"):
            repo_url = repo_url[:-4]

        if "github.com/" in repo_url:
            parts = repo_url.split("github.com/")[1].split("/")
            if len(parts) >= 2:
                return parts[0], parts[1], repo_url

    # Manual setup
    print("🔧 Manual GitHub Setup Required")
    print("1. Create a new repository on GitHub: https://github.com/new")
    print("2. Name it 'ai-answering-service' (or your preferred name)")
    print("3. Don't initialize with README (we have our own)")
    print("4. Copy the repository URL")

    owner = input("\nEnter your GitHub username: ").strip()
    repo = input("Enter repository name [ai-answering-service]: ").strip() or "ai-answering-service"
    repo_url = f"https://github.com/{owner}/{repo}.git"

    # Set remote and push
    run_command(f"git remote add origin {repo_url}", "Adding GitHub remote")
    run_command("git branch -M main", "Setting main branch")
    success, _ = run_command("git push -u origin main", "Pushing to GitHub")

    if not success:
        print("❌ Failed to push to GitHub. Please verify the repository exists and try again.")
        return None, None, None

    return owner, repo, repo_url

def create_render_blueprint():
    """Create Render Blueprint deployment."""
    print(f"\n🚀 Creating Render Blueprint Deployment")

    print("📋 Manual Render Setup (Blueprint Method - Recommended)")
    print("=" * 60)

    print("1. Go to Render Dashboard: https://dashboard.render.com/")
    print("2. Click 'New +' → 'Blueprint'")
    print("3. Connect your GitHub account if not already connected")
    print("4. Select your repository")
    print("5. Render will detect the render.yaml file automatically")
    print("6. Click 'Apply' to create all services")

    print("\n🔑 Environment Variables to Set:")
    print("After services are created, add these environment variables:")

    env_vars = [
        ("ANTHROPIC_API_KEY", "Your Claude API key (sk-ant-...)"),
        ("OPENAI_API_KEY", "Your OpenAI API key (sk-...)"),
        ("TWILIO_ACCOUNT_SID", "Your Twilio Account SID (AC...)"),
        ("TWILIO_AUTH_TOKEN", "Your Twilio Auth Token"),
        ("TWILIO_PHONE_NUMBER", "Your Twilio phone number (+1...)"),
        ("PERPLEXITY_API_KEY", "Optional: Perplexity API key (ppl-...)")
    ]

    for key, description in env_vars:
        print(f"   {key}: {description}")

    print(f"\n📞 Twilio Webhook Configuration:")
    print("After deployment, configure these Twilio webhooks:")
    print("   Incoming Calls: https://ai-secretary-backend.onrender.com/incoming-call")
    print("   Call Status: https://ai-secretary-backend.onrender.com/call-ended")

    return True

def verify_deployment():
    """Provide verification steps."""
    print(f"\n✅ Deployment Verification Steps:")
    print("1. Check service health endpoints:")
    print("   Backend: https://ai-secretary-backend.onrender.com/health")
    print("   Relay: https://ai-conversation-relay.onrender.com/relay/health")
    print("   Frontend: https://ai-secretary-frontend.onrender.com")

    print("\n2. Test the complete system:")
    print("   - Call your Twilio phone number")
    print("   - Verify AI assistant answers")
    print("   - Check call appears in dashboard")

    print("\n3. Monitor in Render Dashboard:")
    print("   - Watch deployment logs")
    print("   - Verify all services are running")
    print("   - Check for any errors")

def main():
    """Main deployment function."""
    print("🚀 AI Answering Service - Quick Deploy")
    print("Austin Kidwell | ASR Inc / Intellegix")
    print("=" * 50)

    # Check prerequisites
    if not check_prerequisites():
        print("❌ Prerequisites not met. Please install required software.")
        sys.exit(1)

    # Verify project structure
    required_files = ["backend/app.py", "frontend/src/App.jsx", "render.yaml"]
    missing = [f for f in required_files if not os.path.exists(f)]

    if missing:
        print("❌ Missing required files:")
        for f in missing:
            print(f"   - {f}")
        print("Please ensure you're in the project root directory.")
        sys.exit(1)

    print("✅ Project structure verified")

    # Setup Git repository
    if not setup_git_repository():
        print("❌ Git repository setup failed")
        sys.exit(1)

    # Get GitHub repository info
    owner, repo, repo_url = get_github_info()
    if not owner or not repo:
        print("❌ GitHub setup incomplete")
        sys.exit(1)

    print(f"✅ GitHub repository: {owner}/{repo}")

    # Create Render deployment
    create_render_blueprint()

    print(f"\n🎉 Setup Complete!")
    print("Your AI Answering Service is ready for deployment on Render.")

    # Save deployment info
    deployment_info = {
        "github_owner": owner,
        "github_repo": repo,
        "github_url": repo_url.replace('.git', ''),
        "render_blueprint": True,
        "next_steps": [
            "Go to Render Dashboard and create Blueprint",
            "Add environment variables",
            "Configure Twilio webhooks",
            "Test the system"
        ]
    }

    with open("deployment_config.json", "w") as f:
        json.dump(deployment_info, f, indent=2)

    print(f"💾 Deployment config saved to deployment_config.json")

    verify_deployment()

if __name__ == "__main__":
    main()