# HLOD PBR and night-window repair

Root owns Unreal processes, imports, map edits, screenshots, HLOD runs and Git.
The previous HLOD job was deliberately stopped after confirming missing PBR bake channels.
No subagents, Unreal/Blender/game launch, Content writes or Git in the delegated task.

## Owned source files

- Tools/Editor/CreateCityWindowLighting.py
- Tools/Editor/CreateCityHLOD.py
- Tools/Editor/CityHLODMaterial.py (new helper)
- Tools/Editor/VerifyCityHLODPBR.py (new independent saved-asset readback)

## Verified data and interfaces

Read Saved/QA/CityHLODSettings.json and Tools/Editor/InspectCityHLODSettings.py.
UE5.8.3 source is C:/Program Files/Epic Games/UE_5.8/Engine.
Layer /Game/ANANTA/City/HLOD/City_HLOD is MESH_SIMPLIFY, cell25600, range120000.
Builder hlod_builder_settings is HLODBuilderMeshSimplifySettings.
Its mesh_simplify_settings has material_settings; normal_map true but emissive_map,
roughness_map and metallic_map are false. calculate_correct_lod_model is false.
Template is /Engine/EngineMaterials/FlattenMaterial_VT, an actual Material.
It has use_material_attributes true. get_material_property_input_node for EMISSIVE_COLOR
returns MaterialExpressionStaticSwitchParameter; verify actual attribute wiring from engine APIs.
MaterialEditingLibrary also exposes get_material_property_input_node_output_name.
Keep all existing template texture/scalar/static parameters and virtual texture compatibility.
Do not edit engine content. Duplicate the template into /Game/ANANTA/City/Materials.

Window material /Game/ANANTA/City/Materials/M_City_WindowGlass currently computes occupied
windows from WorldPosition and MPC_CityLighting.NightAmount, default0.
Eight source facade/storefront meshes share it. Preserve their slots and runtime appearance.

## Required repair

CreateCityWindowLighting.main remains the entry point and must remain idempotent.
Use a supported MaterialProxyReplace path so baking sees fully lit occupied windows,
while normal rendering still multiplies by NightAmount. Keep the collection default0.
Create a city HLOD template that preserves the engine material graph and multiplies its
baked emissive result by the same NightAmount at runtime, including material-attribute wiring.
CreateCityHLOD.main sets that template, enables normal/emissive/roughness/metallic bake channels,
and enables calculate_correct_lod_model. Preserve cell/range and sampling settings for now.
Do not enable identical-mesh bake grouping because project materials use world-space coordinates.

VerifyCityHLODPBR.main opens only saved layer/material assets, never a map, and writes
Saved/QA/CityHLODPBRReadback.json. Assert channels, template, collection default0 and connections
of both source proxy replacement and HLOD runtime modulation. Log CITY_HLOD_PBR_READBACK_OK.
Check actual UE source/API support before implementing material-attribute input changes.
Root will run CreateCityWindowLighting.py, CreateCityHLOD.py, then VerifyCityHLODPBR.py.

## Self-check and reporting

Run Python syntax checks; keep files under300 lines and about120 columns.
Add short Vietnamese comments for the proxy/attribute graph logic.
No claim of Unreal execution or visual acceptance; root owns those remaining gates.
Report once <=15 lines: changed files, graph approach, static checks, exact run order and open risks.
