import sys
import logging
from app import app

# Configure logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

if __name__ == "__main__":
    app.run()
