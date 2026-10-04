"""The mastering chain: settings in, graded image (and optional scope) out.

Order, and why:

    restoration          repair the signal before anything amplifies its flaws
    exposure / WB        in linear light, on the cleanest data
    CDL, contrast        the primary grade
    saturation, split    secondary colour
    LUT                  a look on top of the grade, as colourists stack it
    selective colour     after the look, so the kept hue is the final hue
    clarity, sharpen     detail last among the edits, on the final tones
    intensity            blend the whole grade back towards the original
    dither               very last: anything after it would amplify it

A stage whose controls are at their defaults is skipped entirely.
"""

from __future__ import annotations

import numpy as np
import torch
from PIL import Image

from . import ops
from .controls import GROUPS, NEUTRAL, effective, is_neutral


def _active(s, *names):
    return any(not is_neutral(n, s[n]) for n in names)


def to_tensor(image, device):
    arr = np.asarray(image.convert("RGB"), dtype=np.float32) / 255.0
    return torch.from_numpy(arr).permute(2, 0, 1).unsqueeze(0).to(device)


def to_image(x):
    # np.rint, not a truncating cast: truncation is half a level dark on average.
    arr = x[0].clamp(0.0, 1.0).permute(1, 2, 0).cpu().numpy()
    return Image.fromarray(np.rint(arr * 255.0).astype(np.uint8), "RGB")


@torch.no_grad()
def master(image: Image.Image, s: dict, device="cpu", seed=0, lut_volume=None, mask_fn=None):
    """Return (graded PIL image, false-colour PIL image or None).

    lut_volume: a loaded (1, 3, N, N, N) LUT or None.
    mask_fn:    callable(image) -> (1, 1, H, W) person mask; only called when a
                stage that uses it is active and s["semantic"] is on.
    """
    s = effective(s)
    alpha = image.getchannel("A") if image.mode == "RGBA" else None
    x = torch.nan_to_num(to_tensor(image, device), nan=0.0, posinf=1.0, neginf=0.0)
    original = x

    protect = None
    wants_mask = s["semantic"] and mask_fn is not None and (
        s["clarity"] != 0 or s["sharpen"] > 0 or s["splash_desat"] > 0)
    if wants_mask:
        try:
            protect = mask_fn(image).to(x.device, x.dtype) * s["protect"]
        except Exception as exc:
            print(f"[Digital Mastering] Subject mask failed, continuing without it: {exc}")

    gen = torch.Generator(device=x.device)
    gen.manual_seed(int(seed) & 0x7FFFFFFFFFFFFFFF)

    if s["deblock"] > 0:
        x = ops.deblock(x, s["deblock"])
    if s["dering"] > 0:
        x = ops.dering(x, s["dering"])

    if _active(s, "exposure", "temperature", "tint"):
        x = ops.exposure_white_balance(x, s["exposure"], s["temperature"], s["tint"])
    if _active(s, "slope", "offset", "power"):
        x = ops.cdl(x, s["slope"], s["offset"], s["power"])
    if s["contrast"] != 0:
        x = ops.contrast(x, s["contrast"])
    if _active(s, "saturation", "vibrance"):
        x = ops.saturation_vibrance(x, s["saturation"], s["vibrance"])
    if s["shadow_tint"] > 0 or s["highlight_tint"] > 0:
        x = ops.split_tone(x, s["shadow_hue"], s["shadow_tint"],
                           s["highlight_hue"], s["highlight_tint"], s["tone_balance"])

    if lut_volume is not None and s["lut_strength"] > 0:
        x = ops.apply_lut(x, lut_volume.to(x.device, x.dtype), s["lut_strength"])

    if s["splash_desat"] > 0:
        x = ops.selective_color(x, s["splash_hue"], s["splash_tolerance"],
                                s["splash_desat"], protect)

    if s["clarity"] != 0:
        x = ops.clarity(x, s["clarity"], s["clarity_radius"], protect)
    if s["sharpen"] > 0:
        x = ops.sharpen(x, s["sharpen"], protect)

    x = x.clamp(0.0, 1.0)
    if s["strength"] < 1.0:
        x = torch.lerp(original, x, s["strength"])
    if s["dither"] > 0:
        x = ops.dither(x, s["dither"], gen)

    result = to_image(x)
    if alpha is not None:
        result.putalpha(alpha)
    scope = to_image(ops.false_color(x)) if s["false_color"] else None
    return result, scope


def is_noop(s) -> bool:
    """True if these settings would not change the image at all."""
    s = effective(s)
    if s["strength"] <= 0 and s["dither"] <= 0:
        return True
    ignore = ("strength", "lut", "lut_dir", "lut_strength", "false_color", "semantic", "protect",
              *GROUPS)
    if s["lut"] not in ("", "None") and s["lut_strength"] > 0:
        return False
    return all(is_neutral(k, v) for k, v in s.items() if k in NEUTRAL and k not in ignore)
