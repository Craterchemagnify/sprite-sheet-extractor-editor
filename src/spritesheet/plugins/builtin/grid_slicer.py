"""Built-in grid slicer.

Slices a sheet into a regular cols x rows grid, honoring optional
margin (outer border) and gutter (spacing between cells). If cols/rows
are zero, the slicer attempts to infer them from the sheet dimensions
and a target cell size.
"""
from __future__ import annotations

from spritesheet.models.frame import Frame, Rect
from spritesheet.models.sheet import SheetImage

PLUGIN_NAME = "builtin.grid-slicer"
PLUGIN_VERSION = "0.6.2"

_MIN_CELL = 4


class GridSlicer:
    name = "grid"

    def propose(self, sheet: SheetImage, **params: int) -> list[Rect]:
        cols = int(params.get("cols", 0))
        rows = int(params.get("rows", 0))
        margin = max(0, int(params.get("margin", 0)))
        gutter = max(0, int(params.get("gutter", 0)))

        usable_w = sheet.width - 2 * margin
        usable_h = sheet.height - 2 * margin
        if usable_w <= 0 or usable_h <= 0:
            return []

        if cols <= 0 or rows <= 0:
            cell = int(params.get("cell", 32)) or 32
            cols = cols or max(1, (usable_w + gutter) // (cell + gutter))
            rows = rows or max(1, (usable_h + gutter) // (cell + gutter))

        cell_w = (usable_w - gutter * (cols - 1)) // cols
        cell_h = (usable_h - gutter * (rows - 1)) // rows
        if cell_w < _MIN_CELL or cell_h < _MIN_CELL:
            return []

        rects: list[Rect] = []
        for r in range(rows):
            for c in range(cols):
                x = margin + c * (cell_w + gutter)
                y = margin + r * (cell_h + gutter)
                rects.append(Rect(x, y, cell_w, cell_h))
        return rects

    def frames(self, sheet: SheetImage, **params: int) -> list[Frame]:
        prefix = str(params.get("prefix", "frame"))
        return [
            Frame(name=f"{prefix}_{i:03d}", rect=rect)
            for i, rect in enumerate(self.propose(sheet, **params))
        ]


def register(registry) -> None:
    registry.add_slicer(GridSlicer())