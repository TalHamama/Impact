import logging

from fastapi import APIRouter, Depends
from neo4j import Driver

from app.config import get_settings
from app.db.neo4j import fetch_sites_infrastructures_with_links, get_neo4j_driver
from app.schemas.graph import SitesInfrastructuresLinksResponse

router = APIRouter(prefix='/graph', tags=['graph'])
logger = logging.getLogger(__name__)


@router.get('/sites-infrastructures/links', response_model=SitesInfrastructuresLinksResponse)
async def get_sites_infrastructures_links(driver: Driver = Depends(get_neo4j_driver)) -> SitesInfrastructuresLinksResponse:
    settings = get_settings()
    items = fetch_sites_infrastructures_with_links(driver=driver, database=settings.neo4j_database)

    logger.info('Fetched Site/Infrastrcture links', extra={'count': len(items)})

    return SitesInfrastructuresLinksResponse(count=len(items), items=items)
