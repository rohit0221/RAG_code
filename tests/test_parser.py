# test_parser.py

import logging
from configs.config import CODEBASE_PATH
from configs.logging_config import setup_logging
from rag_code.code_parser.code_parser import parse_codebase

# Set up logging using the centralized config
logger = setup_logging()

def test_parsing():
    """Test parsing a small codebase."""
    logger.info("Test started")
    
    # Simulate parsing a small test folder (modify CODEBASE_PATH or create a folder with test files)
    test_path = '../code_base'  # Assuming you have a test folder
    
    logger.info(f"Starting code parsing for {test_path}")
    result = parse_codebase(test_path)  # Parse the codebase
    
    logger.info(f"Parsing completed. Results: {result}")

    # For testing purposes, you can assert expected results if you know the folder content
    assert result, "Parsing returned empty results!"
    
    logger.info("Test completed successfully")

if __name__ == "__main__":
    test_parsing()
