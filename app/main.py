import logging
import time
import uuid
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.db.neo4j import Neo4jDriver, check_neo4j_ready
from app.routers.graph import router as graph_router
from app.routers.nodes import router as nodes_router
from app.routers.relations import router as relations_router
from app.utils.errors import AppError
from app.utils.responses import error_response, success_response

settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level, logging.INFO),
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
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


docs_enabled = settings.app_env != 'production'
app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
    docs_url='/docs' if docs_enabled else None,
    redoc_url='/redoc' if docs_enabled else None,
    openapi_url='/openapi.json' if docs_enabled else None,
)
app.include_router(graph_router)
app.include_router(nodes_router)
app.include_router(relations_router)

if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

if settings.trusted_hosts:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_hosts)


@app.middleware('http')
async def request_context_middleware(request: Request, call_next):
    request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    response.headers['X-Request-ID'] = request_id
    logger.info(
        'request_complete',
        extra={
            'request_id': request_id,
            'method': request.method,
            'path': request.url.path,
            'status_code': response.status_code,
            'duration_ms': duration_ms,
        },
    )
    return response


@app.get('/health')
async def health() -> JSONResponse:
    return success_response({'status': 'ok'})


@app.get('/ready')
async def ready() -> JSONResponse:
    driver = Neo4jDriver.get_instance().driver
    if check_neo4j_ready(driver=driver, database=settings.neo4j_database):
        return success_response({'status': 'ready'})
    return error_response(
        error_type='ServiceUnavailable',
        message='Service is not ready.',
        details={'dependency': 'neo4j'},
        status_code=503,
    )


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
    if settings.expose_error_details:
        message = str(exc) or 'An unexpected error occurred.'
        details: dict[str, Any] | None = {'exception': repr(exc)}
    else:
        message = 'An unexpected error occurred.'
        details = None

    return error_response(
        error_type='InternalServerError',
        message=message,
        details=details,
        status_code=500,
    )


def run() -> None:
    reload_enabled = settings.app_reload
    workers = 1 if reload_enabled else settings.app_workers
    uvicorn.run(
        'app.main:app',
        host=settings.app_host,
        port=settings.app_port,
        reload=reload_enabled,
        workers=workers,
        log_level=settings.log_level.lower(),
    )


if __name__ == '__main__':
    run()
