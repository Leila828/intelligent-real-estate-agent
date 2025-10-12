# Real Estate AI Chatbot - Deployment Guide

## Overview
This guide provides comprehensive deployment instructions for the Real Estate AI Chatbot application across multiple platforms, including local development, staging, and production environments.

---

## 🚀 Quick Deployment Options

### Option 1: Railway (Recommended)
**Best for**: Quick deployment, automatic scaling, easy management
**Cost**: Free tier available, paid plans for production

### Option 2: Render
**Best for**: Static sites with backend services
**Cost**: Free tier available, reasonable pricing

### Option 3: Heroku
**Best for**: Traditional web applications
**Cost**: Paid plans only (no free tier)

### Option 4: Self-hosted
**Best for**: Full control, custom infrastructure
**Cost**: Server costs only

---

## 📋 Pre-deployment Checklist

### Code Preparation
- [ ] All dependencies listed in `requirements.txt`
- [ ] Environment variables documented
- [ ] Database schema ready
- [ ] Static files organized
- [ ] Error handling implemented
- [ ] Logging configured
- [ ] Security measures in place

### Testing Checklist
- [ ] Local development working
- [ ] All API endpoints tested
- [ ] Database operations verified
- [ ] External API integrations working
- [ ] Frontend functionality complete
- [ ] Performance acceptable
- [ ] Error scenarios handled

---

## 🛠️ Local Development Setup

### Prerequisites
```bash
# Required software
Python 3.8+
Git
Code editor (VS Code recommended)
```

### Setup Steps
```bash
# 1. Clone repository
git clone <repository-url>
cd real-estate-app-chatbot

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Initialize database
python -c "from app import app; app.app_context().push(); import database; database.init_db()"

# 6. Run application
python app.py
```

### Environment Variables (Local)
```bash
# .env file (create in project root)
FLASK_ENV=development
DATABASE_URL=sqlite:///bayut_properties.db
DEBUG=True
PORT=5000
```

---

## 🌐 Railway Deployment

### Prerequisites
- GitHub account
- Railway account (free at railway.app)

### Automatic Deployment
1. **Connect GitHub Repository**
   - Go to [Railway.app](https://railway.app)
   - Sign up with GitHub
   - Click "Deploy from GitHub repo"
   - Select your repository

2. **Configure Deployment**
   - Railway auto-detects Python applications
   - Uses `requirements.txt` for dependencies
   - Runs `python app.py` as start command

3. **Environment Variables**
   ```bash
   FLASK_ENV=production
   PORT=5000
   DATABASE_URL=sqlite:///bayut_properties.db
   ```

4. **Deploy**
   - Railway automatically deploys on git push
   - Get your app URL from Railway dashboard

### Manual Railway Deployment
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Deploy
railway up

# Get deployment URL
railway domain
```

### Railway Configuration Files
```json
// railway.json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python app.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

---

## 🎨 Render Deployment

### Prerequisites
- GitHub account
- Render account (free at render.com)

### Deployment Steps
1. **Create Web Service**
   - Go to [Render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect GitHub repository

2. **Configure Service**
   ```
   Name: real-estate-chatbot
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python app.py
   ```

3. **Environment Variables**
   ```bash
   FLASK_ENV=production
   PORT=10000
   DATABASE_URL=sqlite:///bayut_properties.db
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Render builds and deploys automatically
   - Get your app URL from Render dashboard

### Render Configuration
```yaml
# render.yaml (optional)
services:
  - type: web
    name: real-estate-chatbot
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python app.py
    envVars:
      - key: FLASK_ENV
        value: production
```

---

## 🚀 Heroku Deployment

### Prerequisites
- GitHub account
- Heroku account
- Heroku CLI installed

### Deployment Steps
```bash
# 1. Install Heroku CLI
# Download from https://devcenter.heroku.com/articles/heroku-cli

# 2. Login to Heroku
heroku login

# 3. Create Heroku app
heroku create your-app-name

# 4. Set environment variables
heroku config:set FLASK_ENV=production
heroku config:set DATABASE_URL=sqlite:///bayut_properties.db

# 5. Deploy
git push heroku main

# 6. Open app
heroku open
```

### Heroku Configuration Files
```python
# Procfile
web: python app.py
```

```txt
# runtime.txt
python-3.12.6
```

---

## 🏗️ Self-hosted Deployment

### Server Requirements
- **OS**: Ubuntu 20.04+ or CentOS 8+
- **RAM**: 2GB minimum, 4GB recommended
- **CPU**: 2 cores minimum
- **Storage**: 20GB minimum
- **Network**: Public IP with ports 80/443 open

### Installation Steps
```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install Python and dependencies
sudo apt install python3 python3-pip python3-venv nginx -y

# 3. Create application user
sudo useradd -m -s /bin/bash realestate
sudo su - realestate

# 4. Clone repository
git clone <repository-url>
cd real-estate-app-chatbot

# 5. Set up virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 6. Initialize database
python -c "from app import app; app.app_context().push(); import database; database.init_db()"

# 7. Test application
python app.py
```

### Nginx Configuration
```nginx
# /etc/nginx/sites-available/realestate
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Systemd Service
```ini
# /etc/systemd/system/realestate.service
[Unit]
Description=Real Estate AI Chatbot
After=network.target

[Service]
Type=simple
User=realestate
WorkingDirectory=/home/realestate/real-estate-app-chatbot
Environment=PATH=/home/realestate/real-estate-app-chatbot/venv/bin
ExecStart=/home/realestate/real-estate-app-chatbot/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### SSL Certificate (Let's Encrypt)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

---

## 🔧 Environment Configuration

### Production Environment Variables
```bash
# Core application settings
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-secret-key-here

# Database configuration
DATABASE_URL=sqlite:///bayut_properties.db

# External API settings
PROPERTY_FINDER_API_URL=https://www.propertyfinder.ae
OLLAMA_API_URL=http://localhost:11434/api/generate

# Performance settings
CACHE_TTL=1800  # 30 minutes
MAX_CACHE_SIZE=1000
REQUEST_TIMEOUT=30

# Security settings
CORS_ORIGINS=https://your-domain.com
RATE_LIMIT=100  # requests per minute
```

### Staging Environment Variables
```bash
# Staging-specific settings
FLASK_ENV=staging
DEBUG=True
DATABASE_URL=sqlite:///bayut_properties_staging.db
LOG_LEVEL=DEBUG
```

---

## 📊 Monitoring and Logging

### Application Monitoring
```python
# Add to app.py
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

# Performance monitoring
@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request
def after_request(response):
    duration = time.time() - g.start_time
    logging.info(f"Request completed in {duration:.2f}s")
    return response
```

### Health Check Endpoint
```python
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })
```

### Database Monitoring
```python
# Add database monitoring
def check_database_health():
    try:
        db = database.get_db()
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM search_queries")
        count = cursor.fetchone()[0]
        return {'database': 'healthy', 'queries_cached': count}
    except Exception as e:
        return {'database': 'unhealthy', 'error': str(e)}
```

---

## 🔒 Security Considerations

### Production Security Checklist
- [ ] **Environment Variables**: Never commit secrets to git
- [ ] **HTTPS**: Always use SSL/TLS in production
- [ ] **Input Validation**: Sanitize all user inputs
- [ ] **SQL Injection**: Use parameterized queries
- [ ] **CORS**: Configure appropriate origins
- [ ] **Rate Limiting**: Implement request throttling
- [ ] **Error Handling**: Don't expose sensitive information
- [ ] **Dependencies**: Keep packages updated
- [ ] **Logging**: Monitor for suspicious activity
- [ ] **Backups**: Regular database backups

### Security Headers
```python
# Add to app.py
from flask_talisman import Talisman

# Configure security headers
Talisman(app, force_https=True)
```

### Rate Limiting
```python
# Add rate limiting
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per minute"]
)

@app.route('/api/nl_search', methods=['POST'])
@limiter.limit("10 per minute")
def nl_search():
    # Your existing code
```

---

## 🚨 Troubleshooting

### Common Deployment Issues

#### 1. **Application Won't Start**
```bash
# Check logs
heroku logs --tail
railway logs
render logs

# Common solutions
pip install -r requirements.txt
python app.py
```

#### 2. **Database Issues**
```bash
# Reinitialize database
python -c "from app import app; app.app_context().push(); import database; database.init_db()"

# Check database file
ls -la *.db
```

#### 3. **External API Failures**
```python
# Test API connectivity
import requests
response = requests.get('https://www.propertyfinder.ae')
print(response.status_code)
```

#### 4. **Memory Issues**
```bash
# Monitor memory usage
ps aux | grep python
free -h

# Optimize for production
export PYTHONUNBUFFERED=1
```

### Performance Optimization

#### 1. **Database Optimization**
```python
# Add database indexes
CREATE INDEX idx_query_string ON search_queries(query_string);
CREATE INDEX idx_expires_at ON search_queries(expires_at);
CREATE INDEX idx_property_query ON cached_properties(query_id);
```

#### 2. **Caching Optimization**
```python
# Implement Redis caching (optional)
import redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_cached_data(key):
    return redis_client.get(key)

def set_cached_data(key, value, ttl=1800):
    redis_client.setex(key, ttl, value)
```

#### 3. **Static File Optimization**
```python
# Serve static files efficiently
from flask import send_from_directory

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)
```

---

## 📈 Scaling Considerations

### Horizontal Scaling
```yaml
# docker-compose.yml for scaling
version: '3.8'
services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    deploy:
      replicas: 3
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

### Load Balancer Configuration
```nginx
# nginx.conf
upstream app_servers {
    server app1:5000;
    server app2:5000;
    server app3:5000;
}

server {
    listen 80;
    location / {
        proxy_pass http://app_servers;
    }
}
```

### Database Scaling
```python
# Connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    'sqlite:///bayut_properties.db',
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.8
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          python -m pytest tests/
      
      - name: Deploy to Railway
        run: |
          railway up
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

---

## 📋 Deployment Checklist

### Pre-deployment
- [ ] Code reviewed and tested
- [ ] Dependencies updated
- [ ] Environment variables configured
- [ ] Database schema ready
- [ ] Security measures implemented
- [ ] Monitoring configured
- [ ] Backup strategy in place

### Deployment
- [ ] Deploy to staging environment
- [ ] Run integration tests
- [ ] Performance testing completed
- [ ] Security scan passed
- [ ] Deploy to production
- [ ] Verify all endpoints working
- [ ] Monitor for errors

### Post-deployment
- [ ] Health checks passing
- [ ] Monitoring alerts configured
- [ ] Documentation updated
- [ ] Team notified
- [ ] Backup verification
- [ ] Performance monitoring active

---

## 🎯 Best Practices

### Code Quality
- Write comprehensive tests
- Use type hints
- Follow PEP 8 style guide
- Document all functions
- Handle errors gracefully

### Security
- Never commit secrets
- Use environment variables
- Implement proper authentication
- Regular security updates
- Monitor for vulnerabilities

### Performance
- Implement caching strategies
- Optimize database queries
- Use connection pooling
- Monitor resource usage
- Plan for scaling

### Monitoring
- Set up health checks
- Monitor error rates
- Track performance metrics
- Log important events
- Set up alerts

---

## 📞 Support and Maintenance

### Regular Maintenance Tasks
- **Weekly**: Review logs and performance metrics
- **Monthly**: Update dependencies and security patches
- **Quarterly**: Review and optimize database performance
- **Annually**: Security audit and penetration testing

### Emergency Procedures
1. **Service Down**: Check logs, restart service, contact team
2. **Database Issues**: Restore from backup, investigate cause
3. **Security Breach**: Isolate service, investigate, patch vulnerabilities
4. **Performance Issues**: Scale resources, optimize code

### Contact Information
- **Technical Lead**: [Contact details]
- **DevOps Team**: [Contact details]
- **Security Team**: [Contact details]
- **Emergency**: [24/7 contact]

---

## 🎉 Conclusion

This deployment guide provides comprehensive instructions for deploying the Real Estate AI Chatbot across multiple platforms. Choose the deployment method that best fits your needs:

- **Quick Start**: Railway or Render
- **Enterprise**: Self-hosted with full control
- **Traditional**: Heroku with established workflows

Remember to:
- Test thoroughly in staging
- Monitor production closely
- Keep security updated
- Plan for scaling
- Document everything

**Happy deploying! 🚀**
