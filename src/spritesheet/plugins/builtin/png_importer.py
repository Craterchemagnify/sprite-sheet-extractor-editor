"""Built-in PNG/WebP importer.

Decodes the sheet to RGBA via Pillow and returns a SheetImage with no
frames; slicing is a separate strategy. Handles the common case where
the sheet is a plain image with no embedded atlas metadata.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, UnidentifiedImageError

from spritesheet.models.sheet import SheetImage
from spritesheet.plugins.contracts import PluginError

PLUGIN_NAME = "builtin.png-importer"
PLUGIN_VERSION = "0.6.2"

_EXTENSIONS = (".png", ".webp", ".bmp", ".gif")


class PngImporter:
    name = "png"
    extensions = _EXTENSIONS

    def can_load(self, path: Path) -> bool:
        return path.suffix.lower() in _EXTENSIONS

    def load(self, path: Path) -> SheetImage:
        if not path.is_file():
            raise PluginError(f"file not found: {path}")
        try:
            with Image.open(path) as img:
                rgba = img.convert("RGBA")
                pixels = np.asarray(rgba, dtype=np.uint8).copy()
        except UnidentifiedImageError as exc:
            raise PluginError(f"not a decodable image: {path.name}") from exc
        except OSError as exc:
            raise PluginError(f"failed to read {path.name}: {exc}") from exc

        sheet = SheetImage(pixels=pixels, source_path=path)
        sheet.meta["importer"] = self.name
        sheet.meta["original_format"] = path.suffix.lower().lstrip(".")
        return sheet


def register(registry) -> None:
    registry.add_importer(PngImporter())