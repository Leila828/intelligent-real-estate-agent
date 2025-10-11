import sqlite3
from flask import current_app, g
import click

DATABASE = 'bayut_properties.db'

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
    with current_app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    print("Database initialized.")

def insert_property(property_data):
    db = get_db()
    cursor = db.cursor()

    image_urls_str = ','.join(property_data.get('all_image_urls', []))

    try:
        cursor.execute("""
            INSERT INTO properties (
                id, title, price, area, rooms, baths, purpose, completion_status,
                latitude, longitude, location_name, cover_photo_url, all_image_urls,
                agency_name, contact_name, mobile_number, whatsapp_number, down_payment_percentage
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            property_data.get('id'),
            property_data.get('title'),
            property_data.get('price'),
            property_data.get('area'),
            property_data.get('rooms'),
            property_data.get('baths'),
            property_data.get('purpose'),
            property_data.get('completion_status'),
            property_data.get('latitude'),
            property_data.get('longitude'),
            property_data.get('location_name'),
            property_data.get('cover_photo_url'),
            image_urls_str,
            property_data.get('agency_name'),
            property_data.get('contact_name'),
            property_data.get('mobile_number'),
            property_data.get('whatsapp_number'),
            property_data.get('down_payment_percentage')
        ))
        db.commit()
        return True
    except sqlite3.IntegrityError as e:
        print(f"Skipping property {property_data.get('id')} due to duplicate ID: {e}")
        db.rollback()
        return False
    except Exception as e:
        print(f"An unexpected error occurred during insertion: {e}")
        db.rollback()
        return False

def get_all_properties():
    # This function is not used for the /api/properties anymore, but kept for consistency
    # get_all_properties_paginated is preferred.
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM properties")
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

def get_all_properties_count():
    """
    Returns the total number of properties in the database.
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM properties")
    return cursor.fetchone()[0]


@click.command('init-db')
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)