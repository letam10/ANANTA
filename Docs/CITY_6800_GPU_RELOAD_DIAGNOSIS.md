# GPU and reload diagnosis for the 6.8 km city EXE

Date: 2026-10-10. Scope: read-only review of existing logs, config and runners.

## Findings

- A D3D12 PageFault occurred during gameplay startup in `UnrealEditor-Cmd`.
  Aftermath identifies a VSM/Nanite culling shader as active; that is correlation,
  not proof of root cause.
- Some earlier 3.4 km packaged EXE reloads hit PageFaults. Other packaged reload
  logs later have success markers. The intermittent failure is not confirmed
  fixed or consistently reproduced.
- There is no runtime evidence from a new EXE containing the 6.8 km map. Reload
  stability, GPU stability, visual quality and 90 FPS are unverified for it.

## Evidence and limits

1. `Saved/Logs/CitySettingsCheck.GPUStartupFailure.log:1909-1931` records
   `PageFault`, `AddressTranslationError` and active shader
   `CullPerPageDrawCommandsCs`. Breadcrumbs at 1794-1830 include `ShadowDepths`,
   `RenderVirtualShadowMaps(Nanite)` and `NodeAndClusterCull`. Lines 2041-2050
   report no tracked resource/heap near the fault and local budget/usage of
   7,188/460.55 MB; crash context records `bIsOOM=0`.
2. The crash context at line 1999 identifies `UnrealEditor-Cmd`, UE 5.8.3,
   DX12/SM6, RTX 4060 Laptop, and command `-CitySettingsCheck`. This is an
   Editor commandlet startup crash, not direct evidence from a packaged reload.
3. `Saved/Logs/CityGPUCaptureBlueHour.Failure1.log:2107-2117` contains an older
   PageFault in the same broad VSM/Nanite breadcrumb region and low memory use.
   The shader was not reliably identified in that dump.
4. `Docs/CITY_EXECUTION_STATUS.md:113-120` and
   `Docs/CITY_MOBILITY_ROUND.md:56-63` record earlier 3.4 km EXE reload faults,
   then two Max runs after a Nanite change without a crash. Both documents say
   that is insufficient to conclude the intermittent problem is fixed.
5. Separate packaged runs did pass reload:
   `Saved/Logs/CityGPUMissionReload.log:1750` records
   `CITY_MISSION_CHECK_FINISH mode=Reload success=1`, and
   `Saved/Logs/CityGPUServiceReload.log:1937` records
   `CITY_SERVICE_JOURNEY_FINISH mode=Reload success=1`. These prove only those
   runs and their package/configuration.
6. `Config/DefaultEngine.ini:4-5` sets
   `r.Nanite.Streaming.ReservedResources=0`; its comment says the reserved
   resource path faulted and ordinary native gameplay passed when disabled.
   An older packaged log, `Saved/Logs/CityPackagedMissionReload.log:362`, reads
   the value as `1`. The current setting has not been confirmed in a new EXE;
   it is not a proven fix.
7. `Docs/CITY_6800_INTEGRATION_ROUND.md:1-4,64-72` states the 6.8 km map is
   saved while the EXE previously tested remains 3.4 km; HLOD, new EXE, reload,
   images and FPS remain outstanding. The round runner explicitly excludes GPU
   acceptance.

## Diagnosis

**Confirmed:** two Editor startup logs contain GPU PageFaults; one associates
the active work with VSM per-page culling/Nanite. Some packaged reload runs
passed, while prior round notes document other reload failures.

**Unconfirmed:** whether a shader or map asset caused the fault; whether VRAM
exhaustion caused it; whether `ReservedResources=0` fixes it; or whether the new
6.8 km package reproduces it. Missing resource attribution and successful runs
do not distinguish driver/runtime interaction, resource lifetime/binding, or
other GPU-side causes.

## Verification gates for the new EXE

Run after HLOD rebuild and packaging. Record the EXE hash and hashes of all
`.pak`/`.utoc`/`.ucas` containers. Confirm the packaged map is the 6.8 km map;
do not infer package identity from the current source tree. Keep the contract's
native 1920x1080, 100% scale, VSync off, 90 cap, custom Max settings and DX12.
Do not add diagnostic overrides to acceptance runs.

1. **Launch and journey:** run `Test-CityMaxGraphics.ps1` against
   `ANANTA/Binaries/Win64/ANANTA.exe`. Preserve hashes, logs, stdout/stderr,
   exit code, `Trial.json`, `RenderConfig.txt`, `FrameTimes.csv`, `Report.txt`
   and any crash dump. Require fresh evidence, service journey and observation
   markers; confirm QA slots were reset and restored. This runner checks package
   fingerprints, freshness and gameplay, but does not replace a reload gate.
2. **Menu and render config:** confirm the packaged game reaches menu/map, uses
   DX12/SM6, and reports actual runtime cvars matching the contract: output,
   resolution, scale, VSync, cap, quality groups, HWRT, SMRT, GI/reflections,
   TSR and VSM. Read `RenderConfig.txt`; do not infer effective values from INI.
3. **Short gameplay, all frames retained:** visit representative districts,
   map edges, HLOD areas and accepted gameplay fixtures. Record duration, every
   frame time, render/GPU times, pop-in and visible errors. Do not infer 90 FPS
   from the cap setting.
4. **Cross-process reload:** using the same package hash and config, run Check
   to create a QA save and exit cleanly. Run Reload in a new process. Require a
   success marker, correct state persisted exactly once, fresh log and exit 0.
   Preserve the two QA slots that existed before testing.
5. **Repeatability:** complete at least three independent Check/Reload pairs
   against the same package and conditions (power source, driver, resolution).
   Use separate logs and QA output directories. A single pass does not resolve
   an intermittent fault. On recurrence, retain the log and Aftermath dump,
   timestamp, stage (startup/menu/game/reload), process ID, package hash, runtime
   cvars and related QA save files. Do not change cvars during acceptance.

**Pass criteria:** every launch reaches gameplay and exits without PageFault or
device loss; each new-process Check→Reload pair passes and restores QA slots;
actual render config matches the contract; all frames and measured timings are
retained. Report mean, p95, slow frames and reviewed images separately. Claim
stable 90 FPS only if measured data meets that criterion.

## Sources

- Existing repository logs and notes cited inline above.
- No external Epic documentation was used; this report makes no claim about an
  internal Unreal Engine root cause.
