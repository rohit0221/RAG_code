def clear_graphdb():
    """Clear all nodes and relationships in the Neo4j graph database."""
    with driver.session() as session:
        # Delete all nodes and relationships
        session.run("MATCH (n) DETACH DELETE n")
        logger.info("Cleared the Neo4j database.")

# Call this at the start of your workflow
clear_graphdb()