"""Plugin host: owns discovery, loading, and registration order.

The host is deliberately dumb about what plugins *do*. It finds them,
loads them, and calls `register` with the shared registry. Registration
order is: built-in plugin dirs first (in directory-name order), then
user dirs. Later plugins may shadow earlier ones only by raising, since
the registry rejects duplicate names.
"""
from __future__ import annotations

import logging
from pathlib import Path

from spritesheet.host import loader
from spritesheet.host.registry import Registry
from spritesheet.plugins.contracts import PluginError

log = logging.getLogger("spritesheet.host")


class PluginHost:
    def __init__(self, registry: Registry) -> None:
        self.registry = registry
        self.loaded: list[loader.LoadedPlugin] = []
        self.failed: list[tuple[Path, str]] = []

    def discover_and_load(self, directories: list[Path]) -> int:
        count = 0
        for directory in directories:
            for path in loader.discover(directory):
                try:
                    plugin = loader.load_file(path)
                    self._register(plugin)
                except PluginError as exc:
                    log.warning("plugin load failed: %s", exc)
                    self.failed.append((path, str(exc)))
                    continue
                self.loaded.append(plugin)
                count += 1
        return count

    def _register(self, plugin: loader.LoadedPlugin) -> None:
        register = getattr(plugin.module, "register", None)
        if register is None:
            raise PluginError(f"{plugin.name}: no register() to call")
        register(self.registry)
        log.debug("registered plugin %s v%s", plugin.name, plugin.version)