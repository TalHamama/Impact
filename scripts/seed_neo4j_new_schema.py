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
        'ResponsibleBody',
        'System',
        'Effort',
        'Component',
        'Infrastructure',
        'Fuel',
        'Electricity',
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
            'id': 'site_north',
            'name': 'Northern Air Defense Site',
            'polygon': 'POLYGON((34.8040 32.1130,34.8090 32.1130,34.8090 32.1170,34.8040 32.1170,34.8040 32.1130))',
            'category': 'Air Defense',
            'defence_with_iron_dome': True,
            'level_for_defence_with_upper_layer': 'High',
        },
        {
            'id': 'site_central',
            'name': 'Central Logistics Site',
            'polygon': 'POLYGON((34.7800 32.0530,34.7850 32.0530,34.7850 32.0570,34.7800 32.0570,34.7800 32.0530))',
            'category': 'Logistics',
            'defence_with_iron_dome': False,
            'level_for_defence_with_upper_layer': 'Medium',
        },
    ]

    facilities = [
        {
            'id': 'facility_north_command',
            'name': 'North Command Facility',
            'details_on_facility_purpose': 'Coordinates interception and early warning operations.',
            'operational_significance_if_damaged': 'Degrades regional command and control response times.',
            'sop_if_hit': 'Shift command to backup facility and activate remote crews.',
        },
        {
            'id': 'facility_north_backup',
            'name': 'North Backup Facility',
            'details_on_facility_purpose': 'Backup command post for northern sector operations.',
            'operational_significance_if_damaged': 'Reduces continuity options during a primary facility outage.',
            'sop_if_hit': 'Move to mobile command shelter and reroute communications.',
        },
        {
            'id': 'facility_central_power',
            'name': 'Central Power Control Facility',
            'details_on_facility_purpose': 'Oversees energy distribution and utility coordination.',
            'operational_significance_if_damaged': 'Interrupts power monitoring and infrastructure recovery planning.',
            'sop_if_hit': 'Transfer supervision to reserve operators and manual monitoring.',
        },
    ]

    responsible_bodies = [
        {'id': 'rb_air_defense', 'name': 'Air Defense Directorate'},
        {'id': 'rb_energy_ops', 'name': 'Energy Operations Division'},
    ]

    systems = [
        {'id': 'system_skynet', 'name': 'Sky Shield'},
        {'id': 'system_gridwatch', 'name': 'Grid Watch'},
    ]

    efforts = [
        {'id': 'effort_alerting', 'name': 'Alerting Effort'},
        {'id': 'effort_recovery', 'name': 'Recovery Effort'},
    ]

    components = [
        {
            'id': 'component_radar',
            'name': 'Radar Controller',
            'migon': 'Sheltered',
            'hastara': 'Protected',
            'recovery_capability': 'High',
            'recovery_capability_details': 'Can be restored within hours using spare controller stock.',
        },
        {
            'id': 'component_comms',
            'name': 'Communications Rack',
            'migon': 'Partial',
            'hastara': 'Semi-Protected',
            'recovery_capability': 'Medium',
            'recovery_capability_details': 'Requires replacement modules and field technician support.',
        },
        {
            'id': 'component_switchgear',
            'name': 'Switchgear Cabinet',
            'migon': 'Sheltered',
            'hastara': 'Protected',
            'recovery_capability': 'Medium',
            'recovery_capability_details': 'Restoration depends on available spare breakers and inspection.',
        },
    ]

    infrastructures = [
        {
            'id': 'infra_north_grid',
            'name': 'Northern Utility Grid',
            'polygon': 'POLYGON((34.8110 32.1060,34.8160 32.1060,34.8160 32.1100,34.8110 32.1100,34.8110 32.1060))',
            'extra_labels': ['Electricity'],
        },
        {
            'id': 'infra_central_fuel_farm',
            'name': 'Central Fuel Farm',
            'polygon': 'POLYGON((34.7600 32.0700,34.7640 32.0700,34.7640 32.0730,34.7600 32.0730,34.7600 32.0700))',
            'extra_labels': ['Fuel'],
        },
    ]

    with driver.session(database=database) as session:
        session.run(
            '''
            UNWIND $rows AS row
            MERGE (n:Site {id: row.id})
            SET n.name = row.name,
                n.polygon = row.polygon,
                n.category = row.category,
                n.defence_with_iron_dome = row.defence_with_iron_dome,
                n.level_for_defence_with_upper_layer = row.level_for_defence_with_upper_layer
            ''',
            rows=sites,
        ).consume()
        session.run(
            '''
            UNWIND $rows AS row
            MERGE (n:Facility {id: row.id})
            SET n.name = row.name,
                n.details_on_facility_purpose = row.details_on_facility_purpose,
                n.operational_significance_if_damaged = row.operational_significance_if_damaged,
                n.sop_if_hit = row.sop_if_hit
            ''',
            rows=facilities,
        ).consume()
        session.run(
            '''
            UNWIND $rows AS row
            MERGE (n:ResponsibleBody {id: row.id})
            SET n.name = row.name
            ''',
            rows=responsible_bodies,
        ).consume()
        session.run(
            '''
            UNWIND $rows AS row
            MERGE (n:System {id: row.id})
            SET n.name = row.name
            ''',
            rows=systems,
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
            MERGE (n:Component {id: row.id})
            SET n.name = row.name,
                n.migon = row.migon,
                n.hastara = row.hastara,
                n.recovery_capability = row.recovery_capability,
                n.recovery_capability_details = row.recovery_capability_details
            ''',
            rows=components,
        ).consume()
        session.run(
            '''
            UNWIND $rows AS row
            MERGE (n:Infrastructure {id: row.id})
            SET n.name = row.name,
                n.polygon = row.polygon
            ''',
            rows=infrastructures,
        ).consume()
        session.run(
            '''
            UNWIND $rows AS row
            MATCH (n:Infrastructure {id: row.id})
            FOREACH (_ IN CASE WHEN 'Fuel' IN row.extra_labels THEN [1] ELSE [] END | SET n:Fuel)
            FOREACH (_ IN CASE WHEN 'Electricity' IN row.extra_labels THEN [1] ELSE [] END | SET n:Electricity)
            ''',
            rows=infrastructures,
        ).consume()


def seed_relationships(driver: Driver, database: str) -> None:
    with driver.session(database=database) as session:
        session.run(
            '''
            MATCH (siteNorth:Site {id: 'site_north'})
            MATCH (siteCentral:Site {id: 'site_central'})
            MATCH (northCommand:Facility {id: 'facility_north_command'})
            MATCH (northBackup:Facility {id: 'facility_north_backup'})
            MATCH (centralPower:Facility {id: 'facility_central_power'})
            MATCH (northGrid:Infrastructure {id: 'infra_north_grid'})
            MATCH (centralFuelFarm:Infrastructure {id: 'infra_central_fuel_farm'})
            MATCH (airDefense:ResponsibleBody {id: 'rb_air_defense'})
            MATCH (energyOps:ResponsibleBody {id: 'rb_energy_ops'})
            MATCH (skyShield:System {id: 'system_skynet'})
            MATCH (gridWatch:System {id: 'system_gridwatch'})
            MATCH (radar:Component {id: 'component_radar'})
            MATCH (comms:Component {id: 'component_comms'})
            MATCH (switchgear:Component {id: 'component_switchgear'})
            MATCH (alerting:Effort {id: 'effort_alerting'})
            MATCH (recovery:Effort {id: 'effort_recovery'})
            MERGE (northBackup)-[:BACKUP_FOR]->(siteNorth)
            MERGE (siteNorth)-[:CONTAINS]->(northCommand)
            MERGE (siteNorth)-[:CONTAINS]->(northBackup)
            MERGE (siteCentral)-[:CONTAINS]->(centralPower)

            MERGE (northCommand)-[:DEPENDS]->(northGrid)
            MERGE (northBackup)-[:DEPENDS]->(northGrid)
            MERGE (centralPower)-[:DEPENDS]->(centralFuelFarm)

            MERGE (northCommand)-[:RESPONSIBLE_FOR]->(airDefense)
            MERGE (northBackup)-[:RESPONSIBLE_FOR]->(airDefense)
            MERGE (centralPower)-[:RESPONSIBLE_FOR]->(energyOps)

            MERGE (northCommand)-[:PART_OF_SYSTEM]->(skyShield)
            MERGE (northBackup)-[:PART_OF_SYSTEM]->(skyShield)
            MERGE (centralPower)-[:PART_OF_SYSTEM]->(gridWatch)

            MERGE (northCommand)-[:CONTAINS]->(radar)
            MERGE (northCommand)-[:CONTAINS]->(comms)
            MERGE (centralPower)-[:CONTAINS]->(switchgear)

            MERGE (radar)-[:SUPPORT]->(alerting)
            MERGE (comms)-[:SUPPORT]->(alerting)
            MERGE (switchgear)-[:SUPPORT]->(recovery)
            '''
        ).consume()


def print_counts(driver: Driver, database: str) -> None:
    checks = {
        'Site': 'MATCH (n:Site) RETURN count(n) AS c',
        'Facility': 'MATCH (n:Facility) RETURN count(n) AS c',
        'ResponsibleBody': 'MATCH (n:ResponsibleBody) RETURN count(n) AS c',
        'System': 'MATCH (n:System) RETURN count(n) AS c',
        'Effort': 'MATCH (n:Effort) RETURN count(n) AS c',
        'Component': 'MATCH (n:Component) RETURN count(n) AS c',
        'Infrastructure': 'MATCH (n:Infrastructure) RETURN count(n) AS c',
        'Fuel': 'MATCH (n:Infrastructure:Fuel) RETURN count(n) AS c',
        'Electricity': 'MATCH (n:Infrastructure:Electricity) RETURN count(n) AS c',
        'AllRelationships': 'MATCH ()-[r]->() RETURN count(r) AS c',
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
        print('Neo4j new-schema seed completed.')
        print_counts(driver, database)
    finally:
        driver.close()


if __name__ == '__main__':
    main()
