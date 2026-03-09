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


class QlikSiteInfrastructureNode(BaseModel):
    id: str | None = None
    node_type: str | None = None
    name: str | None = None
    polygon: Any | None = None
    corrected_polygon: str | None = None
    center_x: float | None = None
    center_y: float | None = None


class QlikFacilitySummary(BaseModel):
    id: str | None = None
    site_id: str | None = None
    name: str | None = None
    system_name: list[str] = Field(default_factory=list)
    department_name: list[str] = Field(default_factory=list)
    effort_name: list[str] = Field(default_factory=list)
    site_level_for_defence_with_upper_layer: str | None = None
    backup_site: list[str] = Field(default_factory=list)
    dependent_infrastructures: list[str] = Field(default_factory=list)
    site_defence_with_iron_dome: str | None = None
    facility_purpose_details: str | None = None
    operational_significance_if_damaged: str | None = None


class QlikSitesInfrastructuresLinksResponse(BaseModel):
    nodes: list[QlikSiteInfrastructureNode] = Field(default_factory=list)
    edges: list[SiteInfrastructureEdge] = Field(default_factory=list)
    facilities: list[QlikFacilitySummary] = Field(default_factory=list)


class LinkMapNode(BaseModel):
    id: str | None = None
    name: str | None = None
    node_type: str | None = None


class LinkMapEdge(BaseModel):
    source_id: str | None = None
    target_id: str | None = None
    relationship_type: str


class LinkMapPayload(BaseModel):
    nodes: list[LinkMapNode] = Field(default_factory=list)
    edges: list[LinkMapEdge] = Field(default_factory=list)


class NodeLinkMapResponse(BaseModel):
    node: LinkMapNode
    links_map: LinkMapPayload


class NodeRawResponse(BaseModel):
    id: str
    labels: list[str] = Field(default_factory=list)
    properties: dict[str, Any] = Field(default_factory=dict)
