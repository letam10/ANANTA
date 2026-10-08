# Clinic and transit fixture replacements — 2026-10-08

## Shared contract

- D:/GAME/ANANTA, UE 5.8.3 and Blender 5.2; centimetres, Z up, bottom-centre origins.
- The full HLOD job is live. No agent may run Unreal, use GPU rendering, change Content or Git.
- Preserve characters, services, map coordinates and ordinary gameplay routes.
- Root owns placement, imports, progress documentation, runtime acceptance and commits.
- No subagents beneath the asset agent. One CPU Blender job, at most two threads.

## Assets and ownership

- ClinicSupplyCabinet: bounds [-115,-37,0] to [115,37,184] cm; maximum 7,000 triangles.
- Cabinet replaces a body, three doors and three handles as one model; physical drawers remain static.
- Use detailed bevels, recessed doors, hardware, feet/base and original labelled supply compartments.
- Use opaque coated metal or frosted panels; no new translucent shader or medical brand logos.
- TransitRouteDisplay: bounds [-185,-12,0] to [185,12,150] cm; maximum 4,000 triangles.
- Display replaces the frame, panel, four route lines and four stop blocks.
- Use a slim metal frame, protected matte display, mounting details and a readable city guide texture.
- Guide title: NEIGHBORHOOD GUIDE. Show all eight accessible venues using actual room centre coordinates.
- Source of venue coordinates: Tools/Editor/CityVenueDressing.py ROOMS; X east, Y north on the guide.
- Numbered map markers and a matching clear legend; do not invent active transit routes or gameplay features.
- Both visible fronts are Blender -Y, exported UE +Y. Root will place with yaw 180 facing into the rooms.
- Maximum four material slots per asset; material prefix VenueFixture_; texture maximum 2048 px per side.
- Use original geometry/art plus licensed existing PBR. Keep source provenance and hashes.
- Asset files: Assets/City/VenueFixtures/** and Assets/City/venue_fixture_manifest.json.
- Manifest schemaVersion 1 follows interior_architecture_manifest.json; include exact mesh bounds and slots.
- Include guideVenueCoordinates with all eight source centres and the coordinate convention in the manifest.
- Scripts: Tools/CityAssets/venue_fixture_*.py; optional importer Tools/Editor/ImportCityVenueFixtures.py.
- Evidence: Saved/QA/CityVenueFixtureAssets/**. Do not edit layout, shared import helpers or QA files.

## Root placement contract

- Cabinet root label Dressing_Clinic_MedicalStorage; location relative to room centre (410,650.5,15).
- Remove Dressing_Clinic_StorageDoor0..2 and StorageHandle0..2; keep objects on top at Z 199.
- Cabinet collision remains enabled. Overall bounds equal the old body plus doors and handles.
- Display root label Dressing_Transit_RouteFrame; relative location (-370,788,115), no collision.
- Remove Dressing_Transit_RouteBoard, RouteLine0..3 and RouteStop0..3.
- Exact combined extents preserve wall clearance. No other actor or interaction changes.

## Done criteria

- Save .blend, FBX, texture/material metadata and provenance; each source code file under 300 lines.
- Run factory-startup Blender with python-exit-code 1; validate FBX roundtrip bounds, triangle budgets,
  finite geometry, no degenerate faces or UV faces, material slots, source hashes and guide coordinates.
- Render front and three-quarter CPU views of each asset; inspect all four images and fix visible defects.
- Inspect the guide at its delivered resolution to confirm correct labels and readable marker numbering.
- Report once, at most 15 lines: files, checks, triangle counts, evidence and remaining Unreal validation.
