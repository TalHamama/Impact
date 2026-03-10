# Graph Schema Context for Chatbot Generation

This file describes the current graph entities and relationships used in this project so a chatbot can generate additional compatible nodes and links.

## Goal

Use this document as the schema/context prompt when asking a chatbot to create more graph data for the Neo4j database.

The chatbot should:
- keep entity labels consistent with the existing schema
- keep relationship names consistent with the existing schema
- use realistic IDs, names, and properties
- avoid inventing unsupported labels or relationship types unless explicitly requested

## Canonical Entity Labels

These are the main labels used by the active FastAPI/Neo4j code:

1. `Site`
2. `Facility`
3. `Infrastructure`
4. `Component`
5. `System`
6. `Effort`

Additionally, the newer seed schema also includes:

7. `ResponsibleBody`

## Entity Descriptions and Typical Properties

### 1) `Site`
Represents a major physical site, base, area, or operational location.

Typical properties:
- `id`: unique string ID
- `name`: human-readable name
- `polygon`: geographic polygon or geometry payload
- `category`: optional classification
- `defence_with_iron_dome`: boolean or nullable
- `level_for_defence_with_upper_layer`: string or nullable

Example meaning:
- a regional base
- a central command site
- a logistics site

### 2) `Facility`
Represents a facility located inside a site.

Typical properties:
- `id`
- `name`
- `details_on_facility_purpose`
- `operational_significance_if_damaged`
- `sop_if_hit`

Example meaning:
- command center
- backup center
- power building
- operations room

### 3) `Infrastructure`
Represents a dependency or infrastructure asset used by facilities or sites.

Typical properties:
- `id`
- `name`
- `polygon`

Possible extra labels seen in seed data:
- `Fuel`
- `Electricity`

Example meaning:
- power grid
- fuel farm
- water supply
- communication backbone

### 4) `Component`
Represents a component contained by a facility.

Typical properties:
- `id`
- `name`
- `migon`
- `hastara`
- `recovery_capability`
- `recovery_capability_details`

Example meaning:
- radar
- communications unit
- switchgear
- sensor array

### 5) `System`
Represents a larger system that a facility belongs to.

Typical properties:
- `id`
- `name`

Example meaning:
- air defense system
- monitoring system
- command-and-control system

### 6) `Effort`
Represents an effort/outcome/capability that components support.

Typical properties:
- `id`
- `name`

Example meaning:
- alerting effort
- recovery effort
- communications effort

### 7) `ResponsibleBody`
Represents an organizational or functional body responsible for a facility.

Typical properties:
- `id`
- `name`

Example meaning:
- air defense branch
- energy operations team
- logistics command

## Canonical Relationship Types

These are the main relationship types used by the current schema and code.

### 1) `CONTAINS`
Used for hierarchical containment.

Allowed patterns seen in the project:
- `Site` -> `Facility`
- `Facility` -> `Component`

Meaning:
- a site contains facilities
- a facility contains components

### 2) `BACKUP_FOR`
Allowed pattern:
- `Facility` -> `Site`

Meaning:
- a facility acts as a backup for a site

### 3) `DEPENDS`
Allowed pattern:
- `Facility` -> `Infrastructure`

Meaning:
- a facility depends on a certain infrastructure asset

### 4) `PART_OF_SYSTEM`
Allowed pattern:
- `Facility` -> `System`

Meaning:
- a facility belongs to or operates as part of a larger system

### 5) `SUPPORT`
Allowed pattern:
- `Component` -> `Effort`

Meaning:
- a component supports an effort/capability/outcome

### 6) `RESPONSIBLE_FOR`
Allowed pattern seen in the newer seed schema:
- `Facility` -> `ResponsibleBody`

Meaning:
- a facility is operated, owned, or overseen by a responsible body

## Recommended Topology Rules

When generating new data, prefer this structure:

`Site` -> `Facility` -> `Component` -> `Effort`

Additional optional connections:
- `Facility` -> `Infrastructure`
- `Facility` -> `System`
- `Facility` -> `ResponsibleBody`
- `Facility` -> `Site` using `BACKUP_FOR`

## Important Link-Map Behavior

The current link-map route starts from a given node and traverses the graph until it reaches `Effort` nodes.

Important implications:
- `Effort` nodes should be terminal endpoints
- `Effort` nodes should be included in results
- traversal should not continue beyond `Effort`
- cycles may exist in the graph, so generated data should avoid accidental explosive fan-out unless intentionally modeled

For the link-map response specifically, the route currently returns only these node types inside the map payload:
- `Site`
- `Facility`
- `Component`
- `Effort`

`Infrastructure` and `System` may still participate in traversal or other endpoints, but they are not the main visible node types in the link-map payload.

## ID Guidelines

Use stable, unique, readable IDs.

Recommended patterns:
- `site_north`
- `site_central`
- `facility_north_command`
- `facility_backup_east`
- `infra_main_grid`
- `infra_fuel_farm_alpha`
- `component_radar_alpha`
- `system_air_defense`
- `effort_alerting`
- `rb_energy_ops`

## Data Generation Rules for Chatbot

When generating new entities, follow these rules:

1. Always assign a unique `id`
2. Always assign a meaningful `name`
3. Use only the canonical labels unless explicitly asked otherwise
4. Use only the canonical relationship types unless explicitly asked otherwise
5. Prefer realistic military/operations/infrastructure naming if matching the current domain
6. Keep relationship direction consistent with the schema above
7. Do not connect `Effort` outward to more nodes in normal generation
8. Prefer medium-density graphs rather than connecting everything to everything
9. Keep each facility semantically coherent:
   - one site owner
   - zero or more components
   - zero or more infrastructure dependencies
   - zero or one system
   - zero or one responsible body
10. Components should usually support one or more efforts

## Example Valid Pattern

- `Site(site_north)` `CONTAINS` `Facility(facility_north_command)`
- `Facility(facility_north_command)` `CONTAINS` `Component(component_radar_alpha)`
- `Facility(facility_north_command)` `DEPENDS` `Infrastructure(infra_main_grid)`
- `Facility(facility_north_command)` `PART_OF_SYSTEM` `System(system_air_defense)`
- `Facility(facility_north_command)` `RESPONSIBLE_FOR` `ResponsibleBody(rb_air_defense)`
- `Component(component_radar_alpha)` `SUPPORT` `Effort(effort_alerting)`

## Legacy / Non-Canonical Items Found in Older Seed Files

Older seed files contain spelling variants and experimental labels/relationships such as:
- `Componenet`
- `Infrastrcture`
- `CONTAINES`
- `DEPENDENCY`
- `INTERCHANGEABLE`
- `INFLUENCE`
- `HAS_REPORT`
- `HAS_MAINTENANCE`
- `Report`
- `Maintenance`

These should be treated as legacy or test-only unless you explicitly want the chatbot to generate data for those older schemas.

## Recommended Prompt to Give a Chatbot

You can send the following instruction together with this file:

> Generate additional Neo4j graph data that follows the schema in this document.  
> Use only canonical entity labels and relationship types.  
> Create realistic new nodes and relationships with unique IDs and coherent domain logic.  
> Prefer outputs in structured JSON or Cypher `MERGE` statements.  
> Do not use legacy misspelled labels or relationship names.

