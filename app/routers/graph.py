import logging

from fastapi import APIRouter, Depends
from neo4j import Driver

from app.config import get_settings
from app.db.neo4j import (
    fetch_node_link_map_until_effort,
    fetch_sites_infrastructures_with_links,
    fetch_sites_infrastructures_with_links_for_qlik,
    get_neo4j_driver,
)
from app.schemas.graph import NodeLinkMapResponse, NodeRawResponse, QlikSitesInfrastructuresLinksResponse, SitesInfrastructuresLinksResponse
from app.services.graph import get_node_raw_service

router = APIRouter(tags=['graph'])
logger = logging.getLogger(__name__)


@router.get('/sites-infrastructures/links', response_model=SitesInfrastructuresLinksResponse)
async def get_sites_infrastructures_links(driver: Driver = Depends(get_neo4j_driver)) -> SitesInfrastructuresLinksResponse:
    settings = get_settings()
    graph = fetch_sites_infrastructures_with_links(driver=driver, database=settings.neo4j_database)

    logger.info(
        'Fetched Site/Infrastrcture graph',
        extra={
            'nodes_count': len(graph.get('nodes', [])),
            'edges_count': len(graph.get('edges', [])),
        },
    )

    return SitesInfrastructuresLinksResponse(**graph)


@router.get('/sites-infrastructures/links/qlik', response_model=QlikSitesInfrastructuresLinksResponse)
async def get_sites_infrastructures_links_for_qlik(
    driver: Driver = Depends(get_neo4j_driver),
) -> QlikSitesInfrastructuresLinksResponse:
    settings = get_settings()
    graph = fetch_sites_infrastructures_with_links_for_qlik(driver=driver, database=settings.neo4j_database)

    logger.info(
        'Fetched Site/Infrastructure graph for Qlik',
        extra={
            'nodes_count': len(graph.get('nodes', [])),
            'edges_count': len(graph.get('edges', [])),
            'facilities_count': len(graph.get('facilities', [])),
        },
    )

    return QlikSitesInfrastructuresLinksResponse(**graph)


@router.get('/nodes/{node_id}/link-map', response_model=NodeLinkMapResponse)
async def get_node_link_map(node_id: str, driver: Driver = Depends(get_neo4j_driver)) -> NodeLinkMapResponse:
    graph = fetch_node_link_map_until_effort(
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
