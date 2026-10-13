# Security Policy

## Supported versions

| Version | Supported |
| ------- | --------- |
| 0.6.x   | yes       |
| 0.5.x   | security fixes only |
| < 0.5   | no        |

## Reporting a vulnerability

Do not open a public issue for security problems. Email
`security@sprite-sheet-extractor-editor.dev` with a description,
reproduction steps, and the affected version.

We care specifically about:

- Malicious sheet/atlas files that cause a parser to read out of
  bounds, allocate unbounded memory, or execute code. The importer
  sandbox treats every input as hostile.
- Plugin loading: third-party plugins run in-process by default. Report
  any path that lets a plugin escape its declared capabilities.
- Unsafe deserialization in project files (`.spx`). We use a restricted
  loader; report any bypass.

## Threat model

The tool opens user-supplied image files and project files. Image
decoding is delegated to Pillow; project files are parsed by our own
restricted reader. Plugins are trusted code from the user's plugin
directory — installing a plugin is equivalent to running a script, and
the UI warns on first load.

## Disclosure

We aim to acknowledge within 72 hours and ship a fix within 30 days for
high-severity issues.