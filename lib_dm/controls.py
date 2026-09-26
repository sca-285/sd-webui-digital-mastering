"""Every control, declared once.

The UI, the pipeline, the presets and the PNG-info round trip all read this one
table, so adding a control is one line here plus the code that uses it. A
control at its neutral value is a no-op, which is how the pipeline knows which
stages to skip. Each section also has an Enable box (see GROUPS).
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Control:
    name: str          # key in settings, presets and the infotext
    label: str
    default: object
    minimum: float = 0.0
    maximum: float = 1.0
    step: float = 0.01
    kind: str = "slider"   # slider | checkbox | lut | text
    info: str = ""
    neutral: object = None  # value at which it does nothing; None = same as default


# Where each control sits on screen is decided in lib_dm/layout.py.
CONTROLS = [
    Control("strength", "Intensity", 1.0, 0.0, 1.0, 0.05,
            info="How much of the whole grade to apply. 0 = original image."),
    # --- section switches ------------------------------------------------------
    Control("en_color", "Enable Color", False, kind="checkbox"),
    Control("en_detail", "Enable Detail & Finish", False, kind="checkbox"),
    Control("en_splash", "Enable Selective Color", False, kind="checkbox"),
    Control("en_lut", "Enable LUT", False, kind="checkbox"),
    Control("en_repair", "Enable Restoration", False, kind="checkbox"),
    # --- colour ------------------------------------------------------------
    Control("exposure", "Exposure", 0.0, -2.0, 2.0, 0.05, info="In stops: +1 = twice as bright."),
    Control("contrast", "Contrast", 0.0, -1.0, 1.0, 0.01),
    Control("temperature", "Temperature", 0.0, -1.0, 1.0, 0.01, info="- cool / + warm"),
    Control("tint", "Tint", 0.0, -1.0, 1.0, 0.01, info="- green / + magenta"),
    Control("saturation", "Saturation", 1.0, 0.0, 2.0, 0.01, info="0 = black & white"),
    Control("vibrance", "Vibrance", 0.0, -1.0, 1.0, 0.01, info="Boosts dull colours, spares strong ones."),
    Control("shadow_hue", "Shadow colour", 0.55, 0.0, 1.0, 0.01),
    Control("shadow_tint", "Shadow amount", 0.0, 0.0, 1.0, 0.01),
    Control("highlight_hue", "Highlight colour", 0.08, 0.0, 1.0, 0.01),
    Control("highlight_tint", "Highlight amount", 0.0, 0.0, 1.0, 0.01),
    Control("tone_balance", "Balance", 0.0, -1.0, 1.0, 0.01, info="- favour shadows / + favour highlights"),
    Control("slope", "CDL Slope", 1.0, 0.0, 2.0, 0.01, info="Gain: scales everything, mostly visible in highlights."),
    Control("offset", "CDL Offset", 0.0, -0.5, 0.5, 0.005, info="Lift: + milky blacks, - crushed blacks."),
    Control("power", "CDL Power", 1.0, 0.1, 3.0, 0.01, info="Gamma: < 1 brighter mids, > 1 darker mids."),
    # --- detail & finish ----------------------------------------------------
    Control("clarity", "Clarity", 0.0, -1.0, 2.0, 0.05, info="+ crisp local contrast / - soft glow"),
    Control("sharpen", "Sharpen", 0.0, 0.0, 1.0, 0.05, info="Edges only; flat areas and noise are left alone."),
    Control("vignette", "Vignette", 0.0, -1.0, 1.0, 0.01, info="+ dark corners / - bright corners"),
    Control("grain", "Film grain", 0.0, 0.0, 1.0, 0.01),
    Control("clarity_radius", "Clarity radius", 4.0, 1.0, 10.0, 0.5,
            info="Small = texture, large = shape and depth."),
    Control("grain_size", "Grain size", 1.0, 0.5, 3.0, 0.1),
    Control("dither", "Anti-banding", 0.0, 0.0, 1.0, 0.05,
            info="Invisible noise that breaks up banding in skies and gradients."),
    # --- effects -------------------------------------------------------------
    Control("splash_desat", "Grey out other colours", 1.0, 0.0, 1.0, 0.05, neutral=0.0),
    Control("splash_hue", "Colour to keep", 0.0, 0.0, 1.0, 0.01),
    Control("splash_tolerance", "Colour range", 0.10, 0.01, 0.5, 0.01, info="How wide a band of hues is kept."),
    Control("lut", "LUT (.cube)", "None", kind="lut"),
    Control("lut_strength", "LUT opacity", 1.0, 0.0, 1.0, 0.05),
    Control("lut_dir", "Extra LUT folder", "", kind="text"),
    # --- repair & tools ----------------------------------------------------------
    Control("deblock", "JPEG de-blocking", 0.0, 0.0, 1.0, 0.05),
    Control("dering", "De-ringing", 0.0, 0.0, 1.0, 0.05),
    Control("semantic", "Protect people (AI)", False, kind="checkbox"),
    Control("protect", "Protect strength", 0.75, 0.0, 1.0, 0.05),
    Control("false_color", "Exposure check (false colour)", False, kind="checkbox"),
]

BY_NAME = {c.name: c for c in CONTROLS}
NAMES = [c.name for c in CONTROLS]
DEFAULTS = {c.name: c.default for c in CONTROLS}
NEUTRAL = {c.name: (c.default if c.neutral is None else c.neutral) for c in CONTROLS}

# Each Enable box and the controls it switches. An unticked section counts as
# neutral, whatever its sliders say - so a section can be set up and toggled.
GROUPS = {
    "en_color": ["exposure", "contrast", "temperature", "tint", "saturation", "vibrance",
                 "shadow_hue", "shadow_tint", "highlight_hue", "highlight_tint", "tone_balance",
                 "slope", "offset", "power"],
    "en_detail": ["clarity", "sharpen", "vignette", "grain", "clarity_radius", "grain_size", "dither"],
    "en_splash": ["splash_desat", "splash_hue", "splash_tolerance"],
    "en_lut": ["lut", "lut_strength"],
    "en_repair": ["deblock", "dering"],
}
GROUP_OF = {n: g for g, names in GROUPS.items() for n in names}

# Not part of the look: never pasted from PNG info.
LOCAL_ONLY = {"lut_dir", "false_color"}


def coerce(name, value):
    """A value of the right type for this control, clamped to its range."""
    c = BY_NAME[name]
    if c.kind == "checkbox":
        if isinstance(value, str):
            return value.strip().lower() in ("1", "true", "yes", "on")
        return bool(value)
    if c.kind in ("lut", "text"):
        return "" if value is None else str(value)
    v = float(value)
    return min(max(v, c.minimum), c.maximum)


def settings(values=None, **overrides):
    """A complete settings dict: defaults, then `values`, then keyword overrides."""
    s = dict(DEFAULTS)
    for src in (values or {}), overrides:
        for k, v in src.items():
            if k in BY_NAME:
                s[k] = coerce(k, v)
    return s


def is_default(name, value):
    d = DEFAULTS[name]
    if isinstance(d, float):
        return abs(float(value) - d) < 1e-9
    return value == d


def is_neutral(name, value):
    n = NEUTRAL[name]
    if isinstance(n, float):
        return abs(float(value) - n) < 1e-9
    return value == n


def effective(s):
    """What actually gets applied: unticked sections replaced by neutral values."""
    out = dict(s)
    for en, names in GROUPS.items():
        if not s[en]:
            for n in names:
                out[n] = NEUTRAL[n]
    return out


def compose(values):
    """Settings from a partial dict (a preset, pasted PNG info).

    Every section the dict mentions is switched on, and that section's
    controls it does not mention start from neutral, so the result is exactly
    what the dict describes. Sections it does not mention stay off, at their
    ordinary defaults, ready to be ticked.
    """
    s = dict(DEFAULTS)
    for en, names in GROUPS.items():
        if any(n in values for n in names):
            s[en] = True
            for n in names:
                s[n] = NEUTRAL[n]
    for k, v in values.items():
        if k in BY_NAME:
            s[k] = coerce(k, v)
    return s


# ------------------------------------------------------------------ infotext
#
# One PNG-info key, "Digital Mastering", holding only the non-default values:
#     Digital Mastering: "exposure=0.2; saturation=1.15; lut=Kodak.cube"
# so a plain generation's infotext does not grow thirty entries.

INFOTEXT_KEY = "Digital Mastering"


def to_infotext(s) -> str:
    """Every value of every ticked section; outside sections, only what differs
    from the default. The Enable boxes themselves are implied by which
    sections appear."""
    parts = []
    for c in CONTROLS:
        if c.name in LOCAL_ONLY or c.name in GROUPS:
            continue
        g = GROUP_OF.get(c.name)
        if g is not None and not s[g]:
            continue
        if g is None and is_default(c.name, s[c.name]):
            continue
        v = s[c.name]
        if isinstance(v, float):
            v = f"{v:g}"
        parts.append(f"{c.name}={v}")
    return "; ".join(parts) or "on"


# Earlier releases wrote a different, human-readable format. Parse it too,
# so pasting an older image restores what can be restored.
_LEGACY = [
    (r"Restore\(Deblock:([-\d.]+) Ring:([-\d.]+) Band:([-\d.]+)\)", ("deblock", "dering", "dither")),
    (r"Clarity\(Str:([-\d.]+) Rad:([-\d.]+) Sharp:([-\d.]+)\)", ("clarity", "clarity_radius", "sharpen")),
    (r"CDL\(Slope:([-\d.]+) Off:([-\d.]+) Pwr:([-\d.]+)\)", ("slope", "offset", "power")),
    (r"LUT\((.+?) Str:([-\d.]+)\)", ("lut", "lut_strength")),
    (r"Splash\(Hue:([-\d.]+) Tol:([-\d.]+) BgDesat:([-\d.]+)\)",
     ("splash_hue", "splash_tolerance", "splash_desat")),
    (r"Semantic\(Protect:([-\d.]+)\)", ("protect",)),
]


def from_infotext(text: str):
    """Settings from a PNG-info value, or None if the text is not ours."""
    if not text:
        return None
    text = text.strip().strip('"')
    values = {}
    if "=" in text or text == "on":
        for part in text.split(";"):
            if "=" in part:
                k, v = part.split("=", 1)
                k = k.strip()
                if k in BY_NAME and k not in LOCAL_ONLY and k not in GROUPS:
                    try:
                        values[k] = coerce(k, v.strip())
                    except ValueError:
                        pass
        return compose(values)
    for pattern, names in _LEGACY:
        m = re.search(pattern, text)
        if m:
            for k, v in zip(names, m.groups()):
                try:
                    values[k] = coerce(k, v)
                except ValueError:
                    pass
    if "Semantic(" in text:
        values["semantic"] = True
    return compose(values)
