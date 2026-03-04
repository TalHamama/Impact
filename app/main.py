import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.db.neo4j import Neo4jDriver
from app.routers.entities import router as entities_router
from app.utils.errors import AppError
from app.utils.responses import error_response, success_response

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    Neo4jDriver.init(
        uri=settings.neo4j_uri,
        user=settings.neo4j_user,
        password=settings.neo4j_password,
    )
    logger.info('Neo4j driver initialized')
    try:
        yield
    finally:
        Neo4jDriver.close()
        logger.info('Neo4j driver closed')


app = FastAPI(title='Impact API', lifespan=lifespan)
app.include_router(entities_router)


@app.get('/health')
async def health() -> JSONResponse:
    return success_response({'status': 'ok'})


@app.exception_handler(AppError)
async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    logger.warning(
        'Application error',
        extra={'error_type': exc.error_type, 'details': exc.details},
    )
    return error_response(
        error_type=exc.error_type,
        message=exc.message,
        details=exc.details,
        status_code=exc.status_code,
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    details: list[dict[str, Any]] = [
        {
            'field': '.'.join(str(loc) for loc in err.get('loc', [])),
            'message': err.get('msg', 'Invalid value'),
            'type': err.get('type', 'validation_error'),
        }
        for err in exc.errors()
    ]

    return error_response(
        error_type='ValidationError',
        message='Request validation failed.',
        details={'errors': details},
        status_code=422,
    )


@app.exception_handler(Exception)
async def generic_error_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.exception('Unhandled exception: %s', exc)
    return error_response(
        error_type='InternalServerError',
        message=str(exc) or 'An unexpected error occurred.',
        details={'exception': repr(exc)},
        status_code=500,
    )
