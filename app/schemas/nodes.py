from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas.entities import EntityLink, OtherNode


class NodeDetails(BaseModel):
    id: str | None = None
    labels: list[str] = Field(default_factory=list)
    properties: dict[str, Any] = Field(default_factory=dict)


class ArtifactItem(BaseModel):
    source: Literal['property', 'linked_node']
    id: str | None = None
    labels: list[str] = Field(default_factory=list)
    relationship_type: str | None = None
    properties: dict[str, Any] = Field(default_factory=dict)


class MapEdge(BaseModel):
    source_id: str | None = None
    target_id: str | None = None
    relationship_type: str
    relationship_properties: dict[str, Any] = Field(default_factory=dict)


class HopMap(BaseModel):
    nodes: list[OtherNode] = Field(default_factory=list)
    edges: list[MapEdge] = Field(default_factory=list)


class LinksMap(BaseModel):
    hop_1: HopMap
    hop_2: HopMap


class NodeDetailsResponse(BaseModel):
    node: NodeDetails
    direct_links: list[EntityLink] = Field(default_factory=list)
    maintenance: list[ArtifactItem] = Field(default_factory=list)
    reports: list[ArtifactItem] = Field(default_factory=list)
    links_map: LinksMap


class NodeLinksMapResponse(BaseModel):
    node: NodeDetails
    direct_links: list[EntityLink] = Field(default_factory=list)
    links_map: LinksMap


class NodeFullMapResponse(BaseModel):
    node_id: str
    nodes: list[OtherNode] = Field(default_factory=list)
    edges: list[MapEdge] = Field(default_factory=list)
