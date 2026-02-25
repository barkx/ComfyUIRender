# -*- coding: utf-8 -*-
"""
snapshot.py  —  Capture the active Revit 3D view as a PNG.

Two methods tried in order:
  1. GDI BitBlt  — reads screen pixels of the exact viewport rectangle
  2. ExportImage — Revit's own export, kept as fallback

IronPython 2.7 compatible (no exist_ok, no f-strings, no py3-only stdlib).
"""

import os
import ctypes
import tempfile
import glob

TMP_DIR = os.path.join(tempfile.gettempdir(), "RevitComfyUI")


def _ensure_dir(path):
    """makedirs without exist_ok (IronPython 2.7 compatible)."""
    if not os.path.exists(path):
        os.makedirs(path)


def capture(uidoc):
    """
    Try GDI capture first, then ExportImage fallback.
    Returns path to saved PNG, or raises Exception.
    """
    import time
    _ensure_dir(TMP_DIR)
    # Unique name per capture so WPF never shows a stale cached image
    out = os.path.join(TMP_DIR, "snap_{0}.png".format(int(time.time())))

    errors = []

    # ── Method 1: GDI screen capture ─────────────────────────────────────
    try:
        path = _capture_gdi(uidoc, out)
        if path and os.path.exists(path) and os.path.getsize(path) > 1000:
            crop_to_1366x768(path)
            return path
        else:
            errors.append("GDI: file not created or empty")
    except Exception as ex:
        errors.append("GDI: " + str(ex))

    # ── Method 2: ExportImage fallback ────────────────────────────────────
    try:
        path = _capture_export_image(uidoc.Document, out)
        if path and os.path.exists(path) and os.path.getsize(path) > 1000:
            crop_to_1366x768(path)
            return path
        else:
            errors.append("ExportImage: file not created or empty")
    except Exception as ex:
        errors.append("ExportImage: " + str(ex))

    raise Exception("All snapshot methods failed:\n  " + "\n  ".join(errors))


# ── Method 1: GDI BitBlt ──────────────────────────────────────────────────────

def _capture_gdi(uidoc, out_path):
    import clr
    clr.AddReference("RevitAPIUI")
    clr.AddReference("System.Drawing")
    clr.AddReference("System")

    import System
    import System.Drawing
    import System.Drawing.Imaging

    # Find UIView for active view
    uiview = None
    for v in uidoc.GetOpenUIViews():
        if v.ViewId == uidoc.ActiveView.Id:
            uiview = v
            break

    if uiview is None:
        raise Exception("No open UIView for active view")

    rect   = uiview.GetWindowRectangle()
    left   = rect.Left
    top    = rect.Top
    width  = rect.Right  - rect.Left
    height = rect.Bottom - rect.Top

    if width < 10 or height < 10:
        raise Exception("Viewport rectangle too small ({0}x{1})".format(width, height))

    # Windows GDI calls
    user32 = ctypes.windll.user32
    gdi32  = ctypes.windll.gdi32

    hdc_screen = user32.GetDC(0)
    hdc_mem    = gdi32.CreateCompatibleDC(hdc_screen)
    hbmp       = gdi32.CreateCompatibleBitmap(hdc_screen, width, height)
    gdi32.SelectObject(hdc_mem, hbmp)

    SRCCOPY = 0x00CC0020
    ok = gdi32.BitBlt(hdc_mem, 0, 0, width, height,
                      hdc_screen, left, top, SRCCOPY)

    if not ok:
        gdi32.DeleteObject(hbmp)
        gdi32.DeleteDC(hdc_mem)
        user32.ReleaseDC(0, hdc_screen)
        raise Exception("BitBlt returned 0 (failed)")

    # Convert to System.Drawing.Bitmap and save
    bmp = System.Drawing.Bitmap.FromHbitmap(System.IntPtr(hbmp))
    bmp.Save(out_path, System.Drawing.Imaging.ImageFormat.Png)
    bmp.Dispose()

    gdi32.DeleteObject(hbmp)
    gdi32.DeleteDC(hdc_mem)
    user32.ReleaseDC(0, hdc_screen)

    return out_path


# ── Method 2: ExportImage ─────────────────────────────────────────────────────

def _capture_export_image(doc, out_path):
    import clr
    import shutil
    clr.AddReference("RevitAPI")
    from Autodesk.Revit.DB import (
        ImageExportOptions, ImageFileType,
        ImageResolution, ZoomFitType, ExportRange
    )

    prefix = os.path.join(TMP_DIR, "snap_export")

    # Clean previous
    for f in glob.glob(prefix + "*.png"):
        try:
            os.remove(f)
        except Exception:
            pass

    opts = ImageExportOptions()
    opts.ExportRange            = ExportRange.CurrentView
    opts.FilePath               = prefix
    opts.HLRandWFViewsFileType  = ImageFileType.PNG
    opts.ImageResolution        = ImageResolution.DPI_150
    opts.ZoomType               = ZoomFitType.FitToPage
    opts.PixelSize              = 1280

    doc.ExportImage(opts)

    # Find whatever Revit named the file
    candidates = glob.glob(os.path.join(TMP_DIR, "snap_export*.png"))
    if candidates:
        newest = max(candidates, key=os.path.getmtime)
        shutil.copy2(newest, out_path)
        return out_path

    raise Exception("ExportImage produced no PNG file in " + TMP_DIR)


# ── Public: GDI only (safe from any thread, no Revit API calls) ──────────────
def capture_gdi_only(uidoc):
    """
    Capture viewport using GDI BitBlt only.
    Safe to call from WPF button handlers (no Revit API transactions).
    Uses a timestamped filename so WPF never serves a stale cached image.
    Raises Exception if it fails.
    """
    import time
    _ensure_dir(TMP_DIR)
    # Unique filename per capture so WPF image cache is always invalidated
    out = os.path.join(TMP_DIR, "snap_{0}.png".format(int(time.time())))
    # Remove previous snapshots to avoid clutter
    for old_f in glob.glob(os.path.join(TMP_DIR, "snap_*.png")):
        try:
            os.remove(old_f)
        except Exception:
            pass
    path = _capture_gdi(uidoc, out)
    crop_to_1366x768(path)
    return path
def crop_to_1366x768(src_path):
    """
    Crop the centre of src_path to 16:9 then resize to 1366x768.
    Overwrites the file in-place. Uses System.Drawing (always available).
    Falls back to PIL if present.
    """
    try:
        import clr
        clr.AddReference("System.Drawing")
        import System.Drawing as SD
        import System.Drawing.Imaging as SDI

        src = SD.Bitmap(src_path)
        sw, sh = src.Width, src.Height

        # Crop to 16:9 centre
        target_ratio = 1366.0 / 768.0
        src_ratio    = float(sw) / float(sh)
        if src_ratio > target_ratio:
            crop_w = int(sh * target_ratio)
            crop_h = sh
        else:
            crop_w = sw
            crop_h = int(sw / target_ratio)
        cx = (sw - crop_w) // 2
        cy = (sh - crop_h) // 2

        dst = SD.Bitmap(1366, 768)
        g   = SD.Graphics.FromImage(dst)
        g.InterpolationMode = System.Drawing.Drawing2D.InterpolationMode.HighQualityBicubic
        g.DrawImage(src, SD.Rectangle(0, 0, 1366, 768),
                         SD.Rectangle(cx, cy, crop_w, crop_h),
                         SD.GraphicsUnit.Pixel)
        g.Dispose()
        src.Dispose()

        dst.Save(src_path, SDI.ImageFormat.Png)
        dst.Dispose()
        return src_path
    except Exception as ex:
        # If System.Drawing crop fails, return original unchanged
        return src_path
