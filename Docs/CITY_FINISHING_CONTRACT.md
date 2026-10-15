# City finishing asset discovery

Root owns HLOD process, source edits, Unreal assets, GPU runs and Git.
Current city has 1472 shells and eight venues. Character models must remain unchanged.
HLOD is building from commit 6513f16; do not modify content while that process is running.

## Read-only discovery owner

Inspect D:/APP/HOUSE and D:/GAME/ANANTA/Assets/City/source_catalog.json and manifest.json.
Find unused photorealistic props or reusable authored room elements suited to the current empty areas:
bookshop wall displays, clinic cabinets, market goods, workshop tools, gallery art, rugs or curtains.
Exclude node_modules and build caches from broad file searches.
No subagents, no UE/Blender/game process, no downloads, purchases or Git operations.
Do not change existing source or assets.

May create only Saved/QA/CityFinishAssets.json.
Schema: {candidates: [{id, modelPath, texturePaths, sourceUrl, license, triangleCount,
  intendedVenue, alreadyImported, evidence}], gaps: [string]}.
Use null for facts unavailable from source files; do not infer a license from a filename.
For glTF, count triangles from index accessor counts and inspect PBR texture references without rendering.
For procedural HOUSE modules, report source path and relevant function name in evidence.
Prioritize three additions that would most clearly reduce the present primitive appearance.
Self-check every local path exists and differentiate already imported models from unused candidates.
Report once in at most 15 lines: file, three concrete candidates, validation, and remaining limitations.
