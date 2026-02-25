# ComfyUIRender

A [pyRevit](https://github.com/pyRevitLabs/pyRevit) plugin that connects Autodesk Revit directly to [ComfyUI](https://github.com/comfyanonymous/ComfyUI). Capture your 3D view, write a prompt, and get an AI-rendered image — without leaving Revit.

![ComfyUIRender Screenshot](screenshot.png)

---

## Features

- One-click snapshot of the active Revit 3D view
- Non-modal window — Revit stays fully interactive while rendering
- Prompt-driven rendering via Flux2-Klein
- Live status updates during generation
- Save or open the result directly from the app

---

## Requirements

### Revit
- Autodesk Revit 2025
- [pyRevit](https://github.com/pyRevitLabs/pyRevit/releases/latest) (latest release)

### ComfyUI
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI)

**Custom nodes** — install via [ComfyUI Manager](https://github.com/ltdrdata/ComfyUI-Manager):
- `comfyui-easy-use`
- `derfuu-comfyui-moddednodes`
- `comfyui-essentials`

**Models** — place in your ComfyUI `models/` folder:
- `flux-2-klein-4b-fp8.safetensors` → `models/unet/`
- `qwen_3_4b.safetensors` → `models/clip/`
- `flux2-vae.safetensors` → `models/vae/`

### Hardware
- NVIDIA GPU with at least 8GB VRAM recommended

---

## Installation

### 1. Install pyRevit
Download and install from the [pyRevit releases page](https://github.com/pyRevitLabs/pyRevit/releases/latest).

### 2. Install ComfyUI
Follow the [ComfyUI installation guide](https://github.com/comfyanonymous/ComfyUI#installing). Install all required custom nodes and models listed above.

### 3. Install ComfyUIRender
1. Download the latest `ComfyUIRender.zip` from [Releases](https://github.com/barkx/ComfyUIRender/releases)
2. Extract the ZIP
3. Run `Install.bat`
4. The installer will detect your pyRevit Extensions folder automatically
5. Click **Install / Update Plugin**

### 4. Start using it
1. Start ComfyUI (`python main.py`)
2. Open Revit and switch to a 3D view
3. In the Revit ribbon, go to the **ComfyUI Render** tab
4. Click **Start** — the render window will open with a snapshot of your view
5. Enter a prompt and click **Render**

> **Updating:** Just run `Install.bat` again and click Install / Update, then in Revit go to **pyRevit tab → Reload Scripts**. No Revit restart needed.

---

## Configuration

Click **Settings** inside the app to configure the ComfyUI connection.

| Setting | Default | Description |
|---|---|---|
| Host | `http://127.0.0.1` | ComfyUI server address |
| Port | `8000` | ComfyUI server port |

If ComfyUI is running on a different machine, enter its local IP address as the host.

---

## Workflow

The plugin uses a Flux2-Klein workflow with the following pipeline:

```
Revit 3D View → GDI Screen Capture → Base64 → ComfyUI
→ Scale to side → Crop 1:1 → Flux2-Klein → Save Image
```

Output size is controlled by nodes `141` and `143` in `workflow.py`. Default is `2048` → cropped to `2048×2048`. To change output size, edit these values in `lib/workflow.py`:

```python
"141": {"inputs": {"side_length": 2048, ...
"143": {"inputs": {"width": 2048, "height": 2048, ...
```

---

## File Structure

```
ComfyUIRender.extension/
├── ComfyUI Render.tab/
│   └── Render.panel/
│       └── StartRender.pushbutton/
│           └── script.py          # Ribbon button entry point
└── lib/
    ├── app_state.py               # Global window + stop state
    ├── comfy_http.py              # HTTP calls to ComfyUI API
    ├── render_window.py           # WPF UI
    ├── revit_context.py           # Stores uidoc reference
    ├── settings_manager.py        # Reads/writes settings.json
    ├── snapshot.py                # GDI screen capture
    └── workflow.py                # ComfyUI workflow definition
```

---

## Troubleshooting

**Snapshot failed**
- Make sure a 3D view is active in Revit before clicking Start
- The viewport must be visible on screen

**Connection error**
- Make sure ComfyUI is running (`python main.py`)
- Check the host and port in Settings match your ComfyUI instance
- Default ComfyUI port is `8188` — check your setup

**Render hangs / times out**
- Check the ComfyUI terminal for errors
- Make sure all custom nodes and models are installed correctly
- Click Stop and try again

**Changes not appearing after update**
- In Revit: pyRevit tab → Reload Scripts

---

## Contributing

Pull requests welcome. Please open an issue first to discuss what you'd like to change.

---

## License

MIT © [barkx](https://github.com/barkx)
