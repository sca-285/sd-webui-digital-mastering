"""What goes on which tab, and the guide text shown above each one.

Four tabs. Every control is visible: each tab is a list of titled sections
(title None = no heading), no collapsed "More" part.
"""

QUICK_START = """
**Quick start (3 steps)**

1. Pick a **Look preset**. The line underneath says what it does.
2. Drag **Intensity**: 1 = full, 0.5 = half, 0 = the original image. Intensity stays where you left it when you switch presets, so you can compare them all at the same strength.
3. To fine-tune, open the tabs below. Each section has an **Enable** box: only ticked sections are applied, so you can set a section up and switch it on and off to compare. **Reset** unticks everything and restores the defaults.

A preset ticks the sections it uses and sets their sliders; nothing is hidden, and you can keep adjusting after picking one.
Settings are saved in PNG Info: Send to / Paste restores the exact look.

*Using it with Easy Color Corrector and Optical Realism:* switch each job on in one place only.
Temperature, grain or vignette enabled in two extensions stack up and double.
"""

TABS = [
    {
        "title": "Color",
        "guide": """
**Light and colour.** Tick **Enable Color** first; nothing here applies while it is off.

| Slider | What it does | Typical range |
|---|---|---|
| Exposure | Brighter / darker overall, in stops (+1 = twice as bright) | -0.3 … +0.3 |
| Contrast | S-curve. Negative flattens for a matte look | -0.2 … +0.4 |
| Temperature | Negative cooler (blue), positive warmer (amber) | ±0.1 … ±0.4 |
| Tint | Negative towards green, positive towards magenta | ±0.05 … ±0.2 |
| Saturation | Strength of every colour. 0 = black & white | 0.8 … 1.3 |
| Vibrance | Boosts only the muted colours; leaves skin and already-strong colours alone | 0.1 … 0.4 |

**Split toning**: one colour into the shadows, another into the highlights. This is where "cinematic" looks come from.
The *colour* sliders pick a hue around the wheel: 0 red · 0.08 orange · 0.16 yellow · 0.33 green · 0.5 cyan · 0.66 blue · 0.8 magenta.
*amount* is how strong. Teal & Orange, for example: Shadow colour 0.5, amount 0.4; Highlight colour 0.08, amount 0.4.

**CDL** is for people used to colourist tools: Slope ≈ gain, Offset ≈ lift / crush the blacks, Power ≈ midtone gamma.
""",
        "sections": [
            (None, ["en_color"]),
            ("Light", ["exposure", "contrast"]),
            ("White balance", ["temperature", "tint"]),
            ("Colour", ["saturation", "vibrance"]),
            ("Split toning", ["shadow_hue", "shadow_tint", "highlight_hue", "highlight_tint", "tone_balance"]),
            ("CDL", ["slope", "offset", "power"]),
        ],
    },
    {
        "title": "Detail & Finish",
        "guide": """
**Sharpness and the final finishing layer.** Tick **Enable Detail & Finish** first.

| Slider | What it does | Typical range |
|---|---|---|
| Clarity | Positive: depth, detail stands out. Negative: soft glow, smoother skin | -0.3 … +0.5 |
| Sharpen | Sharpens edges only; flat areas and noise are left alone | 0.1 … 0.3 |
| Vignette | Positive: darker corners, draws the eye in. Negative: brighter corners | 0.15 … 0.4 |
| Film grain | Film-like grain; tied to the seed, so the same seed gives the same grain | 0.1 … 0.3 |

- **Clarity radius**: small affects texture, large affects shape and depth.
- **Grain size**: how coarse the grain is.
- **Anti-banding**: a trace of noise that removes banding in skies and gradients. Always applied last.

Tip: for portraits, turn on **Protect people** in *Repair & Tools* so Clarity and Sharpen do not roughen skin.
""",
        "sections": [
            (None, ["en_detail"]),
            ("Detail", ["clarity", "clarity_radius", "sharpen"]),
            ("Finish", ["vignette", "grain", "grain_size", "dither"]),
        ],
    },
    {
        "title": "Effects",
        "guide": """
**Keep one colour (colour splash)**: the picture goes black & white except for one colour.
1. Tick **Enable Selective Color**. **Grey out other colours** starts at 1 (fully grey); lower it to keep some colour everywhere.
2. **Colour to keep** picks the colour: 0 red · 0.08 orange · 0.16 yellow · 0.33 green · 0.6 blue.
3. **Colour range**: larger keeps more neighbouring hues.
To keep *people* in colour instead, turn on **Protect people** in *Repair & Tools* (preset "Splash: Subject in Colour").

**LUT**: tick **Enable LUT**, copy `.cube` files into `models/LUTs` and press **Refresh**, or enter another folder in *Extra LUT folder*. Presets never change your LUT choice.
**LUT opacity** tones the LUT down. The LUT is applied after the colour grade, the way colourists stack them.
""",
        "sections": [
            ("Selective colour", ["en_splash", "splash_desat", "splash_hue", "splash_tolerance"]),
            ("LUT", ["en_lut", "lut", "lut_strength", "lut_dir"]),
        ],
    },
    {
        "title": "Repair & Tools",
        "guide": """
**Repair** (tick **Enable Restoration**): for img2img sources that are heavily compressed JPEGs or images saved from the web.
- **JPEG de-blocking**: softens the 8×8 JPEG block grid.
- **De-ringing**: removes the "mosquito" speckle around edges.
Images generated from scratch (txt2img) do not need these.

**Protect people (AI)**: finds people with SegFormer-B0 (~15 MB, downloaded on first use) and keeps Clarity, Sharpen and Grey-out off them. *Protect strength* = how much.

**Exposure check**: adds an exposure map next to the result (the image itself is not changed):
purple = crushed black · teal = deep shadow · green = mid-grey · yellow = close to clipping · red = clipped.
""",
        "sections": [
            ("Restoration", ["en_repair", "deblock", "dering"]),
            ("Protect people", ["semantic", "protect"]),
            ("Exposure check", ["false_color"]),
        ],
    },
]

# Hue sliders get a rainbow track (style.css keys off this class).
HUE_SLIDERS = {"shadow_hue", "highlight_hue", "splash_hue"}


def names_in(tab):
    return [n for _, names in tab["sections"] for n in names]
