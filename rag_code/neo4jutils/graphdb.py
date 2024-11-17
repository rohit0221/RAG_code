from neo4j import GraphDatabase
import ast
from dotenv import load_dotenv
from configs.logging_config import setup_logging
from rag_code.code_parser.function_logging import log_parsed_file

from rag_code.code_parser.code_parser import parse_codebase

from configs.config import NEO4J_URI,NEO4J_USERNAME,NEO4J_PASSWORD
# Load environment variables from .env file
load_dotenv()

# Set up logging configuration
logger = setup_logging()

# Neo4j driver initialization
uri = NEO4J_URI  # Replace with your Neo4j connection string
username = NEO4J_USERNAME  # Default username
password = NEO4J_PASSWORD  # Replace with your Neo4j password

print(f"URI{uri}")
print(f"username{username}")
print(f"password{password}")

driver = GraphDatabase.driver(uri, auth=(username, password))

# Define a function to store data in the graph database
def store_in_graphdb(parsed_code):
    """
    Store parsed code information into a Neo4j graph database.
    """
    # Accessing directly as a dictionary
    functions = parsed_code.get("functions", [])
    classes = parsed_code.get("classes", [])
    imports = parsed_code.get("imports", [])
    variables = parsed_code.get("variables", [])

    with driver.session() as session:
        # Create function nodes and relationships
        for func in functions:
            session.write_transaction(create_function_node, func)
            # Create relationships for function calls
            for call in func['calls']:
                session.write_transaction(create_function_call_relationship, func['name'], call)
            # Create relationships for used imports
            for used_import in func['used_imports']:
                session.write_transaction(create_function_import_relationship, func['name'], used_import)
            # Create relationships for used variables
            for used_var in func['used_variables']:
                session.write_transaction(create_function_variable_relationship, func['name'], used_var)
        
        # Create class nodes and relationships
        for cls in classes:
            session.write_transaction(create_class_node, cls)
        
        # Create variable nodes
        for var in variables:
            session.write_transaction(create_variable_node, var)

        # Create import nodes and relationships
        for imp in imports:
            session.write_transaction(create_import_node, imp)


def create_function_node(tx, func):
    """Create a node for a function."""
    # Ensure returns is not None
    returns = func['returns'] if func['returns'] is not None else 'None'
    
    tx.run("""
        MERGE (func:Function {name: $name, returns: $returns})
        """, name=func['name'], returns=returns)

def create_function_call_relationship(tx, func_name, call_name):
    """Create a relationship for function calls within a function."""
    tx.run("""
        MERGE (func:Function {name: $func_name})
        MERGE (call:Function {name: $call_name})
        MERGE (func)-[:CALLS]->(call)
        """, func_name=func_name, call_name=call_name)

def create_function_import_relationship(tx, func_name, import_name):
    """Create a relationship for imports used within a function."""
    tx.run("""
        MERGE (func:Function {name: $func_name})
        MERGE (imp:Import {name: $import_name})
        MERGE (func)-[:USES_IMPORT]->(imp)
        """, func_name=func_name, import_name=import_name)

def create_function_variable_relationship(tx, func_name, var_name):
    """Create a relationship for variables used within a function."""
    tx.run("""
        MERGE (func:Function {name: $func_name})
        MERGE (var:Variable {name: $var_name})
        MERGE (func)-[:USES_VARIABLE]->(var)
        """, func_name=func_name, var_name=var_name)

def create_class_node(tx, cls):
    """Create a node for a class."""
    tx.run("""
        MERGE (cls:Class {name: $name})
        """, name=cls['name'])

def create_variable_node(tx, var):
    """Create a node for a variable."""
    tx.run("""
        MERGE (var:Variable {name: $name, value: $value})
        """, name=var['name'], value=var['value'])

def create_import_node(tx, imp):
    """Create a node for an import."""
    tx.run("""
        MERGE (imp:Import {name: $name})
        """, name=imp)

def clear_graphdb():
    """Clear all nodes and relationships in the Neo4j graph database."""
    with driver.session() as session:
        # Delete all nodes and relationships
        session.run("MATCH (n) DETACH DELETE n")
        logger.info("Cleared the Neo4j database.")

# Call this at the start of your workflow
clear_graphdb()
