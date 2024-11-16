from neo4j import GraphDatabase,RoutingControl

NEO4J_URI="neo4j+s://ea1ec225.databases.neo4j.io:7687"
NEO4J_USERNAME="neo4j"
NEO4J_PASSWORD="m57H5nBYF9FlQP3a0-Wk3jsGQLOhD1Tb066h9FNxqg4"

AUTH = ("neo4j", "m57H5nBYF9FlQP3a0-Wk3jsGQLOhD1Tb066h9FNxqg4")
try:
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    with driver.session() as session:
        result = session.run("RETURN 1")
        print("Connection successful:", result.single()[0])
except Exception as e:
    print("Connection failed:", e)
finally:
    driver.close()
