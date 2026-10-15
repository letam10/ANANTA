"""Create readable contact sheets and verify fresh eight-view coverage."""

import json
import hashlib
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
folder = ROOT / "Saved" / "Upgrade" / "ModelViews"
coverage = json.loads((folder / "coverage.json").read_text(encoding="utf-8"))
for page in range(0, len(coverage), 5):
    items = coverage[page:page + 5]
    sheet = Image.new("RGB", (1600, len(items) * 225), (21, 27, 33))
    draw = ImageDraw.Draw(sheet)
    for row, item in enumerate(items):
        assert len(item["views"]) == 8
        mesh = ROOT / "Assets" / "CoastalUpgrade" / f"{item['model']}.fbx"
        assert item["source_sha256"] == hashlib.sha256(mesh.read_bytes()).hexdigest(), item["model"]
        draw.text((8, row * 225 + 5), item["model"], fill="white")
        for column, path in enumerate(item["views"]):
            with Image.open(path) as source:
                source.load()
                sheet.paste(source.convert("RGB").resize((200, 200)), (column * 200, row * 225 + 25))
            draw.text((column * 200 + 8, row * 225 + 207), f"{column * 45} deg", fill="white")
    sheet.save(folder / f"review-page-{page // 5 + 1}.jpg", quality=92)
print(f"MODEL_REVIEWS_OK {len(coverage)} models, {len(coverage) * 8} rendered views")
