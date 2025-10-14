# 🚀 Deployment Guide - Intelligent Real Estate Agent

This guide covers deploying the Intelligent Real Estate Agent to various platforms using GitHub.

## 📋 Prerequisites

- GitHub account
- Python 3.12+ knowledge
- Basic understanding of web deployment

## 🗂️ File Organization

### Essential Files for Deployment
```
├── app.py                 # Main Flask application
├── intelligent_agent.py   # AI agent implementation  
├── property_finder.py     # Property Finder API integration
├── database.py           # Database utilities
├── ollam.py              # NLP utilities
├── test_prop.py          # Property search functions
├── templates/            # Frontend templates
│   ├── index.html
│   ├── map_page.html
│   └── property_detail.html
├── requirements.txt      # Python dependencies
├── Procfile             # Heroku deployment
├── railway.json         # Railway deployment
├── runtime.txt          # Python version
└── README.md            # Project documentation
```

### Files Excluded from Deployment
- `__pycache__/` - Python cache files
- `venv/` - Virtual environment
- `*.db` - Database files (created at runtime)
- `tests/` - Test files
- Screenshots and temporary files
- Old agent files not used in current system

## 🚀 Deployment Options

### 1. Railway (Recommended - Free Tier Available)

Railway is the easiest and most reliable option for this project.

#### Steps:
1. **Fork the Repository**
   - Go to the GitHub repository
   - Click "Fork" to create your own copy

2. **Connect to Railway**
   - Visit [railway.app](https://railway.app)
   - Sign up with GitHub
   - Click "New Project" → "Deploy from GitHub repo"

3. **Configure Deployment**
   - Select your forked repository
   - Railway will automatically detect the `railway.json` configuration
   - The deployment will start automatically

4. **Environment Variables** (Optional)
   - `FLASK_ENV=production`
   - `PORT=5000` (automatically set by Railway)

5. **Access Your App**
   - Railway provides a public URL
   - Your app will be live at `https://your-app-name.railway.app`

#### Railway Configuration (`railway.json`):
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "name": "intelligent-real-estate-agent",
  "environment": {
    "PYTHON_VERSION": "3.12.0",
    "FLASK_ENV": "production"
  },
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn app:app",
    "healthcheckPath": "/api/intelligent_search",
    "healthcheckTimeout": 30
  }
}
```

### 2. Render (Free Tier Available)

#### Steps:
1. **Fork the Repository** (same as Railway)

2. **Connect to Render**
   - Visit [render.com](https://render.com)
   - Sign up with GitHub
   - Click "New" → "Web Service"

3. **Configure Service**
   - Connect your GitHub repository
   - Use these settings:
     - **Name**: `intelligent-real-estate-agent`
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app`
     - **Instance Type**: Free

4. **Deploy**
   - Click "Create Web Service"
   - Render will build and deploy automatically

### 3. Heroku (Paid - No Free Tier)

#### Steps:
1. **Install Heroku CLI**
   ```bash
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login to Heroku**
   ```bash
   heroku login
   ```

3. **Create Heroku App**
   ```bash
   heroku create your-app-name
   ```

4. **Deploy**
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

5. **Open App**
   ```bash
   heroku open
   ```

## 🔧 Configuration Files

### `requirements.txt`
```
Flask==3.1.2
requests==2.32.5
click==8.3.0
gunicorn==21.2.0
aiohttp==3.9.1
```

### `Procfile` (for Heroku)
```
web: gunicorn app:app
```

### `runtime.txt`
```
python-3.12.0
```

## 🌐 Custom Domain (Optional)

### Railway
1. Go to your project settings
2. Click "Domains"
3. Add your custom domain
4. Update DNS records as instructed

### Render
1. Go to your service settings
2. Click "Custom Domains"
3. Add your domain
4. Follow DNS configuration instructions

## 📊 Monitoring and Logs

### Railway
- View logs in the Railway dashboard
- Monitor performance metrics
- Set up alerts for downtime

### Render
- Access logs in the Render dashboard
- Monitor build and deployment status
- Set up health checks

## 🔒 Security Considerations

1. **Environment Variables**
   - Never commit sensitive data to GitHub
   - Use platform-specific environment variable settings

2. **API Keys**
   - Property Finder API doesn't require keys
   - Ollama LLM is optional (fallback works without it)

3. **Database**
   - SQLite database is created at runtime
   - No sensitive data stored permanently

## 🚨 Troubleshooting

### Common Issues:

1. **Build Failures**
   - Check Python version compatibility
   - Verify all dependencies in `requirements.txt`
   - Review build logs for specific errors

2. **Runtime Errors**
   - Check application logs
   - Verify environment variables
   - Test locally first

3. **Database Issues**
   - Database is created automatically
   - No manual setup required

### Debug Commands:

```bash
# Test locally
python app.py

# Check dependencies
pip list

# Test API endpoints
curl -X POST http://localhost:5000/api/intelligent_search \
  -H "Content-Type: application/json" \
  -d '{"query": "test query"}'
```

## 📈 Performance Optimization

1. **Caching**
   - SQLite caching is built-in
   - Reduces API calls to Property Finder

2. **Async Processing**
   - Uses aiohttp for non-blocking operations
   - Improves response times

3. **Fallback Systems**
   - Graceful degradation when services are unavailable
   - Always provides some response

## 🔄 Updates and Maintenance

### Updating the Application:
1. Make changes to your forked repository
2. Push changes to GitHub
3. Platform will automatically redeploy

### Monitoring:
- Check logs regularly
- Monitor response times
- Set up uptime monitoring

## 📞 Support

If you encounter issues:
1. Check the logs in your deployment platform
2. Test locally first
3. Create an issue in the GitHub repository
4. Review this deployment guide

---

**Happy Deploying! 🚀**