import logging

from fastapi import APIRouter, Depends
from neo4j import Driver

from app.config import get_settings
from app.db.neo4j import (
    fetch_sites_infrastructures_with_links,
    fetch_sites_infrastructures_with_links_for_qlik,
    get_neo4j_driver,
)
from app.schemas.graph import QlikSitesInfrastructuresLinksResponse, SitesInfrastructuresLinksResponse

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
