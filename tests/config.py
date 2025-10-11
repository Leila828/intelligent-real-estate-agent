# config.py
import os

# Define the path for your SQLite database file
# It's good practice to place it within a 'data' or 'instance' directory
# relative to your project root.
DATABASE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'bayut.sqlite')

# Ensure the instance directory exists when this file is imported
os.makedirs(os.path.dirname(DATABASE), exist_ok=True)

# You could also put API keys/secrets here if they were sensitive
# For now, Bayut API keys are hardcoded in bayut_scraper.py as they are public.