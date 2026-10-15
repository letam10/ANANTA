# City model review and instancing round

Date: 2026-10-11
Scope: offline model review coverage and static instance reuse audit.

## What this round adds

`Tools/QA/PrepareModelReviewViews.py` reads the existing `Assets/City/*manifest.json` files and
creates `Saved/QA/CityModelReviewViews.json`. Each unique mesh receives eight local model views:
front, front right, right, rear right, rear, rear left, left and front left. It also receives five
placement views: front, rear, left, right and upper. The view records use the repository convention
of centimetres, X forward and Z up, and store a target, eye position, yaw and pitch.

The output currently covers 93 unique meshes, 744 model views and 465 placement views across 11
source manifests. This is a deterministic camera plan. It does not claim that Unreal rendered the
model, that a material is visually correct, or that a collision shape is accepted.

`Tools/QA/VerifyCityInstanceReuse.py` audits a generated layout when per group records are present.
The signature is mesh, material, collision and hidden state. Instances with the same signature can
share an ISM or HISM component within a streaming cell. The self test passes with three groups and
four instances, including three window instances sharing one signature.

The current `Saved/QA/CityMapBuild.json` contains aggregate counts only, so the production report is
honestly marked `PARTIAL`: 85,387 groups and 1,660,776 instances are recorded, but a reuse ratio
cannot be calculated without per group signatures. Ctrl+D or Ctrl+V in an editor is not evidence of
instancing; the renderer still needs shared mesh and material references and a suitable component.

## Optimization decisions

- Repeated windows, chairs, plants, flowers, signs and static facade details should use the same
  mesh and material signature and be grouped by World Partition cell.
- HISM is the default choice for many static instances. Moving vehicles, interactive doors and
  NPC actors retain their actor state while sharing source meshes and textures where possible.
- Small decorative props keep simple collision or no gameplay collision. They should not cast
  long distance shadows outside interiors.
- Renderer frustum and occlusion culling remain responsible for visibility. The scripts do not
  hide actors by camera direction and do not unload the world when the player turns around.
- Nanite, LOD and HLOD remain separate gates. A shared instance reduces repeated component and
  draw setup, but it does not remove the cost of visible pixels, materials, shadows or simulation.

## Verification performed

- `python -X utf8 -m py_compile Tools/QA/PrepareModelReviewViews.py Tools/QA/VerifyCityInstanceReuse.py`
  passed.
- The model view generator passed validation for all 93 records.
- Instancing self test passed with reuse ratio 2.0.
- Aggregate city report was generated with status `PARTIAL`, preserving the missing signature
  evidence instead of inventing a draw call count.
- No Unreal editor, packaged game, native capture, benchmark, soak test or long gameplay session
  was run in this round.

## Still open

1. Run targeted Unreal captures for priority assets such as factory loading details, airport
   terminal, traffic signals, rail station, beach props and the vessels. Review all eight model
   directions and five placement views before accepting geometry or placement.
2. Export a per group layout receipt from the next map apply so the instance audit can calculate
   reuse ratio, largest signatures and accidental duplicate groups.
3. Rebuild and read back HLOD only after source geometry is accepted. Keep the 6.8 km map dirty
   actor changes separate until map persistence and source control checkout are verified.
4. Continue native GPU and FPS investigation separately. This round does not prove the 90 FPS goal.

Evidence is intentionally split between deterministic source checks and future Unreal visual review.

