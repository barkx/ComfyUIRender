# -*- coding: utf-8 -*-
"""
revit_context.py
Simple module-level storage for the Revit UIDocument.
Populated by script.py on startup so render_window.py
can always find uidoc even when running from a WPF thread.
"""
uidoc = None
