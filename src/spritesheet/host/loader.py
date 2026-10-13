"""Plugin loader: discover `.py` modules and turn them into Plugin objects.

Discovery scans each plugin directory for `*.py` files (skipping
`_`-prefixed), imports them under a namespaced module name, and looks
for a module-level `PLUGIN` object or a `register(registry)` function.
Import errors are captured per-file so one broken plugin doesn't take
down the whole host.
"""
from __future__ import annotations

import importlib.util
import logging
import sys
from pathlib import Path

from spritesheet.plugins.contracts import Plugin, PluginError

log = logging.getLogger("spritesheet.loader")


class LoadedPlugin:
    __slots__ = ("name", "version", "origin", "module")

    def __init__(self, name: str, version: str, origin: Path, module: object) -> None:
        self.name = name
        self.version = version
        self.origin = origin
        self.module = module


def discover(directory: Path) -> list[Path]:
    if not directory.is_dir():
        return []
    return sorted(
        p for p in directory.glob("*.py") if not p.name.startswith("_")
    )


def load_file(path: Path) -> LoadedPlugin:
    mod_name = f"spritesheet_plugin_{path.stem}"
    spec = importlib.util.spec_from_file_location(mod_name, path)
    if spec is None or spec.loader is None:
        raise PluginError(f"cannot build import spec for {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # noqa: BLE001 - surface any plugin fault
        sys.modules.pop(mod_name, None)
        raise PluginError(f"{path.name}: import failed: {exc}") from exc

    plugin_obj = getattr(module, "PLUGIN", None)
    if plugin_obj is not None:
        if not isinstance(plugin_obj, Plugin):
            raise PluginError(f"{path.name}: PLUGIN does not satisfy Plugin protocol")
        return LoadedPlugin(plugin_obj.name, plugin_obj.version, path, module)

    if hasattr(module, "register"):
        name = getattr(module, "PLUGIN_NAME", path.stem)
        version = getattr(module, "PLUGIN_VERSION", "0.0.0")
        return LoadedPlugin(name, version, path, module)

    raise PluginError(f"{path.name}: no PLUGIN object and no register() function")