"""Secondary grading tools: HSL by colour, lift / gamma / gain wheels, black &
white with colour filters, dehaze, tone curves, skin smoothing.

Pure torch, (B, 3, H, W) float sRGB in 0..1, like ops.py.
"""

from __future__ import annotations

import numpy as np
import torch
import torch.nn.functional as F

from .ops import gaussian_blur, hue_to_rgb, luma, rgb_hue_sat, sobel_magnitude

# ------------------------------------------------------------------ HSL

HSL_BANDS = ["red", "orange", "yellow", "green", "aqua", "blue", "purple", "magenta"]
_CENTRES = [0.0, 30.0, 60.0, 120.0, 180.0, 240.0, 270.0, 300.0]


def _band_weights(hue):
    """(B, 8, H, W) weights per band, summing to 1: each hue is split between
    the two band centres around it, like Lightroom's HSL panel."""
    deg = hue * 360.0
    cs = _CENTRES + [360.0]
    ws = []
    for i in range(8):
        c, next_c = cs[i], cs[i + 1]
        prev_c = _CENTRES[-1] - 360.0 if i == 0 else cs[i - 1]
        d = deg if i else torch.where(deg > 180.0, deg - 360.0, deg)
        up = ((d - prev_c) / (c - prev_c)).clamp(0.0, 1.0)
        down = ((next_c - d) / (next_c - c)).clamp(0.0, 1.0)
        ws.append(torch.where(d <= c, up, down))
    return torch.cat(ws, 1)


def _hsv_to_rgb(h, s, v):
    k = torch.cat([(n + h * 6.0) % 6.0 for n in (5.0, 3.0, 1.0)], 1)
    return v - v * s * torch.clamp(torch.minimum(k, 4.0 - k), 0.0, 1.0)


def hsl(x, hue_shift, sat_shift, lum_shift):
    """hue/sat/lum_shift: 8 values each in -1..1, one per band.
    Hue moves up to 30 degrees, saturation scales 0..2x, lightness +-1 stop.
    Greys are left alone: the change fades with the pixel's own saturation."""
    xc = x.clamp(0.0, 1.0)
    hue, sat = rgb_hue_sat(xc)
    val = xc.amax(1, keepdim=True)
    w = _band_weights(hue)
    t = lambda vals: (w * x.new_tensor(vals).view(1, 8, 1, 1)).sum(1, keepdim=True)  # noqa: E731
    colourful = (sat * 2.0).clamp(0.0, 1.0)
    hue = (hue + t(hue_shift) * (30.0 / 360.0) * colourful) % 1.0
    sat = (sat * (1.0 + t(sat_shift))).clamp(0.0, 1.0)
    out = _hsv_to_rgb(hue, sat, val)
    lum = t(lum_shift) * colourful
    return (out * (2.0 ** lum)).clamp(0.0, 1.0)


# ------------------------------------------------------------------ wheels

def _push(hue, amount, x):
    """A zero-mean colour vector: hue's colour minus grey."""
    c = hue_to_rgb(hue, x.device, x.dtype)
    return (c - c.mean(1, keepdim=True)) * amount


def wheels(x, lift, gamma, gain):
    """Lift / gamma / gain, as on a grading panel. Each is (hue, amount, lum):
    amount pushes that colour into the shadows / midtones / highlights, lum
    makes them darker or brighter (-1..1)."""
    (lh, la, ll), (mh, ma, ml), (gh, ga, gl) = lift, gamma, gain
    x = x + (_push(lh, la, x) * 0.20 + ll * 0.10) * (1.0 - x).clamp(0.0, 1.0)
    x = x * (1.0 + _push(gh, ga, x) * 0.40 + gl * 0.30)
    g = (1.0 + _push(mh, ma, x) * 0.60 + ml * 0.40).clamp_min(0.2)
    return x.clamp(0.0, 1.0) ** (1.0 / g)


# ------------------------------------------------------------------ black & white

BW_FILTERS = {
    "Neutral": (0.2126, 0.7152, 0.0722),
    "Red filter": (0.80, 0.30, -0.10),
    "Orange filter": (0.60, 0.45, -0.05),
    "Yellow filter": (0.45, 0.55, 0.00),
    "Green filter": (0.10, 0.80, 0.10),
    "Blue filter": (0.05, 0.25, 0.70),
    "Infrared": (0.45, 1.00, -0.45),
}


def black_and_white(x, amount, filt="Neutral"):
    """Monochrome through a coloured filter, as on black & white film: red
    darkens blue skies, green lightens foliage and smooths skin, infrared
    turns leaves white."""
    w = x.new_tensor(BW_FILTERS.get(filt, BW_FILTERS["Neutral"])).view(1, 3, 1, 1)
    y = (x * w).sum(1, keepdim=True).clamp(0.0, 1.0).expand_as(x)
    return torch.lerp(x, y, amount)


# ------------------------------------------------------------------ dehaze

def dehaze(x, amount):
    """Dark-channel-prior dehaze: estimate the haze's colour and how much of
    it lies over each pixel, then take it back out. Worked out at <= 256 px,
    the transmission map is smooth anyway."""
    if amount <= 0:
        return x
    _, _, h, w = x.shape
    s = min(1.0, 256.0 / max(h, w))
    small = F.interpolate(x, scale_factor=s, mode="area") if s < 1.0 else x
    dark = small.amin(1, keepdim=True)
    dark = -F.max_pool2d(-dark, 15, stride=1, padding=7)
    flat = dark.flatten()
    k = max(1, int(flat.numel() * 0.001))
    idx = flat.topk(k).indices
    air = small.flatten(2)[:, :, idx].mean(2).view(1, 3, 1, 1).clamp(0.3, 1.0)
    t = 1.0 - 0.95 * (-F.max_pool2d(-(small / air).amin(1, keepdim=True), 15, stride=1, padding=7))
    t = gaussian_blur(t, 4.0)
    t = F.interpolate(t, size=(h, w), mode="bilinear", align_corners=False).clamp(0.15, 1.0)
    clear = ((x - air) / t + air).clamp(0.0, 1.0)
    return torch.lerp(x, clear, amount)


# ------------------------------------------------------------------ tone curves

# Points (in, out) per curve; "rgb" for all channels, or per channel r / g / b.
CURVES = {
    "Linear": None,
    "Film S": {"rgb": [(0, 0.02), (0.25, 0.20), (0.5, 0.5), (0.75, 0.80), (1, 0.97)]},
    "Soft S": {"rgb": [(0, 0), (0.25, 0.23), (0.5, 0.5), (0.75, 0.77), (1, 1)]},
    "Strong S": {"rgb": [(0, 0), (0.25, 0.16), (0.5, 0.5), (0.75, 0.86), (1, 1)]},
    "Matte fade": {"rgb": [(0, 0.08), (0.25, 0.27), (0.5, 0.52), (0.75, 0.76), (1, 0.95)]},
    "Crushed blacks": {"rgb": [(0, 0), (0.12, 0.0), (0.5, 0.48), (1, 1)]},
    "Bright mids": {"rgb": [(0, 0), (0.5, 0.60), (1, 1)]},
    "Low contrast": {"rgb": [(0, 0.06), (0.5, 0.5), (1, 0.94)]},
    "Cross process": {"r": [(0, 0), (0.25, 0.18), (0.75, 0.85), (1, 1)],
                      "g": [(0, 0), (0.25, 0.20), (0.75, 0.80), (1, 1)],
                      "b": [(0, 0.12), (0.5, 0.45), (1, 0.85)]},
}


def _monotone_lut(points, n=1024):
    """Fritsch-Carlson monotone cubic through the points, sampled n times."""
    xs, ys = (np.array(v, dtype=np.float64) for v in zip(*points))
    d = np.diff(ys) / np.diff(xs)
    m = np.concatenate([[d[0]], (d[:-1] + d[1:]) / 2, [d[-1]]])
    for i, dk in enumerate(d):
        if dk == 0:
            m[i] = m[i + 1] = 0
        else:
            a, b = m[i] / dk, m[i + 1] / dk
            r = a * a + b * b
            if r > 9:
                t = 3 / np.sqrt(r)
                m[i], m[i + 1] = t * a * dk, t * b * dk
    u = np.linspace(0, 1, n)
    k = np.clip(np.searchsorted(xs, u, side="right") - 1, 0, len(xs) - 2)
    hseg = xs[k + 1] - xs[k]
    t = (u - xs[k]) / hseg
    h00, h10 = 2 * t**3 - 3 * t**2 + 1, t**3 - 2 * t**2 + t
    h01, h11 = -2 * t**3 + 3 * t**2, t**3 - t**2
    y = h00 * ys[k] + h10 * hseg * m[k] + h01 * ys[k + 1] + h11 * hseg * m[k + 1]
    return np.clip(y, 0, 1).astype(np.float32)


def _apply_lut(c, lut):
    n = lut.numel()
    pos = c.clamp(0.0, 1.0) * (n - 1)
    i0 = pos.floor().long().clamp(0, n - 2)
    f = pos - i0
    return lut[i0] * (1 - f) + lut[i0 + 1] * f


def tone_curve(x, name, amount):
    spec = CURVES.get(name)
    if not spec or amount <= 0:
        return x
    chans = []
    for ci, key in enumerate("rgb"):
        pts = spec.get(key, spec.get("rgb"))
        if pts is None:
            chans.append(x[:, ci:ci + 1])
            continue
        lut = torch.from_numpy(_monotone_lut(pts)).to(x.device, x.dtype)
        chans.append(_apply_lut(x[:, ci:ci + 1], lut))
    return torch.lerp(x, torch.cat(chans, 1), amount)


# ------------------------------------------------------------------ skin

def skin_smooth(x, person, amount):
    """Frequency-separation smoothing on skin: the fine texture is softened,
    the tones underneath are kept, and edges (eyes, lips, hair) stay sharp.
    Skin = detected people, within skin-coloured pixels."""
    if amount <= 0 or person is None:
        return x
    _, _, h, w = x.shape
    hue, sat = rgb_hue_sat(x.clamp(0.0, 1.0))
    y = luma(x)
    skin = (((hue < 0.13) | (hue > 0.95)) & (sat > 0.10) & (sat < 0.70) & (y > 0.15) & (y < 0.95)).to(x.dtype)
    mask = gaussian_blur(skin * person, 2.0).clamp(0.0, 1.0)
    edges = (sobel_magnitude(y) * 6.0).clamp(0.0, 1.0)
    low = gaussian_blur(x, max(1.5, 0.004 * min(h, w)))
    keep = 1.0 - 0.85 * amount * mask * (1.0 - edges)
    return low + (x - low) * keep
