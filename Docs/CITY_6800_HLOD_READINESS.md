# 6.8 km HLOD readiness

## Current evidence and decision

- `Saved/QA/CityMapBuild.json` and `CityExpansionApplied.json` identify
  `/Game/ANANTA/Maps/ANANTA_City` as `expanded`, width `6788.2250993908565` m,
  with 85,386 groups and 1,660,761 instances. They set `hlodRebuildRequired=true`;
  these are map-apply evidence, not HLOD acceptance.
- `Saved/QA/CityMobilityMapReadback.json` matches those groups/instances and is PASS.
  `CityWholeMapCollision.json` is PASS (86,180 descriptors, 154,964 blocking instances,
  13,987 road samples). `CityWorldBoundaries.json` now passes all 14 sweeps after waiting
  for mesh compilation and physics creation; native gameplay at the boundary remains pending.
- The last full HLOD log, `Saved/Logs/CityHLOD.log`, and its instance report are dated
  Oct 9 and cover 962 proxies / 591,633 instances. The saved map apply is Oct 10 and
  has 6.8 km extents. They do not establish coverage of the expanded map.
- `CityHLODReadback.json` is older still: 152 actors/descriptors, from Oct 7. It cannot
  be used for this acceptance. `CityHLODSettings.json` and the Oct 8 PBR readback also
  predate the Oct 9 Instancing-layer switch; they describe Mesh Simplify and are stale
  for the current Instancing builder. The Oct 9 instance report does verify Instancing,
  Nanite allowed, filtering disabled, and source mesh/material references for its old map.

## Existing command chain

Run serially from `D:\GAME\ANANTA`, only after the current Unreal boundary diagnostic
and other editor/commandlet processes have exited:

```powershell
powershell -NoProfile -File Tools\Build\Build-CityHLOD.ps1
powershell -NoProfile -File Tools\Build\Run-CityEditor.ps1 `
  -Script Tools/Editor/VerifyCityHLODInstances.py -LogName City6800HLODInstancesReadback
powershell -NoProfile -File Tools\Build\Run-CityEditor.ps1 `
  -Script Tools/Editor/VerifyCityHLOD.py -LogName City6800HLODReadback
```

The build targets the persisted map and calls `WorldPartitionHLODsBuilder` with
`-SetupHLODs -BuildHLODs`; it accepts `-SingleHLOD` only for a sample and
`-EngineRoot` to override the default UE 5.8 install. It checks exit code and calls
`Test-CityHLODLog.ps1`, which requires one positive built count, a unique complete
numbered actor sequence, and (for a sample) its requested label. The sample command is
not full-map acceptance. Do not start any of these while another Unreal process owns
the project.

The two editor readbacks reopen the saved map. `VerifyCityHLODInstances.py` checks the
layer type, `disallow_nanite`, `FILTER_NONE`, each selected proxy's loaded actor,
instanced mesh geometry, positive instance count, and non-null materials. Its full
report is `Saved/QA/CityHLODInstances.json` with `map`, `descriptors`, `actors`,
`instances`, per-proxy `entries`, `errors`, and config flags. `VerifyCityHLOD.py`
checks loaded actors against descriptors, at least one mesh and non-null material slots;
it writes `CityHLODReadback.json` (`map`, actor/descriptor counts, `errors`, actors).
Neither script currently binds its PASS to the 6.8 km map dimensions or expected
generated-group count. The latter's `expanded` threshold is only 153 proxies, so it is
not a sufficient expanded-map coverage gate.

## Acceptance gaps and minimal repair

1. After the build, compare its full actor count/labels with a newly generated instance
   readback and record the expanded-map identity (`stage`, width, source groups/instances)
   in that report. Add assertions in the readback for `stage == expanded`, exact width,
   expected source group/instance totals, and full descriptor-to-actor parity. A mere
   minimum of 153 cannot reject a mostly stale 962-proxy result.
2. The log validator proves the commandlet completed its own discovered set, but does
   not prove that set belongs to this map revision. Pair the fresh log/report with the
   applied-map identity above; do not infer success from old `CityHLOD.log` or QA JSON.
3. `CityScene.instance_group` marks hidden boundary cubes and large water planes with
   `enable_auto_lod_generation=False`; the large water actors are also non-spatial.
   Keep those flags in place and review newly built proxy labels/components to ensure
   they contain no hidden boundary colliders. Current instance verification checks
   HLOD proxy materials/instances, not exclusion of those source actors.
4. Instance/material readback is structural, not visual acceptance. Inspect representative
   expanded-edge and interior proxies and confirm silhouette/material/night-window output;
   `VerifyCityHLOD.py` and the current `NullRHI` readback do not prove rendered appearance.

The map/collision/boundary round is independent from the HLOD builder. Boundary failure
does not prove HLOD generation failed, but it remains an open city acceptance gate.
No current 6.8 km HLOD build/readback evidence exists in the inspected reports/logs.
