import logging

# Configure logging
from configs.logging_config import setup_logging

# Set up logging configuration
logger = setup_logging()

# Sample function for logging parsed file information
def log_parsed_file(file_name, functions, classes, imports, variables):
    """
    Logs the parsed data (functions, classes, imports, variables) for the given file.
    """
    logger.info(f"Parsed file: {file_name}")
    
    # Log functions, if any
    if functions:
        logger.debug(f"Functions in {file_name}: {functions}")
    else:
        logger.debug(f"No functions found in {file_name}")
    
    # Log classes, if any
    if classes:
        logger.debug(f"Classes in {file_name}: {classes}")
    else:
        logger.debug(f"No classes found in {file_name}")
    
    # Log imports, if any
    if imports:
        logger.debug(f"Imports in {file_name}: {imports}")
    else:
        logger.debug(f"No imports found in {file_name}")
    
    # Log variables, if any
    if variables:
        logger.debug(f"Variables in {file_name}: {variables}")
    else:
        logger.debug(f"No variables found in {file_name}")
