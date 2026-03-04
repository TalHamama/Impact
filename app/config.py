import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True, slots=True)
class Settings:
    neo4j_uri: str
    neo4j_user: str
    neo4j_password: str
    neo4j_database: str


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        neo4j_uri=os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
        neo4j_user=os.getenv('NEO4J_USER', 'neo4j'),
        neo4j_password=os.getenv('NEO4J_PASSWORD', 'password'),
        neo4j_database=os.getenv('NEO4J_DATABASE', 'neo4j'),
    )
