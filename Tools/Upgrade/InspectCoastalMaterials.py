"""Read CoastalUpgrade material graph outputs without saving packages."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import unreal


MATERIAL_ROOT = "/Game/ANANTA/CoastalUpgrade/Materials"
SURFACE_ASSET = "/Game/ANANTA/CoastalUpgrade/M_CoastalSurface"
PROPERTIES = {
    "baseColor": unreal.MaterialProperty.MP_BASE_COLOR,
    "roughness": unreal.MaterialProperty.MP_ROUGHNESS,
    "normal": unreal.MaterialProperty.MP_NORMAL,
    "emissive": unreal.MaterialProperty.MP_EMISSIVE_COLOR,
}


def package_path(project: Path, asset_path: str) -> Path:
    package_asset = asset_path.split(".", 1)[0]
    relative = package_asset.removeprefix("/Game/").replace("/", "\\") + ".uasset"
    return project / "Content" / relative


def sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    project = Path(unreal.Paths.project_dir()).resolve()
    paths = unreal.EditorAssetLibrary.list_assets(
        MATERIAL_ROOT,
        recursive=True,
        include_folder=False,
    )
    paths.append(SURFACE_ASSET)
    rows = []
    errors = []

    for asset_path in sorted(set(paths)):
        material = unreal.load_asset(asset_path)
        if not isinstance(material, unreal.Material):
            continue

        package = package_path(project, asset_path)
        before = sha256(package)
        outputs = {}
        for name, prop in PROPERTIES.items():
            node = unreal.MaterialEditingLibrary.get_material_property_input_node(
                material,
                prop,
            )
            outputs[name] = {
                "connected": bool(node),
                "node": node.get_class().get_name() if node else None,
            }


        after = sha256(package)
        if before != after:
            errors.append(f"package changed during readback: {asset_path}")

        rows.append(
            {
                "asset": asset_path,
                "package": str(package.relative_to(project)),
                "packageSha256": after,
                "expressionCount": None,
                "outputs": outputs,
            }
        )

    connected = {
        name: sum(item["outputs"][name]["connected"] for item in rows)
        for name in PROPERTIES
    }
    missing = [
        f"{item['asset']}:{name}"
        for item in rows
        for name, output in item["outputs"].items()
        if not output["connected"]
    ]
    if missing:
        errors.append("missing graph outputs: " + ", ".join(missing))

    if not rows:
        errors.append(f"no materials found under {MATERIAL_ROOT}")

    report = {
        "materialRoot": MATERIAL_ROOT,
        "materialCount": len(rows),
        "materials": rows,
        "connectedOutputs": connected,
        "errors": errors,
        "packagesUnchanged": not errors,
        "headedVisualVerified": False,
    }
    report_path = project / "Saved" / "Upgrade" / "coastal-material-readback.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if errors:
        raise RuntimeError("\n".join(errors))

    unreal.log(
        "COASTAL_MATERIAL_READBACK_OK "
        f"materials={len(rows)} connected={json.dumps(connected, sort_keys=True)} "
        f"report={report_path}"
    )


if __name__ == "__main__":
    main()
