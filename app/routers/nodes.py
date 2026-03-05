import logging

from fastapi import APIRouter, Depends
from neo4j import Driver

from app.config import get_settings
from app.db.neo4j import fetch_node_details, fetch_node_full_map, get_neo4j_driver
from app.schemas.nodes import NodeDetailsResponse, NodeFullMapResponse, NodeLinksMapResponse

router = APIRouter(prefix='/nodes', tags=['nodes'])
logger = logging.getLogger(__name__)


@router.get('/{node_id}/details', response_model=NodeDetailsResponse)
async def get_node_details(node_id: str, driver: Driver = Depends(get_neo4j_driver)) -> NodeDetailsResponse:
    settings = get_settings()
    details = fetch_node_details(driver=driver, node_id=node_id, database=settings.neo4j_database)

    logger.info(
        'Fetched node details',
        extra={'node_id': node_id, 'direct_links_count': len(details.get('direct_links', []))},
    )

    return NodeDetailsResponse(**details)


@router.get('/{node_id}/links-map', response_model=NodeLinksMapResponse)
async def get_node_links_map(node_id: str, driver: Driver = Depends(get_neo4j_driver)) -> NodeLinksMapResponse:
    settings = get_settings()
    details = fetch_node_details(driver=driver, node_id=node_id, database=settings.neo4j_database)

    payload = {
        'node': details['node'],
        'direct_links': details['direct_links'],
        'links_map': details['links_map'],
    }

    logger.info(
        'Fetched node links map',
        extra={
            'node_id': node_id,
            'direct_links_count': len(payload['direct_links']),
            'hop_1_edges_count': len(payload['links_map']['hop_1']['edges']),
            'hop_2_edges_count': len(payload['links_map']['hop_2']['edges']),
        },
    )

    return NodeLinksMapResponse(**payload)


@router.get('/{node_id}/full-map', response_model=NodeFullMapResponse)
async def get_node_full_map(node_id: str, driver: Driver = Depends(get_neo4j_driver)) -> NodeFullMapResponse:
    settings = get_settings()
    payload = fetch_node_full_map(driver=driver, node_id=node_id, database=settings.neo4j_database)

    logger.info(
        'Fetched node full map',
        extra={
            'node_id': node_id,
            'nodes_count': len(payload.get('nodes', [])),
            'edges_count': len(payload.get('edges', [])),
        },
    )

    return NodeFullMapResponse(**payload)
