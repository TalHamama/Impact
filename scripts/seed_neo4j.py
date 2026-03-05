import os

from dotenv import load_dotenv
from neo4j import Driver, GraphDatabase


def get_env(name: str, default: str) -> str:
    value = os.getenv(name, default).strip()
    return value or default


def create_constraints(driver: Driver, database: str) -> None:
    labels = ['Site', 'Facility', 'Componenet', 'Effort', 'Infrastrcture']
    with driver.session(database=database) as session:
        for label in labels:
            session.run(
                f'CREATE CONSTRAINT {label.lower()}_id_unique IF NOT EXISTS '
                f'FOR (n:{label}) REQUIRE n.id IS UNIQUE'
            ).consume()


def seed_nodes(driver: Driver, database: str) -> None:
    sites = [
        {'id': 's1', 'name': 'Site North', 'polygon': 'POLYGON((34.8040 32.1130,34.8090 32.1130,34.8090 32.1170,34.8040 32.1170,34.8040 32.1130))'},
        {'id': 's2', 'name': 'Site South', 'polygon': 'POLYGON((34.7800 32.0530,34.7850 32.0530,34.7850 32.0570,34.7800 32.0570,34.7800 32.0530))'},
        {'id': 's3', 'name': 'Site East', 'polygon': 'POLYGON((34.8700 32.0880,34.8750 32.0880,34.8750 32.0920,34.8700 32.0920,34.8700 32.0880))'},
        {'id': 's4', 'name': 'Site West', 'polygon': 'POLYGON((34.7480 32.0840,34.7530 32.0840,34.7530 32.0880,34.7480 32.0880,34.7480 32.0840))'},
        {'id': 's5', 'name': 'Site Center', 'polygon': 'POLYGON((34.7890 32.0730,34.7940 32.0730,34.7940 32.0770,34.7890 32.0770,34.7890 32.0730))'},
        {'id': 's6', 'name': 'Site Harbor', 'polygon': 'POLYGON((34.7550 32.0440,34.7600 32.0440,34.7600 32.0480,34.7550 32.0480,34.7550 32.0440))'},
    ]

    facilities = [
        {'id': 'f1', 'name': 'Facility Alpha', 'gold_fields': ['priority', 'backup_power']},
        {'id': 'f2', 'name': 'Facility Bravo', 'gold_fields': ['redundant_links']},
        {'id': 'f3', 'name': 'Facility Charlie', 'gold_fields': ['secure_zone', 'ops_center']},
        {'id': 'f4', 'name': 'Facility Delta', 'gold_fields': ['high_capacity']},
        {'id': 'f5', 'name': 'Facility Echo', 'gold_fields': ['disaster_ready']},
        {'id': 'f6', 'name': 'Facility Foxtrot', 'gold_fields': ['priority', 'rapid_response']},
    ]

    componenets = [
        {'id': 'c1', 'name': 'Pump Controller'},
        {'id': 'c2', 'name': 'Power Switchboard'},
        {'id': 'c3', 'name': 'Cooling Unit'},
        {'id': 'c4', 'name': 'Gateway Router'},
        {'id': 'c5', 'name': 'Camera System'},
        {'id': 'c6', 'name': 'Main Sensor'},
        {'id': 'c7', 'name': 'Backup Sensor'},
        {'id': 'c8', 'name': 'Valve Cluster'},
        {'id': 'c9', 'name': 'Pressure Regulator'},
        {'id': 'c10', 'name': 'Firewall Unit'},
        {'id': 'c11', 'name': 'Signal Amplifier'},
        {'id': 'c12', 'name': 'Storage Controller'},
    ]

    efforts = [
        {'id': 'e1', 'name': 'Stability Effort'},
        {'id': 'e2', 'name': 'Security Effort'},
        {'id': 'e3', 'name': 'Power Effort'},
        {'id': 'e4', 'name': 'Water Effort'},
        {'id': 'e5', 'name': 'Communications Effort'},
        {'id': 'e6', 'name': 'Resilience Effort'},
        {'id': 'e7', 'name': 'Maintenance Effort'},
        {'id': 'e8', 'name': 'Optimization Effort'},
    ]

    infrastrctures = [
        {'id': 'i1', 'name': 'Infrastructure North', 'polygon': 'POLYGON((34.8110 32.1060,34.8160 32.1060,34.8160 32.1100,34.8110 32.1100,34.8110 32.1060))'},
        {'id': 'i2', 'name': 'Infrastructure South', 'polygon': 'POLYGON((34.7720 32.0600,34.7770 32.0600,34.7770 32.0640,34.7720 32.0640,34.7720 32.0600))'},
        {'id': 'i3', 'name': 'Infrastructure East', 'polygon': 'POLYGON((34.8560 32.0840,34.8610 32.0840,34.8610 32.0880,34.8560 32.0880,34.8560 32.0840))'},
        {'id': 'i4', 'name': 'Infrastructure West', 'polygon': 'POLYGON((34.7420 32.0750,34.7470 32.0750,34.7470 32.0790,34.7420 32.0790,34.7420 32.0750))'},
        {'id': 'i5', 'name': 'Infrastructure Center', 'polygon': 'POLYGON((34.7910 32.0810,34.7960 32.0810,34.7960 32.0850,34.7910 32.0850,34.7910 32.0810))'},
        {'id': 'i6', 'name': 'Infrastructure Harbor', 'polygon': 'POLYGON((34.7670 32.0490,34.7720 32.0490,34.7720 32.0530,34.7670 32.0530,34.7670 32.0490))'},
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
            SET n.name = row.name, n.gold_fields = row.gold_fields
            ''',
            rows=facilities,
        ).consume()
        session.run(
            '''
            UNWIND $rows AS row
            MERGE (n:Componenet {id: row.id})
            SET n.name = row.name
            ''',
            rows=componenets,
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
            MERGE (n:Infrastrcture {id: row.id})
            SET n.name = row.name, n.polygon = row.polygon
            ''',
            rows=infrastrctures,
        ).consume()


def seed_relationships(driver: Driver, database: str) -> None:
    dependency = [
        {'from_id': 's1', 'to_id': 'i1'},
        {'from_id': 's1', 'to_id': 'i2'},
        {'from_id': 's2', 'to_id': 'i2'},
        {'from_id': 's2', 'to_id': 'i3'},
        {'from_id': 's3', 'to_id': 'i3'},
        {'from_id': 's3', 'to_id': 'i4'},
        {'from_id': 's4', 'to_id': 'i4'},
        {'from_id': 's4', 'to_id': 'i5'},
        {'from_id': 's5', 'to_id': 'i5'},
        {'from_id': 's5', 'to_id': 'i6'},
        {'from_id': 's6', 'to_id': 'i1'},
        {'from_id': 's6', 'to_id': 'i6'},
    ]
    interchangeable = [
        {'from_id': 'f1', 'to_id': 's1'},
        {'from_id': 'f1', 'to_id': 's2'},
        {'from_id': 'f2', 'to_id': 's2'},
        {'from_id': 'f2', 'to_id': 's3'},
        {'from_id': 'f3', 'to_id': 's3'},
        {'from_id': 'f3', 'to_id': 's4'},
        {'from_id': 'f4', 'to_id': 's4'},
        {'from_id': 'f4', 'to_id': 's5'},
        {'from_id': 'f5', 'to_id': 's5'},
        {'from_id': 'f5', 'to_id': 's6'},
        {'from_id': 'f6', 'to_id': 's1'},
        {'from_id': 'f6', 'to_id': 's6'},
    ]
    influence = [
        {'from_id': 'c1', 'to_id': 'e1'},
        {'from_id': 'c1', 'to_id': 'e2'},
        {'from_id': 'c2', 'to_id': 'e2'},
        {'from_id': 'c2', 'to_id': 'e3'},
        {'from_id': 'c3', 'to_id': 'e3'},
        {'from_id': 'c3', 'to_id': 'e4'},
        {'from_id': 'c4', 'to_id': 'e4'},
        {'from_id': 'c4', 'to_id': 'e5'},
        {'from_id': 'c5', 'to_id': 'e5'},
        {'from_id': 'c5', 'to_id': 'e6'},
        {'from_id': 'c6', 'to_id': 'e6'},
        {'from_id': 'c6', 'to_id': 'e7'},
        {'from_id': 'c7', 'to_id': 'e7'},
        {'from_id': 'c7', 'to_id': 'e8'},
        {'from_id': 'c8', 'to_id': 'e8'},
        {'from_id': 'c8', 'to_id': 'e1'},
        {'from_id': 'c9', 'to_id': 'e1'},
        {'from_id': 'c9', 'to_id': 'e2'},
        {'from_id': 'c10', 'to_id': 'e2'},
        {'from_id': 'c10', 'to_id': 'e3'},
        {'from_id': 'c11', 'to_id': 'e3'},
        {'from_id': 'c11', 'to_id': 'e4'},
        {'from_id': 'c12', 'to_id': 'e4'},
        {'from_id': 'c12', 'to_id': 'e5'},
    ]
    connection = [
        {'from_id': 'i1', 'to_id': 'i2'},
        {'from_id': 'i2', 'to_id': 'i3'},
        {'from_id': 'i3', 'to_id': 'i4'},
        {'from_id': 'i4', 'to_id': 'i5'},
        {'from_id': 'i5', 'to_id': 'i6'},
        {'from_id': 'i6', 'to_id': 'i1'},
        {'from_id': 'i1', 'to_id': 'i4'},
        {'from_id': 'i2', 'to_id': 'i5'},
        {'from_id': 'i3', 'to_id': 'i6'},
    ]
    site_containes = [
        {'from_id': 's1', 'to_id': 'f1'},
        {'from_id': 's2', 'to_id': 'f2'},
        {'from_id': 's3', 'to_id': 'f3'},
        {'from_id': 's4', 'to_id': 'f4'},
        {'from_id': 's5', 'to_id': 'f5'},
        {'from_id': 's6', 'to_id': 'f6'},
    ]
    facility_containes = [
        {'from_id': 'f1', 'to_id': 'c1'},
        {'from_id': 'f1', 'to_id': 'c2'},
        {'from_id': 'f2', 'to_id': 'c3'},
        {'from_id': 'f2', 'to_id': 'c4'},
        {'from_id': 'f3', 'to_id': 'c5'},
        {'from_id': 'f3', 'to_id': 'c6'},
        {'from_id': 'f4', 'to_id': 'c7'},
        {'from_id': 'f4', 'to_id': 'c8'},
        {'from_id': 'f5', 'to_id': 'c9'},
        {'from_id': 'f5', 'to_id': 'c10'},
        {'from_id': 'f6', 'to_id': 'c11'},
        {'from_id': 'f6', 'to_id': 'c12'},
    ]

    with driver.session(database=database) as session:
        # Remove old relation naming to keep schema consistent.
        session.run('MATCH ()-[r:CONTAINS]-() DELETE r').consume()

        session.run(
            '''
            UNWIND $rows AS row
            MATCH (a:Site {id: row.from_id})
            MATCH (b:Infrastrcture {id: row.to_id})
            MERGE (a)-[r:DEPENDENCY]->(b)
            SET r.updated_at = datetime()
            ''',
            rows=dependency,
        ).consume()
        session.run(
            '''
            UNWIND $rows AS row
            MATCH (a:Facility {id: row.from_id})
            MATCH (b:Site {id: row.to_id})
            MERGE (a)-[r:INTERCHANGEABLE]-(b)
            SET r.updated_at = datetime()
            ''',
            rows=interchangeable,
        ).consume()
        session.run(
            '''
            UNWIND $rows AS row
            MATCH (a:Componenet {id: row.from_id})
            MATCH (b:Effort {id: row.to_id})
            MERGE (a)-[r:INFLUENCE]->(b)
            SET r.updated_at = datetime()
            ''',
            rows=influence,
        ).consume()
        session.run(
            '''
            UNWIND $rows AS row
            MATCH (a:Infrastrcture {id: row.from_id})
            MATCH (b:Infrastrcture {id: row.to_id})
            MERGE (a)-[r:CONNECTION]-(b)
            SET r.updated_at = datetime()
            ''',
            rows=connection,
        ).consume()
        session.run(
            '''
            UNWIND $rows AS row
            MATCH (a:Site {id: row.from_id})
            MATCH (b:Facility {id: row.to_id})
            MERGE (a)-[r:CONTAINES]->(b)
            SET r.updated_at = datetime()
            ''',
            rows=site_containes,
        ).consume()
        session.run(
            '''
            UNWIND $rows AS row
            MATCH (a:Facility {id: row.from_id})
            MATCH (b:Componenet {id: row.to_id})
            MERGE (a)-[r:CONTAINES]->(b)
            SET r.updated_at = datetime()
            ''',
            rows=facility_containes,
        ).consume()


def verify_counts(driver: Driver, database: str) -> dict[str, int]:
    checks: dict[str, str] = {
        'Site': 'MATCH (n:Site) RETURN count(n) AS c',
        'Facility': 'MATCH (n:Facility) RETURN count(n) AS c',
        'Componenet': 'MATCH (n:Componenet) RETURN count(n) AS c',
        'Effort': 'MATCH (n:Effort) RETURN count(n) AS c',
        'Infrastrcture': 'MATCH (n:Infrastrcture) RETURN count(n) AS c',
        'DEPENDENCY': 'MATCH ()-[r:DEPENDENCY]-() RETURN count(r) AS c',
        'INTERCHANGEABLE': 'MATCH ()-[r:INTERCHANGEABLE]-() RETURN count(r) AS c',
        'INFLUENCE': 'MATCH ()-[r:INFLUENCE]-() RETURN count(r) AS c',
        'CONNECTION': 'MATCH ()-[r:CONNECTION]-() RETURN count(r) AS c',
        'CONTAINES': 'MATCH ()-[r:CONTAINES]-() RETURN count(r) AS c',
        'CONTAINES_SITE_FACILITY': 'MATCH (:Site)-[r:CONTAINES]->(:Facility) RETURN count(r) AS c',
        'CONTAINES_FACILITY_COMPONENT': 'MATCH (:Facility)-[r:CONTAINES]->(:Componenet) RETURN count(r) AS c',
    }
    output: dict[str, int] = {}
    with driver.session(database=database) as session:
        for key, query in checks.items():
            record = session.run(query).single()
            output[key] = int(record['c']) if record is not None else 0
    return output


def verify_facilities_contained(driver: Driver, database: str) -> None:
    query = '''
    MATCH (f:Facility)
    WHERE NOT EXISTS { MATCH (:Site)-[:CONTAINES]->(f) }
    RETURN count(f) AS c
    '''
    with driver.session(database=database) as session:
        record = session.run(query).single()
        unattached = int(record['c']) if record is not None else 0
        if unattached > 0:
            raise RuntimeError(f'Seed validation failed: {unattached} Facility node(s) are not attached to a Site via CONTAINS.')


def main() -> None:
    load_dotenv()

    uri = get_env('NEO4J_URI', 'bolt://localhost:7687')
    user = get_env('NEO4J_USER', 'neo4j')
    password = get_env('NEO4J_PASSWORD', 'password')
    database = get_env('NEO4J_DATABASE', 'neo4j')

    driver = GraphDatabase.driver(uri, auth=(user, password))
    try:
        create_constraints(driver=driver, database=database)
        seed_nodes(driver=driver, database=database)
        seed_relationships(driver=driver, database=database)
        verify_facilities_contained(driver=driver, database=database)
        counts = verify_counts(driver=driver, database=database)
    finally:
        driver.close()

    print('Neo4j seed completed successfully.')
    for key, value in counts.items():
        print(f'- {key}: {value}')


if __name__ == '__main__':
    main()
