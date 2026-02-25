# -*- coding: utf-8 -*-
"""Start — capture 3D view and open the ComfyUI render window (non-modal)."""

import os, sys

EXTENSION_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
LIB_DIR = os.path.join(EXTENSION_DIR, "lib")
if LIB_DIR not in sys.path:
    sys.path.insert(0, LIB_DIR)

import clr
clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")

from Autodesk.Revit.DB import View3D
from pyrevit import revit, forms

import app_state
import revit_context

uidoc = revit.uidoc
revit_context.uidoc = uidoc

if not isinstance(uidoc.ActiveView, View3D):
    forms.alert(
        "Please switch to a 3D view first.\n\n"
        "Click the house icon on the View toolbar.",
        title="ComfyUI Render", warn_icon=True)
else:
    try:
        from snapshot import capture
        snapshot_path = capture(uidoc)

        # If window is already open just update its snapshot
        if app_state.is_window_open():
            app_state.window.update_snapshot(snapshot_path)
        else:
            from render_window import RenderWindow
            win = RenderWindow(snapshot_path, uidoc=uidoc)
            app_state.window = win
            win.show()          # non-modal — Revit stays interactive

    except Exception as ex:
        forms.alert("Error: " + str(ex), title="ComfyUI Render", warn_icon=True)
