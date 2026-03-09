from __future__ import annotations

from collections.abc import Generator
import re
from typing import Any

from neo4j import Driver, GraphDatabase
from neo4j.exceptions import Neo4jError

from app.utils.errors import DatabaseError, NotFoundError

SITE_NODE_LABEL = 'Site'
FACILITY_NODE_LABEL = 'Facility'
INFRASTRUCTURE_NODE_LABEL = 'Infrastructure'
COMPONENT_NODE_LABEL = 'Component'
SYSTEM_NODE_LABEL = 'System'
EFFORT_NODE_LABEL = 'Effort'
CONTAINS_RELATIONSHIP_TYPE = 'CONTAINS'
BACKUP_FOR_RELATIONSHIP_TYPE = 'BACKUP_FOR'
DEPENDS_RELATIONSHIP_TYPE = 'DEPENDS'
PART_OF_SYSTEM_RELATIONSHIP_TYPE = 'PART_OF_SYSTEM'
SUPPORT_RELATIONSHIP_TYPE = 'SUPPORT'
LINK_MAP_INCLUDED_NODE_LABELS = {
    SITE_NODE_LABEL,
    FACILITY_NODE_LABEL,
    COMPONENT_NODE_LABEL,
    EFFORT_NODE_LABEL,
}

SITE_AND_INFRASTRUCTURE_NODE_LABELS_CYPHER = (
    f"['{SITE_NODE_LABEL}', '{INFRASTRUCTURE_NODE_LABEL}']"
)
INFRASTRUCTURE_NODE_LABELS_CYPHER = f"['{INFRASTRUCTURE_NODE_LABEL}']"


class Neo4jDriver:
    _instance: Neo4jDriver | None = None

    def __init__(self, uri: str, user: str, password: str) -> None:
        self._driver: Driver = GraphDatabase.driver(uri, auth=(user, password))
        self._driver.verify_connectivity()

    @classmethod
    def init(cls, uri: str, user: str, password: str) -> Neo4jDriver:
        if cls._instance is None:
            cls._instance = cls(uri=uri, user=user, password=password)
        return cls._instance

    @classmethod
    def get_instance(cls) -> Neo4jDriver:
        if cls._instance is None:
            raise RuntimeError('Neo4jDriver is not initialized.')
        return cls._instance

    @property
    def driver(self) -> Driver:
        return self._driver

    @classmethod
    def close(cls) -> None:
        if cls._instance is not None:
            cls._instance._driver.close()
            cls._instance = None


def get_neo4j_driver() -> Generator[Driver, None, None]:
    yield Neo4jDriver.get_instance().driver


def fetch_relation_types(driver: Driver, database: str | None = None) -> list[str]:
    query = '''
    MATCH ()-[r]-()
    RETURN DISTINCT type(r) AS relationship_type
    ORDER BY relationship_type
    '''

    try:
        with driver.session(database=database) if database else driver.session() as session:
            return [
                record['relationship_type']
                for record in session.run(query)
                if record['relationship_type']
            ]
    except Neo4jError as exc:
        raise DatabaseError(
            message=str(exc) or 'Failed to query relation types from Neo4j.',
            details={
                'database': database,
                'neo4j_error': str(exc),
                'neo4j_code': getattr(exc, 'code', None),
            },
        ) from exc


def check_neo4j_ready(driver: Driver, database: str | None = None) -> bool:
    try:
        with driver.session(database=database) if database else driver.session() as session:
            record = session.run('RETURN 1 AS ok').single()
            return record is not None and record.get('ok') == 1
    except Neo4jError:
        return False


def fetch_entity_relationships(driver: Driver, entity_id: str, database: str | None = None) -> list[dict[str, Any]]:
    check_query = 'MATCH (n {id: $entity_id}) RETURN n LIMIT 1'
    links_query = '''
    MATCH (n {id: $entity_id})-[r]-(m)
    RETURN
      type(r) AS relationship_type,
      CASE
        WHEN startNode(r) = n THEN 'OUTGOING'
        ELSE 'INCOMING'
      END AS direction,
      m.id AS other_node_id,
      labels(m) AS other_node_labels,
      properties(m) AS other_node_properties,
      properties(r) AS relationship_properties
    '''

    try:
        with driver.session(database=database) if database else driver.session() as session:
            entity_exists = session.run(check_query, entity_id=entity_id).single()
            if entity_exists is None:
                raise NotFoundError(
                    message=f'Entity with id "{entity_id}" was not found.',
                    details={'entity_id': entity_id},
                )

            records = session.run(links_query, entity_id=entity_id)
            results: list[dict[str, Any]] = []

            for record in records:
                results.append(
                    {
                        'relationship_type': record['relationship_type'],
                        'direction': record['direction'],
                        'other_node': {
                            'id': record['other_node_id'],
                            'labels': record['other_node_labels'] or [],
                            'properties': _to_json_compatible(record['other_node_properties'] or {}),
                        },
                        'relationship_properties': _to_json_compatible(record['relationship_properties'] or {}),
                    }
                )

            return results
    except NotFoundError:
        raise
    except Neo4jError as exc:
        raise DatabaseError(
            message=str(exc) or 'Failed to query Neo4j.',
            details={
                'entity_id': entity_id,
                'database': database,
                'neo4j_error': str(exc),
                'neo4j_code': getattr(exc, 'code', None),
            },
        ) from exc


def fetch_graph_overview(driver: Driver, database: str | None = None) -> dict[str, Any]:
    relation_types_query = '''
    MATCH ()-[r]-()
    RETURN DISTINCT type(r) AS relationship_type
    ORDER BY relationship_type
    '''

    nodes_query = '''
    MATCH (n)
    OPTIONAL MATCH (n)-[r]-()
    WITH n, collect(DISTINCT type(r)) AS relation_types
    RETURN
      n.id AS node_id,
      labels(n) AS node_labels,
      n.name AS node_name,
      n.polygon AS node_polygon,
      properties(n) AS node_properties,
      relation_types
    ORDER BY coalesce(n.name, n.id, '')
    '''

    relations_query = '''
    MATCH (a)-[r]->(b)
    RETURN DISTINCT
      a.id AS source_id,
      b.id AS target_id,
      type(r) AS relationship_type,
      properties(r) AS relationship_properties
    ORDER BY relationship_type, source_id, target_id
    '''

    try:
        with driver.session(database=database) if database else driver.session() as session:
            relation_types = [
                record['relationship_type']
                for record in session.run(relation_types_query)
                if record['relationship_type']
            ]

            nodes: list[dict[str, Any]] = []
            for record in session.run(nodes_query):
                labels = record['node_labels'] or []
                props = record['node_properties'] or {}
                nodes.append(
                    {
                        'id': record['node_id'],
                        'label': labels[0] if labels else None,
                        'labels': labels,
                        'name': record['node_name'],
                        'location': record['node_polygon'],
                        'properties': _to_json_compatible(props),
                        'relationship_types': [rel for rel in (record['relation_types'] or []) if rel],
                    }
                )

            relations = [
                {
                    'source_id': record['source_id'],
                    'target_id': record['target_id'],
                    'relationship_type': record['relationship_type'],
                    'relationship_properties': _to_json_compatible(record['relationship_properties'] or {}),
                }
                for record in session.run(relations_query)
            ]

            return {
                'relation_types': relation_types,
                'nodes': nodes,
                'relations': relations,
            }
    except Neo4jError as exc:
        raise DatabaseError(
            message=str(exc) or 'Failed to query Neo4j overview.',
            details={
                'database': database,
                'neo4j_error': str(exc),
                'neo4j_code': getattr(exc, 'code', None),
            },
        ) from exc


def fetch_sites_infrastructures_with_links(driver: Driver, database: str | None = None) -> dict[str, Any]:
    nodes_query = f'''
    MATCH (n)
    WHERE any(label IN labels(n) WHERE label IN {SITE_AND_INFRASTRUCTURE_NODE_LABELS_CYPHER})
    RETURN
      n.id AS node_id,
      CASE
        WHEN '{SITE_NODE_LABEL}' IN labels(n) THEN '{SITE_NODE_LABEL}'
        ELSE '{INFRASTRUCTURE_NODE_LABEL}'
      END AS node_type,
      n.name AS node_name,
      n.polygon AS node_polygon
    ORDER BY coalesce(n.name, n.id, '')
    '''

    edges_query = f'''
    CALL () {{
      MATCH (a)-[r]-(b)
      WHERE any(label IN labels(a) WHERE label IN {SITE_AND_INFRASTRUCTURE_NODE_LABELS_CYPHER})
        AND any(label IN labels(b) WHERE label IN {SITE_AND_INFRASTRUCTURE_NODE_LABELS_CYPHER})
      RETURN DISTINCT
        startNode(r).id AS source_id,
        endNode(r).id AS target_id,
        type(r) AS relationship_type

      UNION

      MATCH (s1:{SITE_NODE_LABEL})-[:{CONTAINS_RELATIONSHIP_TYPE}]->(:{FACILITY_NODE_LABEL})-[:{BACKUP_FOR_RELATIONSHIP_TYPE}]->(s2:{SITE_NODE_LABEL})
      WITH
        CASE WHEN s1.id < s2.id THEN s1.id ELSE s2.id END AS source_id,
        CASE WHEN s1.id < s2.id THEN s2.id ELSE s1.id END AS target_id
      WHERE source_id IS NOT NULL AND target_id IS NOT NULL AND source_id <> target_id
      RETURN DISTINCT
        source_id,
        target_id,
        '{BACKUP_FOR_RELATIONSHIP_TYPE}' AS relationship_type

      UNION

      MATCH (s:{SITE_NODE_LABEL})-[:{CONTAINS_RELATIONSHIP_TYPE}]->(:{FACILITY_NODE_LABEL})-[:{DEPENDS_RELATIONSHIP_TYPE}]->(i)
      WHERE any(label IN labels(i) WHERE label IN {INFRASTRUCTURE_NODE_LABELS_CYPHER})
      RETURN DISTINCT
        s.id AS source_id,
        i.id AS target_id,
        '{DEPENDS_RELATIONSHIP_TYPE}' AS relationship_type
    }}
    RETURN DISTINCT source_id, target_id, relationship_type
    ORDER BY relationship_type, source_id, target_id
    '''

    try:
        with driver.session(database=database) if database else driver.session() as session:
            nodes = [
                {
                    'id': record['node_id'],
                    'node_type': record['node_type'],
                    'name': record['node_name'],
                    'polygon': record['node_polygon'],
                }
                for record in session.run(nodes_query)
            ]
            edges = [
                {
                    'source_id': record['source_id'],
                    'target_id': record['target_id'],
                    'relationship_type': record['relationship_type'],
                }
                for record in session.run(edges_query)
            ]
            return {'nodes': _to_json_compatible(nodes), 'edges': _to_json_compatible(edges)}
    except Neo4jError as exc:
        raise DatabaseError(
            message=str(exc) or f'Failed to query {SITE_NODE_LABEL}/{INFRASTRUCTURE_NODE_LABEL} links from Neo4j.',
            details={
                'database': database,
                'neo4j_error': str(exc),
                'neo4j_code': getattr(exc, 'code', None),
            },
        ) from exc


def fetch_sites_infrastructures_with_links_for_qlik(driver: Driver, database: str | None = None) -> dict[str, Any]:
    graph = fetch_sites_infrastructures_with_links(driver=driver, database=database)
    facilities = fetch_facilities_for_qlik(driver=driver, database=database)

    nodes = [
        {
            **node,
            **_build_qlik_polygon_fields(node.get('polygon')),
        }
        for node in graph.get('nodes', [])
    ]

    return {
        'nodes': _to_json_compatible(nodes),
        'edges': _to_json_compatible(graph.get('edges', [])),
        'facilities': _to_json_compatible(facilities),
    }


def fetch_facilities_for_qlik(driver: Driver, database: str | None = None) -> list[dict[str, Any]]:
    query = f'''
    MATCH (site:{SITE_NODE_LABEL})-[:{CONTAINS_RELATIONSHIP_TYPE}]->(facility:{FACILITY_NODE_LABEL})
    WITH DISTINCT site, facility

    CALL (facility) {{
      OPTIONAL MATCH (facility)-[:{PART_OF_SYSTEM_RELATIONSHIP_TYPE}]->(system:{SYSTEM_NODE_LABEL})
      WITH DISTINCT system
      ORDER BY system.name, system.id
      RETURN [name IN collect(system.name) WHERE name IS NOT NULL] AS department_name
    }}

    CALL (facility) {{
      OPTIONAL MATCH (facility)-[:{CONTAINS_RELATIONSHIP_TYPE}]->(:{COMPONENT_NODE_LABEL})-[:{SUPPORT_RELATIONSHIP_TYPE}]->(effort:{EFFORT_NODE_LABEL})
      WITH DISTINCT effort
      ORDER BY effort.name, effort.id
      RETURN [name IN collect(effort.name) WHERE name IS NOT NULL] AS effort_name
    }}

    CALL (facility) {{
      OPTIONAL MATCH (facility)-[:{DEPENDS_RELATIONSHIP_TYPE}]->(infrastructure:{INFRASTRUCTURE_NODE_LABEL})
      WITH DISTINCT infrastructure
      ORDER BY infrastructure.name, infrastructure.id
      RETURN [name IN collect(infrastructure.name) WHERE name IS NOT NULL] AS dependent_infrastructures
    }}

    CALL (site) {{
      OPTIONAL MATCH (backup_site:{SITE_NODE_LABEL})-[:{CONTAINS_RELATIONSHIP_TYPE}]->(:{FACILITY_NODE_LABEL})-[:{BACKUP_FOR_RELATIONSHIP_TYPE}]->(site)
      WITH DISTINCT backup_site
      ORDER BY backup_site.name, backup_site.id
      RETURN [name IN collect(backup_site.name) WHERE name IS NOT NULL] AS backup_site
    }}

    RETURN
      facility.id AS id,
      site.id AS site_id,
      facility.name AS name,
      department_name,
      effort_name,
      site.level_for_defence_with_upper_layer AS site_level_for_defence_with_upper_layer,
      backup_site,
      dependent_infrastructures,
      CASE
        WHEN site.defence_with_iron_dome IS NULL THEN NULL
        ELSE toString(site.defence_with_iron_dome)
      END AS site_defence_with_iron_dome,
      facility.details_on_facility_purpose AS facility_purpose_details,
      facility.operational_significance_if_damaged AS operational_significance_if_damaged
    ORDER BY coalesce(facility.name, facility.id, '')
    '''

    try:
        with driver.session(database=database) if database else driver.session() as session:
            return [
                {
                    'id': record['id'],
                    'site_id': record['site_id'],
                    'name': record['name'],
                    'system_name': record['department_name'] or [],
                    'department_name': record['department_name'] or [],
                    'effort_name': record['effort_name'] or [],
                    'site_level_for_defence_with_upper_layer': record['site_level_for_defence_with_upper_layer'],
                    'backup_site': record['backup_site'] or [],
                    'dependent_infrastructures': record['dependent_infrastructures'] or [],
                    'site_defence_with_iron_dome': record['site_defence_with_iron_dome'],
                    'facility_purpose_details': record['facility_purpose_details'],
                    'operational_significance_if_damaged': record['operational_significance_if_damaged'],
                }
                for record in session.run(query)
            ]
    except Neo4jError as exc:
        raise DatabaseError(
            message=str(exc) or 'Failed to query facilities for Qlik.',
            details={
                'database': database,
                'neo4j_error': str(exc),
                'neo4j_code': getattr(exc, 'code', None),
            },
        ) from exc


def fetch_node_details(driver: Driver, node_id: str, database: str | None = None) -> dict[str, Any]:
    node_query = '''
    MATCH (n {id: $node_id})
    RETURN n.id AS node_id, labels(n) AS node_labels, properties(n) AS node_properties
    LIMIT 1
    '''

    direct_links_query = '''
    MATCH (n {id: $node_id})-[r]-(m)
    RETURN
      type(r) AS relationship_type,
      CASE
        WHEN startNode(r) = n THEN 'OUTGOING'
        ELSE 'INCOMING'
      END AS direction,
      m.id AS other_node_id,
      labels(m) AS other_node_labels,
      properties(m) AS other_node_properties,
      properties(r) AS relationship_properties
    '''

    hop1_query = '''
    MATCH (n {id: $node_id})-[r]-(m)
    RETURN DISTINCT
      m.id AS node_id,
      labels(m) AS node_labels,
      properties(m) AS node_properties,
      startNode(r).id AS source_id,
      endNode(r).id AS target_id,
      type(r) AS relationship_type,
      properties(r) AS relationship_properties
    '''

    hop2_query = '''
    MATCH (n {id: $node_id})-[r1]-(h1)-[r2]-(h2)
    RETURN DISTINCT
      h2.id AS node_id,
      labels(h2) AS node_labels,
      properties(h2) AS node_properties,
      startNode(r2).id AS source_id,
      endNode(r2).id AS target_id,
      type(r2) AS relationship_type,
      properties(r2) AS relationship_properties
    '''

    try:
        with driver.session(database=database) if database else driver.session() as session:
            node_record = session.run(node_query, node_id=node_id).single()
            if node_record is None:
                raise NotFoundError(
                    message=f'Node with id "{node_id}" was not found.',
                    details={'node_id': node_id},
                )

            node_properties = _to_json_compatible(node_record['node_properties'] or {})
            node_payload = {
                'id': node_record['node_id'],
                'labels': node_record['node_labels'] or [],
                'properties': node_properties,
            }

            direct_links = [
                {
                    'relationship_type': record['relationship_type'],
                    'direction': record['direction'],
                    'other_node': {
                        'id': record['other_node_id'],
                        'labels': record['other_node_labels'] or [],
                        'properties': _to_json_compatible(record['other_node_properties'] or {}),
                    },
                    'relationship_properties': _to_json_compatible(record['relationship_properties'] or {}),
                }
                for record in session.run(direct_links_query, node_id=node_id)
            ]

            hop1_nodes_by_id: dict[str, dict[str, Any]] = {}
            hop1_edges_by_key: dict[tuple[str | None, str | None, str], dict[str, Any]] = {}
            for record in session.run(hop1_query, node_id=node_id):
                this_node_id = record['node_id']
                if this_node_id is not None:
                    hop1_nodes_by_id[this_node_id] = {
                        'id': this_node_id,
                        'labels': record['node_labels'] or [],
                        'properties': _to_json_compatible(record['node_properties'] or {}),
                    }

                edge_key = (
                    record['source_id'],
                    record['target_id'],
                    record['relationship_type'],
                )
                hop1_edges_by_key[edge_key] = {
                    'source_id': record['source_id'],
                    'target_id': record['target_id'],
                    'relationship_type': record['relationship_type'],
                    'relationship_properties': _to_json_compatible(record['relationship_properties'] or {}),
                }

            hop2_nodes_by_id: dict[str, dict[str, Any]] = {}
            hop2_edges_by_key: dict[tuple[str | None, str | None, str], dict[str, Any]] = {}
            for record in session.run(hop2_query, node_id=node_id):
                this_node_id = record['node_id']
                if this_node_id is not None:
                    hop2_nodes_by_id[this_node_id] = {
                        'id': this_node_id,
                        'labels': record['node_labels'] or [],
                        'properties': _to_json_compatible(record['node_properties'] or {}),
                    }

                edge_key = (
                    record['source_id'],
                    record['target_id'],
                    record['relationship_type'],
                )
                hop2_edges_by_key[edge_key] = {
                    'source_id': record['source_id'],
                    'target_id': record['target_id'],
                    'relationship_type': record['relationship_type'],
                    'relationship_properties': _to_json_compatible(record['relationship_properties'] or {}),
                }

            return {
                'node': node_payload,
                'direct_links': direct_links,
                'links_map': {
                    'hop_1': {
                        'nodes': list(hop1_nodes_by_id.values()),
                        'edges': list(hop1_edges_by_key.values()),
                    },
                    'hop_2': {
                        'nodes': list(hop2_nodes_by_id.values()),
                        'edges': list(hop2_edges_by_key.values()),
                    },
                },
            }
    except NotFoundError:
        raise
    except Neo4jError as exc:
        raise DatabaseError(
            message=str(exc) or 'Failed to query node details from Neo4j.',
            details={
                'node_id': node_id,
                'database': database,
                'neo4j_error': str(exc),
                'neo4j_code': getattr(exc, 'code', None),
            },
        ) from exc


def fetch_node_details_by_name(driver: Driver, node_name: str, database: str | None = None) -> dict[str, Any]:
    lookup_query = '''
    MATCH (n {name: $node_name})
    RETURN n.id AS node_id
    ORDER BY n.id
    LIMIT 1
    '''

    try:
        with driver.session(database=database) if database else driver.session() as session:
            match_record = session.run(lookup_query, node_name=node_name).single()
            if match_record is None or not match_record.get('node_id'):
                raise NotFoundError(
                    message=f'Node with name "{node_name}" was not found.',
                    details={'node_name': node_name},
                )

            return fetch_node_details(
                driver=driver,
                node_id=match_record['node_id'],
                database=database,
            )
    except NotFoundError:
        raise
    except Neo4jError as exc:
        raise DatabaseError(
            message=str(exc) or 'Failed to query node details by name from Neo4j.',
            details={
                'node_name': node_name,
                'database': database,
                'neo4j_error': str(exc),
                'neo4j_code': getattr(exc, 'code', None),
            },
        ) from exc


def fetch_node_links_map_by_name(
    driver: Driver,
    node_name: str,
    direction: str = 'BOTH',
    depth: int | None = None,
    database: str | None = None,
) -> dict[str, Any]:
    lookup_query = '''
    MATCH (n {name: $node_name})
    RETURN n.id AS node_id
    ORDER BY n.id
    LIMIT 1
    '''

    try:
        with driver.session(database=database) if database else driver.session() as session:
            match_record = session.run(lookup_query, node_name=node_name).single()
            if match_record is None or not match_record.get('node_id'):
                raise NotFoundError(
                    message=f'Node with name "{node_name}" was not found.',
                    details={'node_name': node_name},
                )

            return fetch_node_links_map(
                driver=driver,
                node_id=match_record['node_id'],
                direction=direction,
                depth=depth,
                database=database,
            )
    except NotFoundError:
        raise
    except Neo4jError as exc:
        raise DatabaseError(
            message=str(exc) or 'Failed to query node links map by name from Neo4j.',
            details={
                'node_name': node_name,
                'direction': direction,
                'depth': depth,
                'database': database,
                'neo4j_error': str(exc),
                'neo4j_code': getattr(exc, 'code', None),
            },
        ) from exc


def fetch_node_links_map(
    driver: Driver,
    node_id: str,
    direction: str = 'BOTH',
    depth: int | None = None,
    database: str | None = None,
) -> dict[str, Any]:
    node_query = '''
    MATCH (n {id: $node_id})
    RETURN n.id AS node_id, labels(n) AS node_labels, properties(n) AS node_properties
    LIMIT 1
    '''

    effective_depth = max(1, depth) if depth is not None else None

    if direction == 'INCOMING':
        relationship_pattern = '<-[*1..DEPTH]-'
    elif direction == 'OUTGOING':
        relationship_pattern = '-[*1..DEPTH]->'
    else:
        relationship_pattern = '-[*1..DEPTH]-'

    depth_suffix = '' if effective_depth is None else str(effective_depth)
    relationship_pattern = relationship_pattern.replace('DEPTH', depth_suffix)

    direction_map_query = f'''
    MATCH (start {{id: $node_id}})
    CALL (start) {{
      OPTIONAL MATCH (start){relationship_pattern}(m)
      RETURN [node IN collect(DISTINCT m) WHERE node IS NOT NULL] AS reachable_nodes
    }}
    WITH reachable_nodes + [start] AS subgraph_nodes
    UNWIND subgraph_nodes AS src
    OPTIONAL MATCH (src)-[rel]-(dst)
    WHERE dst IN subgraph_nodes
    WITH
      subgraph_nodes,
      collect(
        DISTINCT CASE
          WHEN rel IS NULL THEN NULL
          ELSE [startNode(rel), rel, endNode(rel)]
        END
      ) AS edge_tuples
    RETURN
      subgraph_nodes AS nodes,
      [edge_tuple IN edge_tuples WHERE edge_tuple IS NOT NULL] AS edges
    '''

    try:
        with driver.session(database=database) if database else driver.session() as session:
            node_record = session.run(node_query, node_id=node_id).single()
            if node_record is None:
                raise NotFoundError(
                    message=f'Node with id "{node_id}" was not found.',
                    details={'node_id': node_id},
                )

            node_payload = {
                'id': node_record['node_id'],
                'labels': node_record['node_labels'] or [],
                'properties': _to_json_compatible(node_record['node_properties'] or {}),
            }

            map_record = session.run(direction_map_query, node_id=node_id).single()
            if map_record is None:
                direction_nodes = []
                direction_edges = []
            else:
                raw_nodes = map_record['nodes'] or []
                raw_edges = map_record['edges'] or []

                direction_nodes = [
                    {
                        'id': raw_node.get('id'),
                        'labels': list(raw_node.labels) if getattr(raw_node, 'labels', None) else [],
                        'properties': _to_json_compatible(dict(raw_node.items()) if hasattr(raw_node, 'items') else {}),
                    }
                    for raw_node in sorted(
                        raw_nodes,
                        key=lambda item: (item.get('name') if hasattr(item, 'get') else None) or (item.get('id') if hasattr(item, 'get') else '') or '',
                    )
                    if raw_node.get('id')
                    and raw_node.get('id') != node_id
                ]

                direction_edges = [
                    {
                        'source_id': source_node.get('id') if hasattr(source_node, 'get') else None,
                        'target_id': target_node.get('id') if hasattr(target_node, 'get') else None,
                        'relationship_type': rel.type if hasattr(rel, 'type') else None,
                        'relationship_properties': _to_json_compatible(dict(rel.items()) if hasattr(rel, 'items') else {}),
                    }
                    for raw_edge in sorted(
                        raw_edges,
                        key=lambda item: (
                            item[1].type if len(item) > 1 and hasattr(item[1], 'type') else '',
                            item[0].get('id') if len(item) > 0 and hasattr(item[0], 'get') else '',
                            item[2].get('id') if len(item) > 2 and hasattr(item[2], 'get') else '',
                        ),
                    )
                    if len(raw_edge) == 3
                    for source_node, rel, target_node in [raw_edge]
                    if hasattr(rel, 'type')
                ]

            return {
                'node': node_payload,
                'links_map': {
                    'direction': direction,
                    'depth': effective_depth,
                    'nodes': direction_nodes,
                    'edges': direction_edges,
                },
            }
    except NotFoundError:
        raise
    except Neo4jError as exc:
        raise DatabaseError(
            message=str(exc) or 'Failed to query node links map from Neo4j.',
            details={
                'node_id': node_id,
                'direction': direction,
                'depth': depth,
                'database': database,
                'neo4j_error': str(exc),
                'neo4j_code': getattr(exc, 'code', None),
            },
        ) from exc


def fetch_node_full_map(driver: Driver, node_id: str, database: str | None = None) -> dict[str, Any]:
    check_query = 'MATCH (n {id: $node_id}) RETURN n LIMIT 1'
    map_query = '''
    MATCH (start {id: $node_id})
    CALL (start) {
      MATCH (start)-[*0..]-(n)
      RETURN collect(DISTINCT n) AS ns
    }
    UNWIND ns AS n
    OPTIONAL MATCH (n)-[r]-(m)
    WHERE m IN ns
    RETURN
      start.id AS node_id,
      collect(DISTINCT {id: n.id, labels: labels(n), properties: properties(n)}) AS nodes,
      collect(
        DISTINCT CASE
          WHEN r IS NULL THEN NULL
          ELSE {
            source_id: startNode(r).id,
            target_id: endNode(r).id,
            relationship_type: type(r),
            relationship_properties: properties(r)
          }
        END
      ) AS raw_edges
    '''

    try:
        with driver.session(database=database) if database else driver.session() as session:
            exists = session.run(check_query, node_id=node_id).single()
            if exists is None:
                raise NotFoundError(
                    message=f'Node with id "{node_id}" was not found.',
                    details={'node_id': node_id},
                )

            record = session.run(map_query, node_id=node_id).single()
            if record is None:
                return {'node_id': node_id, 'nodes': [], 'edges': []}

            nodes = _to_json_compatible(record['nodes'] or [])
            raw_edges = record['raw_edges'] or []
            edges = [_to_json_compatible(edge) for edge in raw_edges if edge is not None]

            return {
                'node_id': record['node_id'] or node_id,
                'nodes': nodes,
                'edges': edges,
            }
    except NotFoundError:
        raise
    except Neo4jError as exc:
        raise DatabaseError(
            message=str(exc) or 'Failed to query full map from Neo4j.',
            details={
                'node_id': node_id,
                'database': database,
                'neo4j_error': str(exc),
                'neo4j_code': getattr(exc, 'code', None),
            },
        ) from exc


def fetch_node_link_map_until_effort(
    driver: Driver,
    node_id: str,
    database: str | None = None,
) -> dict[str, Any]:
    node_query = '''
    MATCH (n {id: $node_id})
    RETURN
      n.id AS node_id,
      n.name AS node_name,
      labels(n) AS node_labels
    LIMIT 1
    '''

    map_query = f'''
    MATCH (start {{id: $node_id}})
    MATCH path = (start)-[*0..]-(reachable)
    WHERE
      (
        size(nodes(path)) = 1
        OR NOT '{EFFORT_NODE_LABEL}' IN labels(start)
      )
      AND all(
        idx IN CASE
          WHEN size(nodes(path)) <= 2 THEN []
          ELSE range(1, size(nodes(path)) - 2)
        END
        WHERE NOT '{EFFORT_NODE_LABEL}' IN labels(nodes(path)[idx])
      )
    WITH collect(DISTINCT path) AS paths
    UNWIND paths AS path
    UNWIND nodes(path) AS path_node
    WITH
      paths,
      collect(DISTINCT path_node) AS raw_nodes
    UNWIND paths AS path
    UNWIND relationships(path) AS rel
    WITH
      raw_nodes,
      collect(
        DISTINCT {{
          source_id: startNode(rel).id,
          target_id: endNode(rel).id,
          relationship_type: type(rel)
        }}
      ) AS raw_edges
    RETURN
      raw_nodes,
      raw_edges
    '''

    try:
        with driver.session(database=database) if database else driver.session() as session:
            node_record = session.run(node_query, node_id=node_id).single()
            if node_record is None:
                raise NotFoundError(
                    message=f'Node with id "{node_id}" was not found.',
                    details={'node_id': node_id},
                )

            root_node = {
                'id': node_record['node_id'],
                'name': node_record['node_name'],
                'node_type': _select_primary_label(node_record['node_labels'] or []),
            }

            map_record = session.run(map_query, node_id=node_id).single()
            if map_record is None:
                return {
                    'node': root_node,
                    'links_map': {'nodes': [], 'edges': []},
                }

            raw_nodes = map_record['raw_nodes'] or []
            raw_edges = map_record['raw_edges'] or []

            nodes = [
                {
                    'id': raw_node.get('id'),
                    'name': raw_node.get('name'),
                    'node_type': primary_label,
                }
                for raw_node in sorted(
                    raw_nodes,
                    key=lambda item: (item.get('name') if hasattr(item, 'get') else None) or (item.get('id') if hasattr(item, 'get') else '') or '',
                )
                for primary_label in [_select_primary_label(list(raw_node.labels) if getattr(raw_node, 'labels', None) else [])]
                if raw_node.get('id') and raw_node.get('id') != node_id
                and primary_label in LINK_MAP_INCLUDED_NODE_LABELS
            ]

            included_node_ids = {node['id'] for node in nodes}
            if root_node['node_type'] in LINK_MAP_INCLUDED_NODE_LABELS and root_node['id']:
                included_node_ids.add(root_node['id'])

            edges = [
                {
                    'source_id': edge.get('source_id'),
                    'target_id': edge.get('target_id'),
                    'relationship_type': edge.get('relationship_type'),
                }
                for edge in sorted(
                    raw_edges,
                    key=lambda item: (
                        item.get('relationship_type') or '',
                        item.get('source_id') or '',
                        item.get('target_id') or '',
                    ),
                )
                if edge.get('relationship_type')
                and edge.get('source_id') in included_node_ids
                and edge.get('target_id') in included_node_ids
            ]

            return {
                'node': root_node,
                'links_map': {
                    'nodes': _to_json_compatible(nodes),
                    'edges': _to_json_compatible(edges),
                },
            }
    except NotFoundError:
        raise
    except Neo4jError as exc:
        raise DatabaseError(
            message=str(exc) or 'Failed to query node link map until Effort from Neo4j.',
            details={
                'node_id': node_id,
                'database': database,
                'neo4j_error': str(exc),
                'neo4j_code': getattr(exc, 'code', None),
            },
        ) from exc


def fetch_node_raw(driver: Driver, node_id: str, database: str | None = None) -> dict[str, Any]:
    query = '''
    MATCH (n {id: $node_id})
    RETURN
      n.id AS node_id,
      labels(n) AS node_labels,
      properties(n) AS node_properties
    LIMIT 1
    '''

    try:
        with driver.session(database=database) if database else driver.session() as session:
            record = session.run(query, node_id=node_id).single()
            if record is None:
                raise NotFoundError(
                    message=f'Node with id "{node_id}" was not found.',
                    details={'node_id': node_id},
                )

            return {
                'id': record['node_id'],
                'labels': record['node_labels'] or [],
                'properties': _to_json_compatible(record['node_properties'] or {}),
            }
    except NotFoundError:
        raise
    except Neo4jError as exc:
        raise DatabaseError(
            message=str(exc) or 'Failed to query raw node from Neo4j.',
            details={
                'node_id': node_id,
                'database': database,
                'neo4j_error': str(exc),
                'neo4j_code': getattr(exc, 'code', None),
            },
        ) from exc


def _to_json_compatible(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, dict):
        return {str(k): _to_json_compatible(v) for k, v in value.items()}

    if isinstance(value, list):
        return [_to_json_compatible(v) for v in value]

    if isinstance(value, tuple):
        return [_to_json_compatible(v) for v in value]

    if isinstance(value, set):
        return [_to_json_compatible(v) for v in value]

    if isinstance(value, (bytes, bytearray)):
        return value.decode('utf-8', errors='replace')

    # Neo4j temporal/spatial values (e.g. neo4j.time.DateTime) are not JSON serializable by default.
    if value.__class__.__module__.startswith('neo4j.'):
        if hasattr(value, 'iso_format'):
            return str(value.iso_format())
        if hasattr(value, 'to_native'):
            try:
                return _to_json_compatible(value.to_native())
            except Exception:
                return str(value)
        return str(value)

    return value


def _select_primary_label(labels: list[str]) -> str | None:
    if not labels:
        return None

    preferred_order = [
        SITE_NODE_LABEL,
        FACILITY_NODE_LABEL,
        INFRASTRUCTURE_NODE_LABEL,
        COMPONENT_NODE_LABEL,
        SYSTEM_NODE_LABEL,
        EFFORT_NODE_LABEL,
    ]

    for label in preferred_order:
        if label in labels:
            return label

    return labels[0]


def _build_qlik_polygon_fields(raw_polygon: Any) -> dict[str, Any]:
    corrected_polygon = _extract_polygon_coordinates(raw_polygon)
    center_x, center_y = _calculate_polygon_center(corrected_polygon)

    return {
        'corrected_polygon': _format_corrected_polygon(corrected_polygon),
        'center_x': center_x,
        'center_y': center_y,
    }


def _extract_polygon_coordinates(raw_polygon: Any) -> list[list[float]]:
    if isinstance(raw_polygon, dict):
        coordinates = raw_polygon.get('coordinates') or raw_polygon.get('cordinates') or []
        if coordinates and isinstance(coordinates, list) and isinstance(coordinates[0], list):
            first_item = coordinates[0]
            if first_item and isinstance(first_item[0], list):
                return [point for point in (_normalize_point(item) for item in first_item) if point is not None]
            return [point for point in (_normalize_point(item) for item in coordinates) if point is not None]
        return []

    if not isinstance(raw_polygon, str):
        return []

    match = re.fullmatch(r'\s*POLYGON\s*\(\((.*)\)\)\s*', raw_polygon, flags=re.IGNORECASE)
    if match is None:
        return []

    points: list[list[float]] = []
    for pair in match.group(1).split(','):
        parts = pair.strip().split()
        if len(parts) < 2:
            continue
        try:
            points.append([float(parts[0]), float(parts[1])])
        except ValueError:
            continue
    return points


def _normalize_point(point: Any) -> list[float] | None:
    if not isinstance(point, (list, tuple)) or len(point) < 2:
        return None

    try:
        return [float(point[0]), float(point[1])]
    except (TypeError, ValueError):
        return None


def _calculate_polygon_center(points: list[list[float]]) -> tuple[float | None, float | None]:
    if not points:
        return None, None

    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    return (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2


def _format_corrected_polygon(points: list[list[float]]) -> str | None:
    if not points:
        return None

    return str([[points]])
