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
    labels = [
        'Site',
        'Facility',
        'Componenet',
        'Infrastrcture',
        'Effort',
        'Report',
        'Maintenance',
    ]
    with driver.session(database=database) as session:
        for label in labels:
            session.run(
                f'CREATE CONSTRAINT {label.lower()}_id_unique IF NOT EXISTS '
                f'FOR (n:{label}) REQUIRE n.id IS UNIQUE'
            ).consume()


def seed_nodes(driver: Driver, database: str) -> None:
    sites = [
        {
            'id': 's1',
            'name': 'Site North',
            'polygon': 'POLYGON((34.8040 32.1130,34.8090 32.1130,34.8090 32.1170,34.8040 32.1170,34.8040 32.1130))',
        },
        {
            'id': 's2',
            'name': 'Site South',
            'polygon': 'POLYGON((34.7800 32.0530,34.7850 32.0530,34.7850 32.0570,34.7800 32.0570,34.7800 32.0530))',
        },
        {
            'id': 's3',
            'name': 'Site East Mini',
            'polygon': 'POLYGON((34.8700 32.0880,34.8740 32.0880,34.8740 32.0910,34.8700 32.0910,34.8700 32.0880))',
        },
        {
            'id': 's4',
            'name': 'Site West Mini',
            'polygon': 'POLYGON((34.7480 32.0840,34.7520 32.0840,34.7520 32.0870,34.7480 32.0870,34.7480 32.0840))',
        },
    ]
    facilities = [
        {'id': 'f1', 'name': 'Facility Alpha'},
        {'id': 'f2', 'name': 'Facility Bravo'},
        {'id': 'f3', 'name': 'Facility Gamma'},
        {'id': 'f4', 'name': 'Facility Delta'},
    ]
    components = [
        {'id': 'c1', 'name': 'Main Sensor'},
        {'id': 'c2', 'name': 'Backup Sensor'},
        {'id': 'c3', 'name': 'Mini Gateway'},
        {'id': 'c4', 'name': 'Mini Controller'},
    ]
    infrastructures = [
        {
            'id': 'i1',
            'name': 'Infrastructure Core',
            'polygon': 'POLYGON((34.8110 32.1060,34.8160 32.1060,34.8160 32.1100,34.8110 32.1100,34.8110 32.1060))',
        },
        {
            'id': 'i2',
            'name': 'Infrastructure Mini Ring',
            'polygon': 'POLYGON((34.7600 32.0700,34.7640 32.0700,34.7640 32.0730,34.7600 32.0730,34.7600 32.0700))',
        },
    ]
    efforts = [
        {'id': 'e1', 'name': 'Reliability Effort'},
        {'id': 'e2', 'name': 'Mini Optimization Effort'},
    ]
    reports = [
        {'id': 'r1', 'name': 'North Weekly Report'},
        {'id': 'r2', 'name': 'Mini Cluster Report'},
    ]
    maintenance = [
        {'id': 'm1', 'name': 'Sensor Maintenance Task'},
        {'id': 'm2', 'name': 'Mini Cluster Maintenance'},
    ]

    with driver.session(database=database) as session:
        session.run(
            '''
            UNWIND $rows AS row
            MERGE (n:Site {id: row.id})
            SET n.name = row.name, n.polygon = row.polygon
            ''',
            rows=sites,
        ).consume()
        session.run(
            '''
            UNWIND $rows AS row
            MERGE (n:Facility {id: row.id})
            SET n.name = row.name
            ''',
            rows=facilities,
        ).consume()
        session.run(
            '''
            UNWIND $rows AS row
            MERGE (n:Componenet {id: row.id})
            SET n.name = row.name
            ''',
            rows=components,
        ).consume()
        session.run(
            '''
            UNWIND $rows AS row
            MERGE (n:Infrastrcture {id: row.id})
            SET n.name = row.name, n.polygon = row.polygon
            ''',
            rows=infrastructures,
        ).consume()
        session.run(
            '''
            UNWIND $rows AS row
            MERGE (n:Effort {id: row.id})
            SET n.name = row.name
            ''',
            rows=efforts,
        ).consume()
        session.run(
            '''
            UNWIND $rows AS row
            MERGE (n:Report {id: row.id})
            SET n.name = row.name
            ''',
            rows=reports,
        ).consume()
        session.run(
            '''
            UNWIND $rows AS row
            MERGE (n:Maintenance {id: row.id})
            SET n.name = row.name
            ''',
            rows=maintenance,
        ).consume()


def seed_relationships(driver: Driver, database: str) -> None:
    with driver.session(database=database) as session:
        session.run(
            '''
            MATCH (s1:Site {id: 's1'})
            MATCH (s2:Site {id: 's2'})
            MATCH (i1:Infrastrcture {id: 'i1'})
            MATCH (f1:Facility {id: 'f1'})
            MATCH (f2:Facility {id: 'f2'})
            MATCH (c1:Componenet {id: 'c1'})
            MATCH (c2:Componenet {id: 'c2'})
            MATCH (e1:Effort {id: 'e1'})
            MATCH (r1:Report {id: 'r1'})
            MATCH (m1:Maintenance {id: 'm1'})
            MERGE (s1)-[:DEPENDENCY]->(i1)
            MERGE (s2)-[:DEPENDENCY]->(i1)
            MERGE (s1)-[:CONTAINES]->(f1)
            MERGE (s2)-[:CONTAINES]->(f2)
            MERGE (f1)-[:CONTAINES]->(c1)
            MERGE (f2)-[:CONTAINES]->(c2)
            MERGE (c1)-[:INTERCHANGEABLE]-(s1)
            MERGE (c1)-[:INTERCHANGEABLE]-(s2)
            MERGE (c2)-[:INTERCHANGEABLE]-(s2)
            MERGE (c1)-[:INFLUENCE]->(e1)
            MERGE (s1)-[:HAS_REPORT]->(r1)
            MERGE (s1)-[:HAS_MAINTENANCE]->(m1)
            '''
        ).consume()
        session.run(
            '''
            MATCH (s3:Site {id: 's3'})
            MATCH (s4:Site {id: 's4'})
            MATCH (i2:Infrastrcture {id: 'i2'})
            MATCH (f3:Facility {id: 'f3'})
            MATCH (f4:Facility {id: 'f4'})
            MATCH (c3:Componenet {id: 'c3'})
            MATCH (c4:Componenet {id: 'c4'})
            MATCH (e2:Effort {id: 'e2'})
            MATCH (r2:Report {id: 'r2'})
            MATCH (m2:Maintenance {id: 'm2'})
            MERGE (s3)-[:DEPENDENCY]->(i2)
            MERGE (s4)-[:DEPENDENCY]->(i2)
            MERGE (s3)-[:CONTAINES]->(f3)
            MERGE (s4)-[:CONTAINES]->(f4)
            MERGE (f3)-[:CONTAINES]->(c3)
            MERGE (f4)-[:CONTAINES]->(c4)
            MERGE (c3)-[:INTERCHANGEABLE]-(s3)
            MERGE (c3)-[:INTERCHANGEABLE]-(s4)
            MERGE (c4)-[:INTERCHANGEABLE]-(s4)
            MERGE (c3)-[:INFLUENCE]->(e2)
            MERGE (s3)-[:HAS_REPORT]->(r2)
            MERGE (s3)-[:HAS_MAINTENANCE]->(m2)
            '''
        ).consume()


def verify_trees_are_disconnected(driver: Driver, database: str) -> None:
    query = '''
    MATCH (a)-[r]-(b)
    WHERE a.id IN ['s1','s2','i1','f1','f2','c1','c2','e1','r1','m1']
      AND b.id IN ['s3','s4','i2','f3','f4','c3','c4','e2','r2','m2']
    RETURN count(r) AS c
    '''
    with driver.session(database=database) as session:
        record = session.run(query).single()
        cross_tree_relationships = int(record['c']) if record else 0
        if cross_tree_relationships != 0:
            raise RuntimeError(
                f'Seed validation failed: found {cross_tree_relationships} cross-tree relationship(s).'
            )


def print_counts(driver: Driver, database: str) -> None:
    checks = {
        'Site': 'MATCH (n:Site) RETURN count(n) AS c',
        'Infrastrcture': 'MATCH (n:Infrastrcture) RETURN count(n) AS c',
        'Facility': 'MATCH (n:Facility) RETURN count(n) AS c',
        'Componenet': 'MATCH (n:Componenet) RETURN count(n) AS c',
        'Effort': 'MATCH (n:Effort) RETURN count(n) AS c',
        'Report': 'MATCH (n:Report) RETURN count(n) AS c',
        'Maintenance': 'MATCH (n:Maintenance) RETURN count(n) AS c',
        'AllRelationships': 'MATCH ()-[r]-() RETURN count(r) AS c',
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
        seed_nodes(driver, database)
        seed_relationships(driver, database)
        verify_trees_are_disconnected(driver, database)
        print('Neo4j small seed completed.')
        print_counts(driver, database)
    finally:
        driver.close()


if __name__ == '__main__':
    main()
