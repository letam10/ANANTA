"""Generate a small, deterministic Nova City modular kit as a self-contained GLB.

The generator deliberately uses only the Python standard library.  It produces
real mesh geometry, PBR material slots, and an embedded procedural facade
texture so the asset can be imported without Blender or a network dependency.
The output is a source artifact for the Unreal import step, not a temporary
cache.
"""

from __future__ import annotations

import argparse
import json
import math
import struct
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


Vec3 = tuple[float, float, float]
Vec2 = tuple[float, float]


@dataclass
class Vertex:
    position: Vec3
    normal: Vec3
    uv: Vec2


class GlbBuilder:
    def __init__(self) -> None:
        self.vertices: list[Vertex] = []
        self.indices: list[int] = []
        self.meshes: list[dict] = []
        self.nodes: list[dict] = []
        self.materials: list[dict] = []
        self.images: list[dict] = []
        self.textures: list[dict] = []
        self.mesh_indices: list[list[int]] = []
        self.binary = bytearray()

    def add_material(
        self,
        name: str,
        color: tuple[float, float, float, float],
        *,
        metallic: float = 0.0,
        roughness: float = 0.6,
        emissive: tuple[float, float, float] | None = None,
        texture_index: int | None = None,
    ) -> int:
        pbr = {
            "baseColorFactor": list(color),
            "metallicFactor": metallic,
            "roughnessFactor": roughness,
        }
        if texture_index is not None:
            pbr["baseColorTexture"] = {"index": texture_index}
        material = {
            "name": name,
            "pbrMetallicRoughness": pbr,
        }
        if emissive is not None:
            material["emissiveFactor"] = list(emissive)
        self.materials.append(material)
        return len(self.materials) - 1

    def add_box(self, name: str, center: Vec3, size: Vec3, material: int, uv_scale: Vec2 = (1.0, 1.0)) -> None:
        cx, cy, cz = center
        sx, sy, sz = (value / 2.0 for value in size)
        corners = [
            (cx - sx, cy - sy, cz - sz), (cx + sx, cy - sy, cz - sz),
            (cx + sx, cy + sy, cz - sz), (cx - sx, cy + sy, cz - sz),
            (cx - sx, cy - sy, cz + sz), (cx + sx, cy - sy, cz + sz),
            (cx + sx, cy + sy, cz + sz), (cx - sx, cy + sy, cz + sz),
        ]
        faces = [
            ((0, 1, 2, 3), (0.0, 0.0, -1.0)),
            ((4, 7, 6, 5), (0.0, 0.0, 1.0)),
            ((0, 4, 5, 1), (0.0, -1.0, 0.0)),
            ((2, 6, 7, 3), (0.0, 1.0, 0.0)),
            ((1, 5, 6, 2), (1.0, 0.0, 0.0)),
            ((3, 7, 4, 0), (-1.0, 0.0, 0.0)),
        ]
        start = len(self.vertices)
        uv = [(0.0, 0.0), (uv_scale[0], 0.0), (uv_scale[0], uv_scale[1]), (0.0, uv_scale[1])]
        for corners4, normal in faces:
            for corner, texcoord in zip(corners4, uv):
                self.vertices.append(Vertex(corners[corner], normal, texcoord))
        for face_index in range(6):
            base = start + face_index * 4
            self.indices.extend((base, base + 1, base + 2, base, base + 2, base + 3))
        self._finish_mesh(name, start, len(self.vertices) - start, material)

    def add_cylinder(self, name: str, center: Vec3, radius: float, height: float, material: int, sides: int = 12) -> None:
        cx, cy, cz = center
        start = len(self.vertices)
        half = height / 2.0
        for cap_z, normal in ((cz - half, (0.0, 0.0, -1.0)), (cz + half, (0.0, 0.0, 1.0))):
            for i in range(sides):
                angle = (2.0 * math.pi * i) / sides
                self.vertices.append(Vertex((cx + radius * math.cos(angle), cy + radius * math.sin(angle), cap_z), normal, (i / sides, 0.0)))
        for i in range(sides):
            angle = (2.0 * math.pi * i) / sides
            normal = (math.cos(angle), math.sin(angle), 0.0)
            for cap_z, v in ((cz - half, 0.0), (cz + half, 1.0)):
                self.vertices.append(Vertex((cx + radius * math.cos(angle), cy + radius * math.sin(angle), cap_z), normal, (i / sides, v)))
        bottom = start
        top = start + sides
        side = start + sides * 2
        for i in range(1, sides - 1):
            self.indices.extend((bottom, bottom + i + 1, bottom + i))
            self.indices.extend((top, top + i, top + i + 1))
        for i in range(sides):
            j = (i + 1) % sides
            a, b = side + i * 2, side + j * 2
            c, d = side + j * 2 + 1, side + i * 2 + 1
            self.indices.extend((a, b, c, a, c, d))
        self._finish_mesh(name, start, len(self.vertices) - start, material)

    def _finish_mesh(self, name: str, first_vertex: int, vertex_count: int, material: int) -> None:
        # The mesh stores the complete shared index range; localise indices in
        # the accessor later by recording the range used by this primitive.
        if not self.meshes:
            self._mesh_index_start = 0
        index_start = getattr(self, "_last_index_start", 0)
        index_count = len(self.indices) - index_start
        local_indices = [value - first_vertex for value in self.indices[index_start:]]
        mesh = {"name": name, "firstVertex": first_vertex, "vertexCount": vertex_count, "indexCount": index_count, "material": material}
        self.meshes.append(mesh)
        self.mesh_indices.append(local_indices)
        self.nodes.append({"name": name, "mesh": len(self.meshes) - 1})
        self._last_index_start = len(self.indices)

    def add_png_texture(self, name: str, png_bytes: bytes) -> int:
        offset = _align4(len(self.binary))
        self.binary.extend(b"\x00" * (offset - len(self.binary)))
        view_offset = len(self.binary)
        self.binary.extend(png_bytes)
        self.images.append({"name": name, "bufferView": None, "mimeType": "image/png"})
        image_index = len(self.images) - 1
        self.images[image_index]["_offset"] = view_offset
        self.images[image_index]["_length"] = len(png_bytes)
        self.textures.append({"name": f"{name}_Texture", "source": image_index})
        return len(self.textures) - 1

    def build(self, output: Path) -> None:
        # Add vertex/index data after texture bytes; this keeps offsets explicit.
        # glTF is Y-up while the modeling helpers above use Z-up.  Swap the
        # exported Y/Z axes so the imported Unreal asset stands upright.
        pos_bytes = b"".join(struct.pack("<3f", v.position[0], v.position[2], v.position[1]) for v in self.vertices)
        norm_bytes = b"".join(struct.pack("<3f", v.normal[0], v.normal[2], v.normal[1]) for v in self.vertices)
        uv_bytes = b"".join(struct.pack("<2f", *v.uv) for v in self.vertices)
        mesh_index_offsets: list[tuple[int, int]] = []
        idx_bytes_builder = bytearray()
        for local_indices in self.mesh_indices:
            idx_offset = len(idx_bytes_builder) // 4
            idx_bytes_builder.extend(struct.pack("<" + "I" * len(local_indices), *local_indices))
            mesh_index_offsets.append((idx_offset, len(local_indices)))
        idx_bytes = bytes(idx_bytes_builder)
        sections: list[tuple[int, bytes, int]] = []
        for payload, target, component in ((pos_bytes, 34962, 5126), (norm_bytes, 34962, 5126), (uv_bytes, 34962, 5126), (idx_bytes, 34963, 5125)):
            offset = _align4(len(self.binary))
            self.binary.extend(b"\x00" * (offset - len(self.binary)))
            self.binary.extend(payload)
            sections.append((offset, payload, component))
        pos_offset, _, _ = sections[0]
        norm_offset, _, _ = sections[1]
        uv_offset, _, _ = sections[2]
        idx_offset, _, _ = sections[3]
        buffer_views: list[dict] = []
        for offset, payload, target in ((pos_offset, pos_bytes, 34962), (norm_offset, norm_bytes, 34962), (uv_offset, uv_bytes, 34962), (idx_offset, idx_bytes, 34963)):
            view = {"buffer": 0, "byteOffset": offset, "byteLength": len(payload)}
            if target:
                view["target"] = target
            buffer_views.append(view)
        for image in self.images:
            view_index = len(buffer_views)
            buffer_views.append({"buffer": 0, "byteOffset": image.pop("_offset"), "byteLength": image.pop("_length")})
            image["bufferView"] = view_index
        positions = [value for vertex in self.vertices for value in (vertex.position[0], vertex.position[2], vertex.position[1])]
        normals = [value for vertex in self.vertices for value in (vertex.normal[0], vertex.normal[2], vertex.normal[1])]
        uvs = [value for vertex in self.vertices for value in vertex.uv]
        accessors: list[dict] = [
            {"bufferView": 0, "componentType": 5126, "count": len(self.vertices), "type": "VEC3", "min": [min(positions[i::3]) for i in range(3)], "max": [max(positions[i::3]) for i in range(3)]},
            {"bufferView": 1, "componentType": 5126, "count": len(self.vertices), "type": "VEC3"},
            {"bufferView": 2, "componentType": 5126, "count": len(self.vertices), "type": "VEC2"},
            {"bufferView": 3, "componentType": 5125, "count": len(self.indices), "type": "SCALAR"},
        ]
        meshes_out: list[dict] = []
        for mesh in self.meshes:
            meshes_out.append({
                "name": mesh["name"],
                "primitives": [{
                    "attributes": {"POSITION": 0, "NORMAL": 1, "TEXCOORD_0": 2},
                    "indices": 3,
                    "material": mesh["material"],
                }],
            })
        # Each primitive uses the full vertex/index arrays; this is valid for
        # a visual kit, and separate nodes still preserve the modular pieces.
        gltf = {
            "asset": {"version": "2.0", "generator": "ANANTA Nova Modular Kit"},
            "scene": 0,
            "scenes": [{"nodes": list(range(len(self.nodes)))}],
            "nodes": self.nodes,
            "meshes": meshes_out,
            "materials": self.materials,
            "textures": self.textures,
            "images": self.images,
            "samplers": [{"magFilter": 9729, "minFilter": 9987, "wrapS": 10497, "wrapT": 10497}],
            "buffers": [{"byteLength": len(self.binary)}],
            "bufferViews": buffer_views,
            "accessors": accessors,
        }
        # The shared accessor strategy uses all data for every primitive.  To
        # avoid drawing unrelated pieces, duplicate the local ranges as
        # accessors per mesh and rebuild primitive references.
        accessors = accessors[:3]
        for mesh_index, mesh in enumerate(self.meshes):
            first = mesh["firstVertex"]
            count = mesh["vertexCount"]
            index_start, index_count = mesh_index_offsets[mesh_index]
            accessors.extend([
                {"bufferView": 0, "byteOffset": first * 12, "componentType": 5126, "count": count, "type": "VEC3"},
                {"bufferView": 1, "byteOffset": first * 12, "componentType": 5126, "count": count, "type": "VEC3"},
                {"bufferView": 2, "byteOffset": first * 8, "componentType": 5126, "count": count, "type": "VEC2"},
                {"bufferView": 3, "byteOffset": index_start * 4, "componentType": 5125, "count": index_count, "type": "SCALAR"},
            ])
            base = len(accessors) - 4
            meshes_out[mesh_index]["primitives"][0] = {
                "attributes": {"POSITION": base, "NORMAL": base + 1, "TEXCOORD_0": base + 2},
                "indices": base + 3,
                "material": mesh["material"],
            }
        gltf["accessors"] = accessors
        gltf["meshes"] = meshes_out
        json_bytes = json.dumps(gltf, separators=(",", ":")).encode("utf-8")
        json_bytes += b" " * ((_align4(len(json_bytes)) - len(json_bytes)) % 4)
        binary_bytes = bytes(self.binary) + b"\x00" * ((_align4(len(self.binary)) - len(self.binary)) % 4)
        header = struct.pack("<4sII", b"glTF", 2, 12 + 8 + len(json_bytes) + 8 + len(binary_bytes))
        payload = header + struct.pack("<I4s", len(json_bytes), b"JSON") + json_bytes + struct.pack("<I4s", len(binary_bytes), b"BIN\x00") + binary_bytes
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(payload)


def _align4(value: int) -> int:
    return (value + 3) & ~3


def _png_rgba(width: int, height: int, pixel_fn) -> bytes:
    rows = []
    for y in range(height):
        row = bytearray([0])
        for x in range(width):
            row.extend(pixel_fn(x, y))
        rows.append(bytes(row))
    raw = b"".join(rows)
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")


def make_facade_texture() -> bytes:
    def pixel(x: int, y: int) -> tuple[int, int, int, int]:
        cell_x = x % 32
        cell_y = y % 32
        band = 8 <= cell_y <= 24 and 5 <= cell_x <= 26
        if band:
            pulse = int(30 * (0.5 + 0.5 * math.sin((x + y) * 0.15)))
            return (20, 95 + pulse, 140 + pulse, 255)
        base = 16 + int(10 * (1.0 - y / 255.0))
        return (base, base + 8, base + 16, 255)
    return _png_rgba(256, 256, pixel)


def build_kit(output: Path) -> None:
    builder = GlbBuilder()
    facade_texture = builder.add_png_texture("T_NovaFacade_Procedural", make_facade_texture())
    facade = builder.add_material("NovaFacade", (1.0, 1.0, 1.0, 1.0), metallic=0.2, roughness=0.58, texture_index=facade_texture)
    concrete = builder.add_material("NovaConcrete", (0.055, 0.075, 0.11, 1.0), metallic=0.25, roughness=0.7)
    glass = builder.add_material("NovaGlass", (0.025, 0.08, 0.15, 1.0), metallic=0.72, roughness=0.16)
    neon = builder.add_material("NovaNeon", (0.01, 0.015, 0.03, 1.0), metallic=0.1, roughness=0.3, emissive=(0.0, 3.5, 5.0))
    magenta = builder.add_material("NovaMagenta", (0.03, 0.005, 0.04, 1.0), metallic=0.1, roughness=0.32, emissive=(3.0, 0.0, 2.8))
    road = builder.add_material("NovaRoad", (0.012, 0.016, 0.026, 1.0), metallic=0.25, roughness=0.38)
    white = builder.add_material("NovaRoadMark", (0.8, 0.86, 0.9, 1.0), metallic=0.0, roughness=0.42)

    # A detailed tower module, with repeated ledges and window bays.
    builder.add_box("NovaTower_Facade", (0.0, 0.0, 12.0), (12.0, 8.0, 24.0), facade, uv_scale=(3.0, 6.0))
    builder.add_box("NovaTower_Base", (0.0, 0.0, 0.35), (14.0, 10.0, 0.7), concrete)
    for z in (4.0, 9.0, 14.0, 19.0):
        builder.add_box(f"NovaTower_Ledge_{z:.0f}", (0.0, -4.25, z), (13.2, 0.6, 0.38), concrete)
        builder.add_box(f"NovaTower_LedgeBack_{z:.0f}", (0.0, 4.25, z), (13.2, 0.6, 0.38), concrete)
    for row, z in enumerate((3.0, 7.0, 11.0, 15.0, 19.0)):
        for col, x in enumerate((-4.5, -1.5, 1.5, 4.5)):
            builder.add_box(f"NovaTower_Window_{row}_{col}", (x, -4.08, z), (2.2, 0.16, 2.6), glass, uv_scale=(1.0, 1.0))
    builder.add_box("NovaTower_NeonBand", (0.0, -4.42, 11.8), (10.4, 0.1, 0.26), neon)
    builder.add_box("NovaTower_MagentaSign", (0.0, -4.5, 17.5), (5.6, 0.14, 1.1), magenta)
    builder.add_cylinder("NovaTower_RooftopCore", (0.0, 0.0, 25.4), 1.3, 2.6, concrete, sides=16)
    builder.add_cylinder("NovaTower_Antenna", (0.0, 0.0, 29.0), 0.12, 6.5, neon, sides=10)

    # Street module with sidewalk, curb, crosswalk and planters.
    builder.add_box("NovaStreet_Road", (0.0, 0.0, 0.10), (34.0, 12.0, 0.20), road, uv_scale=(8.0, 3.0))
    for side in (-1.0, 1.0):
        builder.add_box(f"NovaStreet_Sidewalk_{int(side)}", (0.0, side * 7.1, 0.25), (34.0, 2.0, 0.5), concrete, uv_scale=(6.0, 1.0))
        builder.add_box(f"NovaStreet_Curb_{int(side)}", (0.0, side * 6.05, 0.48), (34.0, 0.25, 0.46), white)
        for x in (-12.0, -4.0, 4.0, 12.0):
            builder.add_box(f"NovaStreet_Planter_{int(side)}_{int(x)}", (x, side * 7.5, 0.85), (1.2, 0.8, 1.2), concrete)
            builder.add_cylinder(f"NovaStreet_PlanterTree_{int(side)}_{int(x)}", (x, side * 7.5, 2.5), 0.42, 3.2, neon, sides=10)
    for index, x in enumerate((-6.0, -4.0, -2.0, 0.0, 2.0, 4.0, 6.0)):
        builder.add_box(f"NovaStreet_Crosswalk_{index}", (x, 0.0, 0.215), (0.85, 5.0, 0.03), white)
    builder.add_cylinder("NovaStreet_LampPole", (-13.0, -6.9, 3.2), 0.10, 6.4, concrete, sides=10)
    builder.add_box("NovaStreet_LampHead", (-13.0, -6.9, 6.5), (1.0, 0.35, 0.22), neon)
    builder.add_box("NovaStreet_NeonBillboard", (10.0, 6.4, 4.0), (4.4, 0.25, 2.1), magenta)

    builder.build(output)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("Saved/Generated/Nova_ModularKit.glb"))
    args = parser.parse_args()
    build_kit(args.output)
    print(json.dumps({"output": str(args.output.resolve()), "bytes": args.output.stat().st_size}, indent=2))


if __name__ == "__main__":
    main()
