# Contract: isolated Reload shadow async comparison

## Goal and ownership

- UE 5.8.3 project `D:\GAME\ANANTA`, Windows PowerShell; root checks native rowboat art in parallel.
- Extend only `Tools/Build/Test-CitySettings.ps1`, `Test-CitySettingsRound.ps1`,
  `Tools/QA/TestCitySettingsDiagnostics.ps1`, and create `Docs/CITY_6800_RELOAD_BASELINE_RUNNER.md`.
- If needed to keep files around 300 lines, create only `Tools/QA/CitySettingsBaselineCases.ps1`
  for the extra stub cases; the existing test entrypoint remains the public command.
- No engine/player/Blender/build, asset/source C++, driver/registry or Git mutation; no grandchildren.
- Read existing contracts/settings runner notes and `CITY_6800_RELOAD_DRED_REVIEW.md` first.

## Public CLI contract

- Keep existing defaults and Check/Reload behavior exactly as already stub-tested.
- Inner `Test-CitySettings.ps1`: add Diagnostic value `NaniteShadowAsyncOff`.
- The new diagnostic is native 1080 only and uses explicit startup ForceDPCVars:
  `r.Nanite.AsyncRasterization=1,r.Nanite.AsyncRasterization.ShadowDepths=0`.
- Existing `NaniteShadowAsyncOn` keeps its current single override.
- Outer `Test-CitySettingsRound.ps1`: optional `-ReloadDiagnostic`, default `Same`.
- Values: `Same` or `NaniteShadowAsyncOff`; the latter requires Check Diagnostic `NaniteShadowAsyncOn`.
- Check uses the chosen Check diagnostic. Reload can use the explicit Off diagnostic.
- RunId is unique and shared by the pair; each diagnostic has its own existing path convention.
- Copy the completed Check settings file byte-for-byte to the Reload evidence folder.
- Do not rerun Check or reset the two QA slots between the paired processes.
- Preserve original QA bytes/metadata in finally on every success/failure path, as the existing outer runner does.
- Keep user saves and generic settings untouched. Preserve same inner EXE plus container identity across the pair.

## Evidence and acceptance

- Round JSON records `diagnostic`, `reloadDiagnostic`, Check/Reload outcome and copy/config hash evidence.
- Expected same fingerprint and same pre-Reload INI bytes; after-Reload content may change only through tested settings.
- Diagnostic output remains separate from product Max/90 FPS acceptance.
- Report actual startup override evidence. Do not assume old packaged RenderConfig includes ShadowDepths:
  it does not; use the effective startup CVar log alongside command provenance.
- Rejection must preserve diagnostics, logs and saved slot originals.
- No loosening gate timeouts, frame/quality/scale checks or silently repairing game saves.

## Done checks

- Run PS AST parsing and the existing diagnostics stub suite; expected old 16 rounds still pass.
- Add focused stub cases for On-Check/Off-Reload config continuity, fresh separate evidence,
  invalid pair/native guard and restoration after Reload failure.
- Verify original Check config bytes and slot state are preserved; no fallback to a stale report.
- `git diff --check` for owned files, files around 300 lines and lines around 120 columns.
- Report ONCE, max 15 lines: changed files, checks, open issues and exact runtime command for root.
- The actual packaged run is root's task after the only active Unreal process exits.
