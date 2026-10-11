# 6.8 km native capture PageFault diagnosis

Scope: read-only diagnosis of the failed native-resolution capture. No runtime test
was run. The review contract records that the first 3% capture is excluded and the
native 1920x1080 / 100% run exited before its first image.

## Verified evidence

- `Saved/Logs/CityPlacement_metro.log:508` sets
  `r.Nanite.Streaming.ReservedResources=0`.
- `Saved/Logs/CityPlacement_metro.log:1685` names the active GPU marker
  `NodeAndClusterCull`; line 1777 reports `PageFault`.
- Lines 1896-1903 report GPU VA `0x3E100000`, current frame 293, zero active
  tracked resources/heaps at the address, zero recently released resources, and
  no DRED breadcrumb head or PageFault data. The log does not identify the
  faulting allocation or prove a Nanite capacity overrun.
- Epic's installed UE 5.8 renderer source sets defaults in
  `Engine/Source/Runtime/Renderer/Private/Nanite/NaniteShared.cpp:38-65`:
  `MaxNodes=2,097,152`, `MaxCandidateClusters=16,777,216`,
  `MaxVisibleClusters=4,194,304`, and `MaxCandidatePatches=2,097,152`.
- Size functions at `NaniteShared.cpp:549-565` define node records as 8/12
  bytes for main/post, plus 4 bytes each when Nanite assemblies or voxels are
  supported; candidate clusters are 8 or 12 bytes; visible records add 4 bytes.
- Allocations are explicit in `NaniteCullRaster.cpp:6882-6885,6913-6933,
  6946`: node buffer is max nodes times main+post record sizes; candidate
  clusters use max count times cluster size; tessellation candidate patches
  use 16 bytes each. `NaniteCullRaster.cpp:4193-4200` allocates visible clusters
  at visible size times max count.
- Conservative extended-size maxima therefore reserve 40 MiB for candidate
  nodes (56 MiB if assemblies/voxels are supported), 192 MiB candidate clusters,
  64 MiB visible clusters, and 32 MiB tessellation candidates. These are
  capacity products, not measured residency; actual allocation is conditional
  for tessellation and persistent culling paths.
- The shader bounds writes/indices: `NaniteHierarchyTraversal.ush:126,145-155,
  287,377,419-421` checks node limits and clamps candidate-cluster ranges.
  These guards make a plain capacity overflow less likely to be the direct
  explanation, but do not establish safety against unrelated driver/GPU faults.

## Assessment

**Verified:** failure is a D3D12 GPU PageFault during a frame whose active marker
was Nanite node/cluster culling. VSM work is present in the crash breadcrumb
context, but a breadcrumb identifies recent GPU work, not the cause. The report
has no DRED page-fault address mapping and no resource attribution.

**Hypotheses only:** an async-compute/queue synchronization issue involving
Nanite shadow rasterization; a driver or hardware fault; or an invalid/stale GPU
resource address. The log does not discriminate among them. The logged 301.04 MB
local usage vs 7,188 MB budget at frame 293 argues against simple local-memory
budget exhaustion at that sampled point, not against every memory or residency
failure.

`ReservedResources=0` is a captured setting, not causal evidence. The reviewed
renderer culling allocation sites do not link this setting to the fault address.
Do not increase Nanite capacity based on this crash: source guards clamp queue
counts, and larger maxima reserve more memory without a demonstrated need.

## Controlled follow-up candidates

Use a separate QA INI / fresh process for each candidate; keep all capture
settings, map, camera, and other CVars fixed. Compare exit status, first-image
production, frame number, and GPU crash log. Do not combine changes.

1. **Async queue isolation:** baseline `r.Nanite.AsyncRasterization=1`
   (renderer default at `NaniteCullRaster.cpp:51-55`); test `=0`. This changes
   async compute rasterization scheduling while leaving the culling capacities
   above unchanged. Source allocation delta: 0 bytes for those four buffers.
   A changed outcome supports a scheduling-path hypothesis, not proof of root
   cause.
2. **Shadow async isolation:** independently test
   `r.Nanite.AsyncRasterization.ShadowDepths=1` against default `=0`
   (`NaniteCullRaster.cpp:57-61`), with global async rasterization left at 1.
   Source allocation delta for the four listed buffers: 0 bytes. A changed
   outcome narrows the suspicion to shadow async scheduling; it does not prove
   VSM itself is defective.

Both are proposals only; neither has been executed. If test 1 is run, restore
baseline before test 2. Capture a new DRED report with resource tracking enabled
only if a separate diagnostic run is approved and its overhead is acceptable.

## References

- Installed UE 5.8.3 source:
  `C:\Program Files\Epic Games\UE_5.8\Engine\Source\Runtime\Renderer\Private\Nanite\NaniteShared.cpp`
- Installed UE 5.8.3 source:
  `C:\Program Files\Epic Games\UE_5.8\Engine\Source\Runtime\Renderer\Private\Nanite\NaniteCullRaster.cpp`
- Installed UE 5.8.3 shader:
  `C:\Program Files\Epic Games\UE_5.8\Engine\Shaders\Private\Nanite\NaniteHierarchyTraversal.ush`
- Official Epic reference: [Nanite Technical Details][nanite-doc]
- Official reference access check was attempted during this diagnosis but the
  documentation fetch endpoint returned HTTP 404. No technical conclusion here
  depends on an unverified interpretation of that page; buffer and guard facts
  above are taken from the installed source lines cited directly.

[nanite-doc]: https://dev.epicgames.com/documentation/en-us/unreal-engine/nanite-technical-details
