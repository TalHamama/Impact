import os

from dotenv import load_dotenv
from neo4j import Driver, GraphDatabase


def get_env(name: str, default: str) -> str:
    value = os.getenv(name, default).strip()
    return value or default


def clear_database(driver: Driver, database: str) -> None:
    with driver.session(database=database) as session:
        session.run('MATCH (n) DETACH DELETE n').consume()


def create_constraints(driver: Driver, database: str) -> None:
    labels = ['Site', 'Facility', 'Infrastrcture']
    with driver.session(database=database) as session:
        for label in labels:
            session.run(
                f'CREATE CONSTRAINT {label.lower()}_id_unique IF NOT EXISTS '
                f'FOR (n:{label}) REQUIRE n.id IS UNIQUE'
            ).consume()


def seed_test_graph(driver: Driver, database: str) -> None:
    with driver.session(database=database) as session:
        session.run(
            '''
            MERGE (sa:Site {id: 'site_a'})
            SET sa.name = 'Site A'
            MERGE (sb:Site {id: 'site_b'})
            SET sb.name = 'Site B'
            MERGE (fa:Facility {id: 'facility_a'})
            SET fa.name = 'Facility A'
            MERGE (i1:Infrastrcture {id: 'infra_a'})
            SET i1.name = 'Infrastructure A'
            MERGE (sa)-[:CONTAINES]->(fa)
            MERGE (fa)-[:INTERCHANGEABLE]->(sb)
            MERGE (fa)-[:DEPENDENCY]->(i1)
            '''
        ).consume()


def print_counts(driver: Driver, database: str) -> None:
    checks = {
        'Site': 'MATCH (n:Site) RETURN count(n) AS c',
        'Facility': 'MATCH (n:Facility) RETURN count(n) AS c',
        'Infrastrcture': 'MATCH (n:Infrastrcture) RETURN count(n) AS c',
        'CONTAINES': 'MATCH ()-[r:CONTAINES]->() RETURN count(r) AS c',
        'INTERCHANGEABLE': 'MATCH ()-[r:INTERCHANGEABLE]->() RETURN count(r) AS c',
        'DEPENDENCY': 'MATCH ()-[r:DEPENDENCY]->() RETURN count(r) AS c',
    }
    with driver.session(database=database) as session:
        for key, query in checks.items():
            record = session.run(query).single()
            print(f'- {key}: {int(record["c"]) if record else 0}')


def main() -> None:
    load_dotenv()
    uri = get_env('NEO4J_URI', 'bolt://localhost:7687')
    user = get_env('NEO4J_USER', 'neo4j')
    password = get_env('NEO4J_PASSWORD', 'password')
    database = get_env('NEO4J_DATABASE', 'neo4j')

    driver = GraphDatabase.driver(uri, auth=(user, password))
    try:
        clear_database(driver, database)
        create_constraints(driver, database)
        seed_test_graph(driver, database)
        print('Seeded Site/Facility INTERCHANGEABLE test graph.')
        print_counts(driver, database)
    finally:
        driver.close()


if __name__ == '__main__':
    main()
