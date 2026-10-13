"""Core data model for a single extracted sprite frame.

A `Frame` is the atomic unit the editor manipulates: a rectangle into
the source sheet plus metadata the exporter needs. Frames are cheap
value objects; mutating the sheet means producing new frames, not
editing pixels in place.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class Rect:
    x: int
    y: int
    w: int
    h: int

    def __post_init__(self) -> None:
        if self.w <= 0 or self.h <= 0:
            raise ValueError(f"rect must be positive: {self!r}")
        if self.x < 0 or self.y < 0:
            raise ValueError(f"rect origin must be non-negative: {self!r}")

    @property
    def right(self) -> int:
        return self.x + self.w

    @property
    def bottom(self) -> int:
        return self.y + self.h

    def intersects(self, other: "Rect") -> bool:
        return not (
            self.right <= other.x
            or other.right <= self.x
            or self.bottom <= other.y
            or other.bottom <= self.y
        )

    def to_tuple(self) -> tuple[int, int, int, int]:
        return (self.x, self.y, self.w, self.h)


@dataclass(slots=True)
class Frame:
    name: str
    rect: Rect
    pivot: tuple[float, float] = (0.5, 0.5)
    tags: list[str] = field(default_factory=list)
    duration_ms: int = 100

    def rename(self, name: str) -> None:
        if not name.strip():
            raise ValueError("frame name cannot be blank")
        self.name = name