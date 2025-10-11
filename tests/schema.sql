DROP TABLE IF EXISTS properties;

CREATE TABLE properties (
    id INTEGER PRIMARY KEY,
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
    all_image_urls TEXT, -- Stored as comma-separated string
    agency_name TEXT,
    contact_name TEXT,
    mobile_number TEXT,
    whatsapp_number TEXT,
    down_payment_percentage REAL
);