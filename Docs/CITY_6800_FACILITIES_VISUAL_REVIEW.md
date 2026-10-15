# City facilities visual review

**Evidence:** `Saved/QA/CityPlacement_facilities_Dred/Contacts/Placement_00.png`–`Placement_09.png`
and the 50 native `View_00.png`–`View_49.png` captures. Each contact shows front, rear, left, right,
and upper views; all five are visible for every placement. Airport views are site-scale and show the
full facility area, but the terminal details are small. No facility is visually accepted yet.

The captures are DRED/allocation diagnostics at 1920×1080 with the listed RenderConfig; they do not
prove stable frame rate or GPU stability. Findings below are image observations only. Collision,
interiors, traversal, and gameplay were not tested.

| Facility | Five views | Visible geometry / placement concern | Prototype art still evident |
|---|---|---|---|
| Station | All visible | Parallel platform roofs and tracks sit alone on a broad paved lot; no clear station hall. | Repeated green roof slabs, sparse platform detail, no readable station signage. |
| Hotel | All visible | Centered; front and rear are largely blank, while windows appear on the side faces. | Plain box massing, simple roof block, weak entry identity. |
| Restaurant | All visible | Centered low block; green awnings appear on one long facade, other faces are mostly blank. | Flat oversized roof and generic shell; restaurant identity is mostly the awning. |
| Theater | All visible | Centered; stepped roof forms read clearly from side and upper views. | Repeated roof pyramids over a box base; sparse facade and no legible venue signage. |
| Cinema | All visible | Centered; one long side has windows and a colored canopy, end walls are mostly blank. | Low generic block and flat roof; little visible distinction from other retail shells. |
| Cafe | All visible | Centered; low slab with a green awning, visually close to Restaurant. | Nearly the same massing and awning language as Restaurant; weak cafe-specific cues. |
| Pool | All visible | Rectangular pool reads clearly on the roof; shell is centered on its lot. | Simple cyan basin and plain roof deck; no visible deck furniture, ladders, or poolside detail. |
| Factory | All visible | Yellow loading pieces appear offset from the main shell in front and upper views; check alignment. | Brick box with repetitive roof ribs/stacks and sparse industrial yard dressing. |
| Airport | All visible, site-scale | Runway/apron and terminal area fit in frame; terminal is small against the large paved field. | Few low green-roofed blocks, little visible taxiway/apron marking or airport perimeter detail. |
| Highway | All visible | Views show a wide, at-grade four-way crossing; center dividers terminate at the junction. | Reads as a basic urban road intersection rather than a highway interchange; minimal roadside detail. |

## Open work

- Resolve the visible identity, facade, and dressing gaps above; recheck Factory loading-piece alignment.
- Review Airport from closer ground-level angles before judging terminal detailing or access layout.
- Keep visual acceptance separate from collision, interior, gameplay, and performance acceptance; these
  captures establish none of those results.
