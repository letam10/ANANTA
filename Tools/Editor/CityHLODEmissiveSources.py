"""Inspect saved package references before selecting an emissive HLOD acceptance sample.

Run with ordinary Python; this reads package metadata without Unreal or Content writes.
Reference presence selects candidates, while the rebuilt texture proves baked emission.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re

PROJECT = Path(__file__).resolve().parents[2]
ACTORS = "/Game/__ExternalActors__/ANANTA/Maps/ANANTA_City/"
WINDOW = "/Game/ANANTA/City/Materials/M_City_WindowGlass"
LABEL = re.compile(rb"Label:(City_HLOD/ANANTA_City_City_L\d+_X-?\d+_Y-?\d+)(?:\r?\n|\x00)")
ACTOR_PATH = re.compile(ACTORS.encode() + rb"[A-Z0-9]/[A-Z0-9]{2}/[A-Z0-9]+")
ASSET_PATH = re.compile(rb"/Game/ANANTA/City/(?:Meshes|Materials)/[A-Za-z0-9_]+")


def package_file(asset_path):
    assert asset_path.startswith("/Game/")
    return PROJECT / "Content" / (asset_path.removeprefix("/Game/") + ".uasset")


def asset_references(data):
    return sorted({value.decode("ascii") for value in ASSET_PATH.findall(data)})


def find_hlod(label):
    folder = PROJECT / "Content/__ExternalActors__/ANANTA/Maps/ANANTA_City"
    matches = []
    for path in folder.rglob("*.uasset"):
        data = path.read_bytes()
        if b"WorldPartitionHLODSourceActorsFromCell" not in data:
            continue
        labels = {value.decode("ascii") for value in LABEL.findall(data)}
        if label in labels:
            matches.append(path)
    assert len(matches) == 1, f"Expected one saved package for {label}: {matches}"
    return matches[0]


def inspect(label):
    path = find_hlod(label)
    data = path.read_bytes()
    own_package = "/Game/" + path.relative_to(PROJECT / "Content").with_suffix("").as_posix()
    references = sorted({value.decode("ascii") for value in ACTOR_PATH.findall(data)} - {own_package})
    sources = []
    missing_sources = []
    # Doc ca mesh: material cua cua so nam trong slot mesh, khong nhat thiet o actor.
    for reference in references:
        source_path = package_file(reference)
        if not source_path.is_file():
            missing_sources.append(reference)
            continue
        source_data = source_path.read_bytes()
        assets = asset_references(source_data)
        meshes = [asset for asset in assets if "/Meshes/" in asset]
        window_meshes = []
        for mesh in meshes:
            if WINDOW in asset_references(package_file(mesh).read_bytes()):
                window_meshes.append(mesh)
        sources.append(dict(package=reference, assets=assets, windowMeshes=window_meshes,
                            windowMaterialDirect=WINDOW in assets))
    window_sources = [entry for entry in sources if entry["windowMeshes"] or entry["windowMaterialDirect"]]
    # Bang build luu trong package cho phep doi chieu vat lieu thuc su da vao proxy.
    build_materials = sorted({value.decode("ascii") for value in re.findall(
        rb"@MAT-[A-Z0-9]+: Material (/Game/ANANTA/City/Materials/[A-Za-z0-9_]+)", data)})
    return dict(label=label, package=own_package, packageSha256=hashlib.sha256(data).hexdigest(),
                sourceCount=len(references), inspectedSourceCount=len(sources),
                missingSourcePackages=missing_sources, windowSourceCount=len(window_sources),
                windowCandidate=bool(window_sources), sources=sources, buildMaterials=build_materials,
                inspection="savedPackageReferences", contentModified=False, mapLoaded=False,
                limitation="References select a sample; live section usage and rebuilt emissive pixels remain gates")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", required=True)
    parser.add_argument("--require-windows", action="store_true")
    args = parser.parse_args()
    report = inspect(args.label)
    print(json.dumps(report, indent=2))
    if args.require_windows and not report["windowCandidate"]:
        raise SystemExit("Selected HLOD has no window-material source references; choose a facade-bearing sample")


if __name__ == "__main__":
    main()
