#!/usr/bin/env python3
"""
GitHub Deployment Setup Script
This script helps you prepare and deploy the Intelligent Real Estate Agent to GitHub
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"[INFO] {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"[SUCCESS] {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {description} failed: {e.stderr}")
        return None

def check_git_status():
    """Check if we're in a git repository"""
    if not os.path.exists('.git'):
        print("[ERROR] Not in a git repository. Please run 'git init' first.")
        return False
    return True

def setup_git_repo():
    """Set up git repository for deployment"""
    print("[INFO] Setting up Git repository for deployment...")
    
    # Check if git is initialized
    if not check_git_status():
        run_command("git init", "Initializing git repository")
    
    # Add all files
    run_command("git add .", "Adding files to git")
    
    # Check if there are changes to commit
    result = run_command("git status --porcelain", "Checking git status")
    if not result or not result.strip():
        print("[INFO] No changes to commit")
        return True
    
    # Commit changes
    run_command('git commit -m "Initial commit: Intelligent Real Estate Agent"', "Committing changes")
    
    return True

def create_github_repo():
    """Guide user to create GitHub repository"""
    print("\n[INFO] GitHub Repository Setup:")
    print("1. Go to https://github.com/new")
    print("2. Create a new repository with these settings:")
    print("   - Repository name: intelligent-real-estate-agent")
    print("   - Description: AI-powered real estate chatbot for UAE market")
    print("   - Visibility: Public (for free deployment)")
    print("   - Don't initialize with README (we already have one)")
    print("3. Copy the repository URL")
    print("4. Run the following commands:")
    print("   git remote add origin <your-repo-url>")
    print("   git branch -M main")
    print("   git push -u origin main")

def show_deployment_options():
    """Show deployment options"""
    print("\n[INFO] Deployment Options:")
    print("\n1. Railway (Recommended - Free):")
    print("   - Go to https://railway.app")
    print("   - Sign up with GitHub")
    print("   - Click 'New Project' → 'Deploy from GitHub repo'")
    print("   - Select your repository")
    print("   - Railway will auto-deploy using railway.json")
    
    print("\n2. Render (Free tier available):")
    print("   - Go to https://render.com")
    print("   - Sign up with GitHub")
    print("   - Create new Web Service")
    print("   - Connect your repository")
    print("   - Build Command: pip install -r requirements.txt")
    print("   - Start Command: gunicorn app:app")
    
    print("\n3. Heroku (Paid):")
    print("   - Install Heroku CLI")
    print("   - Run: heroku create your-app-name")
    print("   - Run: git push heroku main")

def verify_files():
    """Verify all required files are present"""
    print("[INFO] Verifying deployment files...")
    
    required_files = [
        'app.py',
        'intelligent_agent.py',
        'property_finder.py',
        'database.py',
        'ollam.py',
        'test_prop.py',
        'requirements.txt',
        'Procfile',
        'railway.json',
        'runtime.txt',
        'README.md',
        '.gitignore'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
        else:
            print(f"[SUCCESS] {file}")
    
    if missing_files:
        print(f"[ERROR] Missing files: {', '.join(missing_files)}")
        return False
    
    print("[SUCCESS] All required files present")
    return True

def main():
    """Main deployment setup function"""
    print("Intelligent Real Estate Agent - GitHub Deployment Setup")
    print("=" * 60)
    
    # Verify files
    if not verify_files():
        print("[ERROR] Please ensure all required files are present before deployment")
        return
    
    # Setup git repository
    if not setup_git_repo():
        print("[ERROR] Git setup failed")
        return
    
    # Guide user through GitHub setup
    create_github_repo()
    
    # Show deployment options
    show_deployment_options()
    
    print("\n[SUCCESS] Setup complete! Follow the instructions above to deploy your app.")
    print("\n[INFO] For detailed instructions, see DEPLOYMENT_GUIDE.md")

if __name__ == "__main__":
    main()
