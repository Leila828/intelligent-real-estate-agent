# Real Estate App Deployment Guide

## Quick Deploy to Railway (Recommended)

### Option 1: One-Click Deploy
1. Go to [Railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "Deploy from GitHub repo"
4. Connect your GitHub account
5. Select this repository
6. Railway will automatically detect it's a Python app and deploy it

### Option 2: Manual Deploy
1. Install Railway CLI: `npm install -g @railway/cli`
2. Run: `railway login`
3. Run: `railway init`
4. Run: `railway up`

## Alternative: Deploy to Render
1. Go to [Render.com](https://render.com)
2. Sign up with GitHub
3. Create new "Web Service"
4. Connect your GitHub repo
5. Use these settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py`

## Alternative: Deploy to Heroku
1. Install Heroku CLI
2. Run: `heroku create your-app-name`
3. Run: `git push heroku main`

## Testing the Deployed App
Once deployed, your manager can access the app at the provided URL and test:
- Natural language property search
- Property listings with details
- Interactive maps
- Property images

## Features Available
- Search for properties using natural language
- Filter by location, property type, price range
- View property details with images
- Interactive maps for property locations
- Real-time property data from Property Finder
