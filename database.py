import sqlite3
from datetime import datetime, timedelta

import click
from flask import current_app, g

DATABASE = 'bayut_properties.db'
CACHE_LIFETIME_MINUTES = 30  # How long to cache search results


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'], detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    print("Database initialized for search caching.")


def find_cached_query(query_string):
    db = get_db()
    cursor = db.cursor()
    # Check if a non-expired query exists
    cursor.execute("""
        SELECT query_id FROM search_queries 
        WHERE query_string = ? AND expires_at > ?
    """, (query_string, datetime.now()))
    query_row = cursor.fetchone()
    return query_row['query_id'] if query_row else None


def get_properties_for_query(query_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM cached_properties WHERE query_id = ?", (query_id,))
    properties_raw = cursor.fetchall()

    properties_processed = []
    for prop_row in properties_raw:
        prop_dict = dict(prop_row)
        if prop_dict['all_image_urls']:
            prop_dict['all_image_urls'] = prop_dict['all_image_urls'].split(',')
        else:
            prop_dict['all_image_urls'] = []
        properties_processed.append(prop_dict)
    return properties_processed


def save_query_and_properties(query_string, properties_data):
    db = get_db()
    cursor = db.cursor()

    # Calculate expiration time
    expires_at = datetime.now() + timedelta(minutes=CACHE_LIFETIME_MINUTES)

    # Insert new query
    try:
        cursor.execute("""
            INSERT INTO search_queries (query_string, expires_at) VALUES (?, ?)
        """, (query_string, expires_at))
        query_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        # If a concurrent request already inserted the query, fetch its ID
        cursor.execute("SELECT query_id FROM search_queries WHERE query_string = ?", (query_string,))
        query_id = cursor.fetchone()['query_id']
        print(f"Query {query_string} already exists, fetching ID.")

    # Insert all properties
    for prop in properties_data:
        image_urls_str = ','.join(prop.get('all_image_urls', []))
        try:
            cursor.execute("""
                INSERT INTO cached_properties (
                    id, query_id, title, price, area, rooms, baths, purpose, completion_status,
                    latitude, longitude, location_name, cover_photo_url, all_image_urls,
                    agency_name, contact_name, mobile_number, whatsapp_number, down_payment_percentage
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (prop.get('id'), query_id, prop.get('title'), prop.get('price'), prop.get('area'), prop.get('rooms'),
                  prop.get('baths'), prop.get('purpose'), prop.get('completion_status'), prop.get('latitude'),
                  prop.get('longitude'), prop.get('location_name'), prop.get('cover_photo_url'), image_urls_str,
                  prop.get('agency_name'), prop.get('contact_name'), prop.get('mobile_number'),
                  prop.get('whatsapp_number'), prop.get('down_payment_percentage')))
        except sqlite3.IntegrityError:
            # Skip if property already exists for this query
            continue

    db.commit()
    print(f"Saved {len(properties_data)} properties for query ID {query_id}.")
    return query_id


@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
