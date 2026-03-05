from __future__ import annotations

from collections.abc import Generator
from typing import Any

from neo4j import Driver, GraphDatabase
from neo4j.exceptions import Neo4jError

from app.utils.errors import DatabaseError, NotFoundError


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
    nodes_query = '''
    MATCH (n)
    WHERE any(label IN labels(n) WHERE label IN ['Site', 'Infrastrcture'])
    RETURN
      n.id AS node_id,
      CASE
        WHEN 'Site' IN labels(n) THEN 'Site'
        ELSE 'Infrastrcture'
      END AS node_type,
      n.name AS node_name,
      n.polygon AS node_polygon
    ORDER BY coalesce(n.name, n.id, '')
    '''

    edges_query = '''
    CALL {
      MATCH (a)-[r]-(b)
      WHERE any(label IN labels(a) WHERE label IN ['Site', 'Infrastrcture'])
        AND any(label IN labels(b) WHERE label IN ['Site', 'Infrastrcture'])
      RETURN DISTINCT
        startNode(r).id AS source_id,
        endNode(r).id AS target_id,
        type(r) AS relationship_type

      UNION

      MATCH (s1:Site)<-[:INTERCHANGEABLE]-(c:Componenet)-[:INTERCHANGEABLE]->(s2:Site)
      WHERE s1.id < s2.id
      RETURN DISTINCT
        s1.id AS source_id,
        s2.id AS target_id,
        'INTERCHANGEABLE' AS relationship_type
    }
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
            message=str(exc) or 'Failed to query Site/Infrastrcture links from Neo4j.',
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

    linked_artifacts_query = '''
    MATCH (n {id: $node_id})-[r]-(m)
    WHERE any(label IN labels(m) WHERE label IN ['Maintenance', 'Report'])
    RETURN
      m.id AS artifact_id,
      labels(m) AS artifact_labels,
      properties(m) AS artifact_properties,
      type(r) AS relationship_type
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

            maintenance_items: list[dict[str, Any]] = []
            reports_items: list[dict[str, Any]] = []

            for item in _as_list(node_properties.get('maintenance')):
                maintenance_items.append(
                    {
                        'source': 'property',
                        'id': None,
                        'labels': [],
                        'relationship_type': None,
                        'properties': item if isinstance(item, dict) else {'value': item},
                    }
                )

            for item in _as_list(node_properties.get('reports')):
                reports_items.append(
                    {
                        'source': 'property',
                        'id': None,
                        'labels': [],
                        'relationship_type': None,
                        'properties': item if isinstance(item, dict) else {'value': item},
                    }
                )

            for record in session.run(linked_artifacts_query, node_id=node_id):
                labels = record['artifact_labels'] or []
                payload = {
                    'source': 'linked_node',
                        'id': record['artifact_id'],
                        'labels': labels,
                        'relationship_type': record['relationship_type'],
                        'properties': _to_json_compatible(record['artifact_properties'] or {}),
                    }
                if 'Maintenance' in labels:
                    maintenance_items.append(payload)
                if 'Report' in labels:
                    reports_items.append(payload)

            return {
                'node': node_payload,
                'direct_links': direct_links,
                'maintenance': maintenance_items,
                'reports': reports_items,
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

    if direction == 'INCOMING':
        path_pattern = '(n {id: $node_id})<-[*1..DEPTH]-(m)'
    elif direction == 'OUTGOING':
        path_pattern = '(n {id: $node_id})-[*1..DEPTH]->(m)'
    else:
        path_pattern = '(n {id: $node_id})-[*1..DEPTH]-(m)'

    depth_suffix = '' if depth is None else str(max(1, depth))
    path_pattern = path_pattern.replace('DEPTH', depth_suffix)

    direction_nodes_query = f'''
    MATCH p={path_pattern}
    UNWIND nodes(p) AS path_node
    WITH DISTINCT path_node
    WHERE path_node.id <> $node_id
    RETURN
      path_node.id AS node_id,
      labels(path_node) AS node_labels,
      properties(path_node) AS node_properties
    '''

    direction_edges_query = f'''
    MATCH p={path_pattern}
    UNWIND relationships(p) AS rel
    RETURN DISTINCT
      startNode(rel).id AS source_id,
      endNode(rel).id AS target_id,
      type(rel) AS relationship_type,
      properties(rel) AS relationship_properties
    ORDER BY relationship_type, source_id, target_id
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

            direction_nodes = [
                {
                    'id': record['node_id'],
                    'labels': record['node_labels'] or [],
                    'properties': _to_json_compatible(record['node_properties'] or {}),
                }
                for record in session.run(direction_nodes_query, node_id=node_id)
            ]

            direction_edges = [
                {
                    'source_id': record['source_id'],
                    'target_id': record['target_id'],
                    'relationship_type': record['relationship_type'],
                    'relationship_properties': _to_json_compatible(record['relationship_properties'] or {}),
                }
                for record in session.run(direction_edges_query, node_id=node_id)
            ]

            return {
                'node': node_payload,
                'links_map': {
                    'direction': direction,
                    'depth': depth,
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


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


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
