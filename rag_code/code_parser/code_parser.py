import ast
import os
from dotenv import load_dotenv
from configs.logging_config import setup_logging
import chardet
from rag_code.code_parser.function_logging import log_parsed_file

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
                logger.debug(f"Found Python file: {file_path}")
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
    Logs function names from the file along with their parameters, return types, docstrings, decorators,
    and other relevant data.
    """
    logger.info(f"Parsing Python file: {file_path}")
    
    with open(file_path, "r", encoding="utf-8") as file:
        source_code = file.read()

    tree = ast.parse(source_code)

    # Debugging: log the entire AST
    logger.debug(f"AST Tree for {file_path}: {ast.dump(tree)}")

    # Extracting functions and methods
    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            logger.debug(f"Found function definition: {node.name}")

            # Process the return type to handle `ast.Name`
            return_type = None
            if node.returns:
                if isinstance(node.returns, ast.Name):
                    return_type = node.returns.id  # Extract the name from the ast.Name object
                else:
                    return_type = ast.dump(node.returns)  # Fallback to dumping the entire node if it's a different type

            func_info = {
                "name": node.name,
                "args": [arg.arg for arg in node.args.args],  # Function arguments
                "returns": return_type,  # Return type annotation (now a string)
                "docstring": ast.get_docstring(node),  # Function docstring
                "decorators": [decorator.id for decorator in node.decorator_list if isinstance(decorator, ast.Name)],
                "calls": extract_function_calls(node)  # Calls made within the function
            }
            logger.debug(f"Function info: {func_info}")
            functions.append(func_info)

    # Extracting classes
    classes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            logger.debug(f"Found class definition: {node.name}")
            class_info = {
                "name": node.name,
                "methods": [method.name for method in node.body if isinstance(method, ast.FunctionDef)],
                "docstring": ast.get_docstring(node),  # Class docstring
            }
            logger.debug(f"Class info: {class_info}")
            classes.append(class_info)

    # Extracting imports
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            logger.debug(f"Found import: {', '.join(alias.name for alias in node.names)}")
            imports.extend([alias.name for alias in node.names])
        elif isinstance(node, ast.ImportFrom):
            logger.debug(f"Found import from: {node.module}")
            imports.extend([f"{node.module}.{n.name}" for n in node.names])

    # Extracting variables (assignments)
    variables = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    logger.debug(f"Found variable assignment: {target.id} = {ast.dump(node.value)}")
                    variables.append({
                        "name": target.id,
                        "value": ast.dump(node.value),  # Show value (could be further processed for types)
                    })

    # Log the collected information (invoking log_parsed_file)
    log_parsed_file(file_path, functions, classes, imports, variables)

    parsed_data = {
        "functions": functions,
        "classes": classes,
        "imports": imports,
        "variables": variables
    }

    # Save to files
    save_parsed_data_jsonl(parsed_data)

    return {
        "functions": functions,
        "classes": classes,
        "imports": imports,
        "variables": variables
    }


def extract_function_calls(function_node):
    """Helper function to extract function calls within a function."""
    logger.debug(f"Extracting function calls from: {function_node.name}")
    
    calls = []
    for node in ast.walk(function_node):
        if isinstance(node, ast.Call):
            # Extract the function name or callable
            if isinstance(node.func, ast.Name):
                logger.debug(f"Found function call: {node.func.id}")
                calls.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                logger.debug(f"Found method call: {node.func.attr}")
                calls.append(node.func.attr)  # For method calls on objects
    
    logger.debug(f"Function calls: {calls}")
    return calls

import json
import os
from datetime import datetime

def save_parsed_data(parsed_data, logs_dir="logs"):
    """
    Save the parsed data into separate files for functions, classes, imports, and variables.

    Args:
        parsed_data (dict): Parsed data containing 'functions', 'classes', 'imports', and 'variables'.
        logs_dir (str): Path to the logs directory where files will be saved. Defaults to 'logs'.

    Returns:
        None
    """
    # Create a timestamped subdirectory under the logs directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(logs_dir, f"parsed_data_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)

    # File mappings
    data_files = {
        "functions": "functions.json",
        "classes": "classes.json",
        "imports": "imports.json",
        "variables": "variables.json",
    }

    # Write each category to its respective file
    for key, filename in data_files.items():
        file_path = os.path.join(output_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(parsed_data.get(key, []), f, indent=4)
        
        print(f"Saved {key} data to {file_path}")

# Example of invoking the function:
# save_parsed_data({
#     "functions": [{"name": "example_function", "args": [], "returns": "None"}],
#     "classes": [{"name": "ExampleClass", "methods": []}],
#     "imports": ["os", "json"],
#     "variables": [{"name": "example_var", "value": "42"}]
# })


import os
import json

def save_parsed_data_jsonl(parsed_data, logs_dir="logs"):
    """
    Save the parsed data into separate JSONL files for functions, classes, imports, and variables.
    All data will go into a fixed folder, and files will be overwritten if they already exist.

    Args:
        parsed_data (dict): Parsed data containing 'functions', 'classes', 'imports', and 'variables'.
        logs_dir (str): Path to the logs directory where files will be saved. Defaults to 'logs'.

    Returns:
        None
    """
    # Fixed subdirectory for storing the files
    output_dir = os.path.join(logs_dir, "parsed_data")
    os.makedirs(output_dir, exist_ok=True)

    # File mappings
    data_files = {
        "functions": "functions.jsonl",
        "classes": "classes.jsonl",
        "imports": "imports.jsonl",
        "variables": "variables.jsonl",
    }

    # Save each category in JSONL format
    for key, filename in data_files.items():
        file_path = os.path.join(output_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            for item in parsed_data.get(key, []):
                f.write(json.dumps(item) + "\n")  # Write each item as a compact JSON object in a new line
        print(f"Saved {key} data to {file_path}")

    # Inform about completion
    print(f"All parsed data saved in JSONL format in folder: {output_dir}")
