from typing import Any

from pydantic import BaseModel, Field


class GraphRelation(BaseModel):
    source_id: str | None = None
    target_id: str | None = None
    relationship_type: str
    relationship_properties: dict[str, Any] = Field(default_factory=dict)


class GraphNodeSummary(BaseModel):
    id: str | None = None
    label: str | None = None
    labels: list[str] = Field(default_factory=list)
    name: str | None = None
    location: Any | None = None
    properties: dict[str, Any] = Field(default_factory=dict)
    relationship_types: list[str] = Field(default_factory=list)


class GraphOverviewResponse(BaseModel):
    relation_types: list[str] = Field(default_factory=list)
    nodes: list[GraphNodeSummary] = Field(default_factory=list)
    relations: list[GraphRelation] = Field(default_factory=list)


class RelationTypesResponse(BaseModel):
    relation_types: list[str] = Field(default_factory=list)


class SiteInfrastructureNode(BaseModel):
    id: str | None = None
    node_type: str | None = None
    name: str | None = None
    polygon: Any | None = None


class SiteInfrastructureEdge(BaseModel):
    source_id: str | None = None
    target_id: str | None = None
    relationship_type: str


class SitesInfrastructuresLinksResponse(BaseModel):
    nodes: list[SiteInfrastructureNode] = Field(default_factory=list)
    edges: list[SiteInfrastructureEdge] = Field(default_factory=list)
