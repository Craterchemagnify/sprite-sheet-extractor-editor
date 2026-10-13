"""Application bootstrap: parse args, build the plugin host, launch the UI.

The host discovers plugins, wires the registry, and hands the registry
to the editor window. Headless mode (`--extract`) skips the UI and runs
a one-shot extraction, which is what CI and batch scripts use.
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from spritesheet.config.settings import Settings
from spritesheet.host.plugin_host import PluginHost
from spritesheet.host.registry import Registry
from spritesheet.services.batch import run_batch_extract

log = logging.getLogger("spritesheet")


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="spritesheet", description="Sprite sheet extractor & editor")
    p.add_argument("--version", action="store_true", help="print version and exit")
    p.add_argument("--plugin-dir", type=Path, default=None, help="extra plugin directory")
    p.add_argument("--extract", type=Path, default=None, help="headless: sheet to extract")
    p.add_argument("--out", type=Path, default=None, help="headless: output directory")
    p.add_argument("--cols", type=int, default=0, help="headless: fixed column count")
    p.add_argument("--rows", type=int, default=0, help="headless: fixed row count")
    p.add_argument("-v", "--verbose", action="store_true")
    return p


def run(argv: list[str]) -> int:
    args = _build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    if args.version:
        from spritesheet.version import __version__

        print(f"sprite-sheet-extractor-editor {__version__}")
        return 0

    settings = Settings.load()
    if args.plugin_dir:
        settings.extra_plugin_dirs.append(args.plugin_dir)

    registry = Registry()
    host = PluginHost(registry)
    loaded = host.discover_and_load(settings.plugin_dirs())
    log.info("loaded %d plugin(s)", loaded)

    if args.extract:
        if args.out is None:
            log.error("--extract requires --out")
            return 2
        return run_batch_extract(
            registry, args.extract, args.out, cols=args.cols, rows=args.rows
        )

    from spritesheet.ui.editor_window import launch

    return launch(registry, settings)