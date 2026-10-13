"""In-memory representation of a loaded sprite sheet.

Holds the decoded RGBA pixel buffer (numpy, shape HxWx4, uint8), the
frame list, and provenance metadata. The buffer is the single source of
truth for pixels; slicing never mutates it.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from spritesheet.models.frame import Frame, Rect


@dataclass(slots=True)
class SheetImage:
    pixels: np.ndarray  # (H, W, 4) uint8, RGBA
    source_path: Path | None = None
    frames: list[Frame] = field(default_factory=list)
    meta: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.pixels.ndim != 3 or self.pixels.shape[2] != 4:
            raise ValueError(f"expected HxWx4 RGBA buffer, got {self.pixels.shape}")
        if self.pixels.dtype != np.uint8:
            raise ValueError(f"expected uint8 pixels, got {self.pixels.dtype}")

    @property
    def width(self) -> int:
        return int(self.pixels.shape[1])

    @property
    def height(self) -> int:
        return int(self.pixels.shape[0])

    def crop(self, rect: Rect) -> np.ndarray:
        if rect.right > self.width or rect.bottom > self.height:
            raise ValueError(f"rect {rect.to_tuple()} exceeds sheet {self.width}x{self.height}")
        return self.pixels[rect.y : rect.bottom, rect.x : rect.right].copy()

    def add_frame(self, frame: Frame) -> None:
        for existing in self.frames:
            if existing.name == frame.name:
                raise ValueError(f"duplicate frame name: {frame.name!r}")
        self.frames.append(frame)

    def frame_by_name(self, name: str) -> Frame | None:
        return next((f for f in self.frames if f.name == name), None)