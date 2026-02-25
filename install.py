#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RevitComfyUI Installer
Run via Install.bat or:  python install.py
"""

import os, sys, shutil, webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox

HERE = os.path.dirname(os.path.abspath(__file__))
EXT_SRC = os.path.join(HERE, "ComfyUIRender.extension")

BG = "#1A1A2E"; BG2 = "#1E1E32"; BG3 = "#0F0F1E"
ACC = "#6C63FF"; FG = "#E8E8F0"; DIM = "#9090B0"
GRN = "#55CC88"; ORG = "#FFAA55"; RED = "#FF5555"


def find_pyrevit():
    appdata = os.environ.get("APPDATA", "")
    local   = os.environ.get("LOCALAPPDATA", "")
    for root in [
        os.path.join(appdata, "pyRevit"),
        os.path.join(appdata, "pyRevit-Master"),
        os.path.join(local,   "pyRevit"),
        r"C:\pyRevit",
    ]:
        if os.path.isdir(root):
            return True, os.path.join(root, "Extensions")
    return False, os.path.join(appdata, "pyRevit", "Extensions")


class Installer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RevitComfyUI Installer")
        self.geometry("540x600")
        self.resizable(False, False)
        self.configure(bg=BG)

        pyrevit_ok, ext_default = find_pyrevit()
        self._ext = tk.StringVar(value=ext_default)
        self._pyrevit_ok = pyrevit_ok
        self._build_ui()
        self._check()

    # ── UI ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Header
        tk.Label(self, text="⚡ RevitComfyUI", bg=BG, fg=ACC,
                 font=("Segoe UI", 22, "bold")).pack(anchor="w", padx=28, pady=(24,2))
        tk.Label(self, text="Python Plugin  ·  powered by pyRevit",
                 bg=BG, fg=DIM, font=("Segoe UI", 11)).pack(anchor="w", padx=28, pady=(0,20))

        # Section 1 – pyRevit
        self._section("1.  pyRevit installed?")
        self._lbl_pyrevit = tk.Label(self, text="Checking…", bg=BG, fg=DIM,
                                     font=("Segoe UI", 11), wraplength=470, justify="left")
        self._lbl_pyrevit.pack(anchor="w", padx=40, pady=(0,4))
        self._dl_frame = tk.Frame(self, bg=BG)
        self._mk_btn("  Download pyRevit (free)  ", self._dl_pyrevit,
                     parent=self._dl_frame, sec=True).pack(side="left")

        # Section 2 – Extensions folder
        self._section("2.  pyRevit Extensions folder")
        row = tk.Frame(self, bg=BG)
        row.pack(fill="x", padx=28, pady=(0,14))
        self._entry = tk.Entry(row, textvariable=self._ext, bg=BG2, fg=FG,
                               insertbackground=FG, font=("Segoe UI", 10),
                               relief="flat", bd=0,
                               highlightthickness=1,
                               highlightbackground="#3A3A5C",
                               highlightcolor=ACC)
        self._entry.pack(side="left", fill="x", expand=True, ipady=7, ipadx=8)
        self._mk_btn("Browse", self._browse, parent=row, sec=True).pack(side="left", padx=(8,0))
        self._mk_btn("Open",   self._open,   parent=row, sec=True).pack(side="left", padx=(6,0))

        # Section 3 – Plugin files check
        self._section("3.  Plugin files")
        self._lbl_src = tk.Label(self, text="Checking…", bg=BG, fg=DIM,
                                 font=("Segoe UI", 10), wraplength=470, justify="left")
        self._lbl_src.pack(anchor="w", padx=40, pady=(0,14))

        # Divider
        tk.Frame(self, bg="#2E2E4A", height=1).pack(fill="x", padx=28, pady=(0,12))

        # Log
        log_frame = tk.Frame(self, bg=BG3)
        log_frame.pack(fill="both", expand=True, padx=28, pady=(0,12))
        self._log = tk.Text(log_frame, bg=BG3, fg="#9090B0",
                            font=("Consolas", 10), relief="flat",
                            state="disabled", wrap="word",
                            height=5, bd=0, padx=10, pady=8)
        self._log.pack(fill="both", expand=True)

        # Buttons
        btns = tk.Frame(self, bg=BG)
        btns.pack(fill="x", padx=28, pady=(0,8))
        self._mk_btn("  Install Plugin  ", self._install, parent=btns).pack(
            side="left", fill="x", expand=True)
        self._mk_btn("Uninstall", self._uninstall, parent=btns, sec=True).pack(
            side="left", padx=(10,0))

        self._status = tk.Label(self, text="", bg=BG, fg=DIM,
                                font=("Segoe UI", 11), wraplength=480)
        self._status.pack(pady=(0,18))

    def _section(self, title):
        tk.Label(self, text=title, bg=BG, fg=FG,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=28, pady=(4,4))

    def _mk_btn(self, text, cmd, parent=None, sec=False):
        p  = parent or self
        bg = "#2E2E4A" if sec else ACC
        b  = tk.Button(p, text=text, command=cmd, bg=bg, fg=FG,
                       font=("Segoe UI", 10, "bold"), relief="flat",
                       bd=0, cursor="hand2", padx=14, pady=7,
                       activebackground="#7C73FF", activeforeground="white")
        b.bind("<Enter>", lambda e, b=b: b.config(bg="#3E3E5A" if sec else "#7C73FF"))
        b.bind("<Leave>", lambda e, b=b, bg=bg: b.config(bg=bg))
        return b

    # ── Checks ────────────────────────────────────────────────────────────

    def _check(self):
        if self._pyrevit_ok:
            self._lbl_pyrevit.config(text="✅  pyRevit detected.", fg=GRN)
        else:
            self._lbl_pyrevit.config(
                text="⚠️  pyRevit not found. Please install it first — it's free.", fg=ORG)
            self._dl_frame.pack(anchor="w", padx=40, pady=(0,12))

        if os.path.isdir(EXT_SRC):
            self._lbl_src.config(text="✅  " + EXT_SRC, fg=GRN)
        else:
            self._lbl_src.config(
                text="❌  Not found:  " + EXT_SRC + "\n"
                     "    Keep install.py in the same folder as ComfyUIRender.extension", fg=RED)

    # ── Helpers ───────────────────────────────────────────────────────────

    def _write_log(self, msg):
        self._log.config(state="normal")
        self._log.insert("end", msg + "\n")
        self._log.see("end")
        self._log.config(state="disabled")

    def _set_status(self, msg, color=DIM):
        self._status.config(text=msg, fg=color)

    def _browse(self):
        d = filedialog.askdirectory(title="Select pyRevit Extensions folder",
                                    initialdir=self._ext.get())
        if d:
            self._ext.set(d)

    def _open(self):
        p = self._ext.get()
        os.makedirs(p, exist_ok=True)
        os.startfile(p)

    def _dl_pyrevit(self):
        webbrowser.open("https://github.com/pyRevitLabs/pyRevit/releases/latest")

    # ── Install / Uninstall ───────────────────────────────────────────────

    def _install(self):
        if not os.path.isdir(EXT_SRC):
            messagebox.showerror(
                "Files missing",
                "Cannot find:\n\n" + EXT_SRC + "\n\n"
                "Make sure install.py sits in the SAME folder as "
                "ComfyUIRender.extension and that you extracted the full ZIP.")
            return

        dest = os.path.join(self._ext.get().strip(), "ComfyUIRender.extension")
        self._write_log(">> Installing…")
        self._set_status("Installing…")
        self.update()

        try:
            os.makedirs(self._ext.get().strip(), exist_ok=True)
            if os.path.isdir(dest):
                shutil.rmtree(dest)
                self._write_log("   Removed previous version.")
            shutil.copytree(EXT_SRC, dest)
            self._write_log("   ✅  Copied to:  " + dest)
            self._write_log("")
            self._write_log("   Next steps:")
            self._write_log("   1. Start ComfyUI (python main.py)")
            self._write_log("   2. Restart Revit")
            self._write_log("   3. In Revit: pyRevit tab → Reload")
            self._write_log("   4. Look for 'ComfyUI Render' tab in ribbon")
            self._set_status("✅  Installed! Restart Revit → pyRevit → Reload.", GRN)

        except Exception as ex:
            self._write_log("   ERROR: " + str(ex))
            self._set_status("❌  Failed — see log above.", RED)

    def _uninstall(self):
        dest = os.path.join(self._ext.get().strip(), "ComfyUIRender.extension")
        if os.path.isdir(dest):
            shutil.rmtree(dest)
            self._write_log("Removed: " + dest)
            self._set_status("Uninstalled.", ORG)
        else:
            self._set_status("Nothing found at that location.", DIM)


if __name__ == "__main__":
    Installer().mainloop()
