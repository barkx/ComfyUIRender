# Contributing

Thanks for your interest in contributing to ComfyUIRender!

## Getting Started

1. Fork the repo and clone it locally
2. Install pyRevit and ComfyUI with all dependencies (see README)
3. Run `Install.bat` to install the plugin from your local clone
4. Make your changes in `ComfyUIRender.extension/lib/`
5. Test in Revit using **pyRevit tab → Reload Scripts** (no restart needed)

## What's Welcome

- Bug fixes
- Support for additional ComfyUI workflows
- UI improvements
- Compatibility with other Revit versions
- Better error messages and diagnostics

## Submitting a PR

- Open an issue first to discuss the change
- Keep PRs focused — one thing at a time
- Test in Revit before submitting
- Update `CHANGELOG.md` with what you changed

## Code Notes

- All lib code must be **IronPython 2.7 compatible** — no f-strings, no `exist_ok`, no py3-only stdlib
- UI is WPF XAML parsed at runtime via `XamlReader.Parse()` — no compiled resources
- `app_state.py` holds the global window reference so ribbon buttons can communicate with the open window
- `workflow.py` is the easiest place to swap in a different ComfyUI pipeline
