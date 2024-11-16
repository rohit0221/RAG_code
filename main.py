import logging
from configs.config import CODEBASE_PATH
from configs.logging_config import setup_logging
from rag_code.code_parser.code_parser import parse_codebase

# Set up logging using the centralized config
logger = setup_logging()

def main():
    """Main function to run the application."""
    logger.info(f"Starting the code parsing for {CODEBASE_PATH}")
    parse_codebase(CODEBASE_PATH)

if __name__ == "__main__":
    main()
