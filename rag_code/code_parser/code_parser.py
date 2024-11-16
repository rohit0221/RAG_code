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
    with open(file_path, "r", encoding="utf-8") as file:
        source_code = file.read()

    tree = ast.parse(source_code)

    # Extracting functions and methods
    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_info = {
                "name": node.name,
                "args": [arg.arg for arg in node.args.args],  # Function arguments
                "returns": node.returns,  # Return type annotation
                "docstring": ast.get_docstring(node),  # Function docstring
                "decorators": [decorator.id for decorator in node.decorator_list if isinstance(decorator, ast.Name)],
                "calls": extract_function_calls(node)  # Calls made within the function
            }
            functions.append(func_info)

    # Extracting classes
    classes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_info = {
                "name": node.name,
                "methods": [method.name for method in node.body if isinstance(method, ast.FunctionDef)],
                "docstring": ast.get_docstring(node),  # Class docstring
            }
            classes.append(class_info)

    # Extracting imports
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend([alias.name for alias in node.names])
        elif isinstance(node, ast.ImportFrom):
            imports.extend([f"{node.module}.{n.name}" for n in node.names])  # Fixed list comprehension issue

    # Extracting variables (assignments)
    variables = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    variables.append({
                        "name": target.id,
                        "value": ast.dump(node.value),  # Show value (could be further processed for types)
                    })

    # Log the collected information (invoking log_parsed_file)
    log_parsed_file(file_path, functions, classes, imports, variables)

    return {
        "functions": functions,
        "classes": classes,
        "imports": imports,
        "variables": variables
    }

def extract_function_calls(function_node):
    """Helper function to extract function calls within a function."""
    calls = []
    for node in ast.walk(function_node):
        if isinstance(node, ast.Call):
            # Extract the function name or callable
            if isinstance(node.func, ast.Name):
                calls.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                calls.append(node.func.attr)  # For method calls on objects
    return calls