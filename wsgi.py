import sys
import logging
from app import app

# Configure logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Test database connection and schema on startup
    with app.app_context():
        from models import db
        # Try to connect
        connection = db.engine.connect()
        # Check if tables exist
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        if not inspector.has_table("users"):
            logger.warning("Database tables do not exist - they will be created on first request")
        else:
            logger.info("Database schema verified successfully")
        connection.close()
except Exception as e:
    logger.error(f"Database connection failed: {e}")
    if app.debug:
        raise

if __name__ == "__main__":
    app.run()
