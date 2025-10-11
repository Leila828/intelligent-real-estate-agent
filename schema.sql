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
    title TEXT NOT NULL,
    price REAL,
    area REAL,
    rooms INTEGER,
    baths INTEGER,
    purpose TEXT,
    completion_status TEXT,
    latitude REAL,
    longitude REAL,
    location_name TEXT,
    cover_photo_url TEXT,
    all_image_urls TEXT,
    agency_name TEXT,
    contact_name TEXT,
    mobile_number TEXT,
    whatsapp_number TEXT,
    down_payment_percentage REAL,
    PRIMARY KEY (id, query_id),
    FOREIGN KEY (query_id) REFERENCES search_queries (query_id)
);