"""Digital Mastering Suite - UI and host hooks. The work is in lib_dm/."""

import os
import sys
import traceback
import zlib

import gradio as gr
from modules import devices, script_callbacks, scripts, shared
from modules.ui_components import InputAccordion

EXTENSION_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if EXTENSION_ROOT not in sys.path:
    sys.path.insert(0, EXTENSION_ROOT)

from lib_dm import lut, overlay, segment, xyz  # noqa: E402
from lib_dm.controls import (  # noqa: E402
    BY_NAME, GROUP_OF, INFOTEXT_KEY, LOCAL_ONLY, NAMES, coerce, from_infotext, settings, to_infotext,
)
from lib_dm.layout import HUE_SLIDERS, QUICK_START, TABS as LAYOUT  # noqa: E402
from lib_dm.wheels import RAW as WHEEL_RAW, WHEELS, wheels_html  # noqa: E402
from lib_dm.pipeline import is_noop, master  # noqa: E402
from lib_dm.carousel import carousel_html, parse_pick  # noqa: E402
from lib_dm.presets import CATEGORIES, DESCRIPTIONS, NOT_IN_PRESETS, PRESETS  # noqa: E402
from lib_dm.reference import reference_html  # noqa: E402


def lut_folders(extra=""):
    return [os.path.join(shared.models_path, "LUTs"), extra]


def lut_choices(extra=""):
    return ["None", *lut.find_luts(*lut_folders(extra))]


def overlay_folders(extra=""):
    # Shipped set first; a file of the same name in models/overlays wins.
    return [os.path.join(EXTENSION_ROOT, "overlays"), os.path.join(shared.models_path, "overlays"), extra]


def overlay_choices(extra=""):
    return ["None", *overlay.find_overlays(*overlay_folders(extra))]


XYZ_ATTR = "_dm_xyz"


def _register_xyz():
    xyz.register("DM", XYZ_ATTR, [
        ("Preset", str, "preset", lambda: list(PRESETS)),
        ("Intensity", float, "strength", None),
        ("LUT", str, "lut", lambda: lut_choices()),
        ("Overlay layer 1", str, "overlay_1", lambda: overlay_choices()),
        ("Overlay 1 opacity", float, "ov1_opacity", None),
        ("Exposure", float, "exposure", None),
        ("Contrast", float, "contrast", None),
        ("Saturation", float, "saturation", None),
        ("Temperature", float, "temperature", None),
        ("Tone curve", str, "curve", lambda: list(BY_NAME["curve"].choices)),
        ("B&W filter", str, "bw_filter", lambda: list(BY_NAME["bw_filter"].choices)),
        ("Black & white", float, "bw", None),
        ("Dehaze", float, "dehaze", None),
    ])


# Once the scripts are loaded, before the UI is built: the X/Y/Z plot reads its
# axis list when it builds its own panel.
script_callbacks.on_before_ui(_register_xyz)


def _image_seed(p, image):
    """The seed of the image being processed, so grain and dither repeat.

    The hook is not told which image of the batch it has; the host appends each
    one to p.pixels_after_sampling just before calling it, so its length says.
    Falls back to a hash of the pixels, which is at least stable per image.
    """
    try:
        i = len(p.pixels_after_sampling) - 1
        if 0 <= i < len(p.seeds):
            return int(p.seeds[i])
    except Exception:
        pass
    return zlib.crc32(image.resize((32, 32)).tobytes())


class Script(scripts.Script):
    # Where the accordion sits among the other extensions' panels.
    sorting_priority = 160

    def title(self):
        return "Digital Mastering Suite"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        tab = "img2img" if is_img2img else "txt2img"
        comps = {}

        def add(name):
            comps[name] = self._component(BY_NAME[name], tab)

        def add_all(names):
            # One control per line: side by side, the info texts overlapped.
            for n in names:
                add(n)

        # Explicit elem_ids everywhere: InputAccordion's fallback id comes off a
        # global counter, so any other extension being added or removed would
        # silently rebind the saved ui-config.json defaults.
        with InputAccordion(False, label="Digital Mastering",
                            elem_id=f"dm_enabled_{tab}") as enabled:
            gr.HTML(carousel_html(EXTENSION_ROOT, "dm", tab, list(PRESETS), CATEGORIES, DESCRIPTIONS,
                                  display=lambda n: n.split(": ", 1)[-1]),
                    elem_id=f"dm_preset_car_{tab}")
            pick = gr.Textbox(value="", show_label=False, container=False, elem_id=f"dm_preset_pick_{tab}",
                              elem_classes=["dm-pick"])
            with gr.Row(equal_height=True):
                about = gr.Markdown("*Pick a look above, or Reset to start clean.*",
                                    elem_id=f"dm_preset_about_{tab}")
                reset = gr.Button("Reset", scale=0, min_width=100, elem_id=f"dm_reset_{tab}")
            gr.HTML(reference_html(EXTENSION_ROOT, "dm-ref", "Digital Mastering look presets"),
                    elem_id=f"dm_preset_ref_{tab}")
            add("strength")
            gr.Markdown(QUICK_START.strip(), elem_id=f"dm_help_{tab}", elem_classes=["dm-guide"])

            ov_refresh = []
            with gr.Tabs():
                for t in LAYOUT:
                    with gr.Tab(t["title"]):
                        gr.Markdown(t["guide"].strip(), elem_classes=["dm-guide"])
                        if t.get("reference"):
                            gr.HTML(reference_html(EXTENSION_ROOT, "dm-ref", "The shipped overlays",
                                                   file=t["reference"], label="Overlay reference"))
                        for title, names in t["sections"]:
                            if title:
                                gr.Markdown(f"**{title}**", elem_classes=["dm-section"])
                            if "lut" in names:
                                # LUT picker and its Refresh button on one line.
                                add("en_lut")
                                with gr.Row():
                                    add("lut")
                                    refresh = gr.Button("Refresh", size="sm", scale=0, min_width=90,
                                                        elem_id=f"dm_lut_refresh_{tab}")
                                add_all([n for n in names if n not in ("en_lut", "lut")])
                            elif names and names[0] == "en_wheels":
                                # Round wheels drive the hidden hue / amount sliders;
                                # the level sliders sit under them.
                                add("en_wheels")
                                gr.HTML(wheels_html(tab), elem_id=f"dm_wheels_{tab}")
                                with gr.Row():
                                    for w, _, _ in WHEELS:
                                        add(f"{w}_lum")
                                add_all([n for n in names if n in WHEEL_RAW])
                            elif names and names[0].startswith("overlay_") and names[0] != "overlay_dir":
                                with gr.Row():
                                    add(names[0])
                                    ov_refresh.append(gr.Button("Refresh", size="sm", scale=0, min_width=90,
                                                                elem_id=f"dm_{names[0]}_refresh_{tab}"))
                                add_all(names[1:])
                            else:
                                add_all(names)

        outputs = [comps[n] for n in NAMES]

        def refresh_luts(folder, current):
            choices = lut_choices(folder)
            return gr.update(choices=choices, value=current if current in choices else "None")

        refresh.click(refresh_luts, [comps["lut_dir"], comps["lut"]], [comps["lut"]])
        # blur, not change: change fires on every keystroke and rescans the disk.
        comps["lut_dir"].blur(refresh_luts, [comps["lut_dir"], comps["lut"]], [comps["lut"]])

        def refresh_overlays(folder, *current):
            choices = overlay_choices(folder)
            return [gr.update(choices=choices, value=c if c in choices else "None") for c in current]

        ov_inputs = [comps["overlay_dir"], comps["overlay_1"], comps["overlay_2"]]
        ov_outputs = [comps["overlay_1"], comps["overlay_2"]]
        for btn in ov_refresh:
            btn.click(refresh_overlays, ov_inputs, ov_outputs)
        comps["overlay_dir"].blur(refresh_overlays, ov_inputs, ov_outputs)

        def values_for(s):
            return [gr.update() if n in NOT_IN_PRESETS else gr.update(value=s[n]) for n in NAMES]

        def apply_preset(value):
            name = parse_pick(value)
            s = PRESETS.get(name)
            if not s:
                return [gr.update() for _ in range(len(NAMES) + 1)]
            return [gr.update(value=f"**{name}** · *{DESCRIPTIONS.get(name, '')}*")] + values_for(s)

        pick.change(apply_preset, [pick], [about] + outputs)
        reset.click(lambda: [gr.update(value=""), gr.update(value="*Everything back to neutral.*")]
                    + [gr.update(value=v) for v in settings().values()],
                    [], [pick, about] + outputs)

        # PNG info -> controls. Everything comes out of the one "Digital
        # Mastering" entry; an image without it switches the suite off and
        # leaves the controls as they are.
        def field(name):
            def get(params):
                s = from_infotext(params.get(INFOTEXT_KEY, ""))
                return None if s is None else s[name]
            return get

        self.infotext_fields = [(enabled, lambda d: INFOTEXT_KEY in d)]
        self.infotext_fields += [(comps[n], field(n)) for n in NAMES if n not in LOCAL_ONLY]
        self.paste_field_names = [INFOTEXT_KEY]

        return [enabled, *outputs]

    @staticmethod
    def _component(c, tab):
        eid = f"dm_{c.name}_{tab}"
        info = c.info or None
        if c.kind == "checkbox":
            return gr.Checkbox(label=c.label, value=c.default, elem_id=eid, info=info)
        if c.kind == "text":
            hint = {"overlay_dir": "e.g. D:\\Overlays  (models/overlays is always searched)",
                    "lut_dir": "e.g. D:\\LUTs  (models/LUTs is always searched)",
                    "wm_text": "e.g. @yourname",
                    "sub_text": "e.g. I've been waiting for you.",
                    "wm_font": "optional, e.g. C:\\Windows\\Fonts\\arialbd.ttf"}.get(c.name, "")
            return gr.Textbox(label=c.label, value=c.default, elem_id=eid, placeholder=hint)
        if c.kind == "lut":
            return gr.Dropdown(label=c.label, choices=lut_choices(), value="None", elem_id=eid)
        if c.kind == "overlay":
            return gr.Dropdown(label=c.label, choices=overlay_choices(), value="None", elem_id=eid)
        if c.kind == "choice":
            return gr.Dropdown(label=c.label, choices=list(c.choices), value=c.default, elem_id=eid, info=info)
        classes = (["dm-hue"] if c.name in HUE_SLIDERS else []) + (["dm-wheel-raw"] if c.name in WHEEL_RAW else [])
        classes = classes or None
        return gr.Slider(label=c.label, minimum=c.minimum, maximum=c.maximum, step=c.step,
                         value=c.default, elem_id=eid, info=info, elem_classes=classes)

    # After the composite, so an "only masked" inpaint is graded as a whole
    # image instead of leaving a seam at the crop edge.
    def postprocess_image_after_composite(self, p, pp, enabled, *values):
        axis = xyz.overrides(p, XYZ_ATTR)
        if not (enabled or axis) or pp.image is None:
            return
        s = settings(dict(zip(NAMES, values)))
        if axis:
            s = xyz.merged(s, axis, coerce, BY_NAME, GROUP_OF, PRESETS, NOT_IN_PRESETS)
        if is_noop(s) and not s["false_color"]:
            return

        try:
            device = devices.device
            volume = None
            if s["en_lut"] and s["lut"] not in ("", "None") and s["lut_strength"] > 0:
                path = lut.find_luts(*lut_folders(s["lut_dir"])).get(s["lut"])
                volume = lut.load_lut(path, device) if path else None
                if volume is None:
                    print(f"[Digital Mastering] LUT '{s['lut']}' not found or unusable, skipped.")
                    s["en_lut"] = False

            layers = {}
            if s["en_overlay"]:
                found = overlay.find_overlays(*overlay_folders(s["overlay_dir"]))
                for i in (1, 2):
                    name = s[f"overlay_{i}"]
                    if name in ("", "None"):
                        continue
                    loaded = overlay.load(found[name]) if name in found else None
                    if loaded is None:
                        print(f"[Digital Mastering] Overlay '{name}' not found or unreadable, layer {i} skipped.")
                    else:
                        layers[i] = loaded

            result, scope = master(
                pp.image, s, device=device, seed=_image_seed(p, pp.image), lut_volume=volume,
                mask_fn=lambda im: segment.person_mask(im, device), overlays=layers,
            )
        except Exception as exc:
            traceback.print_exc()
            print(f"[Digital Mastering] Error, image left untouched: {exc}")
            return

        pp.image = result
        if scope is not None:
            # A diagnostic rides next to the image; it never replaces it.
            p.extra_result_images.append(scope)
        # Written only after the work succeeded.
        p.extra_generation_params[INFOTEXT_KEY] = to_infotext(s)

    def postprocess(self, p, processed, *args):
        # Once per job: park the segmenter on the CPU (it is reused next job
        # instead of re-read from disk) and drop the LUT volumes.
        segment.park()
        lut.clear_cache()
        overlay.clear_cache()
        devices.torch_gc()
