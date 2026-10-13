# Contributing to sprite-sheet-extractor-editor

Thanks for wanting to peel sprites with us. This project is a Windows
desktop tool that extracts individual frames from sprite sheets/atlases
and lets you edit, repack, and re-export them. Contributions of all
sizes are welcome — new sheet-format loaders, background-removal
heuristics, packer algorithms, editor UX, docs.

## Ground rules

- One feature or fix per pull request.
- Every new importer/exporter lives behind the plugin contract in
  `src/spritesheet/plugins/contracts.py`. Do not fork the loader core.
- Tests are required for anything touching slicing, packing, or
  background removal. `pytest -q` must pass locally.
- Keep the UI thread free. Long work goes in a worker or the plugin runs
  in the process pool.

## Development setup

```bat
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
python -m spritesheet
```

## Plugin authoring

A plugin is a Python module that exposes a `register(registry)` function.
It may contribute:

- `SheetImporter` — parse a file into a `SheetImage` + metadata.
- `SheetExporter` — write frames back out to a target format.
- `SliceStrategy` — propose frame rectangles from a sheet.
- `BackgroundRemover` — strip a keyed color or alpha threshold.

See `src/spritesheet/plugins/builtin/grid_slicer.py` for a minimal
working example and `docs` in the plugin contract docstrings for the
exact return shapes.

## Commit style

`area: short imperative summary` — e.g. `slicer: fix off-by-one on
trailing gutter`, `editor: debounce frame rename`.

## Reporting bugs

Include the sheet file (or a redacted crop), the tool version printed by
`python -m spritesheet --version`, and the exact slice parameters used.