"""
Consolidated code bundle for the node link-map route.

This file collects the actual implementation code that was added for the
link-map route into one transferable file.
"""


# ============================================================================
# Section: schemas/models
# Original target file: app/schemas/graph.py
# ============================================================================

from pydantic import BaseModel, Field


class LinkMapNode(BaseModel):
    id: str | None = None
    name: str | None = None
    node_type: str | None = None


class LinkMapEdge(BaseModel):
    source_id: str | None = None
    target_id: str | None = None
    relationship_type: str


class LinkMapPayload(BaseModel):
    nodes: list[LinkMapNode] = Field(default_factory=list)
    edges: list[LinkMapEdge] = Field(default_factory=list)


class NodeLinkMapResponse(BaseModel):
    node: LinkMapNode
    links_map: LinkMapPayload


# ============================================================================
# Section: helpers
# Original target file: app/db/neo4j.py
# ============================================================================

from typing import Any


SITE_NODE_LABEL = 'Site'
FACILITY_NODE_LABEL = 'Facility'
INFRASTRUCTURE_NODE_LABEL = 'Infrastructure'
COMPONENT_NODE_LABEL = 'Component'
SYSTEM_NODE_LABEL = 'System'
EFFORT_NODE_LABEL = 'Effort'
LINK_MAP_INCLUDED_NODE_LABELS = {
    SITE_NODE_LABEL,
    FACILITY_NODE_LABEL,
    COMPONENT_NODE_LABEL,
    EFFORT_NODE_LABEL,
}


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


# ============================================================================
# Section: repository/query
# Original target file: app/db/neo4j.py
# ============================================================================

from neo4j import Driver
from neo4j.exceptions import Neo4jError

from app.utils.errors import DatabaseError, NotFoundError


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


# ============================================================================
# Section: service
# Original target file: app/services/link_map_service.py
# ============================================================================

from app.db.neo4j import get_neo4j_driver


def get_node_link_map_service(
    driver: Driver,
    node_id: str,
    database: str,
) -> dict[str, Any]:
    return fetch_node_link_map_until_effort(
        driver=driver,
        node_id=node_id,
        database=database,
    )


# ============================================================================
# Section: router
# Original target file: app/routers/graph.py
# ============================================================================

import logging

from fastapi import APIRouter, Depends

from app.config import get_settings


router = APIRouter(tags=['graph'])
logger = logging.getLogger(__name__)


@router.get('/nodes/{node_id}/link-map', response_model=NodeLinkMapResponse)
async def get_node_link_map(node_id: str, driver: Driver = Depends(get_neo4j_driver)) -> NodeLinkMapResponse:
    graph = get_node_link_map_service(
        driver=driver,
        node_id=node_id,
        database=get_settings().neo4j_database,
    )

    logger.info(
        'Fetched node link map until Effort',
        extra={
            'node_id': node_id,
            'nodes_count': len(graph.get('links_map', {}).get('nodes', [])),
            'edges_count': len(graph.get('links_map', {}).get('edges', [])),
        },
    )

    return NodeLinkMapResponse(**graph)


# ============================================================================
# Section: notes for integration
# ============================================================================

# 1. Move the schemas/models block into: app/schemas/graph.py
# 2. Move the helpers + repository/query block into: app/db/neo4j.py
# 3. Move the service block into a service module if your target project uses one;
#    otherwise you can call fetch_node_link_map_until_effort directly from the router.
# 4. Move the router block into: app/routers/graph.py and make sure the router is included by FastAPI.
# 5. Adjust imports if your target project keeps get_neo4j_driver in a different module.
# 6. This code assumes the target project already has:
#    - app.config.get_settings
#    - app.utils.errors.DatabaseError
#    - app.utils.errors.NotFoundError
#    - Neo4j driver dependency wiring compatible with FastAPI Depends
