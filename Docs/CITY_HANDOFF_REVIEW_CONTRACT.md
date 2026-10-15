# City review handoff contract

## Scope

This round is source and documentation only. Do not launch Unreal, do not run a game, do not probe ports,
and do not run a long or benchmark test. Preserve the existing dirty map and external actor changes until a
separate review explicitly accepts them.

## Shared inventory format

Each audit entry must record: path, role, current state, evidence source, safe next action, and whether the
entry is publishable in this round. Counts must distinguish source files from generated `.uasset` actors.

## Model quality contract

Model and dressing reviews must use the eight-view checklist: front, rear, left, right, front-left,
front-right, rear-left, rear-right. Placement reviews must use five gameplay-facing checks: road approach,
side approach, rear approach, elevated view, and interior/close view when relevant. Scripts may encode these
checks and metadata, but this round must not claim visual acceptance without a native capture.

## Optimization contract

Keep repeated props instance-friendly, keep non-interactive interiors sparse, and preserve HLOD/Nanite/collision
limitations in the handoff. Do not claim a target FPS without a short normal gameplay measurement on the current
build; this round intentionally records the target as unverified.

## Deliverables

1. A complete repository and generated-artifact inventory in `Docs/CITY_EXECUTION_HANDOFF.md`.
2. Surgical source changes for model review metadata and realistic dressing guidance only.
3. A dated entry in `Docs/CITY_EXECUTION_STATUS.md` linking the inventory and listing verification limits.
4. Git commit and push only for reviewed source/documentation files; never stage the bulk actor map blindly.
