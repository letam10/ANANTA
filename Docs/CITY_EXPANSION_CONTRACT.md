# City expansion contract — 2026-10-08

The active goal supersedes the previous two-interior restriction. Preserve all character models.
Keep existing mission anchors, old slice, player car and normal save slots. Background work only.
Root owns Tools/Editor, map/Config integration, layout, builds, runtime journeys and final status.
No agent starts Unreal, a build, another agent, commits, downloads paid assets or changes normal saves.
Keep new code files below about 300 lines and 120 columns; Vietnamese comments for complex logic.

## Asset module owner

May create/edit only Tools/CityAssets/expansion_*.py, Assets/City/Expansion/**,
Assets/City/expansion_manifest.json and Saved/QA/CityExpansionAssets/**.
Existing source helpers and Assets/City textures are read-only reusable inputs.
Use the existing geometry/material helpers and FBX export convention. Read Blender skills.
Deliver new meshes: FacadeBrickArch, FacadeBay, FacadeArtDeco, FacadeIndustrial,
TreeBroadleaf, TreeColumnar, BusShelter, MarketStall, TrashBin, BikeRack, StreetSign.
Facades are 400 cm wide x 320 cm high, front -Y, origin at bottom centre; depth under 150 cm.
Facades need visible geometry differences, recessed glazing, trim and existing textured PBR slots.
Trees have trunks/branches and individual clustered leaf geometry, varied silhouettes, no opaque sphere crowns.
Tree height 600-900 cm; crown diameter 350-650 cm. Props use metre-realistic dimensions.
Bus shelter has a walkable open front, seating, glazing and roof; market stall has canopy/counter.
Use UVs, bevels, material separation. Triangle targets: facade under 6000, each tree under 15000,
other props under 12000. No character meshes. Geometry itself must not embed whole street scenes.
Blender executable discovery is allowed. Run background factory startup, python-exit-code 1.
Manifest schema matches Assets/City/manifest.json: schemaVersion=1, units=cm, upAxis=Z,
meshes [{id,file,boundsCm,materialSlots,triangles,source,license,sha256}], materials, sourceFiles.
All paths are relative to Assets/City. Materials may reference existing material IDs without redefining them.
Root imports only new meshes and newly declared materials. Existing mesh files must remain untouched.
Self-check: source syntax, FBX reimport bounds/UV/materials, triangle counts and hashes; produce and inspect
a labelled Blender rendered review sheet. Final report once <=15 lines with exact commands, outputs/issues.

## Runtime service module owner

May create CityServiceInteractable.h/.cpp and CityServiceState.h/.cpp under Source/ANANTA Public/Private/City,
new service automation in Private/Tests, and edit only ANANTACityInteractable.h (virtual dispatch),
ANANTACityState.h/.cpp (additive save data), ANANTACitySubsystem.h/.cpp (service state/message),
ANANTACityHUD.cpp (one short service/inventory message). No controller edits or character model changes.
ACityServiceInteractable derives AANANTACityInteractable; IsAvailable, Interact and GetPrompt become virtual.
Expose ECityServiceKind {Rest, Heal, Supplies, Read}, editable ServiceKind, DisplayName and Description.
Inherited InteractionId is the stable authored ID. Base mission enum and mission state stay unchanged.
Service must require a player pawn, <=320 cm distance and unobstructed visibility; recheck in Interact.
Rest restores health and saves progress; Heal restores health. Supplies adds one inventory unit once per ID.
Read records a discovered location once per ID and displays the authored description.
Keep supplies/read actors visible after collection; prompt reports used/discovered state, repeats add nothing.
Add save fields with defaults so schema version 1 files remain readable: visited IDs, claimed supply IDs,
and supplies count. Validation rejects impossible counts, none IDs; old empty fields remain valid.
Support service status HUD plus discovered location/supply counts, without obscuring mission HUD.
IDs root will author: Cafe_Rest, Apartment_Rest, Bookshop_Read, Clinic_Heal, Market_Supplies,
Gallery_Read, Workshop_Read, Transit_Read. Optional additional supply IDs begin Supply_.
All service claims save via existing QA-aware subsystem. Do not introduce another persistence system.
Focused automation must check repeat claims, invalid IDs/counts, additive save serialization and unchanged mission.
No builds (root serializes UE work). Self-check source and test structure; report once <=15 lines,
including public API/property names and anything root must verify through compile/runtime.
