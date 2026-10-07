"""Lift / gamma / gain as real colour wheels.

Plain HTML; javascript/dm_wheels.js does the dragging. The wheels drive the
hue and amount sliders (hidden, still the source of truth for presets, PNG
info and X/Y/Z): angle = hue, distance from the centre = amount. The level
sliders stay visible under the wheels.
"""

WHEELS = [("lift", "Lift", "shadows"), ("gamma", "Gamma", "midtones"), ("gain", "Gain", "highlights")]
RAW = {f"{w}_{k}" for w, _, _ in WHEELS for k in ("hue", "amt")}


def wheels_html(tab):
    cells = "".join(
        f'<div class="dm-wheel" data-w="{w}">'
        f'<div class="dm-wheel-disc" title="Drag to tint {sub}; double-click to clear">'
        f'<span class="dm-wheel-cross"></span><span class="dm-wheel-puck"></span></div>'
        f'<div class="dm-wheel-label">{label} <span>{sub}</span></div>'
        f'<div class="dm-wheel-val">0.00 · 0.00</div></div>'
        for w, label, sub in WHEELS)
    return f'<div class="dm-wheels" data-tab="{tab}">{cells}</div>'
