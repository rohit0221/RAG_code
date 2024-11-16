import os
import logging
from logging.handlers import TimedRotatingFileHandler
from dotenv import load_dotenv
import glob

# Load environment variables from the .env file
load_dotenv()

def clear_log_folder():
    """Clears all log files in the logs directory."""
    log_dir = 'logs'
    log_files = glob.glob(os.path.join(log_dir, "*.log"))
    for log_file in log_files:
        try:
            os.remove(log_file)  # Remove the log file
            print(f"Deleted log file: {log_file}")
        except Exception as e:
            print(f"Error deleting log file {log_file}: {e}")

def setup_logging():
    # Clear existing log files before setting up new ones
    clear_log_folder()

    # Ensure the logs directory exists
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Get the console log level from environment variable
    console_log_level = os.getenv("LOG_LEVEL_CONSOLE", "WARNING").upper()

    # Get the file log level from environment variable
    file_log_level = os.getenv("LOG_LEVEL_FILE", "DEBUG").upper()

    # Set up the logger
    logger = logging.getLogger('app_logger')
    logger.setLevel(logging.DEBUG)  # Use DEBUG for internal processing of logs

    # Create a console handler for logging to console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_log_level)  # Set the console handler's level based on environment variable

    # Create a timed rotating file handler for logging to a file
    log_file_path = os.path.join(log_dir, 'app.log')
    file_handler = TimedRotatingFileHandler(log_file_path, when='midnight', interval=1, backupCount=3, encoding='utf-8')  # Rotate daily at midnight, keep 3 backups
    file_handler.setLevel(file_log_level)  # Set the file handler's level based on environment variable

    # Set the log format
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
