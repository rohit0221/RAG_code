import json
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
    logger.info(f"Started parsing the codebase at: {os.path.abspath(directory)}")
    
    aggregated_results = {
        "functions": [],
        "classes": [],
        "imports": [],
        "variables": [],
    }

    # Walk through the directory to find Python files
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):  # Only process Python files
                file_path = os.path.join(root, file)
                logger.debug(f"Found Python file: {file_path}")
                parsed_file_data = parse_python_file(file_path, aggregated_results)

                # Append the data for each category
                aggregated_results["functions"].extend(parsed_file_data["functions"])
                aggregated_results["classes"].extend(parsed_file_data["classes"])
                aggregated_results["imports"].extend(parsed_file_data["imports"])
                aggregated_results["variables"].extend(parsed_file_data["variables"])

                # Debugging: print the size of the aggregated results
                logger.debug(
                    f"Aggregated so far: {len(aggregated_results['functions'])} functions, "
                    f"{len(aggregated_results['classes'])} classes, "
                    f"{len(aggregated_results['imports'])} imports, "
                    f"{len(aggregated_results['variables'])} variables."
                )

    logger.info(f"Parsing complete. Total parsed: "
                f"{len(aggregated_results['functions'])} functions, "
                f"{len(aggregated_results['classes'])} classes, "
                f"{len(aggregated_results['imports'])} imports, "
                f"{len(aggregated_results['variables'])} variables.")
    
    return aggregated_results


# Saving parsed data as JSONL (enhanced version to handle different types)
def save_parsed_data_jsonl(parsed_data, logs_dir="logs"):
    """
    Save the aggregated parsed data into separate JSONL files.
    """
    output_dir = os.path.join(logs_dir, "parsed_data")
    os.makedirs(output_dir, exist_ok=True)

    data_files = {
        "functions": "functions.jsonl",
        "classes": "classes.jsonl",
        "imports": "imports.jsonl",
        "variables": "variables.jsonl",
    }

    for key, filename in data_files.items():
        file_path = os.path.join(output_dir, filename)
        
        # Open file in append mode
        logger.info(f"Writing {key} data to {file_path}...")
        
        # Debugging: print the data size
        logger.debug(f"{key.capitalize()} data size: {len(parsed_data.get(key, []))} ")

        with open(file_path, "a", encoding="utf-8") as f:
            for item in parsed_data.get(key, []):
                f.write(json.dumps(item) + "\n")
                logger.debug(f"Wrote {json.dumps(item)} to {file_path}")

        logger.info(f"Saved {key} data to {file_path}")


def parse_python_file(file_path: str, aggregated_results: dict):
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
                "calls": extract_function_calls(node),  # Calls made within the function
                "used_imports": [],
                "used_variables": [],
            }

            # Track imports and variables used in the function body
            for stmt in node.body:
                # Track function calls
                if isinstance(stmt, ast.Call):  # Check for function calls
                    func_called = stmt.func
                    if isinstance(func_called, ast.Name):  # Direct function call like foo()
                        if func_called.id in aggregated_results['imports']:  # Check against imports
                            func_info['used_imports'].append(func_called.id)
                    elif isinstance(func_called, ast.Attribute):  # Check for method calls
                        if func_called.attr in aggregated_results['imports']:  # Method calls like foo.bar()
                            func_info['used_imports'].append(func_called.attr)

                # Track variable assignments
                elif isinstance(stmt, (ast.Assign, ast.AnnAssign, ast.AugAssign)):  # Add AugAssign and AnnAssign
                    for target in stmt.targets:
                        if isinstance(target, ast.Name):
                            func_info['used_variables'].append(target.id)

                # Track function arguments used as variables
                elif isinstance(stmt, ast.arguments):
                    for arg in stmt.args:
                        func_info['used_variables'].append(arg.arg)

            logger.debug(f"Function info: {func_info}")
            functions.append(func_info)

    # Extracting classes and methods
    classes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            logger.debug(f"Found class definition: {node.name}")
            class_info = {
                "name": node.name,
                "methods": [method.name for method in node.body if isinstance(method, ast.FunctionDef)],
                "docstring": ast.get_docstring(node),  # Class docstring
                "used_imports": [],
            }

            # Track imports used in the class
            for imp in aggregated_results['imports']:
                if imp in class_info['docstring']:
                    class_info['used_imports'].append(imp)

            # Assigning methods to class (including tracking imports used within methods)
            for method in class_info["methods"]:
                method_info = next(func for func in functions if func["name"] == method)
                class_info.setdefault("methods_info", []).append(method_info)

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
        if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):  # Add AugAssign and AnnAssign
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
