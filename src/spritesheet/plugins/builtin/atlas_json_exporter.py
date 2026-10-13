"""Built-in exporter: individual PNGs plus a TexturePacker-style JSON atlas.

Writes one PNG per frame plus `atlas.json` describing frame rects,
pivots, and tags. JSON shape matches the common
`{"frames": {...}, "meta": {...}}` layout so it drops into most engines.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image

from spritesheet.models.frame import Frame
from spritesheet.models.sheet import SheetImage
from spritesheet.plugins.contracts import PluginError

PLUGIN_NAME = "builtin.atlas-json-exporter"
PLUGIN_VERSION = "0.6.2"


class AtlasJsonExporter:
    name = "atlas-json"

    def export(
        self,
        sheet: SheetImage,
        frames: list[Frame],
        out_dir: Path,
        *,
        fmt: str,
    ) -> list[Path]:
        if not frames:
            raise PluginError("no frames to export")
        out_dir.mkdir(parents=True, exist_ok=True)
        written: list[Path] = []
        entries: dict[str, dict] = {}

        for frame in frames:
            crop = sheet.crop(frame.rect)
            if fmt == "webp":
                img = Image.fromarray(crop, mode="RGBA")
                target = out_dir / f"{frame.name}.webp"
                img.save(target, format="WEBP", lossless=True)
            else:
                target = out_dir / f"{frame.name}.png"
                Image.fromarray(crop, mode="RGBA").save(target, format="PNG")
            written.append(target)
            entries[frame.name] = {
                "frame": {
                    "x": frame.rect.x,
                    "y": frame.rect.y,
                    "w": frame.rect.w,
                    "h": frame.rect.h,
                },
                "pivot": {"x": frame.pivot[0], "y": frame.pivot[1]},
                "tags": list(frame.tags),
                "duration": frame.duration_ms,
            }

        atlas = {
            "frames": entries,
            "meta": {
                "app": "sprite-sheet-extractor-editor",
                "version": "0.6.2",
                "image": sheet.source_path.name if sheet.source_path else "sheet",
                "size": {"w": sheet.width, "h": sheet.height},
            },
        }
        atlas_path = out_dir / "atlas.json"
        atlas_path.write_text(json.dumps(atlas, indent=2), encoding="utf-8")
        written.append(atlas_path)
        return written


def register(registry) -> None:
    registry.add_exporter(AtlasJsonExporter())