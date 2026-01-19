#!/usr/bin/env python3
"""
GitHub Repository Setup Script
Initializes git repository and pushes AI Answering Service to GitHub
Austin Kidwell | ASR Inc / Intellegix
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description=""):
    """Run a shell command and handle errors."""
    print(f"\n🔄 {description}")
    print(f"Running: {cmd}")

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Error: {result.stderr}")
            return False
        if result.stdout:
            print(f"✅ Output: {result.stdout.strip()}")
        return True
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def check_git_installed():
    """Check if git is installed."""
    return run_command("git --version", "Checking Git installation")

def check_gh_cli_installed():
    """Check if GitHub CLI is installed."""
    return run_command("gh --version", "Checking GitHub CLI installation")

def setup_github_repository():
    """Set up GitHub repository for AI Answering Service."""

    print("🚀 AI Answering Service - GitHub Setup")
    print("=" * 50)

    # Check prerequisites
    if not check_git_installed():
        print("\n❌ Git is not installed. Please install Git first:")
        print("Windows: Download from https://git-scm.com/download/win")
        print("Mac: brew install git")
        print("Linux: sudo apt-get install git")
        return False

    # Get repository details
    print("\n📝 Repository Setup")
    repo_name = input("Enter repository name [ai-answering-service]: ").strip() or "ai-answering-service"
    repo_description = input("Enter repository description [AI-powered phone answering service]: ").strip() or "AI-powered phone answering service"
    make_private = input("Make repository private? [y/N]: ").strip().lower() == 'y'

    # Initialize git if not already initialized
    if not os.path.exists(".git"):
        if not run_command("git init", "Initializing Git repository"):
            return False

    # Create .gitignore if it doesn't exist
    gitignore_path = Path(".gitignore")
    if not gitignore_path.exists():
        print("❌ .gitignore file not found. Please ensure the project files are in the current directory.")
        return False

    # Configure git user (if not already configured)
    print("\n🔧 Configuring Git user")
    git_name = input("Enter your Git name [Austin Kidwell]: ").strip() or "Austin Kidwell"
    git_email = input("Enter your Git email: ").strip()

    if git_email:
        run_command(f'git config user.name "{git_name}"', "Setting Git username")
        run_command(f'git config user.email "{git_email}"', "Setting Git email")

    # Add all files
    if not run_command("git add .", "Adding all files to Git"):
        return False

    # Create initial commit
    commit_message = "Initial commit: Complete AI Answering Service implementation"
    if not run_command(f'git commit -m "{commit_message}"', "Creating initial commit"):
        # Check if there are any changes to commit
        result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
        if not result.stdout.strip():
            print("✅ No changes to commit (repository might already be up to date)")
        else:
            print("❌ Failed to create commit")
            return False

    # Create GitHub repository using GitHub CLI (if available)
    if check_gh_cli_installed():
        print(f"\n🔄 Creating GitHub repository '{repo_name}'")
        visibility = "--private" if make_private else "--public"
        gh_command = f'gh repo create {repo_name} {visibility} --description "{repo_description}" --push'

        if run_command(gh_command, "Creating GitHub repository and pushing"):
            print(f"✅ Repository created successfully!")
            print(f"🌐 Repository URL: https://github.com/{git_email.split('@')[0] if git_email else 'your-username'}/{repo_name}")
            return True
        else:
            print("❌ Failed to create repository with GitHub CLI")
            return manual_github_setup(repo_name, repo_description, make_private)
    else:
        print("\n💡 GitHub CLI not found. You'll need to create the repository manually.")
        return manual_github_setup(repo_name, repo_description, make_private)

def manual_github_setup(repo_name, repo_description, make_private):
    """Provide manual instructions for GitHub setup."""

    print(f"\n📋 Manual GitHub Setup Instructions")
    print("=" * 40)
    print(f"1. Go to https://github.com/new")
    print(f"2. Repository name: {repo_name}")
    print(f"3. Description: {repo_description}")
    print(f"4. Visibility: {'Private' if make_private else 'Public'}")
    print(f"5. Don't initialize with README, .gitignore, or license (we already have these)")
    print(f"6. Click 'Create repository'")
    print(f"\n7. Copy the repository URL and run these commands:")
    print(f"   git branch -M main")

    repo_url = input(f"\n📝 Enter your GitHub repository URL (https://github.com/username/{repo_name}.git): ").strip()

    if repo_url:
        # Set the remote origin
        run_command(f"git remote add origin {repo_url}", "Adding remote origin")
        run_command("git branch -M main", "Setting main branch")
        run_command("git push -u origin main", "Pushing to GitHub")

        print(f"✅ Repository setup complete!")
        print(f"🌐 Repository URL: {repo_url.replace('.git', '')}")
        return True
    else:
        print("❌ Repository URL not provided. Please complete setup manually.")
        return False

def verify_project_structure():
    """Verify all required files are present."""
    required_files = [
        "backend/app.py",
        "backend/conversation_relay.js",
        "backend/requirements.txt",
        "backend/package.json",
        "frontend/src/App.jsx",
        "frontend/package.json",
        "render.yaml",
        "README.md",
        "DEPLOYMENT.md"
    ]

    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)

    if missing_files:
        print("❌ Missing required files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        print("\nPlease ensure you're running this script from the project root directory.")
        return False

    print("✅ All required project files found")
    return True

def main():
    """Main function to set up GitHub repository."""

    # Verify we're in the right directory
    if not verify_project_structure():
        sys.exit(1)

    # Set up GitHub repository
    if setup_github_repository():
        print("\n🎉 GitHub setup complete!")
        print("\n📋 Next Steps:")
        print("1. Run the Render deployment script: python deploy_to_render.py")
        print("2. Add your API keys to Render environment variables")
        print("3. Configure Twilio webhooks to point to your deployed backend")
        print("4. Test your AI answering service!")

        # Save repository info for deployment script
        with open(".github_repo_info", "w") as f:
            f.write("Repository setup completed\n")

    else:
        print("\n❌ GitHub setup failed. Please try again or set up manually.")
        sys.exit(1)

if __name__ == "__main__":
    main()