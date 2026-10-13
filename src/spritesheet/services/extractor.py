"""Extraction service: load a sheet, run a slicer, dedupe, name frames.

This is the headless-friendly core the UI and the batch runner both
call. It never touches Qt.
"""
from __future__ import annotations

import logging
from pathlib import Path

from spritesheet.host.registry import Registry
from spritesheet.models.frame import Frame, Rect
from spritesheet.models.sheet import SheetImage

log = logging.getLogger("spritesheet.extractor")


def load_sheet(registry: Registry, path: