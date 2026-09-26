""".cube LUT discovery and parsing, cached by (path, mtime)."""

from __future__ import annotations

import glob
import os

import numpy as np
import torch

_cache = {}


def find_luts(*folders):
    """{file name: path} for every .cube in the given folders (later wins)."""
    found = {}
    for folder in folders:
        if folder and os.path.isdir(folder):
            for path in sorted(glob.glob(os.path.join(folder, "*.cube"))
                               + glob.glob(os.path.join(folder, "*.CUBE"))):
                found[os.path.basename(path)] = path
    return found


def parse_cube(path):
    """A (N, N, N, 3) array in .cube order (red fastest), or None."""
    size, rows = 0, []
    lo, hi = np.zeros(3, np.float32), np.ones(3, np.float32)
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            head = line.split()[0].upper()
            if head == "LUT_3D_SIZE":
                size = int(line.split()[1])
            elif head == "DOMAIN_MIN":
                lo = np.array(line.split()[1:4], np.float32)
            elif head == "DOMAIN_MAX":
                hi = np.array(line.split()[1:4], np.float32)
            elif head[0].isdigit() or head[0] in "-.":
                try:
                    vals = [float(v) for v in line.split()]
                except ValueError:
                    continue
                if len(vals) == 3:
                    rows.append(vals)
    if size < 2 or len(rows) != size ** 3:
        return None
    # Only the standard 0..1 input domain is supported; a LUT built for another
    # domain (log footage, HDR) is refused rather than silently mis-applied.
    if not (np.allclose(lo, 0.0) and np.allclose(hi, 1.0)):
        return None
    return np.asarray(rows, np.float32).reshape(size, size, size, 3)


def load_lut(path, device, dtype=torch.float32):
    """(1, 3, N, N, N) tensor for grid_sample, or None if the file is unusable."""
    try:
        key = (path, os.path.getmtime(path), str(device), dtype)
    except OSError:
        return None
    vol = _cache.get(key)
    if vol is None:
        arr = parse_cube(path)
        if arr is None:
            print(f"[Digital Mastering] Could not use LUT (bad size or non-0..1 domain): {path}")
            return None
        # arr is [blue][green][red][rgb]; grid_sample's (x, y, z) indexes
        # (W, H, D), so x = red, y = green, z = blue lines up with it.
        vol = torch.from_numpy(arr).permute(3, 0, 1, 2).unsqueeze(0).to(device, dtype)
        _cache[key] = vol
    return vol


def clear_cache():
    _cache.clear()
