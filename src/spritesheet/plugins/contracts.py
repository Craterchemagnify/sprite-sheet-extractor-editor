"""Shared plugin contracts.

Every contribution a plugin can make is one of the Protocols below. The
host validates that a registered object satisfies its protocol before
adding it to the registry, so a malformed plugin fails at load time
with a clear error instead of at call time with an AttributeError.

All callables are pure with respect to the host: they receive a
`SheetImage` and return new data. They must not mutate the input sheet.
"""
from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

import numpy as np

from spritesheet.models.frame import Frame, Rect
from spritesheet.models.sheet import SheetImage


class PluginError(RuntimeError):
    """Raised by plugins for expected, user-facing failures."""


@runtime_checkable
class SheetImporter(Protocol):
    """Turn a file on disk into a SheetImage."""

    name: str
    extensions: tuple[str, ...]

    def can_load(self, path: Path) -> bool: ...

    def load(self, path: Path) -> SheetImage: ...


@runtime_checkable
class SheetExporter(Protocol):
    """Write frames back out to a target format."""

    name: str

    def export(
        self,
        sheet: SheetImage,
        frames: list[Frame],
        out_dir: Path,
        *,
        fmt: str,
    ) -> list[Path]: ...


@runtime_checkable
class SliceStrategy(Protocol):
    """Propose frame rectangles from a sheet.

    Returns candidate rects ordered as the strategy believes they should
    appear. The host deduplicates overlapping candidates.
    """

    name: str

    def propose(self, sheet: SheetImage, **params: int) -> list[Rect]: ...


@runtime_checkable
class BackgroundRemover(Protocol):
    """Produce an alpha mask for a sheet, given keying parameters."""

    name: str

    def mask(
        self,
        pixels: np.ndarray,
        *,
        key_color: tuple[int, int, int],
        tolerance: int,
    ) -> np.ndarray: ...


@runtime_checkable
class Plugin(Protocol):
    """A plugin module's entry object."""

    name: str
    version: str

    def register(self, registry: "PluginRegistryLike") -> None: ...


class PluginRegistryLike(Protocol):
    def add_importer(self, importer: SheetImporter) -> None: ...
    def add_exporter(self, exporter: SheetExporter) -> None: ...
    def add_slicer(self, slicer: SliceStrategy) -> None: ...
    def add_remover(self, remover: BackgroundRemover) -> None: ...