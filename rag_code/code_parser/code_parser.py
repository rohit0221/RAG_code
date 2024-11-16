import ast
import logging
import os
from dotenv import load_dotenv
from configs.logging_config import setup_logging
import chardet
# Load environment variables from .env file
load_dotenv()

# Set up logging configuration
logger = setup_logging()

def parse_codebase(directory: str):
    """
    Parses Python code files in the given directory and extracts relevant details.
    Logs the progress and results.
    """
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

def parse_python_file(file_path: str):
    """
    Parses a single Python file and extracts key information.
    Logs function names, classes, and imports.
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
    
    # Initialize lists to store the extracted elements
    functions = []
    classes = []
    imports = []
    variables = []

    # Walk through the AST and extract relevant data
    for node in ast.walk(tree):
        # Extract function definitions
        if isinstance(node, ast.FunctionDef):
            functions.append(node.name)

        # Extract class definitions
        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)

        # Extract import statements
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imports.append(f"{node.module}.{alias.name}")

        # Extract top-level variables (assignments outside of functions/classes)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    variables.append(target.id)

    # Log the parsed information
    logger.info(f"Parsed file: {file_path} - Functions: {functions}, Classes: {classes}, Imports: {imports}, Variables: {variables}")
    
    # Return a structured data dictionary
    return {
        'file_path': file_path,
        'functions': functions,
        'classes': classes,
        'imports': imports,
        'variables': variables,
    }
