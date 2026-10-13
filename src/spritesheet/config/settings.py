"""User settings: plugin paths, editor defaults, exporter preferences.

Settings resolve from (lowest to highest precedence): built-in defaults,
`config/default.toml` shipped with the repo, then the user config at
`%APPDATA%/sprite-sheet-extractor-editor/config.toml`.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    import tomllib  # py3.11+
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore[no-redef]


def _appdata() -> Path:
    base = os.environ.get("APPDATA")
    if base:
        return Path(base) / "sprite-sheet-extractor-editor"
    return Path.home() / ".config" / "sprite-sheet-extractor-editor"


@dataclass
class Settings:
    extra_plugin_dirs: list[Path] = field(default_factory=list)
    default_gutter: int = 0
    default_margin: int = 0
    bg_key_color: tuple[int, int, int] = (255, 0, 255)
    bg_alpha_threshold: int = 8
    export_format: str = "png"

    @classmethod
    def load(cls) -> "Settings":
        data: dict = {}
        for candidate in _config_candidates():
            if candidate.is_file():
                with candidate.open("rb") as fh:
                    data.update(tomllib.load(fh))
        s = cls()
        extract = data.get("extract", {})
        s.default_gutter = int(extract.get("gutter", s.default_gutter))
        s.default_margin = int(extract.get("margin", s.default_margin))
        export = data.get("export", {})
        s.export_format = str(export.get("format", s.export_format))
        plugins = data.get("plugins", {})
        for p in plugins.get("extra_dirs", []):
            s.extra_plugin_dirs.append(Path(p))
        return s

    def plugin_dirs(self) -> list[Path]:
        dirs = [Path(__file__).resolve().parent.parent / "plugins" / "builtin"]
        dirs.append(_appdata() / "plugins")
        dirs.extend(self.extra_plugin_dirs)
        return [d for d in dirs if d.is_dir()]


def _config_candidates() -> list[Path]:
    repo_default = Path(__file__).resolve().parents[3] / "config" / "default.toml"
    return [repo_default, _appdata() / "config.toml"]