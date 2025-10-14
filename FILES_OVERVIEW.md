# 📁 Files Overview - Intelligent Real Estate Agent

This document provides a comprehensive overview of all files used in the intelligent agent system.

## 🎯 Core Application Files

### Main Application
- **`app.py`** - Main Flask application with intelligent search endpoints
  - Contains `/api/intelligent_search` and `/api/nl_search` routes
  - Integrates with the intelligent agent
  - Handles both new agent and fallback systems

### AI Agent System
- **`intelligent_agent.py`** - Core AI agent implementation
  - `IntelligentRealEstateAgent` class with LLM-based understanding
  - Dynamic location extraction for any UAE location
  - Intent recognition and response generation
  - Handles comparisons, affordability, price analysis, guides, and property search

### Property Search & API Integration
- **`property_finder.py`** - Property Finder API integration
  - `search_location()` - Find location IDs
  - `fetch_propertyfinder_listings()` - Get property data
  - `initialise()` - Get build ID for API calls
  - Data mapping and processing

- **`test_prop.py`** - Property search functions
  - `search_properties()` - Main search function used by the agent
  - Caching logic and database integration
  - Used by both old and new systems

### Database & Caching
- **`database.py`** - SQLite database utilities
  - `init_db()` - Initialize database tables
  - `find_cached_query()` - Check cache for existing queries
  - `cache_query()` - Store new queries and results
  - `get_cached_properties()` - Retrieve cached properties

### Natural Language Processing
- **`ollam.py`** - NLP utilities and query parsing
  - `parse_natural_query()` - Parse user queries with regex and LLM fallback
  - `llama_fallback()` - LLaMA model integration
  - Multi-question handling and entity extraction

## 🎨 Frontend Files

### Templates Directory (`templates/`)
- **`index.html`** - Main web interface
  - Intelligent search form
  - `renderIntelligentResults()` - Display agent responses
  - `renderSearchResults()` - Display fallback results
  - Property cards and interactive elements

- **`property_detail.html`** - Property details page
- **`map_page.html`** - Map view for properties

## ⚙️ Configuration Files

### Deployment Configuration
- **`requirements.txt`** - Python dependencies
  ```
  Flask==3.1.2
  requests==2.32.5
  click==8.3.0
  gunicorn==21.2.0
  aiohttp==3.9.1
  ```

- **`Procfile`** - Heroku deployment configuration
  ```
  web: gunicorn app:app
  ```

- **`railway.json`** - Railway deployment configuration
  ```json
  {
    "name": "intelligent-real-estate-agent",
    "environment": {
      "PYTHON_VERSION": "3.12.0",
      "FLASK_ENV": "production"
    },
    "deploy": {
      "startCommand": "gunicorn app:app"
    }
  }
  ```

- **`runtime.txt`** - Python version specification
  ```
  python-3.12.0
  ```

### Git Configuration
- **`.gitignore`** - Excludes unnecessary files from version control
- **`.github/workflows/test.yml`** - GitHub Actions CI/CD pipeline

## 📚 Documentation Files

### User Documentation
- **`README.md`** - Main project documentation
- **`DEPLOYMENT_GUIDE.md`** - Detailed deployment instructions
- **`FILES_OVERVIEW.md`** - This file

### Database Schema
- **`schema.sql`** - Database table definitions
  ```sql
  CREATE TABLE search_queries (
      id INTEGER PRIMARY KEY,
      query_string TEXT UNIQUE,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );
  
  CREATE TABLE cached_properties (
      id INTEGER PRIMARY KEY,
      query_id INTEGER,
      property_data TEXT,
      FOREIGN KEY (query_id) REFERENCES search_queries (id)
  );
  ```

## 🚀 Deployment Scripts

- **`deploy_to_github.py`** - Automated GitHub setup script
- **`deploy.py`** - Railway deployment automation

## 🗂️ File Dependencies

### Core Dependencies
```
app.py
├── intelligent_agent.py
├── ollam.py
├── database.py
├── test_prop.py
└── property_finder.py

intelligent_agent.py
├── test_prop.py (for property search)
└── aiohttp (for async operations)

test_prop.py
├── property_finder.py
├── database.py
└── ollam.py

property_finder.py
└── requests (for API calls)

database.py
└── sqlite3 (built-in)
```

### Frontend Dependencies
```
templates/index.html
├── Leaflet (for maps)
├── Bootstrap (for styling)
└── Custom JavaScript functions
```

## 📊 File Sizes and Complexity

| File | Lines | Purpose | Complexity |
|------|-------|---------|------------|
| `app.py` | ~1400 | Main application | High |
| `intelligent_agent.py` | ~600 | AI agent | High |
| `property_finder.py` | ~300 | API integration | Medium |
| `ollam.py` | ~600 | NLP processing | High |
| `database.py` | ~100 | Database utilities | Low |
| `test_prop.py` | ~300 | Property search | Medium |

## 🔄 File Relationships

### Data Flow
1. **User Query** → `templates/index.html`
2. **API Request** → `app.py` → `intelligent_agent.py`
3. **Query Processing** → `ollam.py` (if needed)
4. **Property Search** → `test_prop.py` → `property_finder.py`
5. **Caching** → `database.py`
6. **Response** → `templates/index.html`

### Agent Flow
1. **Query Understanding** → `intelligent_agent.py`
2. **Intent Recognition** → `intelligent_agent.py`
3. **Location Extraction** → `intelligent_agent.py`
4. **Property Search** → `test_prop.py`
5. **Response Generation** → `intelligent_agent.py`
6. **Frontend Rendering** → `templates/index.html`

## 🧹 Cleanup Recommendations

### Files to Keep (Essential)
- All files listed in "Core Application Files"
- All files listed in "Configuration Files"
- All files listed in "Documentation Files"
- `templates/` directory

### Files to Remove (Not Used)
- `agent_integration.py` - Old agent integration
- `agent_integration_fixed.py` - Old agent integration
- `app_with_agent.py` - Temporary test file
- `ai_agent_architecture.py` - Old agent architecture
- `agent_requirements.txt` - Old requirements
- `tests/` directory - Test files not needed for deployment
- `venv/` directory - Virtual environment
- `__pycache__/` directories - Python cache
- `*.db` files - Database files (created at runtime)
- Screenshot files - Not needed for deployment

## 🚀 Deployment Checklist

Before deploying, ensure these files are present:
- [ ] `app.py`
- [ ] `intelligent_agent.py`
- [ ] `property_finder.py`
- [ ] `database.py`
- [ ] `ollam.py`
- [ ] `test_prop.py`
- [ ] `requirements.txt`
- [ ] `Procfile`
- [ ] `railway.json`
- [ ] `runtime.txt`
- [ ] `README.md`
- [ ] `.gitignore`
- [ ] `templates/` directory
- [ ] `schema.sql`

---

**Total Essential Files: ~15 files**
**Total Lines of Code: ~3,500 lines**
**Deployment Size: ~2MB (excluding dependencies)**
