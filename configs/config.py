import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read environment variables directly
CODEBASE_PATH = os.getenv("CODEBASE_PATH")
LOG_LEVEL_CONSOLE = os.getenv("LOG_LEVEL_CONSOLE", "WARNING").upper()
LOG_LEVEL_FILE = os.getenv("LOG_LEVEL_FILE", "DEBUG").upper()
