# Team Onboarding Guide - Real Estate AI Chatbot

## Welcome to the Team! 🚀

This comprehensive onboarding guide will help new team members quickly understand and contribute to the Real Estate AI Chatbot project.

---

## 📋 Quick Start Checklist

### Pre-requisites Setup
- [ ] **Python 3.8+** installed and configured
- [ ] **Git** installed and configured
- [ ] **Code Editor** (VS Code recommended with Python extension)
- [ ] **Postman/Insomnia** for API testing
- [ ] **Node.js** (for Railway CLI if needed)

### Development Environment Setup
- [ ] Clone the repository
- [ ] Set up virtual environment
- [ ] Install dependencies
- [ ] Initialize database
- [ ] Run the application
- [ ] Test all endpoints
- [ ] Review codebase structure

---

## 🏗️ Project Architecture Overview

### System Components
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Flask App     │    │   Database      │
│   (HTML/JS)     │◄──►│   (Python)      │◄──►│   (SQLite)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  External APIs  │
                       │  (Property      │
                       │   Finder)       │
                       └─────────────────┘
```

### Key Technologies
- **Backend**: Python Flask
- **Database**: SQLite with caching
- **AI/ML**: Ollama (LLaMA 3)
- **Frontend**: HTML5, CSS3, JavaScript
- **Maps**: Leaflet.js
- **Deployment**: Railway/Render/Heroku

---

## 🚀 Development Setup

### 1. Repository Setup
```bash
# Clone the repository
git clone <repository-url>
cd real-estate-app-chatbot

# Check Python version (should be 3.8+)
python --version

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Dependencies Installation
```bash
# Install required packages
pip install -r requirements.txt

# Verify installation
pip list
```

### 3. Database Initialization
```bash
# Initialize the database
python -c "from app import app; app.app_context().push(); import database; database.init_db()"

# Verify database creation
ls -la *.db
```

### 4. Application Startup
```bash
# Run the application
python app.py

# Expected output:
# Database initialized for search caching.
# * Running on http://127.0.0.1:5000
# * Debug mode: on
```

### 5. Testing the Setup
```bash
# Test the API endpoint
curl -X POST -H "Content-Type: application/json" \
  -d '{"query": "villas for sale in Dubai"}' \
  http://localhost:5000/api/nl_search

# Expected: JSON response with property listings
```

---

## 📁 Codebase Structure

### Directory Layout
```
real-estate-app-chatbot/
├── app.py                 # Main Flask application
├── database.py            # Database operations and caching
├── property_finder.py     # Property Finder API integration
├── ollam.py              # Natural language processing
├── test_prop.py          # Alternative implementation
├── requirements.txt      # Python dependencies
├── schema.sql           # Database schema
├── Procfile             # Deployment configuration
├── railway.json         # Railway deployment config
├── templates/           # HTML templates
│   ├── index.html       # Main application interface
│   ├── map_page.html    # Map view template
│   └── property_detail.html
├── tests/               # Test files
└── docs/                # Documentation
```

### Key Files to Understand

#### 1. **`app.py`** - Main Application
**Purpose**: Flask application server and API endpoints
**Key Functions**:
- `nl_search()`: Natural language search endpoint
- `search_properties()`: Property search logic
- `estimate_property_price()`: Price estimation
- Route handlers for all endpoints

**Learning Focus**:
- Flask route decorators
- Request/response handling
- Error handling patterns
- Integration with other modules

#### 2. **`ollam.py`** - Natural Language Processing
**Purpose**: Convert natural language to structured queries
**Key Functions**:
- `parse_natural_query()`: Main parsing function
- `llama_fallback()`: AI-powered parsing
- `_split_location_and_keywords()`: Location extraction

**Learning Focus**:
- Regex patterns for text parsing
- AI integration with Ollama
- Query normalization
- Error handling and fallbacks

#### 3. **`property_finder.py`** - External API Integration
**Purpose**: Real-time property data from Property Finder
**Key Functions**:
- `search_location()`: Location name resolution
- `property_finder_search()`: Main search orchestrator
- `_map_pf_data_to_db_schema()`: Data transformation

**Learning Focus**:
- External API integration
- Data mapping and transformation
- Error handling for API failures
- Response caching strategies

#### 4. **`database.py`** - Data Persistence
**Purpose**: Database operations and caching
**Key Functions**:
- `init_db()`: Database initialization
- `find_cached_query()`: Cache lookup
- `save_query_and_properties()`: Cache storage

**Learning Focus**:
- SQLite database operations
- Caching strategies
- Data modeling
- Performance optimization

---

## 🧪 Testing and Quality Assurance

### Manual Testing Checklist

#### API Endpoints Testing
- [ ] **Natural Language Search**
  ```bash
  curl -X POST -H "Content-Type: application/json" \
    -d '{"query": "villas for sale in Dubai Marina"}' \
    http://localhost:5000/api/nl_search
  ```

- [ ] **Structured Search**
  ```bash
  curl "http://localhost:5000/api/search?purpose=for-sale&rooms=3"
  ```

- [ ] **Property Details**
  ```bash
  curl "http://localhost:5000/api/properties/15316766"
  ```

- [ ] **Image Proxy**
  ```bash
  curl "http://localhost:5000/get_image?url=..."
  ```

#### Frontend Testing
- [ ] **Homepage**: Load `http://localhost:5000`
- [ ] **Search Functionality**: Test natural language queries
- [ ] **Property Cards**: Click and view property details
- [ ] **Map Integration**: Test location mapping
- [ ] **Image Gallery**: Test image viewing

### Automated Testing
```python
# Example test structure
import unittest
from app import app

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
    
    def test_nl_search(self):
        response = self.app.post('/api/nl_search', 
                               json={'query': 'test query'})
        self.assertEqual(response.status_code, 200)
    
    def test_search_endpoint(self):
        response = self.app.get('/api/search?purpose=for-sale')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
```

---

## 🔧 Development Workflow

### Daily Development Process

#### 1. **Morning Setup**
```bash
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Pull latest changes
git pull origin main

# Run application
python app.py
```

#### 2. **Feature Development**
```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes
# Test changes
# Commit changes
git add .
git commit -m "Add new feature"

# Push to remote
git push origin feature/new-feature
```

#### 3. **Code Review Process**
- Create pull request
- Request review from team members
- Address feedback
- Merge to main branch

### Debugging Tips

#### Common Issues and Solutions

**1. Database Connection Issues**
```python
# Check database file exists
import os
print(os.path.exists('bayut_properties.db'))

# Reinitialize database
from app import app
with app.app_context():
    import database
    database.init_db()
```

**2. API Integration Issues**
```python
# Test Property Finder API directly
import property_finder
result = property_finder.search_location('Dubai')
print(result)
```

**3. Cache Issues**
```python
# Clear cache manually
import sqlite3
conn = sqlite3.connect('bayut_properties.db')
cursor = conn.cursor()
cursor.execute("DELETE FROM search_queries")
cursor.execute("DELETE FROM cached_properties")
conn.commit()
conn.close()
```

---

## 📊 Performance Monitoring

### Key Metrics to Monitor

#### 1. **Response Times**
- API response time: < 2 seconds
- Cache hit rate: > 70%
- Database query time: < 100ms

#### 2. **Error Rates**
- 4xx errors: < 5%
- 5xx errors: < 1%
- Timeout errors: < 2%

#### 3. **Resource Usage**
- Memory usage: < 512MB
- CPU usage: < 80%
- Disk I/O: Monitor database size

### Monitoring Tools
```python
# Add to app.py for monitoring
import time
import logging

@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request
def after_request(response):
    duration = time.time() - g.start_time
    logging.info(f"Request took {duration:.2f} seconds")
    return response
```

---

## 🚀 Deployment Process

### Local Development
```bash
# Run in development mode
python app.py
# Access at http://localhost:5000
```

### Production Deployment

#### Railway Deployment
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

#### Manual Deployment
1. Push code to GitHub
2. Connect to Railway/Render/Heroku
3. Configure environment variables
4. Deploy application

---

## 🎯 Learning Objectives

### Week 1: Foundation
- [ ] Understand project architecture
- [ ] Set up development environment
- [ ] Review codebase structure
- [ ] Test all functionality
- [ ] Understand data flow

### Week 2: Deep Dive
- [ ] Study natural language processing
- [ ] Understand caching mechanisms
- [ ] Review API integrations
- [ ] Practice debugging techniques
- [ ] Contribute to documentation

### Week 3: Contribution
- [ ] Implement small features
- [ ] Fix minor bugs
- [ ] Improve code quality
- [ ] Add unit tests
- [ ] Optimize performance

### Week 4: Advanced Topics
- [ ] Understand deployment process
- [ ] Learn monitoring techniques
- [ ] Study scalability patterns
- [ ] Contribute to architecture decisions
- [ ] Mentor new team members

---

## 📚 Learning Resources

### Technical Documentation
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [Ollama Documentation](https://ollama.ai/docs)
- [Property Finder API](https://www.propertyfinder.ae/)

### Code Quality
- [PEP 8 Style Guide](https://pep8.org/)
- [Python Best Practices](https://docs.python.org/3/tutorial/)
- [Flask Best Practices](https://flask.palletsprojects.com/en/2.0.x/patterns/)

### Tools and Utilities
- [Postman for API Testing](https://www.postman.com/)
- [VS Code Python Extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- [GitHub for Version Control](https://github.com/)

---

## 🤝 Team Collaboration

### Communication Channels
- **Daily Standups**: Progress updates and blockers
- **Code Reviews**: Peer review for all changes
- **Documentation**: Keep docs updated with changes
- **Knowledge Sharing**: Regular tech talks

### Code Review Guidelines
1. **Check for bugs** and potential issues
2. **Verify functionality** works as expected
3. **Ensure code quality** follows standards
4. **Test edge cases** and error scenarios
5. **Update documentation** if needed

### Contribution Process
1. **Create feature branch** from main
2. **Implement changes** with tests
3. **Create pull request** with description
4. **Address feedback** from reviewers
5. **Merge to main** after approval

---

## 🎉 Success Metrics

### Individual Goals
- [ ] Successfully set up development environment
- [ ] Understand and explain system architecture
- [ ] Contribute meaningful code changes
- [ ] Help onboard other team members
- [ ] Improve system performance or features

### Team Goals
- [ ] Maintain high code quality
- [ ] Achieve 99% uptime
- [ ] Keep response times under 2 seconds
- [ ] Maintain 70%+ cache hit rate
- [ ] Deliver new features on schedule

---

## 🆘 Getting Help

### Internal Resources
- **Team Lead**: For architectural decisions
- **Senior Developers**: For technical guidance
- **Documentation**: This guide and inline comments
- **Code Reviews**: Learn from peer feedback

### External Resources
- **Stack Overflow**: For specific technical issues
- **Official Documentation**: Flask, Python, SQLite
- **Community Forums**: Python and Flask communities
- **Online Courses**: Python and web development

### Emergency Contacts
- **Technical Issues**: Team lead or senior developer
- **Deployment Issues**: DevOps team or deployment guide
- **API Issues**: External service documentation
- **Database Issues**: Database administrator

---

## 🎯 Next Steps

### Immediate Actions (Today)
1. Complete development environment setup
2. Run the application successfully
3. Test all API endpoints
4. Review this documentation thoroughly

### Short-term Goals (This Week)
1. Understand the codebase structure
2. Make your first code contribution
3. Participate in code reviews
4. Ask questions and seek clarification

### Long-term Goals (This Month)
1. Become proficient with the system
2. Contribute to major features
3. Help improve documentation
4. Mentor other new team members

---

## 🎊 Welcome to the Team!

You're now ready to contribute to the Real Estate AI Chatbot project. Remember:

- **Ask questions** - We're here to help!
- **Start small** - Begin with simple tasks
- **Learn continuously** - Technology evolves rapidly
- **Share knowledge** - Help others grow
- **Have fun** - Enjoy the learning process!

**Happy coding! 🚀**
