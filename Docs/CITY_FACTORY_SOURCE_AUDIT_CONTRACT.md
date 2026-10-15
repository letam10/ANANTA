# Factory source audit contract

Root engine ApplyCityExpansion is running; no other engine/build may start.
Audit the current CityMetroDistrict.factory implementation from commit cf96b47ce.
Ownership: Tools/QA/VerifyCityFactorySource.py, Tools/QA/TestCityFactorySource.py,
Docs/CITY_FACTORY_SOURCE_AUDIT.md only. Do not edit factory source, maps or other files.
Do not spawn agents, commit or push. Report once <=15 lines.

API: audit_factory() -> dict with passed, issues, instanceCount, sourceFile,
sourceSha256, reserveCm, accessLaneCm, geometryChecks; units centimetres.
Main writes Saved/QA/CityFactorySourceAudit.json and prints a compact status.
Geometry concerns must report exact dimensions/bounds, not source-token matching.
Use a recording layout implementing box(material, location, size, collision=True)
and add(mesh, location, scale=(1,1,1), yaw=0, material=None, collision=True, hidden=False).
Call real factory using SITES Factory entry. Derive Cube AABBs exactly.
Read manifests for non-Cube mesh bounds when required, do not guess dimensions.
Keep shell footprint/reserve and public access lane clear using actual source values.
Measure shutter-to-shell mounting gaps and shutter-to-apron vertical clearance.
Identify current 700 cm bollards as inappropriate human-scale safety posts; accepted
post height range 80-140 cm is the documented target, not a universal engine rule.
Check visual collisions with planters when manifest bounds support it.
Do not claim collision/visual/player acceptance from source checks.
Tests should prove issues are detected in the real source and that corrected bounds
would pass the specific geometric predicate; do not reproduce implementation tokens.
Self-check unittest, py_compile, diff whitespace and <300 lines/file, <120 columns.
