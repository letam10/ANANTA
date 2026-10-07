# ANANTA modular city asset library

`manifest.json` is the import contract. Paths are relative to this directory.
The library contains original architecture, street furniture and a compact electric car,
plus 12 CC0 furniture models copied from the existing HOUSE library.
Road and pavement materials use Poly Haven Asphalt 02 and Concrete Floor 02 at 2K resolution.

## Coordinates and geometry

- FBX coordinates use centimetres and `UnitScaleFactor=1`; import scale must be 1.
- FBX axis conversion is X forward, Z up. Apply the FBX scene transform during import.
- In authoring space all facade fronts face -Y. X is facade width and Z is height.
- Facade modules are 400 cm wide and 320 cm tall, with origin at the bottom centre.
- Car forward is +X; its wheels contact Z=0. Wheels are included in the combined static mesh.
- Source `CityKit.blend` uses metres; export explicitly converts geometry to centimetres.
- Every FBX contains one combined static mesh, triangles, material slots and UV0.
- Original geometry has modelled bevels, window recesses, separate frames, sills and thickness.
- UV0 on authored architecture tiles once per 2 metres. Furniture retains original texture UVs.
- `CafeEntry` and `ApartmentEntry` have a genuinely open central doorway, approximately 140 cm wide.
- `Storefront` is the cafe entry variant, retained as a reusable required kit identifier.
- `Balcony` includes structural supports below its slab; bounds extend below the origin.

## Materials

Base colour textures are sRGB. Roughness, metallic, AO and normal textures are linear data.
Normals are OpenGL tangent space; Unreal should flip the green channel once during texture import.
Null maps mean the corresponding scalar or colour factor applies.
`roughnessFactor` is supplied in addition to the contract's factors where the source has one.
glTF packed metallic/roughness textures have been split into grayscale G/B images.
glTF AO is extracted from the R channel of its explicitly referenced occlusion texture.
No packed RGB ARM map is described as an ordinary roughness texture.
`twoSided` records the source material flag, including the potted plant leaves.

Exterior glass is opaque reflective glass for modular shells. Entry door openings have no glass.
This avoids pretending the closed facade windows contain furnished accessible rooms.
Only the two designated interior modules should be connected to furnished cafe/apartment rooms.

## Collision and LOD recommendations

- Facade trim and windows: no individual gameplay collision; use the building shell collision.
- Entry modules: three simple boxes for jambs and lintel, preserving the central doorway.
- Balcony: simple slab, side rail and front rail boxes; exclude decorative balusters.
- Bench: two leg boxes and seat/back boxes. Bollard: capsule or short convex hull.
- Planter: simple outer box. Lamp: narrow pole capsule and base cylinder.
- Car: compound hulls for chassis and cabin; wheel geometry is visual only.
- Furniture: simple boxes or convex decomposition with 4-8 hulls, avoiding fine upholstery detail.
- Suggested LOD ratios: 100%, 50%, 20% at screen sizes 1.0, 0.4, 0.15.
- Fine decorative furniture should not cast long distance shadows or appear outside interiors.
- Plant and book source meshes are reduced to at most 35,000 triangles before cleanup.
- Imported CC0 furniture retains intentional open upholstery, leaf and assembly boundaries.
- Per mesh boundary and nonmanifold counts are recorded in `geometry_audit.json`; use simple collision.
- LOD meshes and Unreal collision are recommendations, not prebuilt engine assets.

## Sources and reproducibility

`Sources/HOUSE` preserves complete selected glTF files, binary buffers, textures and source metadata.
The source models and texture sets are Poly Haven CC0-1.0 assets.
Every copied source file is individually SHA-256 recorded in the manifest.
The HOUSE directory is read-only and is never modified by these scripts.
The excluded CC-BY GlamVelvetSofa is only named in the copied metadata; its files are not included.
Original geometry and generator scripts are authored for this project.
`Sources/Generator` snapshots the generator source files used for the delivery.

From the repository root, run these commands one at a time:

```powershell
python Tools/CityAssets/fetch_street_textures.py
python Tools/CityAssets/prepare_sources.py
$blender = 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
& $blender -b --factory-startup --python-exit-code 1 -P Tools/CityAssets/build_city_assets.py
& $blender -b --factory-startup --python-exit-code 1 -P Tools/CityAssets/verify_fbx.py
& $blender -b --factory-startup --python-exit-code 1 -P Tools/CityAssets/review_assets.py
python Tools/CityAssets/audit_delivery.py
```

`Saved/QA/CityAssets` contains independent FBX readback, measured mesh geometry,
source/texture validation and a Cycles contact sheet of every delivered mesh.
Blender asset QA does not establish Unreal import appearance, gameplay collision, or frame rate.
