# Contributing

Keep changes small and focused.

## Adding a Detector

- Follow the existing file style in `detectors/`.
- Reuse `detectors/core/` helpers instead of rebuilding geometry or cooldown logic.
- Keep detector files short and easy to read.
- Rewrite ideas from `ref-things/reference-codes/` instead of copying code.

## Adding an Example

- Keep it minimal and runnable from its own folder.
- Give it a short `README.md` with goal, how it works, and how to run it.
- Prefer a self-contained script over shared example infrastructure.

## Code Style

- Follow [ref-things/project/CLAUDE.md](ref-things/project/CLAUDE.md).
- Use clear names and short functions.
- Avoid speculative abstraction.

## Pull Requests

- Keep each PR focused on one detector, one example, or one docs slice.
- Include the verification steps you ran.
