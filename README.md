# 🤖 Intelligent Real Estate Agent

A sophisticated AI-powered real estate chatbot that provides intelligent property search, market analysis, and personalized recommendations for the UAE market.

## ✨ Features

- **🧠 Intelligent Query Understanding**: Uses LLM-based natural language processing
- **🏠 Property Search**: Search properties across all UAE locations
- **📊 Market Analysis**: Price comparisons, affordability calculations, and market insights
- **🎯 Location-Aware**: Works with any UAE location dynamically
- **💬 Natural Conversations**: Handles complex queries like "Compare prices in Palm Jumeirah vs Dubai Marina"
- **📱 Modern UI**: Beautiful, responsive web interface
- **⚡ Fast Performance**: Intelligent caching and optimized API calls

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/intelligent-real-estate-agent.git
   cd intelligent-real-estate-agent
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:5000`

## 🏗️ Architecture

### Core Components

- **`app.py`**: Main Flask application with intelligent search endpoints
- **`intelligent_agent.py`**: AI agent with LLM-based query understanding
- **`property_finder.py`**: Property Finder API integration
- **`database.py`**: SQLite caching system
- **`ollam.py`**: Natural language processing utilities
- **`templates/`**: Frontend HTML templates

### API Endpoints

- `POST /api/intelligent_search` - Main intelligent search endpoint
- `POST /api/nl_search` - Fallback natural language search
- `GET /api/properties/<id>` - Property details
- `GET /get_image` - Image proxy

## 🎯 Usage Examples

### Property Search
```
"Show me villas in Victory Heights"
"Find apartments in Dubai Marina under 2 million AED"
"Properties in Arabian Ranches with 3+ bedrooms"
```

### Market Analysis
```
"Compare prices in Palm Jumeirah vs Dubai Marina"
"What's the average price of villas in Sports City?"
"How many years of work needed to buy a villa in Victory Heights?"
```

### How-to Guides
```
"How to buy a villa in Dubai?"
"What's the process for selling property in UAE?"
```

## 🚀 Deployment

### Railway (Recommended)
1. Fork this repository
2. Connect your GitHub account to [Railway](https://railway.app)
3. Deploy from GitHub repository
4. Railway will automatically detect the `railway.json` configuration

### Render
1. Connect your GitHub repository to [Render](https://render.com)
2. Create a new Web Service
3. Use the following settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

### Heroku
1. Install [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
2. Create a new Heroku app: `heroku create your-app-name`
3. Deploy: `git push heroku main`

## 🔧 Configuration

### Environment Variables
- `FLASK_ENV`: Set to `production` for production deployment
- `PORT`: Port number (automatically set by deployment platforms)

### Database
The application uses SQLite for caching. The database is automatically created on first run.

## 📊 Performance

- **Intelligent Caching**: Reduces API calls and improves response times
- **Async Processing**: Non-blocking operations for better user experience
- **Fallback Systems**: Graceful degradation when external services are unavailable

## 🛠️ Development

### Project Structure
```
├── app.py                 # Main Flask application
├── intelligent_agent.py   # AI agent implementation
├── property_finder.py     # Property Finder API integration
├── database.py           # Database utilities
├── ollam.py              # NLP utilities
├── templates/            # Frontend templates
├── requirements.txt      # Python dependencies
├── Procfile             # Deployment configuration
└── railway.json         # Railway deployment config
```

### Adding New Features
1. Extend the `IntelligentRealEstateAgent` class in `intelligent_agent.py`
2. Add new intent handlers for different query types
3. Update the frontend templates for new response types

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in this repository
- Check the documentation in the `/docs` folder
- Review the API documentation in `API_DOCUMENTATION.md`

## 🎉 Acknowledgments

- Property Finder API for property data
- Ollama for LLM capabilities
- Flask for the web framework
- All contributors and testers

---

**Built with ❤️ for the UAE real estate market**