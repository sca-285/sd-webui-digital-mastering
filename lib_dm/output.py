"""Output: the last steps before the picture leaves. Frame (letterbox,
border) can be part of a look; export (crop, resize, sharpening, watermark)
belongs to one picture."""

from __future__ import annotations

import torch.nn.functional as F
from PIL import Image, ImageDraw, ImageFont

ASPECTS = ["Original", "1:1", "4:5", "3:4", "2:3", "9:16", "5:4", "4:3", "3:2", "16:9", "21:9"]
BORDERS = ["None", "White", "Black", "Cream", "Polaroid"]
LETTERBOXES = ["None", "1.85:1", "2:1", "2.39:1", "2.76:1"]
SUB_COLOURS = {"White": (245, 245, 240), "Yellow": (250, 222, 80)}
POSITIONS = ["Bottom right", "Bottom left", "Bottom centre", "Top right", "Top left", "Centre"]

_BORDER_RGB = {"White": (255, 255, 255), "Black": (0, 0, 0), "Cream": (243, 236, 222),
               "Polaroid": (246, 244, 238)}


def crop_box(w, h, aspect, cx=0.5, cy=0.5):
    """(left, top, right, bottom) of the largest `aspect` window in w x h,
    centred as near (cx, cy) as the frame allows; None for 'Original'."""
    if aspect not in ASPECTS or aspect == "Original":
        return None
    a, b = (float(v) for v in aspect.split(":"))
    target = a / b
    if w / h > target:
        cw, ch = int(round(h * target)), h
    else:
        cw, ch = w, int(round(w / target))
    if (cw, ch) == (w, h):
        return None
    left = min(max(int(round(cx * w - cw / 2)), 0), w - cw)
    top = min(max(int(round(cy * h - ch / 2)), 0), h - ch)
    return left, top, left + cw, top + ch


def crop(x, box):
    left, top, right, bottom = box
    return x[:, :, top:bottom, left:right]


def resize_long_edge(x, long_edge):
    """Resize so the longer side is long_edge px (0 = keep)."""
    h, w = x.shape[-2:]
    if long_edge <= 0 or max(h, w) == long_edge:
        return x
    s = long_edge / max(h, w)
    size = (max(1, int(round(h * s))), max(1, int(round(w * s))))
    return F.interpolate(x, size=size, mode="bicubic", align_corners=False,
                         antialias=s < 1.0).clamp(0.0, 1.0)


def _font(size, path=""):
    for candidate in (path, "DejaVuSans.ttf", "arial.ttf", "Arial.ttf"):
        if candidate:
            try:
                return ImageFont.truetype(candidate, size)
            except (OSError, ValueError):
                pass
    try:
        return ImageFont.load_default(size=size)
    except TypeError:                     # Pillow < 10.1: bitmap font, one size
        return ImageFont.load_default()


def letterbox(image: Image.Image, ratio):
    """Black bars over the top and bottom so the visible picture has a cinema
    shape; the frame keeps its size. Nothing happens if the picture is already
    that wide or wider."""
    if ratio not in LETTERBOXES or ratio == "None":
        return image
    a, b = (float(v) for v in ratio.split(":"))
    w, h = image.size
    bar = int(round((h - w * b / a) / 2))
    if bar <= 0:
        return image
    out = image.copy()
    d = ImageDraw.Draw(out)
    black = (0, 0, 0, 255) if image.mode == "RGBA" else (0, 0, 0)
    d.rectangle((0, 0, w, bar - 1), fill=black)
    d.rectangle((0, h - bar, w, h), fill=black)
    return out


def letterbox_bar(size, ratio):
    """Height of the bottom bar letterbox() would draw, 0 if none."""
    if ratio not in LETTERBOXES or ratio == "None":
        return 0
    a, b = (float(v) for v in ratio.split(":"))
    w, h = size
    return max(0, int(round((h - w * b / a) / 2)))


def subtitle(image: Image.Image, text, colour="White", size=0.035, font_path="", bar=0):
    """A film subtitle: centred at the bottom with a dark outline, or in the
    middle of the bottom letterbox bar when there is one deep enough."""
    text = (text or "").strip()
    if not text:
        return image
    w, h = image.size
    font = _font(max(10, int(round(min(w, h) * size))), font_path)
    out = image.convert("RGBA")
    d = ImageDraw.Draw(out)
    stroke = max(1, int(round(min(w, h) * size * 0.08)))
    l, t, r, b = d.textbbox((0, 0), text, font=font, stroke_width=stroke)
    tw, th = r - l, b - t
    if bar >= th * 1.3:
        y = h - bar + (bar - th) // 2
    else:
        y = h - th - int(round(min(w, h) * 0.06))
    x = (w - tw) // 2
    fill = SUB_COLOURS.get(colour, SUB_COLOURS["White"]) + (255,)
    d.text((x - l, y - t), text, font=font, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0, 200))
    return out if image.mode == "RGBA" else out.convert(image.mode)


def border(image: Image.Image, kind, size):
    """Frame the picture. size: border width as a share of the shorter side.
    Polaroid leaves a deeper strip at the bottom."""
    if kind not in _BORDER_RGB or size <= 0:
        return image
    w, h = image.size
    b = max(1, int(round(min(w, h) * size)))
    bottom = b * 4 if kind == "Polaroid" else b
    out = Image.new(image.mode, (w + 2 * b, h + b + bottom),
                    _BORDER_RGB[kind] + ((255,) if image.mode == "RGBA" else ()))
    out.paste(image, (b, b))
    return out


def watermark(image: Image.Image, text, position="Bottom right", opacity=0.6, size=0.03, font_path=""):
    """Text on the picture: white with a soft shadow, so it reads on light
    and dark alike. size: text height as a share of the shorter side."""
    text = (text or "").strip()
    if not text or opacity <= 0:
        return image
    w, h = image.size
    font = _font(max(8, int(round(min(w, h) * size))), font_path)
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    l, t, r, b = d.textbbox((0, 0), text, font=font)
    tw, th = r - l, b - t
    m = int(round(min(w, h) * 0.03))
    x = {"left": m, "right": w - tw - m}.get(position.split()[-1], (w - tw) // 2)
    y = m if position.startswith("Top") else (h - th) // 2 if position == "Centre" else h - th - m
    x, y = x - l, y - t
    a = int(round(255 * min(max(opacity, 0.0), 1.0)))
    off = max(1, int(round(th * 0.06)))
    d.text((x + off, y + off), text, font=font, fill=(0, 0, 0, a // 2))
    d.text((x, y), text, font=font, fill=(255, 255, 255, a))
    base = image.convert("RGBA")
    base.alpha_composite(layer)
    return base if image.mode == "RGBA" else base.convert(image.mode)


def unsharp(x, amount, radius_px):
    """Output sharpening: a small unsharp mask on luminance, for the export size."""
    from .ops import gaussian_blur, luma
    if amount <= 0:
        return x
    y = luma(x)
    detail = y - gaussian_blur(y, max(0.3, radius_px))
    return (x + detail * (1.5 * amount)).clamp(0.0, 1.0)


def frame_active(s):
    return s["en_frame"] and (s["out_letterbox"] != "None" or s["out_border"] != "None")


def export_active(s):
    return s["en_export"] and (s["out_aspect"] != "Original" or s["out_long_edge"] > 0
                               or s["out_sharpen"] > 0 or bool((s["wm_text"] or "").strip())
                               or bool((s["sub_text"] or "").strip()))
