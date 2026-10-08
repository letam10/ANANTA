# Landscape source selection contract

- Read-only discovery for D:/GAME/ANANTA; prefer available D:/APP/HOUSE resources.
- Goal: find better realistic street trees or outdoor planters for the visibly coarse current plaza vegetation.
- Agent owns only Saved/QA/CityLandscapeAssetCandidates.md. Do not edit game assets, layout or Git.
- Report format: exact source path, model format, textures, license/provenance path, measured counts when cheap,
  expected import cost and recommendation. Select at most three candidates.
- Read current Assets/City/manifest.json and expansion_manifest.json to avoid proposing already used sources.
- Prefer textured PBR, sensible real scale, manageable foliage cost, opacity masks over translucent leaf stacks.
- Do not claim quality without a preview or asset evidence. Missing license or preview is an explicit open issue.
- Discovery only: no downloads, Blender/Unreal processes, model edits, installs, benchmarks or subagents.
- Use rg and manifests/catalogs first; do not dump every asset filename or revalidate unrelated assets.
- Self-check every cited path exists. If nothing suitable exists, report the concrete search coverage and gap.
- Report once, at most 15 lines, with the recommendation and outstanding checks; no interim status reports.
