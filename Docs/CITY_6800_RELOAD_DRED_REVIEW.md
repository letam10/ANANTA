# City 6800 settings reload versus DRED review

## Scope

Read-only comparison of the packaged settings reload fault and the packaged
DRED journey. This is evidence about two different runs, not a root-cause
finding. No engine, player, Blender, build, or settings operation was run for
this review.

## Anchored observations

- The Settings run is `20261010T051302934-ee0861d8e6874febbd92c806b506ca93`.
  `Round.json` records start `05:13:02.951Z`, Check passed, Reload failed,
  slots reset/restored, and process exit code 3.
- Check's packaged process used `-CitySettingsCheck` at 1920x1080 and exited
  normally at `05:13:43.951` (`...Check.log`, line 1243). Its report records
  quality groups 3, 100% scale, 90 cap, VSync off, and settings UI checks.
- Reload used the same packaged inner executable and isolated settings file,
  1920x1080, `-CitySettingsReload`, and
  `-ForceDPCVars=r.Nanite.AsyncRasterization.ShadowDepths=1`
  (`...Reload.log`, lines 27 and 300). UE logs the device-profile CVar as 1
  and sets `r.Nanite.AsyncRasterization.ShadowDepths:1` (lines 668-669).
- Reload faulted at `05:13:54.202`, current frame 42 with last completed frame
  cached as 41. It reports a shader MMU page fault at GPU VA
  `0xFFFFFFFF0CB90000`, zero tracked resources/heaps/released resources in
  the queried range, no DRED breadcrumb head, and no DRED PageFault data
  (`...Reload.log`, lines 1181, 1197-1204). Crash context says DRED disabled.
- Reload's crash breadcrumbs show active `ShadowDepths` work and Nanite
  `DrawGeometry` / `NodeAndClusterCull` work, with `PatchSplit` not completed
  (`...Reload.log`, around lines 975-976 and crash context line 1167).
  Breadcrumb position identifies recent/in-flight work; it does not prove
  which pass caused the fault.
- DRED baseline used the same packaged executable and container fingerprints
  as the Settings run (`Trial.json`). Its command line used
  `-CityServiceCheck -CityObserveGraphics -dred` and
  `-ini:Engine:[SystemSettings]:D3D12.TrackAllAllocations=1`; the log confirms
  tracking and DRED enabled (`CityMaxGraphicsPackagedDred.log`, lines 300,
  368, 722-723). Its RenderConfig has global
  `r.Nanite.AsyncRasterization=1` and does not specify the ShadowDepths
  override (`Saved/QA/CityMaxGraphicsPackagedDred/RenderConfig.txt`).
- That DRED run completed its ordinary service journey in 281.93 seconds,
  averaging 60.94 FPS; stable 90 was false (`Summary.json`). It did not run
  the Settings Reload gate. The DRED/tracking options change instrumentation
  and scheduling, so this pass is not ordinary Max performance evidence.
- The recorded non-DRED ordinary journey with shadow async on completed
  281.76 seconds at 71.58 FPS, stable 90 false (contract summary). Separate
  baseline and global-async-off trials faulted at frames 39 and 36
  (contract summary). Those frame numbers are not directly comparable to
  Reload's cached/current frame IDs.

## Inferences and limits

- The candidate CVar was effectively set for the failing Reload. Its failure
  rejects this run as evidence for promoting that setting; it does not by
  itself prove the CVar caused the fault.
- DRED completion shows only that a differently instrumented, ordinary
  journey with global async rasterization on completed. Since its command did
  not request ShadowDepths async and it did not execute the Reload sequence,
  it cannot establish that the candidate is safe or that async shadow depth
  work is the root cause.
- The fault's nearby ShadowDepths/Nanite breadcrumbs support investigating
  that work path, but absent DRED fault data and resource attribution leave
  the specific faulting instruction/allocation unknown.

## One supported next diagnosis

Repeat the isolated packaged Settings Reload gate with global
`r.Nanite.AsyncRasterization=1` and ShadowDepths async explicitly `=0`, holding
the executable, content, settings file, resolution, and reload sequence fixed.
This tests whether the Reload fault reproduces without the candidate CVar;
it is a diagnostic comparison, not a fix or a capacity recommendation.
