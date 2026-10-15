# Reload versus DRED review contract

## Scope and known results

- Read-only analysis in `D:\GAME\ANANTA`; UE 5.8.3, Windows, DX12, Nanite and VSM.
- Root integrates the new rowboat and captures native metro placements in parallel.
- No engine, player, Blender, build, driver or registry operations are allowed in this review.
- No grandchildren and no Git mutations.
- Write only `Docs/CITY_6800_RELOAD_DRED_REVIEW.md`, under 200 lines and about 120 columns.

## Evidence format and constants

- Candidate command line: `-ForceDPCVars=r.Nanite.AsyncRasterization.ShadowDepths=1`.
- Native Max: 1920x1080, screen percentage 100, quality groups 3, VSync 0, cap 90.
- Same packaged inner EXE: `Saved/Builds/City6800/Windows/ANANTA/Binaries/Win64/ANANTA.exe`.
- Base failed at frame 39; global Nanite async off failed at frame 36.
- Shadow async on ordinary journey completed 281.76 seconds, 71.58 FPS, stable90 false.
- Settings RunId: `20261010T051302934-ee0861d8e6874febbd92c806b506ca93`.
- Its Check passed; Reload exited 3 with a GPU page fault. Do not promote the candidate.
- DRED + D3D12.TrackAllAllocations=1 completed 281.93 seconds, 60.94 FPS.
- DRED overhead changes scheduling and is not ordinary Max performance evidence.

## Files to read

- `Saved/QA/CitySettingsPackagedNaniteShadowAsyncOn-<RunId>/Round.json` and corresponding Check/Reload logs.
- `Saved/Logs/CityMaxGraphicsPackagedDred.log` and relevant saved trial/config summaries.
- `Docs/CITY_6800_NANITE_NATIVE_DIAGNOSIS.md`, installed UE renderer source only if needed.
- Settings reload and graphics observation C++ sources may explain sequence differences.
- Avoid full crash XML, account identifiers, credentials and giant unspecific log dumps.

## Done criteria

- Report actual flags, timeline and fault pass differences from anchored log excerpts.
- Separate observations from inferences. Identify one concrete next diagnosis only if supported.
- Do not recommend blind capacity changes or make a root-cause claim from the DRED pass.
- Verify the document with `git diff --check -- Docs/CITY_6800_RELOAD_DRED_REVIEW.md`.
- Report once, at most 15 lines: changed file, checks and open issues. No status messages.
