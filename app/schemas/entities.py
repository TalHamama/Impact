from typing import Any, Literal

from pydantic import BaseModel, Field


class OtherNode(BaseModel):
    id: str | None = None
    labels: list[str] = Field(default_factory=list)
    properties: dict[str, Any] = Field(default_factory=dict)


class EntityLink(BaseModel):
    relationship_type: str
    direction: Literal['OUTGOING', 'INCOMING']
    other_node: OtherNode
    relationship_properties: dict[str, Any] = Field(default_factory=dict)


class EntityLinksResponse(BaseModel):
    entity_id: str
    count: int
    links: list[EntityLink] = Field(default_factory=list)
