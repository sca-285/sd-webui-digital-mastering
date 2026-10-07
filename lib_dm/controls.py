"""Every control, declared once.

The UI, the pipeline, the presets and the PNG-info round trip all read this one
table, so adding a control is one line here plus the code that uses it. A
control at its neutral value is a no-op, which is how the pipeline knows which
stages to skip. Each section also has an Enable box (see GROUPS).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .grade import BW_FILTERS, CURVES, HSL_BANDS
from .output import ASPECTS, BORDERS, LETTERBOXES, POSITIONS, SUB_COLOURS
from .overlay import BLENDS, FITS


@dataclass(frozen=True)
class Control:
    name: str          # key in settings, presets and the infotext
    label: str
    default: object
    minimum: float = 0.0
    maximum: float = 1.0
    step: float = 0.01
    kind: str = "slider"   # slider | checkbox | lut | overlay | choice | text
    info: str = ""
    neutral: object = None  # value at which it does nothing; None = same as default
    choices: tuple = field(default_factory=tuple)


# Where each control sits on screen is decided in lib_dm/layout.py.
CONTROLS = [
    Control("strength", "Intensity", 1.0, 0.0, 1.0, 0.05,
            info="How much of the whole grade to apply. 0 = original image."),
    # --- section switches ------------------------------------------------------
    Control("en_color", "Enable Color", False, kind="checkbox"),
    Control("en_detail", "Enable Detail & Finish", False, kind="checkbox"),
    Control("en_splash", "Enable Selective Color", False, kind="checkbox"),
    Control("en_lut", "Enable LUT", False, kind="checkbox"),
    Control("en_hsl", "Enable HSL", False, kind="checkbox"),
    Control("en_wheels", "Enable Color wheels", False, kind="checkbox"),
    Control("en_overlay", "Enable Overlay", False, kind="checkbox"),
    Control("en_local", "Enable Local", False, kind="checkbox"),
    Control("en_frame", "Enable Frame", False, kind="checkbox"),
    Control("en_export", "Enable Export", False, kind="checkbox"),
    # --- colour ------------------------------------------------------------
    Control("exposure", "Exposure", 0.0, -2.0, 2.0, 0.05, info="In stops: +1 = twice as bright."),
    Control("contrast", "Contrast", 0.0, -1.0, 1.0, 0.01),
    Control("dehaze", "Dehaze", 0.0, 0.0, 1.0, 0.05, info="Takes haze and milkiness out of a picture."),
    Control("curve", "Tone curve", "Linear", kind="choice", choices=tuple(CURVES)),
    Control("curve_amount", "Curve amount", 1.0, 0.0, 1.0, 0.05),
    Control("bw", "Black & white", 0.0, 0.0, 1.0, 0.05, info="1 = fully monochrome."),
    Control("bw_filter", "B&W filter", "Neutral", kind="choice", choices=tuple(BW_FILTERS),
            info="Red: dark skies. Green: smooth skin. Infrared: white leaves."),
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
    # --- color wheels: lift / gamma / gain -----------------------------------
    *[c for w, lab in (("lift", "Lift (shadows)"), ("gamma", "Gamma (midtones)"), ("gain", "Gain (highlights)"))
      for c in (Control(f"{w}_hue", f"{lab} colour", 0.55 if w == "lift" else 0.08, 0.0, 1.0, 0.01),
                Control(f"{w}_amt", f"{lab} colour amount", 0.0, 0.0, 1.0, 0.01),
                Control(f"{w}_lum", f"{lab} level", 0.0, -1.0, 1.0, 0.01))],
    # --- HSL: hue / saturation / lightness by colour ---------------------------
    Control("hsl_h_red", "Red: hue", 0.0, -1.0, 1.0, 0.05),
    Control("hsl_s_red", "Red: saturation", 0.0, -1.0, 1.0, 0.05),
    Control("hsl_l_red", "Red: lightness", 0.0, -1.0, 1.0, 0.05),
    Control("hsl_h_orange", "Orange: hue", 0.0, -1.0, 1.0, 0.05),
    Control("hsl_s_orange", "Orange: saturation", 0.0, -1.0, 1.0, 0.05),
    Control("hsl_l_orange", "Orange: lightness", 0.0, -1.0, 1.0, 0.05),
    Control("hsl_h_yellow", "Yellow: hue", 0.0, -1.0, 1.0, 0.05),
    Control("hsl_s_yellow", "Yellow: saturation", 0.0, -1.0, 1.0, 0.05),
    Control("hsl_l_yellow", "Yellow: lightness", 0.0, -1.0, 1.0, 0.05),
    Control("hsl_h_green", "Green: hue", 0.0, -1.0, 1.0, 0.05),
    Control("hsl_s_green", "Green: saturation", 0.0, -1.0, 1.0, 0.05),
    Control("hsl_l_green", "Green: lightness", 0.0, -1.0, 1.0, 0.05),
    Control("hsl_h_aqua", "Aqua: hue", 0.0, -1.0, 1.0, 0.05),
    Control("hsl_s_aqua", "Aqua: saturation", 0.0, -1.0, 1.0, 0.05),
    Control("hsl_l_aqua", "Aqua: lightness", 0.0, -1.0, 1.0, 0.05),
    Control("hsl_h_blue", "Blue: hue", 0.0, -1.0, 1.0, 0.05),
    Control("hsl_s_blue", "Blue: saturation", 0.0, -1.0, 1.0, 0.05),
    Control("hsl_l_blue", "Blue: lightness", 0.0, -1.0, 1.0, 0.05),
    Control("hsl_h_purple", "Purple: hue", 0.0, -1.0, 1.0, 0.05),
    Control("hsl_s_purple", "Purple: saturation", 0.0, -1.0, 1.0, 0.05),
    Control("hsl_l_purple", "Purple: lightness", 0.0, -1.0, 1.0, 0.05),
    Control("hsl_h_magenta", "Magenta: hue", 0.0, -1.0, 1.0, 0.05),
    Control("hsl_s_magenta", "Magenta: saturation", 0.0, -1.0, 1.0, 0.05),
    Control("hsl_l_magenta", "Magenta: lightness", 0.0, -1.0, 1.0, 0.05),
    # --- detail & finish ----------------------------------------------------
    Control("clarity", "Clarity", 0.0, -1.0, 2.0, 0.05, info="+ crisp local contrast / - soft glow"),
    Control("sharpen", "Sharpen", 0.0, 0.0, 1.0, 0.05, info="Edges only; flat areas and noise are left alone."),
    Control("skin_smooth", "Skin smoothing (AI)", 0.0, 0.0, 1.0, 0.05,
            info="Softens skin texture, keeps tone and edges. Uses people detection."),
    Control("clarity_radius", "Clarity radius", 4.0, 1.0, 10.0, 0.5,
            info="Small = texture, large = shape and depth."),
    Control("dither", "Anti-banding", 0.0, 0.0, 1.0, 0.05,
            info="Invisible noise that breaks up banding in skies and gradients."),
    # --- effects -------------------------------------------------------------
    Control("splash_desat", "Grey out other colours", 1.0, 0.0, 1.0, 0.05, neutral=0.0),
    Control("splash_hue", "Colour to keep", 0.0, 0.0, 1.0, 0.01),
    Control("splash_tolerance", "Colour range", 0.10, 0.01, 0.5, 0.01, info="How wide a band of hues is kept."),
    Control("lut", "LUT (.cube)", "None", kind="lut"),
    Control("lut_strength", "LUT opacity", 1.0, 0.0, 1.0, 0.05),
    Control("lut_dir", "Extra LUT folder", "", kind="text"),
    # --- overlay: two layers, then what they share ---------------------------
    *[c for i in (1, 2) for c in (
        Control(f"overlay_{i}", f"Layer {i}", "None", kind="overlay"),
        Control(f"ov{i}_blend", "Blend", "Auto", kind="choice", choices=tuple(BLENDS),
                info="Auto: Normal for transparent PNGs, Screen for textures on black."),
        Control(f"ov{i}_opacity", "Opacity", 0.8, 0.0, 1.0, 0.05),
        Control(f"ov{i}_hue", "Colour shift", 0.0, -0.5, 0.5, 0.01,
                info="Turns the layer's colours round the wheel: 0.5 = opposite colour."),
        Control(f"ov{i}_zoom", "Zoom", 1.0, 1.0, 3.0, 0.05, info="Crops into the texture: bigger specks, fewer of them."),
        Control(f"ov{i}_fit", "Fit", "Cover", kind="choice", choices=tuple(FITS),
                info="Cover keeps the texture's shape and crops; Stretch fills the frame exactly."),
    )],
    Control("ov_vary", "Vary with seed", True, kind="checkbox",
            info="A different flip and shift per seed."),
    Control("ov_rotate", "Turn to match orientation", True, kind="checkbox",
            info="A landscape texture on a portrait image is turned 90° instead of cropped."),
    Control("overlay_dir", "Extra overlay folder", "", kind="text"),
    # --- local: graduated filter, radial filter, people / background ----------
    Control("grad_stops", "Graduated filter", 0.0, -2.0, 2.0, 0.05,
            info="Stops: − darkens a sky, + lifts the foreground."),
    Control("grad_angle", "Filter comes from", 0.0, 0.0, 360.0, 5.0,
            info="Degrees: 0 top, 90 right, 180 bottom, 270 left."),
    Control("grad_position", "Filter reaches", 0.45, 0.0, 1.0, 0.01,
            info="Where the transition sits, from the filtered edge (0) across the frame (1)."),
    Control("grad_softness", "Filter softness", 0.40, 0.02, 1.0, 0.01),
    Control("grad_hue", "Filter colour", 0.08, 0.0, 1.0, 0.01),
    Control("grad_tint", "Filter colour amount", 0.0, 0.0, 1.0, 0.01,
            info="A coloured grad: orange for a sunset sky, blue for a cold one."),
    Control("rad_inside", "Radial: inside", 0.0, -1.0, 1.0, 0.05, info="Exposure in stops inside the ellipse."),
    Control("rad_outside", "Radial: outside", 0.0, -2.0, 1.0, 0.05,
            info="Exposure in stops outside it: - pulls the eye to the centre."),
    Control("rad_x", "Radial centre X", 0.5, 0.0, 1.0, 0.01),
    Control("rad_y", "Radial centre Y", 0.45, 0.0, 1.0, 0.01),
    Control("rad_size", "Radial size", 0.6, 0.1, 1.5, 0.01, info="Radius as a share of the shorter side."),
    Control("rad_softness", "Radial softness", 0.5, 0.02, 1.0, 0.01),
    Control("rad_on_people", "Centre the radial on people (AI)", False, kind="checkbox",
            info="Finds the people and centres the ellipse on them; X / Y are then ignored."),
    Control("subject_light", "People: light", 0.0, -1.0, 1.0, 0.05,
            info="Stops on detected people."),
    Control("background_light", "Background: light", 0.0, -2.0, 1.0, 0.05,
            info="Exposure in stops on everything else. Uses people detection."),
    # --- output: frame and export, set by hand, never by a preset ------------
    Control("out_letterbox", "Letterbox", "None", kind="choice", choices=tuple(LETTERBOXES),
            info="Black cinema bars; 2.39:1 = scope."),
    Control("out_aspect", "Crop to", "Original", kind="choice", choices=tuple(ASPECTS),
            info="4:5 Instagram feed, 9:16 Story / Reels, 1:1 square, 3:2 print..."),
    Control("out_crop_x", "Crop centre X", 0.5, 0.0, 1.0, 0.01),
    Control("out_crop_y", "Crop centre Y", 0.5, 0.0, 1.0, 0.01),
    Control("out_crop_people", "Keep people in the crop (AI)", False, kind="checkbox",
            info="Centres the crop on the detected people; X / Y are then ignored."),
    Control("out_long_edge", "Resize long edge (px)", 0.0, 0.0, 4096.0, 8.0,
            info="0 = keep. 1080 / 1350 for a feed, 2048 for most sites."),
    Control("out_sharpen", "Output sharpening", 0.0, 0.0, 1.0, 0.05,
            info="A touch of sharpening for the final size, after any resize."),
    Control("out_border", "Border", "None", kind="choice", choices=tuple(BORDERS)),
    Control("out_border_size", "Border width", 0.04, 0.005, 0.15, 0.005,
            info="As a share of the shorter side. Polaroid has a deeper bottom strip."),
    Control("wm_text", "Watermark", "", kind="text"),
    Control("wm_position", "Watermark position", "Bottom right", kind="choice", choices=tuple(POSITIONS)),
    Control("wm_opacity", "Watermark opacity", 0.6, 0.0, 1.0, 0.05),
    Control("wm_size", "Watermark size", 0.03, 0.01, 0.10, 0.005, info="Text height as a share of the shorter side."),
    Control("sub_text", "Subtitle", "", kind="text"),
    Control("sub_colour", "Subtitle colour", "White", kind="choice", choices=tuple(SUB_COLOURS)),
    Control("sub_size", "Subtitle size", 0.035, 0.015, 0.08, 0.005, info="Text height as a share of the shorter side."),
    Control("wm_font", "Font file (watermark and subtitle)", "", kind="text"),
    # --- repair & tools ----------------------------------------------------------
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
                 "slope", "offset", "power", "dehaze", "curve", "curve_amount", "bw", "bw_filter"],
    "en_wheels": [f"{w}_{k}" for w in ("lift", "gamma", "gain") for k in ("hue", "amt", "lum")],
    "en_hsl": [f"hsl_{k}_{b}" for b in HSL_BANDS for k in "hsl"],
    "en_detail": ["clarity", "sharpen", "clarity_radius", "dither", "skin_smooth"],
    "en_splash": ["splash_desat", "splash_hue", "splash_tolerance"],
    "en_lut": ["lut", "lut_strength"],
    "en_local": ["grad_stops", "grad_angle", "grad_position", "grad_softness", "grad_hue", "grad_tint",
                 "rad_inside", "rad_outside", "rad_x", "rad_y", "rad_size", "rad_softness", "rad_on_people",
                 "subject_light", "background_light"],
    "en_frame": ["out_letterbox", "out_border", "out_border_size"],
    "en_export": ["out_aspect", "out_crop_x", "out_crop_y", "out_crop_people", "out_long_edge", "out_sharpen",
                  "wm_text", "wm_position", "wm_opacity", "wm_size", "sub_text", "sub_colour", "sub_size"],
    "en_overlay": [n for i in (1, 2) for n in (f"overlay_{i}", f"ov{i}_blend", f"ov{i}_opacity", f"ov{i}_hue",
                                               f"ov{i}_zoom", f"ov{i}_fit")] + ["ov_vary", "ov_rotate"],
}
GROUP_OF = {n: g for g, names in GROUPS.items() for n in names}

# Not part of the look: never pasted from PNG info.
LOCAL_ONLY = {"lut_dir", "overlay_dir", "wm_font", "false_color"}
OVERLAY_CONTROLS = set(GROUPS["en_overlay"]) | {"en_overlay", "overlay_dir"}
# The Output tab (frame and export) belongs to one picture, not to a look:
# presets leave it be. Local light is part of a look, and presets may set it.
PER_IMAGE_CONTROLS = (set(GROUPS["en_frame"]) | set(GROUPS["en_export"])
                      | {"en_frame", "en_export", "wm_font"})


def coerce(name, value):
    """A value of the right type for this control, clamped to its range."""
    c = BY_NAME[name]
    if c.kind == "checkbox":
        if isinstance(value, str):
            return value.strip().lower() in ("1", "true", "yes", "on")
        return bool(value)
    if c.kind in ("lut", "overlay", "text"):
        value = "" if value is None else str(value)
        if name in ("wm_text", "sub_text"):
            # PNG info is "k=v; k=v": keep the separators and quotes out.
            value = "".join(ch for ch in value if ch not in ';="\n').strip()[:80]
        return value
    if c.kind == "choice":
        value = str(value)
        return value if value in c.choices else c.default
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
    # JPEG repair moved to Auto Color Corrector; only the anti-banding part still applies here.
    (r"Restore\(Deblock:([-\d.]+) Ring:([-\d.]+) Band:([-\d.]+)\)", (None, None, "dither")),
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
                if k is None:
                    continue
                try:
                    values[k] = coerce(k, v)
                except ValueError:
                    pass
    if "Semantic(" in text:
        values["semantic"] = True
    return compose(values)
