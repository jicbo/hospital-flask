import sys
import logging
from app import app

# Configure logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

try:
    # Test database connection on startup
    with app.app_context():
        from models import db
        db.engine.connect()
        logging.info("Database connection successful")
except Exception as e:
    logging.error(f"Database connection failed: {e}")
    # Don't raise in production
    if app.debug:
        raise

if __name__ == "__main__":
    app.run()
