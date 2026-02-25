# Changelog

## [1.0.0] - 2026-02-25

First public release.

### Features
- GDI BitBlt screen capture of active Revit 3D view
- Non-modal WPF window — Revit stays interactive during rendering
- Base64 image injection into ComfyUI workflow
- Flux2-Klein workflow with DF_Image_scale_to_side + ImageCrop+ nodes
- Prompt input with random seed per render
- Live status updates during generation
- Save result as PNG or open in system viewer
- Inline Settings panel (ComfyUI host + port)
- Stop button to cancel in-progress renders (calls /interrupt on ComfyUI)
- Two-column UI — large render output on the left, controls on the right
- Settings persist to `%APPDATA%\RevitComfyUI\settings.json`
- GUI installer (`Install.bat`) with auto-detection of pyRevit Extensions folder
