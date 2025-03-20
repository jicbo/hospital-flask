import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    
    # Get DATABASE_URL from Vercel environment
    database_url = os.environ.get('POSTGRES_URL')
    if database_url:
        # Convert the URL to the correct format for SQLAlchemy
        database_url = database_url.replace('postgres://', 'postgresql://')
        SQLALCHEMY_DATABASE_URI = database_url
    else:
        # Fallback to SQLite for local development
        SQLALCHEMY_DATABASE_URI = 'sqlite:///hospital.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False