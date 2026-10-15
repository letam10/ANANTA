# Isolated Check-On / Reload-Off diagnostic

From `D:\GAME\ANANTA`, after the active Unreal process exits:

```powershell
powershell -NoProfile -File Tools/Build/Test-CitySettingsRound.ps1 `
  -ExecutablePath 'D:\GAME\ANANTA\Saved\Builds\City6800\Windows\ANANTA\Binaries\Win64\ANANTA.exe' `
  -Diagnostic NaniteShadowAsyncOn -ReloadDiagnostic NaniteShadowAsyncOff
```

Check starts at native 1920x1080 with the existing single override
`-ForceDPCVars=r.Nanite.AsyncRasterization.ShadowDepths=1`.
Reload starts at the same resolution with explicit
`-ForceDPCVars=r.Nanite.AsyncRasterization=1,r.Nanite.AsyncRasterization.ShadowDepths=0`.
This compares the Reload fault with shadow async disabled; it does not promote a product setting.
Do not run another settings runner against this package during the pair.

The optional outer `-ReloadDiagnostic` defaults to `Same`, retaining the existing Check/Reload
diagnostic and shared config path. Its only alternative, `NaniteShadowAsyncOff`, requires
`-Diagnostic NaniteShadowAsyncOn`; invalid pairs reject before touching slots or launching.
The inner runner accepts `-Diagnostic NaniteShadowAsyncOff` and rejects diagnostic Height=720.

For the explicit comparison, one unique RunId names both evidence directories:

- Check: `Saved/QA/CitySettingsPackagedNaniteShadowAsyncOn-<RunId>/`.
- Reload: `Saved/QA/CitySettingsPackagedNaniteShadowAsyncOff-<RunId>/`.
- Stage logs retain the corresponding diagnostic, RunId and Check/Reload suffix under `Saved/Logs`.

The wrapper snapshots and resets the two QA save slots once before Check. It copies Check's completed
`GameUserSettings.ini` byte-for-byte to the separate Reload directory, compares SHA256, and verifies
the same inner executable and container fingerprints immediately before Reload. It does not rerun
Check or reset QA slots between processes. Both original QA slots, including absence, bytes,
creation/write timestamps and attributes, are restored in `finally` on success or failure.
Normal player saves and the generic settings INI are outside this runner's operations.

`Round.json` lives in the Check directory and retains schemaVersion=1 with additive fields:

- `diagnostic`, effective `reloadDiagnostic`, `reloadDiagnosticSelection` and shared `runId`.
- `checkEvidence` and `reloadEvidence`, plus Check/Reload outcomes and restoration status.
- `artifactFingerprint`, `reloadArtifactFingerprint` and `artifactUnchanged`.
- `config`: Check/Reload paths, `copied`, `checkSha256`, `reloadBeforeSha256`,
  `reloadAfterSha256`, `checkAfterSha256`, and `continuity`.

The pre-Reload INI hash must equal Check's completed hash. Reload can update its own INI through
the tested settings operations; the resulting hash is recorded even when Reload fails.
The separate Check INI remains available with its original bytes for comparison.

Each diagnostic stage records `Check/Startup.json` or `Reload/Startup.json`, including requested
arguments, executable path, log path, log freshness, observed CVar values and matching log lines.
Observed values come from the last `LogConfig: Set CVar [[name:value]]` entry for each requested CVar
in the fresh stage log. Missing entries remain unconfirmed. The new Off diagnostic requires both
explicit values to be observed before it can pass. Existing On/default gates remain unchanged.
The packaged RenderConfig may omit ShadowDepths; it is not used to infer this override.
Command provenance shows what was requested; the fresh CVar log shows what startup applied.

Failures retain Round.json, stage reports/captures when fresh, startup evidence and logs. No older
runtime report can satisfy a new stage. A PASS covers these menu/reload gates only; it does not
prove Max/90 FPS, visual acceptance, long-term stability or the GPU fault's cause.

Validation command (no Unreal launch; temporary inert executable intercepted by a stub):

```powershell
powershell -NoProfile -File Tools/QA/TestCitySettingsDiagnostics.ps1
```

The suite parses all four scripts, retains the original 16 rounds, two guards and legacy pair,
then tests nine On/Off rounds and two additional guards. New cases cover separate fresh evidence,
exact INI continuity, legitimate Reload config updates, startup CVar confirmation, changed package
rejection, stale Reload evidence, Reload process/launch failures, and both QA slots' restoration.
Stub PASS is runner validation; the packaged runtime comparison still must be run separately.

Verified 2026-10-10: AST parse PASS; original 16 rounds/two guards/legacy pair PASS;
nine baseline rounds/two baseline guards PASS. All five owned files are under 300 lines/120 columns.
