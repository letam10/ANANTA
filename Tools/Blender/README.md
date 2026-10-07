# Nova City Blender generator

`GenerateNovaCitySlice.py` is the deterministic art-side step for the ANANTA
vertical slice. It builds a small original Nova City district from metric,
modular primitives and writes a Blender source file, a GLB import artifact, a
manifest, and an optional low-resolution preview.

Use the pinned local Blender 4.5 LTS executable:

```powershell
$blender = 'C:\Program Files\Blender Foundation\Blender 4.5\blender.exe'
& $blender --background --python .\Tools\Blender\GenerateNovaCitySlice.py -- `
  --output-dir .\Saved\Generated\NovaCitySlice --seed 17
```

The seed and object names are stable. The manifest records dimensions in
metres, material slots, and asset roles so the UE-MCP import step can validate
the output before placing it in a map. The generator never touches existing
project assets; it writes only to the requested output directory.

## Urban prop and connector kit

`GenerateNovaCityProps.py` is an independent pass for traffic-scale detail:
two vehicles plus a scooter, traffic signal, street sign, bench, barrier, and
24 m road/sidewalk connector pieces. It uses mid-tone physically based
materials so the preview remains readable while the kit can still be relit in
Unreal.

```powershell
$blender = 'C:\Program Files\Blender Foundation\Blender 4.5\blender.exe'
& $blender --background --python .\Tools\Blender\GenerateNovaCityProps.py -- `
  --output-dir .\Saved\Generated\NovaCityProps --seed 17
```

The command writes `NovaCityProps.glb`, `NovaCityProps.manifest.json`, a
source `.blend`, and a small preview under `Saved/Generated/NovaCityProps`.

## Hero facade kit

`GenerateNovaHeroFacadeKit.py` creates three adjacent hero facades for a
vertical-slice street: a balcony residential frontage, an awning storefront,
and a metro/commercial entrance. The output keeps variant prefixes and role
metadata so each facade can be placed or replaced independently in UE.

```powershell
$blender = 'C:\Program Files\Blender Foundation\Blender 4.5\blender.exe'
& $blender --background --python .\Tools\Blender\GenerateNovaHeroFacadeKit.py -- `
  --output-dir .\Saved\Generated\NovaHeroFacadeKit --seed 17
```

The command writes `NovaHeroFacadeKit.glb`,
`NovaHeroFacadeKit.manifest.json`, a source `.blend`, and a preview under
`Saved/Generated/NovaHeroFacadeKit`.
