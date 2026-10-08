# ANANTA interior finishing assets

Three portable static meshes, centimetres, FBX X forward / Z up.
The visible front of the sofa and curtain is local -Y; rug top is +Z.
Origins are at the floor beneath the centre. The curtain includes its hardware.
Material and source paths resolve relative to `Assets/City/finishing_manifest.json`.

| Mesh | Dimensions, cm | Triangles | Slots |
| --- | --- | --- | --- |
| House_GlamVelvetSofa | 218.8443 x 102.2829 x 78.7541 | 4196 | 3 |
| InteriorWovenRug | 300 x 200 x 1.5 | 1668 | 2 |
| InteriorLinenCurtain | 240 x 24 x 260.0008 | 6428 | 3 |

## Source attribution

The sofa source README is preserved verbatim in `Sources/HOUSE/GlamVelvetSofa/README.md`.
Its Legal section states:

&copy; 2021, Wayfair, LLC. [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/legalcode)

 - Eric Chadwick for Everything

The source glTF, binary buffer, normal map and ambient occlusion map are preserved unchanged.
The sofa was joined into a single static mesh, recentered at the floor and exported as FBX.
The navy fabric is approximated with standard metallic/roughness shading: navy diffuse
colour, roughness 0.78, and the source normal map with its 5x tiling, 0.36-radian rotation
and 0.75 strength baked into a portable 2048px OpenGL normal map. The approximation
does not reproduce glTF sheen or coloured specular extensions. The AO remains on UV0.
Source shape and UVs are retained; no geometry reduction was needed.

The rug and curtain geometry are original ANANTA project assets. Their woven surfaces
reuse [Poly Haven rough_linen](https://polyhaven.com/a/rough_linen), CC0-1.0, already held
in the local City source catalog. Raw linen maps and portable copies are both included.
The curtain has six pleats per panel, a weighted doubled hem, hanging tabs, fourteen
rings, a rod, two finials, brackets and wall rosettes. The rug has bound edges, an inset
border and ninety short fringe bundles.

## Import notes

Use `finishing_manifest.json` to rebuild material channels; FBX material conversion is
not the material authority. Colour images are sRGB; normals, AO and roughness are linear.
Normal maps are OpenGL: flip the green channel when an Unreal material pipeline expects
DirectX normals. Material UVs intentionally tile and overlap on cloth. Generate a separate
lightmap channel if static lighting is required. The curtain is closed thin geometry;
two-sided cloth shading is also documented in its material records.

Independent FBX roundtrip evidence and 1024px CPU renders are under
`Saved/QA/CityFinishingAssets`. No Unreal import or in-game visual acceptance is claimed.
