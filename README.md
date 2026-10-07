# Stable Diffusion Extension - Digital Mastering Suite

Post-processing grade applied to every generated image, after the inpaint
composite. Works on Forge, reForge and Forge Classic (Neo). 58 look presets in eight groups,
each with an icon and a one-line description. Grade only: camera traits such as vignette
and grain are in Optical Realism (see below).

![Preset reference](preset_reference.jpg)

## Layout

```
[x] Digital Mastering
    [All] [Natural] [Portrait] [Film] [Cinema] [Auteur] [Mood] [B&W] [Splash]
    ‹ [icon] [icon] [icon] [icon] [icon] ... ›     <- preset carousel
    description of the picked preset    [Reset]
    [▦ Preset reference]           <- click to unfold the picture above
    Intensity  ------o---          <- how much of the whole grade, 0 = original
    > Quick start                  <- (closed)
    [ Color | Detail & Finish | Effects | HSL & Wheels | Local | Overlay | Output | Tools ]
      > Guide                      <- guide for this tab (closed)
      Section title
        [x] Enable ...
        every control, nothing hidden
```

| Tab | Sections |
|---|---|
| Color | Enable Color · Light (exposure, contrast, dehaze) · Tone curve · White balance · Colour (saturation, vibrance) · Split toning · Black & white (amount, colour filter) · CDL |
| Detail & Finish | Enable Detail & Finish · Detail (clarity, clarity radius, sharpen, skin smoothing) · Finish (anti-banding) |
| Effects | Selective colour · LUT (picker + Refresh, opacity, extra folder) |
| HSL & Wheels | Enable HSL · hue, saturation, lightness for red, orange, yellow, green, aqua, blue, purple, magenta · Enable Color wheels · lift, gamma, gain (colour, amount, level) |
| Local | Enable Local · Graduated filter (exposure, direction, reach, softness, colour) · Radial filter (inside, outside, centre on people, position, size, softness) · People / Background light |
| Overlay | Enable Overlay · Layer 1 and Layer 2 (file + Refresh, blend, opacity, colour shift, zoom, fit) · Both layers (vary with seed, turn to match orientation, extra folder) |
| Output | Frame: Enable Frame · Letterbox (1.85, 2, 2.39, 2.76:1) · Border (none, white, black, cream, Polaroid). Export: Enable Export · Crop (aspect, keep people in, centre) · Size (long edge, output sharpening) · Subtitle (text, colour, size) · Watermark (text, position, opacity, size, font file) |
| Tools | Protect people · Exposure check |

Each section has an **Enable** box (Color, Detail & Finish, Selective Color,
HSL, Color wheels, LUT, Local, Overlay, Frame, Export); an unticked section is ignored whatever its sliders say.
A preset ticks the sections it uses (their other controls at neutral) and
unticks the rest, Local light included; it never touches Intensity, the LUT, the overlays or the Output tab (frame and export), so you can set
Intensity once and flick through presets. The colour sliders show a colour
wheel on their track.

**Picking a preset**: a carousel of small icons, one per preset, each the preset on a sample picture with a short word mark and its group. The chips above it filter by group, the arrows (or a sideways scroll) move along, a click applies the preset. Hover a card for its description.

**Preset reference** unfolds a picture of every preset on three sample photos
(portrait, still life, night scene). Scroll inside the box, or click the
picture to open it full size in a new tab. Click the button again to fold it.

## Auto Color Corrector, Optical Realism and Digital Mastering

Three extensions split the work the way a photo is made, and run in this
order:

| 1. [Auto Color Corrector](https://github.com/sca-285/sd-forge-auto-color-corrector) | 2. [Optical Realism](https://github.com/sca-285/sd-forge-optical-realism) | 3. [Digital Mastering](https://github.com/sca-285/sd-webui-digital-mastering) |
|---|---|---|
| **Correction**, automatic: measures the image and fixes only what is off (colour cast, black and white points, exposure, flat or harsh contrast, dull colour, JPEG blocks, noise, a tilted horizon), or matches a reference picture | **The camera**: lens geometry, vignette, purple fringing, depth of field and bokeh, tilt-shift, blur, bloom, flare, anamorphic streak, star filter, god rays, halation, light wrap, flash, haze, grain, dust, scratches, date stamp, highlight roll-off, retro video | **The grade**, by hand or by preset: exposure, contrast, white balance, saturation, vibrance, split toning, CDL, LUT, selective colour, clarity, sharpen, overlays, HSL, colour wheels, tone curves, black & white, dehaze, skin smoothing, local light, subtitles, anti-banding |

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
any grade. Most use Local light; add a letterbox under Output if you want the bars. Pair them with an Optical
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

The classic stocks: *Kodachrome* (deep reds and blues, dense shadows),
*Velvia* (saturated landscape slide film, greens and skies pushed), *Cool Slide
Stock*, *Faded Vintage* (a matte fade curve), *Bleach Bypass*, *Cross Process*
(the cross-process curve) and *Instant Photo*. *B&W: Infrared* turns foliage
white and skies black through the infrared filter; *Natural: Crisp Clear*
takes haze out with dehaze before a light polish.

## HSL, colour wheels, black & white

- **HSL**: hue (up to 30°), saturation and lightness for eight colours, split
  smoothly between neighbouring bands; greys are never touched. The Film presets
  use it for their olive greens and warm skin.
- **Colour wheels**: lift, gamma and gain, each with a colour push and a level,
  the primary grade of a grading panel. Split toning cannot tint the midtones;
  the gamma wheel can.
- **Black & white**: monochrome through a filter as on B&W film (neutral, red,
  orange, yellow, green, blue, infrared). The B&W presets use it: yellow for
  Classic Silver, red for Hard Noir.
- **Dehaze** (dark-channel method), **tone curves** (Film S, Soft S, Strong S,
  Matte fade, Crushed blacks, Bright mids, Low contrast, Cross process) and
  **skin smoothing** (frequency separation on detected skin, edges kept) round
  it out. JPEG repair moved to Auto Color Corrector, which finds and fixes it by
  itself; older PNG info with it still pastes.

## Order

dehaze -> exposure/WB (linear light) -> CDL -> colour wheels -> contrast -> tone
curve -> saturation -> HSL -> black & white -> split toning -> local light -> LUT
-> selective colour -> skin smoothing -> clarity -> sharpen -> overlay layers ->
Intensity -> crop -> resize -> output sharpening -> dither -> letterbox ->
subtitle -> watermark -> border. Overlays go on after sharpening, so their specks are never
sharpened. The size-changing output steps follow Intensity, which blends with
the original at its own size. Dither is the last pixel step so that nothing
amplifies it; letterbox, subtitle, watermark and border are drawn on top.

## X/Y/Z plot

Axes for the X/Y/Z plot script, under `[DM]`: Preset, Intensity, LUT, Overlay
layer 1, Overlay 1 opacity, Exposure, Contrast, Saturation, Temperature, Tone
curve, B&W filter, Black & white, Dehaze. A cell
that sets any of them switches the suite on for that cell, so it can stay off
in the panel; a Preset axis is applied first, the way the picker applies it,
then the other axes on top. Pair a `[DM] Preset` axis with Optical Realism's
`[OR] Preset` to compare looks side by side.

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
lib_dm/presets.py              the 58 looks, each listing only what it changes
lib_dm/layout.py               tabs, sections and guide texts
lib_dm/pipeline.py             the chain, in order, skipping inactive stages
lib_dm/ops.py                  the image operations, pure torch
lib_dm/grade.py                HSL, colour wheels, black & white, dehaze, tone curves, skin smoothing
lib_dm/lut.py                  .cube discovery and parsing
lib_dm/overlay.py              overlay discovery, loading and fitting
lib_dm/output.py               crop, resize, output sharpening, border, watermark
lib_dm/xyz.py                  X/Y/Z plot axes
lib_dm/segment.py              SegFormer-B0 person mask
lib_dm/reference.py            the folded preset reference
lib_dm/carousel.py             the preset carousel (HTML)
javascript/dm_carousel.js      the preset carousel (clicks, filter, scroll)
preset_icons/                  the preset icons, one picture per preset
preset_reference.jpg           the preset reference picture
overlays/                      the shipped overlay textures
overlay_reference.jpg          every shipped overlay on the sample photos
style.css                      colour-wheel sliders, section titles, reference box, preset carousel
```

## Credits

Overlays: *Bokeh - Lavender*, *Bokeh - Pastel*, *Film Dirt - Hairs & Lines*,
*Light Leak - Fire*, *Light Leak - Yellow*, *Prism Flare*, *Scratches - Cracked*
and *Sparkle Dust - Orange* are the author's own; the other six were
generated in code for this extension.

Sample photos in `preset_reference.jpg` and `overlay_reference.jpg`, from scikit-image's sample data:
Eileen Collins by NASA (public domain), coffee cup by Rachel Michetti (CC0),
Falcon 9 launch by SpaceX (public domain).

Preset icons (`preset_icons/`): photos from the Open Images dataset, by Flickr
photographers under CC BY 2.0 (each author and source listed in
`preset_icons/CREDITS.md`), cropped, with the preset applied and lettering in
Bebas Neue (SIL Open Font License 1.1; only the rendered pictures are shipped).

Thanks also to **Claude**, for help building this
extension.

## License

MIT, see `LICENSE`.
