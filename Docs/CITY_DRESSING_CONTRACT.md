# City dressing pass after runtime acceptance

Workspace D:/GAME/ANANTA, UE5.8, root owns editor application, lighting, runtime and git.
Current map is expanded, 1472 shells and eight tested services. Preserve all character models and mission anchors.
No subagents, UE/build/Blender processes, changes to existing assets or Git operations.
Read CityExpansionData.py, CityExpansionVenues.py, CityRooms.py and CityScene.py for geometry/API.

## Interior module owner

May create only Tools/Editor/CityVenueDressing.py and Tools/QA/VerifyCityVenueDressing.py.
Deliver describe() returning a list of dictionaries plus dress() applying it through CityScene prop/box/text.
Each item has label, mesh (or Cube), location in cm, scale, yaw, collision, optional material.
Labels start Dressing_. Use existing imported asset IDs only, existing material IDs only.
All eight venues receive meaningful detail; existing six new venues look empty in GPU photos.
Room floor z15, ceiling z327, walls at authored +/- width/depth halves.
Cafe centre(-26150,2400), size1600x1200, front+X; apartment centre(2350,2500), size2000x1600, front-X.
Six new room sizes/locations come from CityExpansionData.VENUES.
Prefer real HOUSE chairs, sofas, plants, books, lamps, tables and vases with correct metric scale.
Add reading islands/back wall bookcases in bookshop, checkout/stock displays in market, seating/reception
and medical-storage detail in clinic, display plinth/art/seating in gallery, parts/work areas in workshop,
route display/seating/ticket desk in transit, additional believable cafe/apartment arrangements.
Can use shallow textured boxes for cabinets, shelves, rugs and signage, not whole primitive furnishing sets.
Add supporting surfaces under the current service meshes (at z80/95/100), collision=false, correct height.
Keep x-axis doorway and service access corridor |y-centreY| <=220 clear of colliding dressing in every venue.
Do not overlap current furniture: inspect current placements and mesh bounds from manifest as source data.
Keep visible furniture spacing realistic for standing/walking. Avoid a grid of identical chairs everywhere.
Cap additions at 250 props total; repeated decorative books may be non-colliding.
No lights in this module. Root tunes existing room lights separately.
Use Vietnamese comments for placement constraints and files <=300 lines.
Self-check describes deterministic output, unique labels, valid referenced meshes/materials, physical room bounds,
clear entry corridor and count cap. Write report under Saved/QA/CityVenueDressingAudit.json.
Root applies and views GPU results. Report once <=15 lines with exact self-check and pending integration risks.

## Street landmark module owner

May create only Tools/Editor/CityStreetLandmarks.py and Tools/QA/VerifyCityStreetLandmarks.py.
Deliver describe() returning item dictionaries with same schema and dress() using CityScene helpers.
Labels start Landmark_. Existing mesh/material assets only; no import, no character changes.
Create three distinct small authored public spaces: west cafe square near(-28700,5200),
central garden near(0,6200), east transit plaza near(26000,7000).
Must inspect CityExpansionLayout.generate building rectangles and reserved footprints before choosing exact points.
Avoid all buildings/venues, road area abs(position-roadLine)<1350, and mission encounter rectangle
x[24700,27300], y[3300,5700]. Keep clue/giver positions and their 500cm surroundings clear.
Use tree groups, planting beds, seats, low walls, bicycle stands, waste bins, signs, market furniture and shelters.
Design a walkable arrangement with a clear centre and intentional edges, not uniform random scatter.
Cap additions at 160 props. Collision on seating/low walls only where routes remain clear; cosmetic foliage no collision.
Do not rely solely on free point centres: audit placed mesh XY bounds using manifests and transforms.
Self-check unique labels, bounds outside forbidden areas, known assets and cap, report Saved/QA/CityLandmarkAudit.json.
No changes to CityExpansionLayout itself. Root integrates, renders and runs gameplay regression.
Report once <=15 lines with evidence and open issues.
