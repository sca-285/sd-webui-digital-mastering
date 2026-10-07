"""The mastering chain: settings in, graded image (and optional scope) out.

Order, and why:

    dehaze               take the haze out first, before anything grades it
    exposure / WB        in linear light, on the cleanest data
    CDL, wheels,         the primary grade
    contrast, curve
    saturation, HSL,     secondary colour
    B&W, split
    local                graduated / radial filters, people and background light
    LUT                  a look on top of the grade, as colourists stack it
    selective colour     after the look, so the kept hue is the final hue
    clarity, sharpen     detail last among the edits, on the final tones
    overlay layers       textures on top of the finished grade, never sharpened
    intensity            blend the whole grade back towards the original
    crop, resize,        output framing; after the blend, which needs the
    output sharpen       original's size
    dither               last of the pixel work: anything after it would amplify it
    letterbox, watermark, drawn on top, untouched by the grade
    border

A stage whose controls are at their defaults is skipped entirely.
"""

from __future__ import annotations

import numpy as np
import torch
from PIL import Image

from . import grade, ops
from . import output as out
from . import overlay as ov
from .controls import GROUPS, NEUTRAL, OVERLAY_CONTROLS, effective, is_neutral


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
def master(image: Image.Image, s: dict, device="cpu", seed=0, lut_volume=None, mask_fn=None,
           overlays=None):
    """Return (graded PIL image, false-colour PIL image or None).

    lut_volume: a loaded (1, 3, N, N, N) LUT or None.
    mask_fn:    callable(image) -> (1, 1, H, W) person mask; only called when a
                stage that uses it is active and s["semantic"] is on.
    overlays:   {layer number: (RGBA PIL image, has_alpha)} for the overlay
                layers that are picked and could be loaded.
    """
    s = effective(s)
    alpha = image.getchannel("A") if image.mode == "RGBA" else None
    x = torch.nan_to_num(to_tensor(image, device), nan=0.0, posinf=1.0, neginf=0.0)
    original = x

    protect = person = None
    wants_protect = s["semantic"] and (s["clarity"] != 0 or s["sharpen"] > 0 or s["splash_desat"] > 0)
    wants_people = s["skin_smooth"] > 0
    wants_people = wants_people or (s["en_local"] and (s["subject_light"] != 0 or s["background_light"] != 0
                                       or (s["rad_on_people"] and _active(s, "rad_inside", "rad_outside"))))
    wants_people = wants_people or (s["en_export"] and s["out_crop_people"] and s["out_aspect"] != "Original")
    if mask_fn is not None and (wants_protect or wants_people):
        try:
            person = mask_fn(image).to(x.device, x.dtype)
        except Exception as exc:
            print(f"[Digital Mastering] Subject mask failed, continuing without it: {exc}")
    if person is not None and wants_protect:
        protect = person * s["protect"]

    gen = torch.Generator(device=x.device)
    gen.manual_seed(int(seed) & 0x7FFFFFFFFFFFFFFF)

    if s["dehaze"] > 0:
        x = grade.dehaze(x, s["dehaze"])
    if _active(s, "exposure", "temperature", "tint"):
        x = ops.exposure_white_balance(x, s["exposure"], s["temperature"], s["tint"])
    if _active(s, "slope", "offset", "power"):
        x = ops.cdl(x, s["slope"], s["offset"], s["power"])
    if s["en_wheels"] and _active(s, *GROUPS["en_wheels"]):
        x = grade.wheels(x, *[(s[f"{w}_hue"], s[f"{w}_amt"], s[f"{w}_lum"]) for w in ("lift", "gamma", "gain")])
    if s["contrast"] != 0:
        x = ops.contrast(x, s["contrast"])
    if s["curve"] != "Linear" and s["curve_amount"] > 0:
        x = grade.tone_curve(x, s["curve"], s["curve_amount"])
    if _active(s, "saturation", "vibrance"):
        x = ops.saturation_vibrance(x, s["saturation"], s["vibrance"])
    if s["en_hsl"] and _active(s, *GROUPS["en_hsl"]):
        x = grade.hsl(x, *[[s[f"hsl_{k}_{b}"] for b in grade.HSL_BANDS] for k in "hsl"])
    if s["bw"] > 0:
        x = grade.black_and_white(x, s["bw"], s["bw_filter"])
    if s["shadow_tint"] > 0 or s["highlight_tint"] > 0:
        x = ops.split_tone(x, s["shadow_hue"], s["shadow_tint"],
                           s["highlight_hue"], s["highlight_tint"], s["tone_balance"])

    if s["en_local"]:
        x = _local(x, s, person)

    if lut_volume is not None and s["lut_strength"] > 0:
        x = ops.apply_lut(x, lut_volume.to(x.device, x.dtype), s["lut_strength"])

    if s["splash_desat"] > 0:
        x = ops.selective_color(x, s["splash_hue"], s["splash_tolerance"],
                                s["splash_desat"], protect)

    if s["skin_smooth"] > 0:
        x = grade.skin_smooth(x, person, s["skin_smooth"])
    if s["clarity"] != 0:
        x = ops.clarity(x, s["clarity"], s["clarity_radius"], protect)
    if s["sharpen"] > 0:
        x = ops.sharpen(x, s["sharpen"], protect)

    if s["en_overlay"] and overlays:
        # Its own random stream: picking a layer must not change the dither.
        ov_gen = torch.Generator(device=x.device)
        ov_gen.manual_seed((int(seed) * 1000003 + 11) & 0x7FFFFFFFFFFFFFFF)
        for i in (1, 2):
            if i not in overlays or s[f"ov{i}_opacity"] <= 0:
                continue
            rgba, has_alpha = overlays[i]
            layer = ov.prepare(rgba, image.size, fit=s[f"ov{i}_fit"], zoom=s[f"ov{i}_zoom"],
                               match_orientation=s["ov_rotate"],
                               generator=ov_gen if s["ov_vary"] else None,
                               device=x.device, dtype=x.dtype)
            mode = s[f"ov{i}_blend"]
            if mode == "Auto":
                mode = "Normal" if has_alpha else "Screen"
            x = ops.blend_overlay(x, layer, mode, s[f"ov{i}_opacity"], s[f"ov{i}_hue"])

    x = x.clamp(0.0, 1.0)
    if s["strength"] < 1.0:
        x = torch.lerp(original, x, s["strength"])
    box = None
    if s["en_export"]:
        x, box = _output_pixels(x, s, person)
    if s["dither"] > 0:
        x = ops.dither(x, s["dither"], gen)

    result = to_image(x)
    if alpha is not None:
        if box is not None:
            alpha = alpha.crop(box)
        if alpha.size != result.size:
            alpha = alpha.resize(result.size, Image.LANCZOS)
        result.putalpha(alpha)
    # Letterbox bars first, subtitle and watermark over the picture, the border round all.
    if s["en_frame"]:
        result = out.letterbox(result, s["out_letterbox"])
    if s["en_export"]:
        bar = out.letterbox_bar(result.size, s["out_letterbox"]) if s["en_frame"] else 0
        result = out.subtitle(result, s["sub_text"], s["sub_colour"], s["sub_size"], s.get("wm_font", ""), bar)
        result = out.watermark(result, s["wm_text"], s["wm_position"], s["wm_opacity"], s["wm_size"],
                               s.get("wm_font", ""))
    if s["en_frame"]:
        result = out.border(result, s["out_border"], s["out_border_size"])
    scope = to_image(ops.false_color(x)) if s["false_color"] else None
    return result, scope


def _local(x, s, person):
    """Graduated and radial filters and people / background light, as one
    exposure map (stops per pixel) applied once in linear light."""
    _, _, h, w = x.shape
    stops = torch.zeros((1, 1, h, w), device=x.device, dtype=x.dtype)
    tint_rgb = tint_amount = None
    if s["grad_stops"] != 0 or s["grad_tint"] > 0:
        g = ops.gradient_mask(h, w, s["grad_angle"], s["grad_position"], s["grad_softness"], x.device, x.dtype)
        stops = stops + s["grad_stops"] * g
        if s["grad_tint"] > 0:
            # Half-strength colour: a real coloured grad is a tint, not a gel.
            tint_rgb = 0.5 + 0.5 * ops.hue_to_rgb(s["grad_hue"], x.device, x.dtype)
            tint_amount = g * s["grad_tint"]
    if s["rad_inside"] != 0 or s["rad_outside"] != 0:
        cx, cy = s["rad_x"], s["rad_y"]
        if s["rad_on_people"] and person is not None:
            found = ops.mask_centre(person)
            if found is not None:
                cx, cy = found[0], found[1]
        m = ops.radial_mask(h, w, cx, cy, s["rad_size"], s["rad_softness"], x.device, x.dtype)
        stops = stops + s["rad_inside"] * m + s["rad_outside"] * (1.0 - m)
    if person is not None and (s["subject_light"] != 0 or s["background_light"] != 0):
        # Feathered, so the change of light has no visible edge round the subject.
        soft = ops.gaussian_blur(person, max(1.0, 0.012 * min(h, w))).clamp(0.0, 1.0)
        stops = stops + s["subject_light"] * soft + s["background_light"] * (1.0 - soft)
    if tint_rgb is None and not bool((stops != 0).any()):
        return x
    return ops.local_light(x, stops, tint_rgb, tint_amount)


def _output_pixels(x, s, person):
    """Crop, resize and output sharpening. Returns the image and the crop
    box used (None if not cropped), so the alpha channel can follow."""
    _, _, h, w = x.shape
    cx, cy = s["out_crop_x"], s["out_crop_y"]
    if s["out_crop_people"] and person is not None:
        found = ops.mask_centre(person)
        if found is not None:
            cx, cy = found[0], found[1]
    box = out.crop_box(w, h, s["out_aspect"], cx, cy)
    if box is not None:
        x = out.crop(x, box)
    if s["out_long_edge"] > 0:
        x = out.resize_long_edge(x, int(s["out_long_edge"]))
    if s["out_sharpen"] > 0:
        x = out.unsharp(x, s["out_sharpen"], 0.8)
    return x, box


def is_noop(s) -> bool:
    """True if these settings would not change the image at all."""
    s = effective(s)
    if out.frame_active(s) or out.export_active(s):
        return False
    if s["strength"] <= 0 and s["dither"] <= 0:
        return True
    ignore = ("strength", "lut", "lut_dir", "lut_strength", "false_color", "semantic", "protect",
              *GROUPS, *OVERLAY_CONTROLS)
    if any(s[f"overlay_{i}"] not in ("", "None") and s[f"ov{i}_opacity"] > 0 for i in (1, 2)):
        return False
    if s["lut"] not in ("", "None") and s["lut_strength"] > 0:
        return False
    return all(is_neutral(k, v) for k, v in s.items() if k in NEUTRAL and k not in ignore)
