import os
from configs.logging_config import setup_logging  # Import logger setup
import ast
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = setup_logging()

# Set up logging configuration

def parse_codebase(directory: str):
    """
    Parses Python code files in the given directory and extracts relevant details.
    Logs the progress and results.
    """
    # logger.info(f"Started parsing the codebase at: {directory}")
    logger.info(f"Started parsing the codebase at: {os.path.abspath(directory)}")

    
    parsed_results = []

    # Walk through the directory to find Python files
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):  # Only process Python files
                file_path = os.path.join(root, file)
                parsed_results.append(parse_python_file(file_path))
    
    # After parsing, log the results
    if parsed_results:
        logger.info(f"Parsed {len(parsed_results)} files.")
    else:
        logger.warning(f"No Python files found in {directory}.")
    
    return parsed_results

import chardet

def parse_python_file(file_path: str):
    """
    Parses a single Python file and extracts key information.
    Logs function names from the file.
    """
    # Try to detect the file's encoding using chardet
    with open(file_path, "rb") as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']
    
    try:
        with open(file_path, "r", encoding=encoding) as file:
            source_code = file.read()
    except UnicodeDecodeError as e:
        logger.error(f"Failed to read file {file_path} due to encoding error: {e}")
        return None  # Or handle as needed
    
    # Parse the source code into an AST (Abstract Syntax Tree)
    tree = ast.parse(source_code)
    
    # Example: Extract function names from the AST
    functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    
    # Log the parsed information
    logger.info(f"Parsed file: {file_path} - Found functions: {functions}")
    
    return f"File: {file_path} - Functions: {functions}"

