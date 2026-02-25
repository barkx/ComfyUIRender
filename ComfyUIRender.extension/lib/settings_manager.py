# -*- coding: utf-8 -*-
"""Persist settings to %APPDATA%/RevitComfyUI/settings.json"""

import os
import json

_DIR  = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "RevitComfyUI")
_FILE = os.path.join(_DIR, "settings.json")

DEFAULTS = {
    "comfy_url":     "http://127.0.0.1:8000",
    "model_name":    "v1-5-pruned-emaonly.safetensors",
    "workflow_path": "",
    "steps":         20,
    "cfg_scale":     7.0,
    "denoise":       0.75,
}


def load():
    if os.path.exists(_FILE):
        try:
            with open(_FILE, "r") as f:
                data = json.load(f)
            for k, v in DEFAULTS.items():
                data.setdefault(k, v)
            return data
        except Exception:
            pass
    return dict(DEFAULTS)


def save(data):
    if not os.path.exists(_DIR):
        os.makedirs(_DIR)
    with open(_FILE, "w") as f:
        json.dump(data, f, indent=2)
