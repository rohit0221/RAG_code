from configs.config import CODEBASE_PATH
from configs.logging_config import setup_logging
from rag_code.code_parser.code_parser import parse_codebase

from rag_code.neo4jutils.graphdb import store_in_graphdb, clear_graphdb
# Set up logging using the centralized config
logger = setup_logging()

def main():
    """Main function to run the application."""
    logger.info(f"Starting the code parsing for {CODEBASE_PATH}")

    clear_graphdb()


    parsed_code=parse_codebase(CODEBASE_PATH)
    # print(type(parsed_code))
    store_in_graphdb(parsed_code)

if __name__ == "__main__":
    main()
