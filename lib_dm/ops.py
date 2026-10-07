"""The image operations. Pure torch, (B, 3, H, W) float in 0..1, no WebUI imports.

Values may leave 0..1 between steps (clarity headroom, exposure) and are only
clamped where an operation needs it and once at the very end.
"""

from __future__ import annotations

import math

import torch
import torch.nn.functional as F

LUMA = (0.2126, 0.7152, 0.0722)   # Rec.709, which is what sRGB primaries are


def luma(x):
    w = x.new_tensor(LUMA).view(1, 3, 1, 1)
    return (x * w).sum(1, keepdim=True)


def smoothstep(e0, e1, x):
    t = ((x - e0) / (e1 - e0)).clamp(0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def srgb_to_linear(x):
    x = x.clamp_min(0.0)
    return torch.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)


def linear_to_srgb(x):
    x = x.clamp_min(0.0)
    return torch.where(x <= 0.0031308, x * 12.92, 1.055 * x ** (1 / 2.4) - 0.055)


def hue_to_rgb(h: float, device, dtype):
    """Fully saturated colour of hue h (0..1), as a (1, 3, 1, 1) tensor."""
    k = torch.tensor([5.0, 3.0, 1.0], device=device, dtype=dtype)
    k = (k + h * 6.0) % 6.0
    rgb = 1.0 - torch.clamp(torch.minimum(k, 4.0 - k), 0.0, 1.0)
    return rgb.view(1, 3, 1, 1)


# ---------------------------------------------------------------- filters

_kernels = {}


def _gauss1d(sigma, radius, device, dtype):
    key = (round(float(sigma), 4), radius, device, dtype)
    k = _kernels.get(key)
    if k is None:
        t = torch.arange(-radius, radius + 1, device=device, dtype=dtype)
        k = torch.exp(-0.5 * (t / sigma) ** 2)
        k = k / k.sum()
        _kernels[key] = k
    return k


def gaussian_blur(x, sigma, radius=None):
    """Gaussian blur; separable (2(2r+1) taps instead of (2r+1)^2) above r = 3.

    radius defaults to 3 sigma. The detail filters pass a smaller radius (a
    kernel cut off at about 1 sigma), which suits their look and is cheaper.
    """
    if sigma <= 0:
        return x
    c = x.shape[1]
    radius = max(1, int(math.ceil(3.0 * sigma)) if radius is None else int(radius))
    k = _gauss1d(sigma, radius, x.device, x.dtype)
    # Reflect padding needs the pad to be smaller than the side.
    mode = "reflect" if radius < min(x.shape[-2:]) else "replicate"
    if radius <= 3:
        # Small kernels: one 2-D pass beats two 1-D ones (measured: 1-D
        # depthwise convs take a slow path on CPU; 5x5 in one pass is 2x faster).
        k2 = torch.outer(k, k).view(1, 1, 2 * radius + 1, 2 * radius + 1)
        return F.conv2d(F.pad(x, (radius,) * 4, mode=mode), k2.expand(c, 1, -1, -1), groups=c)
    x = F.pad(x, (radius, radius, 0, 0), mode=mode)
    x = F.conv2d(x, k.view(1, 1, 1, -1).expand(c, 1, 1, -1), groups=c)
    x = F.pad(x, (0, 0, radius, radius), mode=mode)
    return F.conv2d(x, k.view(1, 1, -1, 1).expand(c, 1, -1, 1), groups=c)


def sobel_magnitude(y):
    """|gradient| of a single-channel (B, 1, H, W) image."""
    k = y.new_tensor([[-1.0, 0.0, 1.0], [-2.0, 0.0, 2.0], [-1.0, 0.0, 1.0]])
    k = torch.stack([k, k.t()]).unsqueeze(1)            # (2, 1, 3, 3): x and y
    g = F.conv2d(F.pad(y, (1, 1, 1, 1), mode="replicate"), k)
    return torch.sqrt((g * g).sum(1, keepdim=True) + 1e-12)


# ---------------------------------------------------------------- restoration

# ---------------------------------------------------------------- tone & colour

def exposure_white_balance(x, exposure, temperature, tint):
    """In linear light, where a gain is a gain. Brightness-neutral WB gains."""
    gains = torch.tensor([1.0 + 0.4 * temperature, 1.0 - 0.4 * tint,
                          1.0 - 0.4 * temperature], dtype=x.dtype, device=x.device)
    gains = gains / (gains * gains.new_tensor(LUMA)).sum()
    gains = gains * (2.0 ** exposure)
    return linear_to_srgb(srgb_to_linear(x) * gains.view(1, 3, 1, 1))


def cdl(x, slope, offset, power):
    """ASC CDL slope/offset/power. clamp_min(0), not an epsilon: 1e-6 ** 0.1 is
    0.25, which would turn every black milky."""
    return (x * slope + offset).clamp_min(0.0) ** power


def contrast(x, amount):
    """S-curve around mid-grey; negative flattens. Out-of-range values pass."""
    xc = x.clamp(0.0, 1.0)
    return x + amount * (xc * xc * (3.0 - 2.0 * xc) - xc)


def saturation_vibrance(x, saturation, vibrance):
    y = luma(x)
    factor = x.new_full((1, 1, 1, 1), saturation)
    if vibrance:
        chroma = (x.amax(1, keepdim=True) - x.amin(1, keepdim=True)).clamp(0.0, 1.0)
        # Vibrance acts on what is still muted and leaves saturated colour be.
        factor = factor * (1.0 + vibrance * (1.0 - chroma) ** 2)
    return y + (x - y) * factor


def split_tone(x, shadow_hue, shadow_amt, high_hue, high_amt, balance):
    """Push shadows towards one hue and highlights towards another.

    The tint is added with its own luma removed, so it recolours without
    brightening or darkening.
    """
    y = luma(x).clamp(0.0, 1.0)
    pivot = 0.5 - 0.3 * balance
    w_high = torch.sigmoid((y - pivot) * 8.0)
    out = x
    for hue, amt, w in ((shadow_hue, shadow_amt, 1.0 - w_high), (high_hue, high_amt, w_high)):
        if amt <= 0:
            continue
        c = hue_to_rgb(hue, x.device, x.dtype)
        c = c - luma(c)
        out = out + c * (0.40 * amt) * w
    return out


def apply_lut(x, volume, strength):
    """Trilinear 3D LUT through grid_sample. volume: (1, 3, N, N, N), .cube order."""
    b, _, h, w = x.shape
    grid = (x.clamp(0.0, 1.0) * 2.0 - 1.0).permute(0, 2, 3, 1).reshape(b, 1, h, w, 3)
    mapped = F.grid_sample(volume.expand(b, -1, -1, -1, -1), grid, mode="bilinear",
                           padding_mode="border", align_corners=True)
    return torch.lerp(x, mapped[:, :, 0], strength)


def rgb_hue_sat(x):
    """HSV hue in 0..1 and saturation, vectorised."""
    r, g, b = x[:, 0:1], x[:, 1:2], x[:, 2:3]
    cmax, cmin = x.amax(1, keepdim=True), x.amin(1, keepdim=True)
    delta = cmax - cmin
    d = delta + 1e-6
    hue = torch.where(cmax == r, ((g - b) / d) % 6.0,
          torch.where(cmax == g, (b - r) / d + 2.0, (r - g) / d + 4.0)) / 6.0
    hue = torch.where(delta > 0, hue, torch.zeros_like(hue))
    sat = delta / (cmax + 1e-6)
    return hue, sat


def selective_color(x, keep_hue, tolerance, desat, protect_mask=None):
    """Desaturate everything except one hue (and, optionally, people)."""
    xc = x.clamp(0.0, 1.0)
    hue, sat = rgb_hue_sat(xc)
    dist = (hue - keep_hue).abs()
    dist = torch.minimum(dist, 1.0 - dist)
    keep = 1.0 - ((dist - 0.7 * tolerance) / (0.3 * tolerance + 1e-6)).clamp(0.0, 1.0)
    keep = keep * ((sat - 0.1) * 5.0).clamp(0.0, 1.0)
    if protect_mask is not None:
        keep = (keep + protect_mask * 0.6).clamp(0.0, 1.0)
    grey = luma(x).expand_as(x)
    return torch.lerp(torch.lerp(x, grey, desat), x, keep)


# ---------------------------------------------------------------- detail

def clarity(x, amount, radius, protect_mask=None):
    """Local contrast on luma, weighted to the midtones.

    Luma only, so it cannot fringe colour edges; midtone weighting keeps it off
    clipped highlights and crushed shadows, where it only makes halos. Negative
    amounts give the diffusion/glow look and are applied everywhere.
    """
    y = luma(x)
    detail = y - gaussian_blur(y, radius, radius=math.ceil(radius))
    if amount > 0:
        yc = y.clamp(0.0, 1.0)
        detail = detail * (4.0 * yc * (1.0 - yc)).clamp(0.25, 1.0)
    if protect_mask is not None:
        detail = detail * (1.0 - protect_mask)
    return x + detail * amount


def sharpen(x, amount, protect_mask=None):
    """Unsharp mask on luma, only where there are edges (never on flat noise)."""
    y = luma(x)
    detail = y - gaussian_blur(y, 1.0, radius=1)
    mask = (sobel_magnitude(y) * 5.0).clamp(0.0, 1.0)
    if protect_mask is not None:
        mask = mask * (1.0 - protect_mask)
    return x + detail * (2.0 * amount) * mask


# ---------------------------------------------------------------- finishing

# ---------------------------------------------------------------- local

def gradient_mask(h, w, angle, position, softness, device, dtype):
    """(1, 1, H, W) graduated-filter mask: 1 on the filtered side, 0 beyond.

    angle: degrees the filter comes from, 0 = top, 90 = right, 180 = bottom.
    position: where the transition is centred along that direction, 0..1
    from the filtered edge. softness: transition width, as a share of the frame.
    """
    t = math.radians(angle)
    yy = torch.linspace(-0.5, 0.5, h, device=device, dtype=dtype).view(1, 1, h, 1)
    xx = torch.linspace(-0.5, 0.5, w, device=device, dtype=dtype).view(1, 1, 1, w)
    # Distance from the filtered edge along the filter's direction, 0..1.
    d = 0.5 - (xx * math.sin(t) - yy * math.cos(t))
    half = max(float(softness), 0.02) / 2
    return 1.0 - smoothstep(position - half, position + half, d)


def radial_mask(h, w, cx, cy, size, softness, device, dtype):
    """(1, 1, H, W): 1 inside an ellipse centred at (cx, cy) (0..1 of the
    frame), fading to 0 outside. size is the radius as a share of the frame's
    shorter side; the ellipse follows the frame's proportions."""
    yy = torch.linspace(0.0, 1.0, h, device=device, dtype=dtype).view(1, 1, h, 1)
    xx = torch.linspace(0.0, 1.0, w, device=device, dtype=dtype).view(1, 1, 1, w)
    short = min(h, w)
    d = torch.sqrt(((xx - cx) * w / short) ** 2 + ((yy - cy) * h / short) ** 2) / max(size, 1e-3)
    s = max(float(softness), 0.02)
    return 1.0 - smoothstep(1.0 - s, 1.0 + s, d)


def local_light(x, stops, tint_rgb=None, tint_amount=None):
    """Per-pixel exposure (stops map, (1, 1, H, W)) in linear light, with an
    optional colour filter (tint_rgb (1, 3, 1, 1), tint_amount map)."""
    lin = srgb_to_linear(x) * (2.0 ** stops)
    if tint_rgb is not None:
        filt = tint_rgb / (tint_rgb * tint_rgb.new_tensor(LUMA).view(1, 3, 1, 1)).sum(1, keepdim=True)
        lin = lin * torch.lerp(torch.ones_like(filt), filt, tint_amount)
    return linear_to_srgb(lin)


def mask_centre(mask, threshold=0.5):
    """Centre (cx, cy, 0..1) and rough radius of the masked area, or None."""
    m = (mask[0, 0] > threshold).to(mask.dtype)
    total = float(m.sum())
    if total < 0.002 * m.numel():
        return None
    h, w = m.shape
    ys = torch.arange(h, device=m.device, dtype=m.dtype).view(h, 1)
    xs = torch.arange(w, device=m.device, dtype=m.dtype).view(1, w)
    cy = float((m * ys).sum()) / total / max(h - 1, 1)
    cx = float((m * xs).sum()) / total / max(w - 1, 1)
    return cx, cy, math.sqrt(total / m.numel())


def hue_rotate(rgb, turns):
    """Rotate the hue of an RGB tensor by `turns` of the colour wheel (YIQ)."""
    if abs(turns) < 1e-6:
        return rgb
    t = 2.0 * math.pi * turns
    c, s = math.cos(t), math.sin(t)
    to_yiq = rgb.new_tensor([[0.299, 0.587, 0.114], [0.596, -0.274, -0.322], [0.211, -0.523, 0.312]])
    rot = rgb.new_tensor([[1.0, 0.0, 0.0], [0.0, c, -s], [0.0, s, c]])
    m = torch.linalg.inv(to_yiq) @ rot @ to_yiq
    return torch.einsum("ij,bjhw->bihw", m, rgb).clamp(0.0, 1.0)


def blend_overlay(x, layer, mode, opacity, hue=0.0):
    """Lay an RGBA layer (from overlay.prepare) over x with a blend mode."""
    c = hue_rotate(layer[:, :3], hue)
    a = layer[:, 3:4] * opacity
    base = x.clamp(0.0, 1.0)
    if mode == "Screen":
        out = 1.0 - (1.0 - base) * (1.0 - c)
    elif mode == "Add":
        out = base + c
    elif mode == "Multiply":
        out = base * c
    elif mode == "Overlay":
        out = torch.where(base < 0.5, 2.0 * base * c, 1.0 - 2.0 * (1.0 - base) * (1.0 - c))
    elif mode == "Soft light":
        out = (1.0 - 2.0 * c) * base * base + 2.0 * c * base
    else:  # Normal
        out = c
    return torch.lerp(x, out, a)


def dither(x, strength, generator):
    """TPDF dither of about one 8-bit step, to break up banding on export."""
    r = torch.rand((2, *x.shape), generator=generator, device=x.device, dtype=x.dtype)
    return x + (r[0] - r[1]) * (1.5 / 255.0) * strength


# ---------------------------------------------------------------- scopes

def false_color(x):
    y = luma(x.clamp(0.0, 1.0))
    out = y.expand(-1, 3, -1, -1).clone()
    bands = [
        (y < 0.05, (0.5, 0.0, 0.5)),                  # crushed
        ((y >= 0.05) & (y < 0.15), (0.0, 0.5, 0.5)),  # deep shadow
        ((y >= 0.45) & (y <= 0.55), (0.0, 1.0, 0.0)), # mid-grey
        ((y > 0.85) & (y <= 0.95), (1.0, 1.0, 0.0)),  # near clip
        (y > 0.95, (1.0, 0.0, 0.0)),                  # clipped
    ]
    for m, rgb in bands:
        out = torch.where(m, x.new_tensor(rgb).view(1, 3, 1, 1), out)
    return out
