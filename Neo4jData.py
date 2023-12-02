from neo4j import GraphDatabase


class Neo4jData:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def get_employees(self):
        with self.driver as driver:
            records, summary, keys = driver.execute_query(
                "MATCH (p:Person) RETURN p.name AS name",
                database_="neo4j",
            )
            print(records, summary, keys)
