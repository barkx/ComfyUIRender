# -*- coding: utf-8 -*-
"""
comfy_http.py
HTTP calls to ComfyUI API.
IronPython 2.7 compatible.
"""

import os
import json
import base64

# ── urllib fallback (always works in IronPython) ──────────────────────────────
def _get_urlopen():
    try:
        from urllib.request import urlopen, Request
        return urlopen, Request
    except ImportError:
        from urllib2 import urlopen, Request
        return urlopen, Request

def _url_quote(s):
    try:
        from urllib.parse import quote
        return quote(str(s))
    except ImportError:
        from urllib import quote
        return quote(str(s))


# ── POST JSON ─────────────────────────────────────────────────────────────────
def post_json(base_url, endpoint, payload):
    """POST dict as JSON. Returns parsed response dict. Raises on error."""
    url  = base_url.rstrip("/") + endpoint
    body = json.dumps(payload).encode("utf-8")

    urlopen, Request = _get_urlopen()
    req = Request(url, body)
    req.add_header("Content-Type", "application/json")

    try:
        resp = urlopen(req, timeout=60)
        raw  = resp.read().decode("utf-8")
        return json.loads(raw)
    except Exception as ex:
        # Attach useful context to the exception
        msg = str(ex)
        # For urllib HTTPError, read the body for more detail
        try:
            body_text = ex.read().decode("utf-8")
            msg = "HTTP {0} from {1}\nResponse: {2}".format(
                ex.code, url, body_text[:500])
        except Exception:
            msg = "Request failed: {0}\nURL was: {1}".format(str(ex), url)
        raise Exception(msg)


# ── GET JSON ──────────────────────────────────────────────────────────────────
def get_json(url):
    """GET URL, return parsed JSON. Returns {} on any error."""
    try:
        urlopen, Request = _get_urlopen()
        resp = urlopen(url, timeout=30)
        return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return {}


# ── GET bytes ─────────────────────────────────────────────────────────────────
def get_bytes(url):
    """GET URL, return raw bytes. Raises on error."""
    urlopen, Request = _get_urlopen()
    try:
        resp = urlopen(url, timeout=120)
        return resp.read()
    except Exception as ex:
        try:
            msg = "HTTP {0} downloading {1}".format(ex.code, url)
        except Exception:
            msg = "Download failed: {0}\nURL: {1}".format(str(ex), url)
        raise Exception(msg)


# ── Image to base64 ───────────────────────────────────────────────────────────
def image_to_base64(image_path):
    """Read PNG file, return base64 string (no header prefix)."""
    with open(image_path, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data)
    if isinstance(encoded, bytes):
        return encoded.decode("utf-8")
    return str(encoded)


# ── Download result ───────────────────────────────────────────────────────────
def download_image(base_url, filename):
    """
    Download output image from /view endpoint.
    Tries type=output first, then type=temp, then type=input.
    ComfyUI nodes like easyPreview save to temp, not output.
    """
    enc      = _url_quote(filename)
    base     = base_url.rstrip("/")
    urlopen, Request = _get_urlopen()

    for ftype in ("output", "temp", "input"):
        url = "{0}/view?filename={1}&type={2}".format(base, enc, ftype)
        try:
            resp = urlopen(url, timeout=120)
            data = resp.read()
            if len(data) > 1000:   # real image, not an error page
                return data
        except Exception:
            pass   # try next type

    raise Exception(
        "Could not download image \'\'{0}\'\' from ComfyUI.\n"
        "Tried types: output, temp, input.\n"
        "URL base: {1}".format(filename, base)
    )


# ── Connection test ───────────────────────────────────────────────────────────
def test_connection(base_url):
    """
    Quick check that ComfyUI is reachable.
    Returns (True, "OK") or (False, error_message).
    """
    try:
        urlopen, Request = _get_urlopen()
        url  = base_url.rstrip("/") + "/system_stats"
        resp = urlopen(url, timeout=5)
        resp.read()
        return True, "Connected"
    except Exception as ex:
        return False, "Cannot reach {0}\n{1}".format(base_url, str(ex))
