# Interior finishing contract

Root owns Unreal Content, map placement, runtime, HLOD, floor textures and Git.
Current HLOD job must not be interrupted or supplied changed Content while it runs.
No character changes, no subagents, no desktop applications, no publishing.

## Model asset owner

Own only Tools/CityAssets/finishing_*.py, Assets/City/Finishing/**,
Assets/City/finishing_manifest.json and Saved/QA/CityFinishingAssets/**.
Read existing Tools/CityAssets/{geometry,materials,build_city_assets,expansion_build}.py.
Read Blender expert and relevant shading/UV skills plus required references.
Prepare GlamVelvetSofa from D:/APP/HOUSE/assets/models/GlamVelvetSofa and two original
models: tailored woven rug and pleated linen curtain with rod/rings/weighted hem.
Record source attribution exactly from local README; do not infer CC0 for the sofa.
Original rug/curtain geometry may reuse existing City_rough_linen texture with its source license.

## Shared schema and constants

Use the schema of Assets/City/expansion_manifest.json:
schemaVersion=1, units=cm, upAxis=Z, forwardAxis=X, meshes, materials, sourceFiles.
Every mesh: id, file relative to Assets/City, boundsCm {min,max,size}, materialSlots,
triangles, source, license, sha256, lodRecommendation.
IDs: House_GlamVelvetSofa, InteriorWovenRug, InteriorLinenCurtain.
Rug dimensions 300 x 200 x 1.5 cm; curtain including rod 240 x 24 x 260 cm.
Sofa retains measured physical dimensions from source; origin bottom centre.
All FBX exports match existing axis convention X forward/Z up; document visible front direction.
Budgets: sofa <=6000 triangles; rug <=2500; curtain <=7000; max 4 material slots each.
Use existing material IDs where suitable, new ones prefixed Finish_.
New material records use baseColor/normal/roughness/ao/metallic relative paths or null,
baseColorFactor RGBA, metallicFactor, roughnessFactor, normalConvention OpenGL, twoSided if needed.
Do not require unsupported glTF sheen at runtime; document appearance approximation.
All source textures must remain portable, preserve raw sources and SHA256 checksums.

## Verification

Run Blender headless only, CPU rendering with <=2 threads while HLOD is active.
Use --background --factory-startup --python-exit-code 1; never start Unreal.
Verify FBX roundtrip dimensions/UV/material slots, no degenerate faces, budgets and hashes.
Render material previews of all three models at >=960 px; inspect images yourself.
Write audit JSON with numeric results, warnings and preview paths.
No claim that assets are imported into Unreal or passed in-game.
Keep scripts under about 300 lines; no edits to existing shared helpers.
Report once, <=15 lines: files, asset dimensions/triangles, checks, unresolved issues.
