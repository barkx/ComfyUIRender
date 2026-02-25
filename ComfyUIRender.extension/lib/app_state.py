# -*- coding: utf-8 -*-
"""
app_state.py
Shared module-level state so ribbon buttons can communicate
with the currently open render window.

window        -- reference to the active RenderWindow instance (or None)
stop_requested -- set to True to cancel a running render
"""

window         = None
stop_requested = False


def request_stop():
    global stop_requested
    stop_requested = True


def clear_stop():
    global stop_requested
    stop_requested = False


def is_window_open():
    global window
    if window is None:
        return False
    try:
        # WPF window IsLoaded property — False once closed
        return bool(window._win.IsLoaded)
    except Exception:
        return False
