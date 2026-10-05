"""Looks. Each preset lists only what it changes. Picking one ticks the Enable
box of every section it uses (with that section's other controls at neutral)
and unticks the rest, so presets never inherit leftovers.

Hues: 0 red, 0.08 orange, 0.12 amber, 0.16 yellow, 0.33 green, 0.47 teal,
0.5 cyan, 0.6 azure, 0.66 blue, 0.75 violet, 0.83 magenta, 0.92 pink.

Presets do not touch Intensity, the LUT or the exposure check: pick a preset,
then dial Intensity to taste, and it stays put while you try other presets.

Grade only: vignette, grain and every other camera trait are Optical
Realism's. Pair a look here with one of its camera presets (see README).
"""

from .controls import OVERLAY_CONTROLS, PER_IMAGE_CONTROLS, compose

# Like the LUT, overlays are your own pick and stay put across presets.
NOT_IN_PRESETS = {"strength", "en_lut", "lut", "lut_dir", "lut_strength", "false_color", *OVERLAY_CONTROLS,
                  *PER_IMAGE_CONTROLS}

CUSTOM = "Custom"

_P = {
    # ---- natural --------------------------------------------------------
    "Natural: Clean Polish": dict(
        contrast=0.10, vibrance=0.15, clarity=0.20, sharpen=0.15),
    "Natural: Vivid Pop": dict(
        contrast=0.20, saturation=1.10, vibrance=0.40, clarity=0.25, sharpen=0.20,
        grad_stops=-0.35),
    "Natural: Soft Matte": dict(
        offset=0.04, slope=0.96, contrast=-0.15, saturation=0.90),
    "Natural: HDR Detail": dict(
        contrast=-0.10, vibrance=0.25, clarity=0.90, clarity_radius=6.0, sharpen=0.25,
        grad_stops=-0.45, grad_position=0.40),

    # ---- portrait -------------------------------------------------------
    "Portrait: Studio Skin": dict(
        temperature=0.10, offset=0.01, contrast=0.05, vibrance=0.15, highlight_hue=0.95,
        highlight_tint=0.12, clarity=0.25, clarity_radius=6.0, sharpen=0.10,
        semantic=True, protect=0.90,
        subject_light=0.15, background_light=-0.25),
    "Portrait: Soft Glamour": dict(
        temperature=0.08, offset=0.02, contrast=-0.10, highlight_hue=0.92, highlight_tint=0.15,
        clarity=-0.35, clarity_radius=8.0, semantic=True, protect=0.85,
        rad_inside=0.15, rad_outside=-0.20, rad_on_people=True, rad_size=0.55, rad_softness=0.8),
    "Portrait: Golden Skin": dict(
        temperature=0.25, contrast=0.10, vibrance=0.10, highlight_hue=0.09,
        highlight_tint=0.25, semantic=True, protect=0.80,
        grad_angle=315.0, grad_position=0.55, grad_softness=0.8, grad_hue=0.09, grad_tint=0.35),
    "Portrait: Editorial Crisp": dict(
        slope=1.05, offset=-0.02, contrast=0.25, saturation=0.90, clarity=0.45,
        clarity_radius=3.0, sharpen=0.35, semantic=True, protect=0.60,
        background_light=-0.35),

    # ---- film -------------------------------------------------------------------
    "Film: Portra Golden": dict(
        temperature=0.15, slope=0.94, offset=0.025, contrast=0.10, saturation=0.95, vibrance=0.05,
        shadow_hue=0.18, shadow_tint=0.15, highlight_hue=0.09, highlight_tint=0.28),
    "Film: Olive Signature": dict(
        exposure=-0.05, slope=0.93, offset=0.03, contrast=0.15, saturation=0.95,
        shadow_hue=0.20, shadow_tint=0.20, highlight_hue=0.10, highlight_tint=0.20),
    "Film: Tungsten Amber": dict(
        exposure=-0.20, temperature=0.30, slope=0.93, offset=0.02, contrast=0.20, saturation=1.00,
        shadow_hue=0.13, shadow_tint=0.25, highlight_hue=0.11, highlight_tint=0.30,
        rad_outside=-0.25, rad_size=0.75),
    "Film: Emerald": dict(
        exposure=-0.10, tint=-0.15, slope=0.93, offset=0.02, contrast=0.25, saturation=1.00,
        shadow_hue=0.30, shadow_tint=0.28, highlight_hue=0.10, highlight_tint=0.18),
    "Film: Travel Ektar": dict(
        temperature=0.08, slope=0.94, offset=0.03, contrast=0.15, saturation=1.05, vibrance=0.15,
        shadow_hue=0.45, shadow_tint=0.12, highlight_hue=0.12, highlight_tint=0.15,
        grad_stops=-0.25),
    "Film: Red Neon Night": dict(
        exposure=-0.30, temperature=0.15, slope=0.92, contrast=0.30, saturation=1.05,
        shadow_hue=0.35, shadow_tint=0.20, highlight_hue=0.01, highlight_tint=0.30,
        rad_outside=-0.30, rad_size=0.70),
    "Film: Cool Slide Stock": dict(
        contrast=0.30, saturation=1.20, temperature=-0.10, shadow_hue=0.64, shadow_tint=0.15),
    "Film: Faded Vintage": dict(
        offset=0.07, slope=0.88, contrast=-0.10, saturation=0.75, highlight_hue=0.12,
        highlight_tint=0.20, shadow_hue=0.55, shadow_tint=0.10),
    "Film: Bleach Bypass": dict(
        slope=1.05, offset=-0.02, contrast=0.45, saturation=0.45, clarity=0.50),
    "Film: Cross Process": dict(
        tint=-0.15, contrast=0.30, saturation=1.20, shadow_hue=0.66, shadow_tint=0.35,
        highlight_hue=0.16, highlight_tint=0.40),
    "Film: Instant Photo": dict(
        offset=0.08, contrast=-0.10, saturation=0.70, tint=0.10, highlight_hue=0.13,
        highlight_tint=0.30, shadow_hue=0.50, shadow_tint=0.25,
        out_border="Polaroid", out_border_size=0.05),

    # ---- cinema ----------------------------------------------------------------
    "Cinema: Teal & Orange": dict(
        contrast=0.20, saturation=1.05, vibrance=0.10, shadow_hue=0.50, shadow_tint=0.45,
        highlight_hue=0.08, highlight_tint=0.40,
        out_letterbox="2.39:1"),
    "Cinema: Blockbuster": dict(
        slope=1.08, offset=-0.03, contrast=0.40, clarity=0.30, shadow_hue=0.50,
        shadow_tint=0.25, highlight_hue=0.08, highlight_tint=0.20,
        grad_stops=-0.25, out_letterbox="2.39:1"),
    "Cinema: Moody Dark": dict(
        exposure=-0.30, offset=-0.02, contrast=0.25, saturation=0.75, shadow_hue=0.58,
        shadow_tint=0.30,
        rad_outside=-0.35, rad_size=0.70, out_letterbox="1.85:1"),
    "Cinema: Digital Green": dict(
        tint=-0.50, contrast=0.30, saturation=0.70, shadow_hue=0.38, shadow_tint=0.40,
        highlight_hue=0.30, highlight_tint=0.20),
    "Cinema: Neo-Noir Blue": dict(
        temperature=-0.45, contrast=0.35, saturation=0.60, shadow_hue=0.64, shadow_tint=0.40,
        out_letterbox="2.39:1"),
    "Cinema: Dusty Night": dict(
        exposure=-0.35, offset=-0.01, contrast=0.25, saturation=1.05, temperature=-0.10, tint=-0.05,
        shadow_hue=0.52, shadow_tint=0.40, highlight_hue=0.07, highlight_tint=0.20,
        out_letterbox="2.39:1"),
    "Cinema: Day for Night": dict(
        exposure=-2.00, slope=0.85, power=1.20, offset=-0.02, temperature=-0.40, tint=-0.08,
        contrast=0.30, saturation=0.70, shadow_hue=0.60, shadow_tint=0.45, highlight_hue=0.55,
        highlight_tint=0.10,
        grad_stops=-0.60, grad_position=0.50, grad_softness=0.60),
    "Cinema: Desert Heat": dict(
        temperature=0.45, contrast=0.20, saturation=1.10, highlight_hue=0.10,
        highlight_tint=0.30, clarity=0.20,
        grad_stops=-0.20, grad_hue=0.09, grad_tint=0.40, out_letterbox="2.39:1"),

    # ---- auteur: homages to how certain films look ----------------------------
    "Auteur: Chungking Neon": dict(
        exposure=-0.15, tint=-0.25, contrast=0.35, saturation=1.25, shadow_hue=0.42, shadow_tint=0.45,
        highlight_hue=0.10, highlight_tint=0.25, clarity=-0.10,
        rad_outside=-0.30, rad_size=0.75, out_letterbox="1.85:1"),
    "Auteur: Mood for Love": dict(
        exposure=-0.25, temperature=0.20, contrast=0.30, saturation=1.15, shadow_hue=0.02, shadow_tint=0.30,
        highlight_hue=0.10, highlight_tint=0.35, clarity=-0.15,
        rad_inside=0.10, rad_outside=-0.40, rad_size=0.60, rad_softness=0.7, out_letterbox="1.85:1"),
    "Auteur: Fallen Angels": dict(
        exposure=-0.30, tint=-0.30, contrast=0.55, saturation=0.55, shadow_hue=0.45, shadow_tint=0.40,
        highlight_hue=0.15, highlight_tint=0.15, clarity=0.30,
        rad_outside=-0.40, rad_size=0.65, out_letterbox="1.85:1"),
    "Auteur: 2046": dict(
        exposure=-0.20, temperature=-0.15, slope=1.05, contrast=0.35, saturation=0.90, shadow_hue=0.55,
        shadow_tint=0.35, highlight_hue=0.98, highlight_tint=0.20,
        rad_outside=-0.30, rad_size=0.70, out_letterbox="2.39:1"),
    "Auteur: Happy Together": dict(
        temperature=0.35, tint=0.08, contrast=0.30, saturation=1.25, highlight_hue=0.13, highlight_tint=0.40,
        shadow_hue=0.05, shadow_tint=0.20,
        grad_hue=0.11, grad_tint=0.35, out_letterbox="1.85:1"),
    "Auteur: Hong Kong 90s": dict(
        offset=0.04, slope=0.92, temperature=0.12, tint=0.10, contrast=0.10, saturation=0.90,
        shadow_hue=0.50, shadow_tint=0.20, highlight_hue=0.95, highlight_tint=0.15, clarity=-0.20),
    "Auteur: Saigon Rain": dict(
        exposure=-0.25, offset=-0.01, contrast=0.30, saturation=1.10, temperature=-0.05,
        shadow_hue=0.50, shadow_tint=0.45, highlight_hue=0.07, highlight_tint=0.30, clarity=0.15,
        grad_stops=-0.30, out_letterbox="2.39:1"),
    "Auteur: Matte Street": dict(
        offset=0.05, slope=0.94, contrast=0.15, saturation=0.80, shadow_hue=0.50, shadow_tint=0.30,
        highlight_hue=0.09, highlight_tint=0.20, clarity=0.20,
        background_light=-0.20),
    "Auteur: Golden Anamorphic": dict(
        temperature=0.30, contrast=0.20, saturation=1.05, highlight_hue=0.09, highlight_tint=0.35,
        shadow_hue=0.55, shadow_tint=0.15, clarity=-0.10,
        grad_angle=315.0, grad_position=0.50, grad_softness=0.8, grad_hue=0.08, grad_tint=0.40,
        out_letterbox="2.39:1"),
    "Auteur: Sickly Thriller": dict(
        exposure=-0.15, tint=-0.20, temperature=0.10, contrast=0.35, saturation=0.60, shadow_hue=0.40,
        shadow_tint=0.30, highlight_hue=0.15, highlight_tint=0.25,
        rad_outside=-0.35, rad_size=0.70, out_letterbox="2.39:1"),
    "Auteur: Nordic Noir": dict(
        exposure=-0.15, temperature=-0.30, contrast=0.25, saturation=0.50, shadow_hue=0.60, shadow_tint=0.30,
        highlight_hue=0.55, highlight_tint=0.10,
        grad_stops=-0.40, out_letterbox="2.39:1"),
    "Auteur: Pastel Symmetry": dict(
        exposure=0.10, offset=0.03, temperature=0.10, contrast=0.05, saturation=1.10, highlight_hue=0.95,
        highlight_tint=0.25, shadow_hue=0.12, shadow_tint=0.15,
        out_border="Cream", out_border_size=0.03),

    # ---- mood ----------------------------------------------------------------------
    "Mood: Golden Hour": dict(
        temperature=0.35, tint=0.05, contrast=0.10, vibrance=0.25, highlight_hue=0.10,
        highlight_tint=0.40, shadow_hue=0.75, shadow_tint=0.15,
        grad_position=0.55, grad_softness=0.7, grad_hue=0.09, grad_tint=0.45),
    "Mood: Blue Hour": dict(
        exposure=-0.10, temperature=-0.35, contrast=0.15, shadow_hue=0.64, shadow_tint=0.35,
        highlight_hue=0.80, highlight_tint=0.15,
        grad_stops=-0.30, grad_hue=0.70, grad_tint=0.25),
    "Mood: Lavender Dusk": dict(
        slope=0.95, offset=0.04, contrast=-0.05, saturation=0.85, highlight_hue=0.92, highlight_tint=0.28,
        shadow_hue=0.70, shadow_tint=0.12, clarity=-0.15,
        grad_position=0.50, grad_softness=0.7, grad_hue=0.90, grad_tint=0.30),
    "Mood: Cyberpunk Neon": dict(
        contrast=0.35, saturation=1.35, shadow_hue=0.80, shadow_tint=0.50,
        highlight_hue=0.50, highlight_tint=0.45, clarity=0.30),
    "Mood: Autumn Warmth": dict(
        temperature=0.30, tint=0.05, contrast=0.15, vibrance=0.30, highlight_hue=0.10,
        highlight_tint=0.30, shadow_hue=0.02, shadow_tint=0.15,
        grad_hue=0.06, grad_tint=0.25),
    "Mood: Arctic Cold": dict(
        exposure=0.15, temperature=-0.50, contrast=0.10, saturation=0.70,
        highlight_hue=0.55, highlight_tint=0.20, clarity=0.20,
        grad_stops=0.20, grad_hue=0.58, grad_tint=0.20),
    "Mood: Flash Snapshot": dict(
        slope=1.04, contrast=0.30, saturation=1.05, vibrance=0.10, temperature=-0.08, clarity=0.10,
        sharpen=0.20),
    "Mood: Anime Vivid": dict(
        exposure=0.05, contrast=0.20, saturation=1.30, vibrance=0.30, clarity=0.15,
        sharpen=0.35),

    # ---- black & white ------------------------------------------------------------
    "B&W: Classic Silver": dict(
        saturation=0.0, contrast=0.25, clarity=0.30),
    "B&W: Hard Noir": dict(
        saturation=0.0, exposure=-0.20, contrast=0.60, clarity=0.50,
        rad_outside=-0.40, rad_size=0.65, out_letterbox="1.85:1"),
    "B&W: Sepia": dict(
        saturation=0.0, offset=0.02, contrast=0.10, highlight_hue=0.09, highlight_tint=0.45,
        shadow_hue=0.07, shadow_tint=0.35,
        out_border="Cream", out_border_size=0.04),

    # ---- colour splash ---------------------------------------------------------
    "Splash: Red Accent": dict(
        splash_hue=0.0, splash_tolerance=0.08, splash_desat=1.0, contrast=0.20, clarity=0.30),
    "Splash: Golden Yellow": dict(
        splash_hue=0.15, splash_tolerance=0.10, splash_desat=1.0, contrast=0.15, clarity=0.25),
    "Splash: Neon Blue": dict(
        splash_hue=0.60, splash_tolerance=0.15, splash_desat=0.90, contrast=0.25, clarity=0.35),
    "Splash: Subject in Colour": dict(
        splash_hue=0.0, splash_tolerance=0.01, splash_desat=0.80, contrast=0.15, clarity=0.20,
        semantic=True, protect=1.0),

    # ---- repair ---------------------------------------------------------------------
    "Repair: Web JPEG": dict(deblock=0.40, dering=0.30, dither=0.20),
    "Repair: Heavy Compression": dict(deblock=0.85, dering=0.75, dither=0.40),
}

PRESETS = {name: compose(p) for name, p in _P.items()}
CHOICES = [CUSTOM, *PRESETS]

# One line each, shown under the preset dropdown.
DESCRIPTIONS = {
    "Natural: Clean Polish": "A light clean-up: a touch more contrast, detail and colour. Suits almost anything.",
    "Natural: Vivid Pop": "Clearly richer colour and crisper detail. Good for landscapes and products.",
    "Natural: Soft Matte": "Lifted blacks and low contrast; easy on the eye, social-media style.",
    "Natural: HDR Detail": "Strong detail, open shadows and highlights. Easy to overdo on skin.",
    "Portrait: Studio Skin": "Gently warm portrait that keeps skin smooth (uses people detection).",
    "Portrait: Soft Glamour": "Soft glow with a pink touch in the highlights; beauty-shot look.",
    "Portrait: Golden Skin": "Warm golden skin, like late-afternoon sun.",
    "Portrait: Editorial Crisp": "Magazine portrait: contrasty, crisp, slightly muted colour.",
    "Film: Portra Golden": "Golden-hour portrait film: creamy warm highlights, soft olive shadows, whites that never clip.",
    "Film: Olive Signature": "Editorial film look: olive-green shadows, cream highlights, rich but calm colour.",
    "Film: Tungsten Amber": "Hotel-lamp interiors on film: deep amber, warm-green shadows, edges in shadow.",
    "Film: Emerald": "Deep emerald greens with warm skin: forests, green walls, green light.",
    "Film: Travel Ektar": "Daylight travel on film: rich blues and warm stone, soft whites, deeper sky.",
    "Film: Red Neon Night": "Night on film under red light: crimson highlights, green shadows, dark.",
    "Film: Cool Slide Stock": "Slide film: cool, saturated, high contrast.",
    "Film: Faded Vintage": "Old faded print: lifted blacks, washed colour, warm highlights.",
    "Film: Bleach Bypass": "Silvery, near-desaturated, harsh contrast; war-film look.",
    "Film: Cross Process": "Cross-processed: blue shadows, yellow highlights, bold odd colour.",
    "Film: Instant Photo": "Instant camera: faded, teal shadows, yellow highlights.",
    "Cinema: Teal & Orange": "The classic Hollywood look: teal shadows, warm orange skin.",
    "Cinema: Blockbuster": "A stronger Teal & Orange with more contrast and depth.",
    "Cinema: Moody Dark": "Dark, muted and cool: brooding and mysterious.",
    "Cinema: Digital Green": "Cold green cast of a digital world, Matrix-style.",
    "Cinema: Neo-Noir Blue": "Cold blue, little colour, high contrast.",
    "Cinema: Dusty Night": "Dark night grade: teal-blue shadows, warm lights, deep contrast.",
    "Cinema: Day for Night": "Daylight graded to moonlit night: dark, blue, low colour. No lights come on.",
    "Cinema: Desert Heat": "Hot amber-orange and saturated: desert, high summer.",
    "Auteur: Chungking Neon": "Hong Kong night in the spirit of Chungking Express: fluorescent green, saturated neon, 1.85 bars.",
    "Auteur: Mood for Love": "After In the Mood for Love: dark rich reds and amber, light pooled on the subject.",
    "Auteur: Fallen Angels": "Fallen Angels night: hard contrast, sickly green-teal, little colour.",
    "Auteur: 2046": "Cool and glossy with red in the highlights, deep shadows, scope bars.",
    "Auteur: Happy Together": "Hot saturated amber and gold, as in Happy Together's Buenos Aires.",
    "Auteur: Hong Kong 90s": "Soft, faded 90s Hong Kong film print: warm, a little magenta, gentle.",
    "Auteur: Saigon Rain": "Wet city street: teal shadows, warm lamps, darker sky, scope bars.",
    "Auteur: Matte Street": "Street cinematic: matte blacks, muted teal, warm skin, background eased down (people detection).",
    "Auteur: Golden Anamorphic": "Low warm sun from the corner, soft and wide, scope bars.",
    "Auteur: Sickly Thriller": "Murky yellow-green thriller grade, low colour, edges pulled down.",
    "Auteur: Nordic Noir": "Cold, grey-blue and quiet, heavy sky, scope bars.",
    "Auteur: Pastel Symmetry": "Bright storybook pastels with pink highlights and a cream border.",
    "Mood: Golden Hour": "Golden late-afternoon sun with slightly violet shadows.",
    "Mood: Blue Hour": "Blue dusk with a pink-violet touch in the highlights.",
    "Mood: Lavender Dusk": "Pink-lavender dusk: soft, airy, low contrast, a blush in the sky.",
    "Mood: Cyberpunk Neon": "Neon magenta and cyan, very saturated.",
    "Mood: Autumn Warmth": "Warm red-orange autumn-leaf colour.",
    "Mood: Arctic Cold": "Icy cold, bright, low colour.",
    "Mood: Flash Snapshot": "Point-and-shoot flash colour: punchy contrast, slightly cool, crisp.",
    "Mood: Anime Vivid": "Bright, saturated, crisp edges: suits anime / illustration.",
    "B&W: Classic Silver": "Classic black & white, crisp midtones.",
    "B&W: Hard Noir": "Hard-contrast black & white; film noir.",
    "B&W: Sepia": "Brown sepia, like an old photograph.",
    "Splash: Red Accent": "Keeps only red/orange; everything else black & white.",
    "Splash: Golden Yellow": "Keeps only yellow.",
    "Splash: Neon Blue": "Keeps only blue.",
    "Splash: Subject in Colour": "People stay in colour, the background goes grey (people detection, ~15 MB download on first use).",
    "Repair: Web JPEG": "Repairs lightly compressed JPEGs: fewer blocks, less edge speckle.",
    "Repair: Heavy Compression": "Repairs heavily compressed images. Softens the picture.",
}
