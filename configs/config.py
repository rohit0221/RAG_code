import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read environment variables directly
CODEBASE_PATH = os.getenv("CODEBASE_PATH")
DEBUG = os.getenv("DEBUG", "False") == "True"  # Convert string 'True' to boolean
