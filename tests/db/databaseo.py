import sqlite3
import click
from flask import current_app, g

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with current_app.open_resource('schemaa.sql', mode='r') as f:
        db.executescript(f.read())

    # Ensure latitude and longitude are correctly populated in existing data
    # This part is for migration if you don't have lat/lng columns or they are empty
    # You might need a separate script for large existing databases
    cursor = db.cursor()
    cursor.execute("PRAGMA table_info(properties);")
    columns = [info[1] for info in cursor.fetchall()]
    if 'latitude' not in columns or 'longitude' not in columns:
        print("Adding latitude and longitude columns to properties table...")
        db.execute("ALTER TABLE properties ADD COLUMN latitude REAL;")
        db.execute("ALTER TABLE properties ADD COLUMN longitude REAL;")
        db.commit()
        print("Columns added. You might need to re-fetch data to populate them.")
    print("Database initialized.")


# ... (rest of your database.py, like insert_property, get_all_properties_count)
# Ensure insert_property also stores latitude and longitude
def insert_property(prop):
    db = get_db()
    try:
        # ... other fields ...
        latitude = prop.get('latitude')
        longitude = prop.get('longitude')
        all_image_urls = ','.join(prop.get('all_image_urls', []))

        cursor = db.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO properties (
                id, title, price, area, rooms, baths, purpose, completion_status,
                latitude, longitude, location_name, cover_photo_url, all_image_urls,
                agency_name, contact_name, mobile_number, whatsapp_number, down_payment_percentage
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            prop['id'], prop['title'], prop.get('price'), prop.get('area'),
            prop.get('rooms'), prop.get('baths'), prop.get('purpose'),
            prop.get('completion_status'), latitude, longitude,
            prop.get('location_name'), prop.get('cover_photo_url'), all_image_urls,
            prop.get('agency_name'), prop.get('contact_name'),
            prop.get('mobile_number'), prop.get('whatsapp_number'),
            prop.get('down_payment_percentage')
        ))
        db.commit()
        return True
    except sqlite3.IntegrityError as e:
        print(f"Failed to insert property {prop.get('id')} due to integrity error: {e}")
        return False
    except Exception as e:
        print(f"An error occurred while inserting property {prop.get('id')}: {e}")
        return False

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

def get_all_properties_count():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM properties")
    return cursor.fetchone()[0]