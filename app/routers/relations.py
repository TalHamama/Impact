import logging

from fastapi import APIRouter, Depends
from neo4j import Driver

from app.config import get_settings
from app.db.neo4j import fetch_relation_types, get_neo4j_driver
from app.schemas.graph import RelationTypesResponse

router = APIRouter(prefix='/relations', tags=['relations'])
logger = logging.getLogger(__name__)


@router.get('/types', response_model=RelationTypesResponse)
async def get_relation_types(driver: Driver = Depends(get_neo4j_driver)) -> RelationTypesResponse:
    settings = get_settings()
    relation_types = fetch_relation_types(driver=driver, database=settings.neo4j_database)

    logger.info('Fetched relation types', extra={'relation_types_count': len(relation_types)})

    return RelationTypesResponse(relation_types=relation_types)
