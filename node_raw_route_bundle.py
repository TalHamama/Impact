"""
Consolidated code bundle for the raw node route.

This file collects the actual implementation code that was added for the
raw node route into one transferable file.
"""


# ============================================================================
# Section: schemas/models
# Original target file: app/schemas/graph.py
# ============================================================================

from typing import Any

from pydantic import BaseModel, Field


class NodeRawResponse(BaseModel):
    id: str
    labels: list[str] = Field(default_factory=list)
    properties: dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# Section: helpers
# Original target file: app/db/neo4j.py
# ============================================================================


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


# ============================================================================
# Section: repository/query
# Original target file: app/db/neo4j.py
# ============================================================================

from neo4j import Driver
from neo4j.exceptions import Neo4jError

from app.utils.errors import DatabaseError, NotFoundError


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


# ============================================================================
# Section: service
# Original target file: app/services/graph.py
# ============================================================================


def get_node_raw_service(driver: Driver, node_id: str, database: str) -> dict[str, Any]:
    return fetch_node_raw(driver=driver, node_id=node_id, database=database)


# ============================================================================
# Section: router
# Original target file: app/routers/graph.py
# ============================================================================

import logging

from fastapi import APIRouter, Depends

from app.config import get_settings
from app.db.neo4j import get_neo4j_driver


router = APIRouter(tags=['graph'])
logger = logging.getLogger(__name__)


@router.get('/nodes/{node_id}', response_model=NodeRawResponse)
async def get_node_raw(node_id: str, driver: Driver = Depends(get_neo4j_driver)) -> NodeRawResponse:
    node = get_node_raw_service(
        driver=driver,
        node_id=node_id,
        database=get_settings().neo4j_database,
    )

    logger.info(
        'Fetched raw node',
        extra={
            'node_id': node_id,
            'labels_count': len(node.get('labels', [])),
            'properties_count': len(node.get('properties', {})),
        },
    )

    return NodeRawResponse(**node)


# ============================================================================
# Section: notes for integration
# ============================================================================

# 1. Move the schemas/models block into: app/schemas/graph.py
# 2. Move the helpers + repository/query block into: app/db/neo4j.py
# 3. Move the service block into: app/services/graph.py
# 4. Move the router block into: app/routers/graph.py and make sure the router is included by FastAPI.
# 5. Adjust imports if your target project keeps get_neo4j_driver in a different module.
# 6. This code assumes the target project already has:
#    - app.config.get_settings
#    - app.utils.errors.DatabaseError
#    - app.utils.errors.NotFoundError
#    - Neo4j driver dependency wiring compatible with FastAPI Depends
