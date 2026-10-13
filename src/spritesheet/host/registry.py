"""Plugin registry: the shared table every extension writes into.

The registry is the single lookup point for importers, exporters,
slicers, and background removers. It validates protocols on add and
resolves by name or by file capability at lookup time.
"""
from __future__ import annotations

import logging
from pathlib import Path

from spritesheet.plugins.contracts import (
    BackgroundRemover,
    PluginError,
    SheetExporter,
    SheetImporter,
    SliceStrategy,
)

log = logging.getLogger("spritesheet.registry")


class Registry:
    def __init__(self) -> None:
        self._importers: dict[str, SheetImporter] = {}
        self._exporters: dict[str, SheetExporter] = {}
        self._slicers: dict[str, SliceStrategy] = {}
        self._removers: dict[str, BackgroundRemover] = {}

    def add_importer(self, importer: SheetImporter) -> None:
        self._register(self._importers, importer, "importer")

    def add_exporter(self, exporter: SheetExporter) -> None:
        self._register(self._exporters, exporter, "exporter")

    def add_slicer(self, slicer: SliceStrategy) -> None:
        self._register(self._slicers, slicer, "slicer")

    def add_remover(self, remover: BackgroundRemover) -> None:
        self._register(self._removers, remover, "background remover")

    @staticmethod
    def _register(table: dict, obj: object, kind: str) -> None:
        name = getattr(obj, "name", None)
        if not isinstance(name, str) or not name:
            raise PluginError(f"{kind} must expose a non-empty .name")
        if name in table:
            raise PluginError(f"duplicate {kind} name: {name!r}")
        table[name] = obj

    def importer_for(self, path: Path) -> SheetImporter:
        for imp in self._importers.values():
            if imp.can_load(path):
                return imp
        raise PluginError(f"no importer registered for {path.suffix or path.name}")

    def importer(self, name: str) -> SheetImporter:
        return self._lookup(self._importers, name, "importer")

    def exporter(self, name: str) -> SheetExporter:
        return self._lookup(self._exporters, name, "exporter")

    def slicer(self, name: str) -> SliceStrategy:
        return self._lookup(self._slicers, name, "slicer")

    def remover(self, name: str) -> BackgroundRemover:
        return self._lookup(self._removers, name, "background remover")

    def names(self) -> dict[str, list[str]]:
        return {
            "importers": sorted(self._importers),
            "exporters": sorted(self._exporters),
            "slicers": sorted(self._slicers),
            "removers": sorted(self._removers),
        }

    @staticmethod
    def _lookup(table: dict, name: str, kind: str):
        try:
            return table[name]
        except KeyError:
            raise PluginError(f"unknown {kind}: {name!r}") from None