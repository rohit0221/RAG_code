import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read environment variables directly
CODEBASE_PATH = os.getenv("CODEBASE_PATH")
LOG_LEVEL_CONSOLE = os.getenv("LOG_LEVEL_CONSOLE", "WARNING").upper()
NEO4J_URI = os.getenv("NEO4J_URI", "DEBUG")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "DEBUG")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "DEBUG")