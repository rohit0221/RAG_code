Step 1: Install Required Libraries
Open your terminal and activate your Poetry environment.

Run the following commands to add the libraries.

Core Libraries (Required for parsing and graphing):
bash
Copy code
poetry add jedi networkx
Optional Libraries (For future steps):
bash
Copy code
poetry add py2neo # Neo4j driver for interacting with the graph database
poetry add python-dotenv # To manage environment variables (like database credentials)
poetry add tqdm # For progress bars during ingestion



Why These Libraries?
jedi: For advanced static analysis and cross-module insights.
networkx: To create and manipulate graphs in memory (useful for preprocessing).
py2neo: To connect and push data to Neo4j when we build the graph DB.
python-dotenv: To manage sensitive configuration values (like database credentials).
tqdm: For better progress tracking during analysis of large codebases.