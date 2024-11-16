import os
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    # Ensure the logs directory exists
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Set up the logger
    logger = logging.getLogger('app_logger')
    logger.setLevel(logging.INFO)

    # Create a console handler for logging to console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create a file handler for logging to a file
    log_file_path = os.path.join(log_dir, 'app.log')
    file_handler = RotatingFileHandler(log_file_path, maxBytes=10**6, backupCount=5)  # 1MB size limit, 5 backups
    file_handler.setLevel(logging.INFO)

    # Set the log format
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
