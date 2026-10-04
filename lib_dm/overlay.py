"""Overlay layers: image textures (light leaks, dust, bokeh...) laid over the
grade. Discovery and loading here; the blending is in ops.blend_overlay.

An overlay is any PNG / WebP / JPEG. Transparent PNGs carry their own alpha
and suit Normal; an opaque texture on black is meant for Screen or Add, and
one on white for Multiply. "Auto" picks Normal or Screen from the file.
"""

from __future__ import annotations

import glob
import os

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image

EXTENSIONS = ("*.png", "*.webp", "*.jpg", "*.jpeg", "*.PNG", "*.WEBP", "*.JPG", "*.JPEG")
BLENDS = ["Auto", "Normal", "Screen", "Add", "Multiply", "Overlay", "Soft light"]
FITS = ["Cover", "Stretch"]

_cache = {}


def find_overlays(*folders):
    """{name without extension: path} for every image in the folders (later wins)."""
    found = {}
    for folder in folders:
        if folder and os.path.isdir(folder):
            paths = sorted({p for pat in EXTENSIONS for p in glob.glob(os.path.join(folder, pat))})
            for path in paths:
                found[os.path.splitext(os.path.basename(path))[0]] = path
    return dict(sorted(found.items(), key=lambda kv: kv[0].lower()))


def load(path):
    """The file as RGBA, plus whether it had real transparency. Cached."""
    try:
        key = (path, os.path.getmtime(path))
    except OSError:
        return None
    hit = _cache.get(key)
    if hit is None:
        try:
            with Image.open(path) as im:
                has_alpha = im.mode in ("RGBA", "LA", "PA") or "transparency" in im.info
                rgba = im.convert("RGBA")
        except Exception as exc:
            print(f"[Digital Mastering] Could not read overlay {path}: {exc}")
            return None
        if has_alpha:
            has_alpha = np.asarray(rgba.getchannel("A")).min() < 255
        hit = (rgba, has_alpha)
        _cache[key] = hit
    return hit


def clear_cache():
    _cache.clear()


def prepare(rgba: Image.Image, size, fit="Cover", zoom=1.0, match_orientation=True,
            generator=None, device="cpu", dtype=torch.float32):
    """(1, 4, H, W) straight (not premultiplied) RGBA in 0..1, fitted to `size` (W, H).

    generator: when given, the layer is flipped and its crop window moved at
    random, reproducibly from the seed, so a batch does not repeat one texture.
    """
    w, h = size
    ow, oh = rgba.size
    arr = torch.from_numpy(np.asarray(rgba, dtype=np.float32) / 255.0).permute(2, 0, 1).unsqueeze(0)
    arr = arr.to(device, dtype)
    if match_orientation and (ow > oh) != (w > h) and ow != oh and w != h:
        arr = torch.rot90(arr, 1, dims=(2, 3))
        ow, oh = oh, ow

    def rand():
        return float(torch.rand(1, generator=generator, device=generator.device)) if generator else 0.5

    if generator is not None:
        if rand() < 0.5:
            arr = torch.flip(arr, dims=(3,))
        if rand() < 0.5:
            arr = torch.flip(arr, dims=(2,))

    # Resample premultiplied, so transparent pixels do not bleed dark fringes.
    a = arr[:, 3:4]
    pre = torch.cat((arr[:, :3] * a, a), 1)
    if fit == "Stretch":
        tw, th = w, h
    else:
        scale = max(w / ow, h / oh) * max(1.0, float(zoom))
        tw, th = max(w, int(round(ow * scale))), max(h, int(round(oh * scale)))
    pre = F.interpolate(pre, size=(th, tw), mode="bilinear", align_corners=False,
                        antialias=(tw < ow or th < oh))
    if (tw, th) != (w, h):
        x0 = int(round((tw - w) * rand()))
        y0 = int(round((th - h) * rand()))
        pre = pre[:, :, y0:y0 + h, x0:x0 + w]
    a = pre[:, 3:4].clamp(0.0, 1.0)
    rgb = (pre[:, :3] / a.clamp_min(1e-6)).clamp(0.0, 1.0)
    return torch.cat((rgb, a), 1)
