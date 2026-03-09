from __future__ import annotations

from typing import Any

from neo4j import Driver

from app.db.neo4j import fetch_node_raw


def get_node_raw_service(driver: Driver, node_id: str, database: str) -> dict[str, Any]:
    return fetch_node_raw(driver=driver, node_id=node_id, database=database)
