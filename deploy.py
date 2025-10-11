#!/usr/bin/env python3
"""
Simple deployment script for the Real Estate App
This script helps deploy the app to Railway platform
"""

import subprocess
import sys
import os

def check_railway_cli():
    """Check if Railway CLI is installed"""
    try:
        result = subprocess.run(['railway', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Railway CLI is installed")
            return True
    except FileNotFoundError:
        print("❌ Railway CLI not found")
        return False

def install_railway_cli():
    """Install Railway CLI"""
    print("Installing Railway CLI...")
    try:
        subprocess.run(['npm', 'install', '-g', '@railway/cli'], check=True)
        print("✅ Railway CLI installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install Railway CLI")
        print("Please install it manually: npm install -g @railway/cli")
        return False

def deploy_to_railway():
    """Deploy the app to Railway"""
    print("Deploying to Railway...")
    try:
        # Login to Railway
        subprocess.run(['railway', 'login'], check=True)
        print("✅ Logged in to Railway")
        
        # Initialize project
        subprocess.run(['railway', 'init'], check=True)
        print("✅ Railway project initialized")
        
        # Deploy
        subprocess.run(['railway', 'up'], check=True)
        print("✅ App deployed successfully!")
        
        # Get the URL
        result = subprocess.run(['railway', 'domain'], capture_output=True, text=True)
        if result.returncode == 0:
            url = result.stdout.strip()
            print(f"🌐 Your app is available at: {url}")
            return url
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed: {e}")
        return None

def main():
    print("🚀 Real Estate App Deployment Script")
    print("=" * 40)
    
    # Check if Railway CLI is installed
    if not check_railway_cli():
        print("Installing Railway CLI...")
        if not install_railway_cli():
            print("\n📋 Manual Deployment Instructions:")
            print("1. Go to https://railway.app")
            print("2. Sign up with GitHub")
            print("3. Click 'Deploy from GitHub repo'")
            print("4. Select this repository")
            print("5. Railway will automatically deploy your app")
            return
    
    # Deploy to Railway
    url = deploy_to_railway()
    if url:
        print(f"\n🎉 Deployment successful!")
        print(f"Share this link with your manager: {url}")
        print("\n📱 Features your manager can test:")
        print("- Search for properties using natural language")
        print("- View property details and images")
        print("- Interactive maps")
        print("- Real-time property data")
    else:
        print("\n❌ Deployment failed. Please try manual deployment.")

if __name__ == "__main__":
    main()
