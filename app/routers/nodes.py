from typing import Literal
import logging

from fastapi import APIRouter, Depends, Query
from neo4j import Driver

from app.config import get_settings
from app.db.neo4j import fetch_node_details, fetch_node_links_map, get_neo4j_driver
from app.schemas.nodes import NodeDetailsResponse, NodeLinksMapResponse

router = APIRouter(prefix='/nodes', tags=['nodes'])
logger = logging.getLogger(__name__)


@router.get('/{node_id}/details', response_model=NodeDetailsResponse)
async def get_node_details(node_id: str, driver: Driver = Depends(get_neo4j_driver)) -> NodeDetailsResponse:
    settings = get_settings()
    details = fetch_node_details(driver=driver, node_id=node_id, database=settings.neo4j_database)
    payload = {
        'node': details['node'],
        'relations': details['direct_links'],
    }

    logger.info(
        'Fetched node details',
        extra={'node_id': node_id, 'relations_count': len(payload['relations'])},
    )

    return NodeDetailsResponse(**payload)


@router.get('/{node_id}/links-map', response_model=NodeLinksMapResponse)
async def get_node_links_map(
    node_id: str,
    direction: Literal['INCOMING', 'OUTGOING', 'BOTH'] = Query(default='BOTH'),
    depth: int | None = Query(default=None, ge=1),
    driver: Driver = Depends(get_neo4j_driver),
) -> NodeLinksMapResponse:
    settings = get_settings()
    payload = fetch_node_links_map(
        driver=driver,
        node_id=node_id,
        direction=direction,
        depth=depth,
        database=settings.neo4j_database,
    )

    logger.info(
        'Fetched node links map',
        extra={
            'node_id': node_id,
            'direction': direction,
            'depth': depth,
            'edges_count': len(payload['links_map']['edges']),
        },
    )

    return NodeLinksMapResponse(**payload)
