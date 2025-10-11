-----

# Real Estate API Backend with Query Caching

##  How It Works (Architecture)

The application follows a simple but powerful caching strategy:

1.  A user's search request arrives at the `/api/search` endpoint with filters (e.g., `rooms=4`, `purpose=for-sale`).
2.  The API creates a unique identifier (a canonical string) for this specific query.
3.  It checks the local SQLite database to see if a fresh cache for this query exists.
4.  **Cache Hit:** If a recent entry is found, the API retrieves the stored properties and returns them to the user immediately.
5.  **Cache Miss:** If no cache is found or the existing cache has expired, the API does the following:
      * It makes a live API call to Algolia using the user's filters.
      * It stores the fetched properties in the local database, linked to the unique query string.
      * It returns the newly fetched data to the user.

This ensures that the user always gets fresh data for a new search, but never has to wait for a repeated search.

##  Prerequisites

  * Python 3.8 or higher
  * `pip` (Python package installer)

## Installation & Setup

1.  **Clone the project** (or create the files as instructed).
2.  **Install dependencies:** Navigate to the project directory and install the required libraries.
    ```bash
    pip install -r requirements.txt
    ```
3.  **Start the server:** Run the main application file. This will automatically create and initialize the database.
    ```bash
    python app.py
    ```
    The API will be available at `http://127.0.0.1:5000`.

## API Endpoints

### `GET /api/search`

The primary endpoint for searching properties with a caching layer.

**Query Parameters:**
| Parameter | Type | Description |
| :--- | :--- | :--- |
| `page` | `int` | The page number to retrieve (default: 1). |
| `limit` | `int` | The number of properties per page (default: 10). |
| `purpose` | `str` | Filter by purpose (e.g., `for-sale`, `for-rent`). |
| `rooms` | `int` | Filter by number of rooms. |
| `baths` | `int` | Filter by number of bathrooms. |
| `min_price` | `int` | Filter by a minimum price. |
| `max_price` | `int` | Filter by a maximum price. |

**Example Usage:**

```bash
# Search for 4-bedroom apartments for sale under 1.5 million AED
curl "http://127.0.0.1:5000/api/search?purpose=for-sale&rooms=4&max_price=1500000"

# Access page 2 of 20 results for the same query
curl "http://127.0.0.1:5000/api/search?purpose=for-sale&rooms=4&max_price=1500000&page=2&limit=20"
```

### `GET /get_image`

A simple proxy to fetch and serve images from the external API's CDN. This is useful for bypassing CORS issues in client-side applications.

**Query Parameters:**
| Parameter | Type | Description |
| :--- | :--- | :--- |
| `url` | `str` | The full URL of the image to retrieve. |

**Example Usage:**

```bash
# Note: The 'url' parameter must be URL-encoded in a real request
<img src="http://127.0.0.1:5000/get_image?url=https%3A%2F%2Fimages.bayut.com%2Fthumbnails%2Fexample-id-400x300.webp" />
```

## 📂 Project Structure

```
/project_root
├── app.py              # Main Flask application and API routes
├── database.py         # SQLite database functions and caching logic
├── schema.sql          # SQL commands to create the database tables
├── requirements.txt    # Python package dependencies
└── README.md           # This file
```

## 📝 Database Schema (`schema.sql`)

The database is built on two tables to support the caching mechanism.

```sql
DROP TABLE IF EXISTS cached_properties;
DROP TABLE IF EXISTS search_queries;

CREATE TABLE search_queries (
    query_id INTEGER PRIMARY KEY AUTOINCREMENT,
    query_string TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL
);

CREATE TABLE cached_properties (
    id TEXT NOT NULL,
    query_id INTEGER NOT NULL,
    ... (all other property columns) ...
    PRIMARY KEY (id, query_id),
    FOREIGN KEY (query_id) REFERENCES search_queries (query_id)
);
```
