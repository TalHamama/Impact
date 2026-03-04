from __future__ import annotations

from collections.abc import Generator
from typing import Any

from neo4j import Driver, GraphDatabase
from neo4j.exceptions import Neo4jError

from app.utils.errors import DatabaseError, NotFoundError


class Neo4jDriver:
    _instance: Neo4jDriver | None = None

    def __init__(self, uri: str, user: str, password: str) -> None:
        self._driver: Driver = GraphDatabase.driver(uri, auth=(user, password))
        self._driver.verify_connectivity()

    @classmethod
    def init(cls, uri: str, user: str, password: str) -> Neo4jDriver:
        if cls._instance is None:
            cls._instance = cls(uri=uri, user=user, password=password)
        return cls._instance

    @classmethod
    def get_instance(cls) -> Neo4jDriver:
        if cls._instance is None:
            raise RuntimeError('Neo4jDriver is not initialized.')
        return cls._instance

    @property
    def driver(self) -> Driver:
        return self._driver

    @classmethod
    def close(cls) -> None:
        if cls._instance is not None:
            cls._instance._driver.close()
            cls._instance = None


def get_neo4j_driver() -> Generator[Driver, None, None]:
    yield Neo4jDriver.get_instance().driver


def fetch_entity_relationships(driver: Driver, entity_id: str, database: str | None = None) -> list[dict[str, Any]]:
    check_query = 'MATCH (n {id: $entity_id}) RETURN n LIMIT 1'
    links_query = '''
    MATCH (n {id: $entity_id})-[r]-(m)
    RETURN
      type(r) AS relationship_type,
      CASE
        WHEN startNode(r) = n THEN 'OUTGOING'
        ELSE 'INCOMING'
      END AS direction,
      m.id AS other_node_id,
      labels(m) AS other_node_labels,
      properties(m) AS other_node_properties,
      properties(r) AS relationship_properties
    '''

    try:
        with driver.session(database=database) if database else driver.session() as session:
            entity_exists = session.run(check_query, entity_id=entity_id).single()
            if entity_exists is None:
                raise NotFoundError(
                    message=f'Entity with id "{entity_id}" was not found.',
                    details={'entity_id': entity_id},
                )

            records = session.run(links_query, entity_id=entity_id)
            results: list[dict[str, Any]] = []

            for record in records:
                results.append(
                    {
                        'relationship_type': record['relationship_type'],
                        'direction': record['direction'],
                        'other_node': {
                            'id': record['other_node_id'],
                            'labels': record['other_node_labels'] or [],
                            'properties': record['other_node_properties'] or {},
                        },
                        'relationship_properties': record['relationship_properties'] or {},
                    }
                )

            return results
    except NotFoundError:
        raise
    except Neo4jError as exc:
        raise DatabaseError(
            message=str(exc) or 'Failed to query Neo4j.',
            details={
                'entity_id': entity_id,
                'database': database,
                'neo4j_error': str(exc),
                'neo4j_code': getattr(exc, 'code', None),
            },
        ) from exc
