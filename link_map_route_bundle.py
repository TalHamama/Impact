"""
Consolidated code bundle for the site link-map route.

This bundle contains the fixed-pattern implementation for the link-map route.
It matches only this structure:

Real DB pattern:
Site -[:CONTAINS]-> Facility -[:CONTAINS]-> Component
Facility -[:SUPPORTS]-> Effort

Projected graph pattern returned to the frontend:
Site -[:CONTAINS]-> Facility -[:CONTAINS]-> Component -[:SUPPORTS]-> Effort
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
CONTAINS_RELATIONSHIP_TYPE = 'CONTAINS'
SUPPORT_RELATIONSHIP_TYPE = 'SUPPORTS'
LINK_MAP_INCLUDED_NODE_LABELS = {
    SITE_NODE_LABEL,
    FACILITY_NODE_LABEL,
    COMPONENT_NODE_LABEL,
    EFFORT_NODE_LABEL,
}
PRIMARY_LABEL_PREFERENCE = [
    SITE_NODE_LABEL,
    FACILITY_NODE_LABEL,
    INFRASTRUCTURE_NODE_LABEL,
    COMPONENT_NODE_LABEL,
    SYSTEM_NODE_LABEL,
    EFFORT_NODE_LABEL,
]


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

    for label in PRIMARY_LABEL_PREFERENCE:
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
    MATCH (n:Site {id: $node_id})
    RETURN
      n.id AS node_id,
      n.name AS node_name,
      labels(n) AS node_labels
    LIMIT 1
    '''

    map_query = f'''
    MATCH (start:{SITE_NODE_LABEL} {{id: $node_id}})
    OPTIONAL MATCH (start)-[site_facility_rel:{CONTAINS_RELATIONSHIP_TYPE}]->(facility:{FACILITY_NODE_LABEL})
    WITH start, facility, collect(DISTINCT site_facility_rel) AS site_facility_rels
    CALL (facility) {{
      OPTIONAL MATCH (facility)-[facility_component_rel:{CONTAINS_RELATIONSHIP_TYPE}]->(component:{COMPONENT_NODE_LABEL})
      WITH facility, facility_component_rel, component
      ORDER BY coalesce(component.name, component.id, '')
      RETURN
        collect(DISTINCT component) AS facility_components,
        collect(DISTINCT facility_component_rel) AS facility_component_rels,
        head(collect(component)) AS representative_component
    }}
    CALL (facility, representative_component) {{
      OPTIONAL MATCH (facility)-[:{SUPPORT_RELATIONSHIP_TYPE}]->(effort:{EFFORT_NODE_LABEL})
      WITH facility, representative_component, effort
      ORDER BY coalesce(effort.name, effort.id, '')
      RETURN
        collect(DISTINCT effort) AS facility_efforts,
        collect(
          DISTINCT CASE
            WHEN representative_component IS NULL OR effort IS NULL THEN NULL
            ELSE {{
              source_id: representative_component.id,
              target_id: effort.id,
              relationship_type: '{SUPPORT_RELATIONSHIP_TYPE}'
            }}
          END
        ) AS projected_component_effort_edges
    }}
    WITH
      start,
      collect(DISTINCT facility) AS facilities,
      collect(DISTINCT site_facility_rels) AS grouped_site_facility_rels,
      collect(DISTINCT facility_components) AS grouped_components,
      collect(DISTINCT facility_component_rels) AS grouped_facility_component_rels,
      collect(DISTINCT facility_efforts) AS grouped_efforts,
      collect(DISTINCT projected_component_effort_edges) AS grouped_component_effort_edges
    CALL (start, facilities, grouped_components, grouped_efforts) {{
      WITH
        start,
        facilities,
        reduce(acc = [], component_group IN grouped_components | acc + component_group) AS all_components,
        reduce(acc = [], effort_group IN grouped_efforts | acc + effort_group) AS all_efforts
      WITH start, facilities + all_components + all_efforts AS candidate_nodes
      UNWIND candidate_nodes AS n
      WITH DISTINCT start, n
      WITH start, n, [label IN $primary_label_preference WHERE label IN labels(n)][0] AS primary_label
      WHERE n IS NOT NULL
        AND n.id IS NOT NULL
        AND n.id <> start.id
        AND primary_label IN $included_node_labels
      ORDER BY coalesce(n.name, n.id, '')
      RETURN collect({{
        id: n.id,
        name: n.name,
        node_type: primary_label
      }}) AS raw_nodes,
      collect(n.id) AS projected_node_ids
    }}
    WITH
      start,
      raw_nodes,
      projected_node_ids,
      reduce(acc = [], rel_group IN grouped_site_facility_rels | acc + rel_group) AS site_facility_relationships,
      reduce(acc = [], rel_group IN grouped_facility_component_rels | acc + rel_group) AS facility_component_relationships,
      reduce(acc = [], edge_group IN grouped_component_effort_edges | acc + edge_group) AS projected_component_effort_edges
    CALL (start, site_facility_relationships, facility_component_relationships, projected_component_effort_edges, projected_node_ids) {{
      WITH
        CASE
          WHEN start.id IS NOT NULL THEN projected_node_ids + start.id
          ELSE projected_node_ids
        END AS included_node_ids,
        site_facility_relationships,
        facility_component_relationships,
        projected_component_effort_edges
      CALL {{
        WITH site_facility_relationships, facility_component_relationships
        UNWIND site_facility_relationships + facility_component_relationships AS rel
        WITH DISTINCT rel
        WHERE rel IS NOT NULL
        RETURN collect({{
          source_id: startNode(rel).id,
          target_id: endNode(rel).id,
          relationship_type: type(rel)
        }}) AS physical_edges
      }}
      WITH included_node_ids, physical_edges, projected_component_effort_edges
      UNWIND physical_edges + projected_component_effort_edges AS edge
      WITH DISTINCT edge, included_node_ids
      WHERE edge IS NOT NULL
        AND edge.source_id IN included_node_ids
        AND edge.target_id IN included_node_ids
      ORDER BY edge.relationship_type, edge.source_id, edge.target_id
      RETURN collect(edge) AS raw_edges
    }}
    RETURN raw_nodes, raw_edges
    '''

    try:
        with driver.session(database=database) if database else driver.session() as session:
            node_record = session.run(node_query, node_id=node_id).single()
            if node_record is None:
                raise NotFoundError(
                    message=f'Site with id "{node_id}" was not found.',
                    details={'node_id': node_id},
                )

            root_node = {
                'id': node_record['node_id'],
                'name': node_record['node_name'],
                'node_type': _select_primary_label(node_record['node_labels'] or []),
            }

            map_record = session.run(
                map_query,
                node_id=node_id,
                included_node_labels=sorted(LINK_MAP_INCLUDED_NODE_LABELS),
                primary_label_preference=PRIMARY_LABEL_PREFERENCE,
            ).single()
            if map_record is None:
                return {
                    'node': root_node,
                    'links_map': {'nodes': [], 'edges': []},
                }

            raw_nodes = map_record['raw_nodes'] or []
            raw_edges = map_record['raw_edges'] or []

            return {
                'node': root_node,
                'links_map': {
                    'nodes': _to_json_compatible(raw_nodes),
                    'edges': _to_json_compatible(raw_edges),
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
