# 🏠 Real Estate AI Chatbot

> An intelligent real estate search platform powered by natural language processing and real-time property data aggregation.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1.2-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Deploy](https://img.shields.io/badge/Deploy-Railway-000000.svg)](https://railway.app)

## ✨ Features

- 🤖 **Natural Language Processing**: Search properties using conversational queries
- 🏘️ **Real-time Property Data**: Live listings from Property Finder API
- 🧠 **AI-Powered Intelligence**: LLaMA 3 integration for smart query understanding
- ⚡ **Intelligent Caching**: 30-minute cache system for optimal performance
- 🗺️ **Interactive Maps**: Location-based property visualization
- 💰 **Price Estimation**: AI-powered property valuation
- 📱 **Responsive Design**: Works on desktop and mobile devices
- 🔍 **Advanced Search**: Multiple filters and search options

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Git
- Code editor (VS Code recommended)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/real-estate-app-chatbot.git
cd real-estate-app-chatbot

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from app import app; app.app_context().push(); import database; database.init_db()"

# Run the application
python app.py
```

Visit `http://localhost:5000` to see the application in action!

## 🎯 Usage Examples

### Natural Language Queries
```
"Show me villas for sale in Dubai Marina"
"Find apartments under 2 million in Downtown Dubai"
"What's the average price of 3-bedroom villas in Damac Hills?"
"All current villa for sale in Damac hills"
```

### API Endpoints

#### Search Properties
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"query": "villas for sale in Dubai"}' \
  http://localhost:5000/api/nl_search
```

#### Get Property Details
```bash
curl http://localhost:5000/api/properties/15316766
```

## 🏗️ Architecture

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
- **Database**: SQLite with intelligent caching
- **AI/ML**: Ollama (LLaMA 3) for natural language processing
- **Frontend**: HTML5, CSS3, JavaScript, Leaflet Maps
- **External APIs**: Property Finder API
- **Deployment**: Railway/Render/Heroku ready

## 📁 Project Structure

```
real-estate-app-chatbot/
├── app.py                 # Main Flask application
├── database.py            # Database operations and caching
├── property_finder.py     # Property Finder API integration
├── ollam.py              # Natural language processing
├── requirements.txt      # Python dependencies
├── schema.sql           # Database schema
├── templates/           # HTML templates
│   ├── index.html       # Main application interface
│   ├── map_page.html    # Map view template
│   └── property_detail.html
├── tests/               # Test files
└── docs/                # Documentation
```

## 🔧 Configuration

### Environment Variables
```bash
# Development
FLASK_ENV=development
DEBUG=True
DATABASE_URL=sqlite:///bayut_properties.db

# Production
FLASK_ENV=production
DEBUG=False
DATABASE_URL=sqlite:///bayut_properties.db
```

### Database Schema
The application uses SQLite with two main tables:
- `search_queries`: Stores query metadata and expiration
- `cached_properties`: Stores property data with 30-minute TTL

## 🚀 Deployment

### Railway (Recommended)
1. Go to [Railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "Deploy from GitHub repo"
4. Select this repository
5. Railway automatically deploys your app

### Render
1. Go to [Render.com](https://render.com)
2. Create new "Web Service"
3. Connect your GitHub repo
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `python app.py`

### Heroku
```bash
# Install Heroku CLI
heroku create your-app-name
git push heroku main
```

## 📊 Performance

### Caching Strategy
- **TTL**: 30 minutes for all cached queries
- **Cache Key**: Based on query parameters
- **Storage**: SQLite database
- **Hit Rate**: Target 70%+ cache efficiency

### Performance Metrics
- **Response Time**: < 2 seconds for cached queries
- **API Latency**: < 5 seconds for fresh data
- **Concurrent Users**: Support 100+ simultaneous users

## 🧪 Testing

### Manual Testing
```bash
# Test natural language search
curl -X POST -H "Content-Type: application/json" \
  -d '{"query": "villas for sale in Dubai Marina"}' \
  http://localhost:5000/api/nl_search

# Test structured search
curl "http://localhost:5000/api/search?purpose=for-sale&rooms=3"
```

### Automated Testing
```python
# Run tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=app tests/
```

## 📚 Documentation

- **[Project Documentation](PROJECT_DOCUMENTATION.md)**: Comprehensive technical documentation
- **[API Documentation](API_DOCUMENTATION.md)**: Complete API reference
- **[Architecture Diagrams](ARCHITECTURE_DIAGRAMS.md)**: System architecture and workflows
- **[Team Onboarding](TEAM_ONBOARDING.md)**: Guide for new team members
- **[Deployment Guide](DEPLOYMENT_GUIDE.md)**: Production deployment instructions

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Code Style
- Follow PEP 8 Python style guide
- Use type hints where appropriate
- Write docstrings for all functions
- Implement proper error handling

## 🐛 Troubleshooting

### Common Issues

#### Application Won't Start
```bash
# Check Python version
python --version

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from app import app; app.app_context().push(); import database; database.init_db()"
```

#### Database Issues
```bash
# Reinitialize database
rm bayut_properties.db
python -c "from app import app; app.app_context().push(); import database; database.init_db()"
```

#### API Integration Issues
```python
# Test Property Finder API
import property_finder
result = property_finder.search_location('Dubai')
print(result)
```

## 📈 Roadmap

### Version 1.1
- [ ] User authentication and profiles
- [ ] Property favorites and saved searches
- [ ] Advanced filtering options
- [ ] Property comparison tool

### Version 1.2
- [ ] Machine learning price predictions
- [ ] Property recommendations
- [ ] Market analytics dashboard
- [ ] Mobile app (React Native)

### Version 2.0
- [ ] Multi-language support
- [ ] International property listings
- [ ] Virtual property tours
- [ ] AI-powered property matching

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Property Finder**: For providing comprehensive property data
- **Ollama**: For powerful local LLM capabilities
- **Flask Community**: For the excellent web framework
- **Open Source Contributors**: For the amazing tools and libraries

## 📞 Support

- **Documentation**: Check the docs folder for detailed guides
- **Issues**: Report bugs and request features on GitHub
- **Discussions**: Join our community discussions
- **Email**: Contact us at [your-email@domain.com]

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=your-username/real-estate-app-chatbot&type=Date)](https://star-history.com/#your-username/real-estate-app-chatbot&Date)

---

**Built with ❤️ by the Real Estate AI Team**

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app)
[![Deploy on Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com)
