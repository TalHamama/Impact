import logging

from fastapi import APIRouter, Depends
from neo4j import Driver

from app.config import get_settings
from app.db.neo4j import fetch_entity_relationships, get_neo4j_driver
from app.schemas.entities import EntityLinksResponse

router = APIRouter(prefix='/entities', tags=['entities'])
logger = logging.getLogger(__name__)


@router.get('/{entity_id}/links', response_model=EntityLinksResponse)
async def get_entity_links(entity_id: str, driver: Driver = Depends(get_neo4j_driver)) -> EntityLinksResponse:
    settings = get_settings()
    links = fetch_entity_relationships(driver=driver, entity_id=entity_id, database=settings.neo4j_database)

    logger.info(
        'Fetched entity links',
        extra={'entity_id': entity_id, 'links_count': len(links)},
    )

    return EntityLinksResponse(entity_id=entity_id, count=len(links), links=links)
