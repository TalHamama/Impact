import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True, slots=True)
class Settings:
    app_name: str
    app_env: str
    log_level: str
    debug: bool
    expose_error_details: bool
    app_host: str
    app_port: int
    app_reload: bool
    app_workers: int
    app_enable_docs: bool
    cors_origins: list[str]
    trusted_hosts: list[str]
    neo4j_uri: str
    neo4j_user: str
    neo4j_password: str
    neo4j_database: str


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    app_env = os.getenv('APP_ENV', 'development').strip().lower()
    debug_default = app_env != 'production'
    expose_default = app_env != 'production'

    return Settings(
        app_name=os.getenv('APP_NAME', 'Impact API'),
        app_env=app_env,
        log_level=os.getenv('LOG_LEVEL', 'INFO').upper(),
        debug=_as_bool(os.getenv('DEBUG'), debug_default),
        expose_error_details=_as_bool(os.getenv('EXPOSE_ERROR_DETAILS'), expose_default),
        app_host=os.getenv('APP_HOST', '127.0.0.1'),
        app_port=_as_int(os.getenv('APP_PORT'), 8000),
        app_reload=_as_bool(os.getenv('APP_RELOAD'), app_env != 'production'),
        app_workers=max(_as_int(os.getenv('APP_WORKERS'), 1), 1),
        app_enable_docs=_as_bool(os.getenv('APP_ENABLE_DOCS'), app_env != 'production'),
        cors_origins=_as_csv(os.getenv('CORS_ORIGINS', '*')),
        trusted_hosts=_as_csv(os.getenv('TRUSTED_HOSTS', '*')),
        neo4j_uri=os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
        neo4j_user=os.getenv('NEO4J_USER', 'neo4j'),
        neo4j_password=os.getenv('NEO4J_PASSWORD', 'password'),
        neo4j_database=os.getenv('NEO4J_DATABASE', 'neo4j'),
    )


def _as_csv(value: str | None) -> list[str]:
    if value is None:
        return []
    return [item.strip() for item in value.split(',') if item.strip()]


def _as_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    normalized = value.strip().lower()
    return normalized in {'1', 'true', 'yes', 'on'}


def _as_int(value: str | None, default: int) -> int:
    if value is None:
        return default
    try:
        return int(value.strip())
    except ValueError:
        return default
