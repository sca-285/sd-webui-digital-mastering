# Stable Diffusion Extension - Digital Mastering Suite

Post-processing grade applied to every generated image, after the inpaint
composite. Works on Forge, reForge and Forge Classic (Neo). 56 look presets,
each with a one-line description. Grade only: camera traits such as vignette
and grain are in Optical Realism (see below).

![Preset reference](preset_reference.jpg)

## Layout

```
[x] Digital Mastering
    Look preset [..........v]  [Reset]
    one-line description of the preset
    [▦ Preset reference]           <- click to unfold the picture above
    Intensity  ------o---          <- how much of the whole grade, 0 = original
    > Quick start                  <- (closed)
    [ Color | Detail & Finish | Effects | Local | Overlay | Output | Repair & Tools ]
      > Guide                      <- guide for this tab (closed)
      Section title
        [x] Enable ...
        every control, nothing hidden
```

| Tab | Sections |
|---|---|
| Color | Enable Color · Light (exposure, contrast) · White balance · Colour (saturation, vibrance) · Split toning · CDL |
| Detail & Finish | Enable Detail & Finish · Detail (clarity, clarity radius, sharpen) · Finish (anti-banding) |
| Effects | Selective colour · LUT (picker + Refresh, opacity, extra folder) |
| Local | Enable Local · Graduated filter (exposure, direction, reach, softness, colour) · Radial filter (inside, outside, centre on people, position, size, softness) · People / Background light |
| Overlay | Enable Overlay · Layer 1 and Layer 2 (file + Refresh, blend, opacity, colour shift, zoom, fit) · Both layers (vary with seed, turn to match orientation, extra folder) |
| Output | Frame: Enable Frame · Letterbox (1.85, 2, 2.39, 2.76:1) · Border (none, white, black, cream, Polaroid). Export: Enable Export · Crop (aspect, keep people in, centre) · Size (long edge, output sharpening) · Watermark (text, position, opacity, size, font file) |
| Repair & Tools | Restoration · Protect people · Exposure check |

Each section has an **Enable** box (Color, Detail & Finish, Selective Color,
LUT, Local, Overlay, Frame, Export, Restoration); an unticked section is ignored whatever its sliders say.
A preset ticks the sections it uses (their other controls at neutral) and
unticks the rest, Local light and Frame (letterbox, border) included; it never touches Intensity, the LUT, the overlays or Export (crop, size, watermark), so you can set
Intensity once and flick through presets. The colour sliders show a colour
wheel on their track.

**Preset reference** unfolds a picture of every preset on three sample photos
(portrait, still life, night scene). Scroll inside the box, or click the
picture to open it full size in a new tab. Click the button again to fold it.

## Auto Color Corrector, Optical Realism and Digital Mastering

Three extensions split the work the way a photo is made, and run in this
order:

| 1. [Auto Color Corrector](https://github.com/sca-285/sd-forge-auto-color-corrector) | 2. [Optical Realism](https://github.com/sca-285/sd-forge-optical-realism) | 3. [Digital Mastering](https://github.com/sca-285/sd-webui-digital-mastering) |
|---|---|---|
| **Correction**, automatic: measures the image and fixes only what is off (colour cast, black and white points, exposure, flat or harsh contrast, dull colour), or matches a reference picture | **The camera**: lens geometry, vignette, depth of field, blur, bloom, flare, halation, light wrap, flash, haze, grain, dust, scratches, date stamp, highlight roll-off | **The grade**, by hand or by preset: exposure, contrast, white balance, saturation, vibrance, split toning, CDL, LUT, selective colour, clarity, sharpen, overlays, anti-banding, JPEG repair |

No two of them do the same job. Auto Color Corrector and Digital Mastering
both touch exposure and white balance, but for opposite ends: the corrector
brings a faulty picture back to neutral by itself and leaves a sound one
alone; Digital Mastering moves a picture away from neutral, on purpose, by
the amount you set. Correct first, then shoot, then grade.

Optical Realism and Digital Mastering presets each cover only their own
side, so a look is one preset from each. Pairs that go together:

| Optical Realism | Digital Mastering |
|---|---|
| Subtle Real Camera | Natural: Clean Polish |
| Portrait 85mm f/1.8 | Portrait: Studio Skin |
| Portrait f/1.2 Dreamy | Portrait: Soft Glamour |
| Street 35mm f/5.6 | Natural: Vivid Pop or Film: Cool Slide Stock |
| Macro Close-up | Natural: HDR Detail |
| Vintage Lens | Film: Faded Vintage or Film: Instant Photo |
| Film Camera 35mm | Film: Portra Golden or Film: Olive Signature |
| Heavy Film Grain | B&W: Classic Silver or B&W: Hard Noir |
| Pro-Mist Cinema | Cinema: Teal & Orange |
| Anamorphic Flare | Cinema: Blockbuster |
| Night City Glow | Mood: Cyberpunk Neon or Film: Red Neon Night |
| Landscape Aerial Haze | Mood: Golden Hour |
| Foggy Morning | Natural: Soft Matte or Mood: Blue Hour |
| Backlit Rim Light | Mood: Golden Hour |
| Dusty Night Film | Cinema: Dusty Night or Cinema: Moody Dark |
| Digital Flash | Mood: Flash Snapshot |

## Auteur presets

Twelve looks after how certain films and edits read: *Chungking Neon*, *Mood for
Love*, *Fallen Angels*, *2046* and *Happy Together* after Wong Kar-wai's films
(Christopher Doyle's photography), plus *Hong Kong 90s*, *Saigon Rain*, *Matte
Street*, *Golden Anamorphic*, *Sickly Thriller*, *Nordic Noir* and *Pastel
Symmetry*. They are homages built from this suite's own controls, not copies of
any grade. Most use Local light and a letterbox; pair them with an Optical
Realism preset for grain, halation and glow (e.g. *Night City Glow* with
*Chungking Neon*, *Film Camera 35mm* with *Mood for Love*).

## Film presets

*Portra Golden*, *Olive Signature*, *Tungsten Amber*, *Emerald*, *Travel Ektar*
and *Red Neon Night* follow the colour of contemporary editorial film photography,
measured rather than guessed: olive-to-amber shadows instead of the usual teal,
cream highlights, whites held a little below clipping, blacks just lifted.
*Lavender Dusk* covers the pink-sky evenings of the same style. Pair them with
Optical Realism's *Film Camera 35mm* or *Heavy Film Grain* for the grain and
halation that finish the look.

## Order

restoration -> exposure/WB (linear light) -> CDL -> contrast -> saturation ->
split toning -> local light -> LUT -> selective colour -> clarity -> sharpen ->
overlay layers -> Intensity -> crop -> resize -> output sharpening -> dither ->
letterbox -> watermark -> border. Overlays go on after sharpening, so their specks are never
sharpened. The size-changing output steps follow Intensity, which blends with
the original at its own size. Dither is the last pixel step so that nothing
amplifies it; letterbox, watermark and border are drawn on top.

## PNG info

One entry, only the non-default values:

    Digital Mastering: "temperature=0.35; contrast=0.1; highlight_tint=0.4"

Send-to / paste restores all of it. The older `Restore(...) | CDL(...)` format
still pastes. `vignette`, `grain` and `grain_size` from images made before
they moved to Optical Realism are ignored.

## Notes

- Exposure and white balance work in linear light. Clarity and sharpen work on
  luminance only, so they cannot fringe colour edges; clarity is weighted to
  the midtones so it does not halo clipped areas.
- Dither is seeded from the image's seed: the same seed gives the same result.
- **Protect people** uses SegFormer-B0 (about 15 MB, downloaded on first use).
  The model is parked on the CPU between jobs.
- **Overlays**: 14 ship in `overlays/` (see `overlay_reference.jpg`, also
  folded in the Overlay tab). Add your own PNG / WebP / JPEG to
  `models/overlays` or name another folder, then press **Refresh**; a file
  with the same name as a shipped one replaces it. Blend *Auto* uses Normal for
  transparent PNGs and Screen for opaque textures (light on black). **Vary
  with seed** flips and shifts the layers per image, reproducibly. A missing
  overlay is skipped with a message and the rest of the grade still applies.
- LUTs: put `.cube` files in `models/LUTs`, or name another folder. LUTs with a
  non-0..1 `DOMAIN_MIN/MAX` are refused with a message; a missing LUT is
  skipped and the rest of the grade still applies.

## Files

```
scripts/digital_mastering.py   UI + host hooks, built from the control table
lib_dm/controls.py             every control, declared once (UI, presets, PNG info)
lib_dm/presets.py              the 56 looks, each listing only what it changes
lib_dm/layout.py               tabs, sections and guide texts
lib_dm/pipeline.py             the chain, in order, skipping inactive stages
lib_dm/ops.py                  the image operations, pure torch
lib_dm/lut.py                  .cube discovery and parsing
lib_dm/overlay.py              overlay discovery, loading and fitting
lib_dm/output.py               crop, resize, output sharpening, border, watermark
lib_dm/segment.py              SegFormer-B0 person mask
lib_dm/reference.py            the folded preset reference
preset_reference.jpg           the preset reference picture
overlays/                      the shipped overlay textures
overlay_reference.jpg          every shipped overlay on the sample photos
style.css                      colour-wheel sliders, section titles, reference box
```

## Credits

Overlays: *Bokeh - Lavender*, *Bokeh - Pastel*, *Film Dirt - Hairs & Lines*,
*Light Leak - Fire*, *Light Leak - Yellow*, *Prism Flare*, *Scratches - Cracked*
and *Sparkle Dust - Orange* are the author's own; the other six were
generated in code for this extension.

Sample photos in `preset_reference.jpg` and `overlay_reference.jpg`, from scikit-image's sample data:
Eileen Collins by NASA (public domain), coffee cup by Rachel Michetti (CC0),
Falcon 9 launch by SpaceX (public domain).

Thanks also to **Claude**, for help building this
extension.

## License

MIT, see `LICENSE`.
