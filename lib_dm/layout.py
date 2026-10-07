"""What goes on which tab, and the guide text shown above each one.

Four tabs. Every control is visible: each tab is a list of titled sections
(title None = no heading), no collapsed "More" part.
"""

QUICK_START = """
Pick a look, then set **Intensity** (0 = original). Each tab's **Enable** box switches it on or off; **Reset** clears everything.
Settings travel in PNG info. Full guide: README on GitHub.
"""

TABS = [
    {
        "title": "Color",
        "guide": """
Exposure in stops, contrast, white balance, saturation. **Split toning** tints shadows and highlights (hue: 0 red, 0.08 orange, 0.5 cyan, 0.66 blue). **CDL**: slope / offset / power.
""",
        "sections": [
            (None, ["en_color"]),
            ("Light", ["exposure", "contrast", "dehaze"]),
            ("Tone curve", ["curve", "curve_amount"]),
            ("White balance", ["temperature", "tint"]),
            ("Colour", ["saturation", "vibrance"]),
            ("Split toning", ["shadow_hue", "shadow_tint", "highlight_hue", "highlight_tint", "tone_balance"]),
            ("Black & white", ["bw", "bw_filter"]),
            ("CDL", ["slope", "offset", "power"]),
        ],
    },
    {
        "title": "Detail & Finish",
        "guide": """
**Clarity**: + depth, − soft glow. **Sharpen** works on edges only. **Anti-banding** removes steps in skies. Skin smoothing uses people detection.
""",
        "sections": [
            (None, ["en_detail"]),
            ("Detail", ["clarity", "clarity_radius", "sharpen", "skin_smooth"]),
            ("Finish", ["dither"]),
        ],
    },
    {
        "title": "Effects",
        "guide": """
**Selective colour** keeps one hue and greys the rest. **LUT**: put `.cube` files in `models/LUTs` and press Refresh.
""",
        "sections": [
            ("Selective colour", ["en_splash", "splash_desat", "splash_hue", "splash_tolerance"]),
            ("LUT", ["en_lut", "lut", "lut_strength", "lut_dir"]),
        ],
    },
    {
        "title": "HSL & Wheels",
        "guide": """
**HSL**: hue, saturation and lightness per colour. **Wheels**: drag the dot to tint shadows (lift), midtones (gamma) or highlights (gain); further out = stronger, double-click clears.
""",
        "sections": [
            ("HSL", ["en_hsl"]),
            *[(band.capitalize(), [f"hsl_h_{band}", f"hsl_s_{band}", f"hsl_l_{band}"])
              for band in ("red", "orange", "yellow", "green", "aqua", "blue", "purple", "magenta")],
            ("Color wheels", ["en_wheels", "lift_hue", "lift_amt", "lift_lum", "gamma_hue", "gamma_amt",
                              "gamma_lum", "gain_hue", "gain_amt", "gain_lum"]),
        ],
    },
    {
        "title": "Local",
        "guide": """
Exposure in one part of the frame: **graduated** (sky), **radial** (centre / outside) and **people / background** light.
""",
        "sections": [
            (None, ["en_local"]),
            ("Graduated filter", ["grad_stops", "grad_angle", "grad_position", "grad_softness",
                                  "grad_hue", "grad_tint"]),
            ("Radial filter", ["rad_inside", "rad_outside", "rad_on_people", "rad_x", "rad_y",
                               "rad_size", "rad_softness"]),
            ("People / Background", ["subject_light", "background_light"]),
        ],
    },
    {
        "title": "Overlay",
        "guide": """
Light leaks, dust, bokeh and other textures on top. Blend *Auto* suits most files. Add your own to `models/overlays` and press Refresh.
""",
        "sections": [
            (None, ["en_overlay"]),
            ("Layer 1", ["overlay_1", "ov1_blend", "ov1_opacity", "ov1_hue", "ov1_zoom", "ov1_fit"]),
            ("Layer 2", ["overlay_2", "ov2_blend", "ov2_opacity", "ov2_hue", "ov2_zoom", "ov2_fit"]),
            ("Both layers", ["ov_vary", "ov_rotate", "overlay_dir"]),
        ],
        "reference": "overlay_reference.jpg",
    },
    {
        "title": "Output",
        "guide": """
Runs last and presets never touch it. **Frame**: letterbox bars, border. **Export**: crop for a platform, resize, sharpen, subtitle, watermark.
""",
        "sections": [
            ("Frame", ["en_frame", "out_letterbox", "out_border", "out_border_size"]),
            ("Export: crop", ["en_export", "out_aspect", "out_crop_people", "out_crop_x", "out_crop_y"]),
            ("Export: size", ["out_long_edge", "out_sharpen"]),
            ("Export: subtitle", ["sub_text", "sub_colour", "sub_size"]),
            ("Export: watermark", ["wm_text", "wm_position", "wm_opacity", "wm_size", "wm_font"]),
        ],
    },
    {
        "title": "Tools",
        "guide": """
**Protect people** keeps clarity, sharpen and grey-out off people. **Exposure check** adds a false-colour map beside the result.
""",
        "sections": [
            ("Protect people", ["semantic", "protect"]),
            ("Exposure check", ["false_color"]),
        ],
    },
]

# Hue sliders get a rainbow track (style.css keys off this class).
HUE_SLIDERS = {"shadow_hue", "highlight_hue", "splash_hue", "lift_hue", "gamma_hue", "gain_hue", "grad_hue"}


def names_in(tab):
    return [n for _, names in tab["sections"] for n in names]
