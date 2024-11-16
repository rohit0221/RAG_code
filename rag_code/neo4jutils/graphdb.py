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

class CodeParserGraph:
    def __init__(self, uri, username, password):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))

    def close(self):
        self.driver.close()

    def create_file_node(self, file_name):
        with self.driver.session() as session:
            session.write_transaction(self._create_file, file_name)

    def create_function_node(self, file_name, func_info):
        with self.driver.session() as session:
            session.write_transaction(self._create_function, file_name, func_info)

    def create_class_node(self, file_name, class_info):
        with self.driver.session() as session:
            session.write_transaction(self._create_class, file_name, class_info)

    def create_import_edge(self, file_name, imported_module):
        with self.driver.session() as session:
            session.write_transaction(self._create_import_edge, file_name, imported_module)

    def create_contains_edge(self, file_name, node_name, node_type):
        with self.driver.session() as session:
            session.write_transaction(self._create_contains_edge, file_name, node_name, node_type)

    def create_calls_edge(self, file_name, calling_func, called_func):
        with self.driver.session() as session:
            session.write_transaction(self._create_calls_edge, file_name, calling_func, called_func)

    def _create_file(self, tx, file_name):
        tx.run("MERGE (f:File {name: $file_name})", file_name=file_name)

    def _create_function(self, tx, file_name, func_info):
        # Extract values from func_info, ensure they are simple data types
        func_name = func_info['name']
        args = [arg.id if isinstance(arg, ast.Name) else str(arg) for arg in func_info['args']]  # Extracting variable names
        returns = func_info['returns']
        docstring = func_info.get('docstring', "")

        tx.run("""
            MATCH (f:File {name: $file_name})
            MERGE (func:Function {name: $func_name})
            MERGE (f)-[:CONTAINS]->(func)
            SET func.args = $args, func.returns = $returns, func.docstring = $docstring
        """, file_name=file_name, func_name=func_name, args=args, returns=returns, docstring=docstring)


    def _create_class(self, tx, file_name, class_info):
        tx.run("""
            MATCH (f:File {name: $file_name})
            MERGE (cls:Class {name: $class_name})
            MERGE (f)-[:CONTAINS]->(cls)
            SET cls.methods = $methods, cls.docstring = $docstring
        """, file_name=file_name, class_name=class_info['name'],
            methods=class_info['methods'], docstring=class_info['docstring'])

    def _create_import_edge(self, tx, file_name, imported_module):
        tx.run("""
            MATCH (f:File {name: $file_name})
            MERGE (imp:Import {name: $imported_module})
            MERGE (f)-[:IMPORTS]->(imp)
        """, file_name=file_name, imported_module=imported_module)

    def _create_contains_edge(self, tx, file_name, node_name, node_type):
        tx.run("""
            MATCH (f:File {name: $file_name})
            MATCH (n: {node_type} {name: $node_name})
            MERGE (f)-[:CONTAINS]->(n)
        """, file_name=file_name, node_name=node_name, node_type=node_type)

    def _create_calls_edge(self, tx, file_name, calling_func, called_func):
        tx.run("""
            MATCH (caller:Function {name: $calling_func})
            MATCH (callee:Function {name: $called_func})
            MERGE (caller)-[:CALLS]->(callee)
        """, calling_func=calling_func, called_func=called_func)


# Initialize the graph object
graph_db = CodeParserGraph(uri, username, password)

def store_parsed_data_in_graph(parsed_data, file_name):
    # Store file node
    graph_db.create_file_node(file_name)
    
    # Store functions
    for func in parsed_data['functions']:
        graph_db.create_function_node(file_name, func)

    # Store classes
    for cls in parsed_data['classes']:
        graph_db.create_class_node(file_name, cls)
    
    # Store imports
    for imp in parsed_data['imports']:
        graph_db.create_import_edge(file_name, imp)

    # Store function calls (relationships)
    for func in parsed_data['functions']:
        for called_func in func['calls']:
            graph_db.create_calls_edge(file_name, func['name'], called_func)

def parse_and_store(directory):
    # Reuse parse_codebase to get parsed results
    parsed_data_list = parse_codebase(directory)
    
    for parsed_data in parsed_data_list:
        file_path = parsed_data.get("file_path")  # Assuming you are getting file path in parsed data
        store_parsed_data_in_graph(parsed_data, file_path)

