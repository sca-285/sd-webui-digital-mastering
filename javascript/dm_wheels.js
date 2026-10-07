// Digital Mastering: lift / gamma / gain colour wheels. Angle = hue (red at
// the top, clockwise through yellow, green, cyan, blue, magenta), distance
// from the centre = amount. They write into the hidden hue / amount sliders.
(function () {
    function app() {
        return typeof gradioApp === "function" ? gradioApp() : document;
    }

    function inputs(w, k, tab) {
        const box = app().querySelector("#dm_" + w + "_" + k + "_" + tab);
        return box ? [box.querySelector("input[type=range]"), box.querySelector("input[type=number]")] : [];
    }

    function read(w, k, tab) {
        const [range, num] = inputs(w, k, tab);
        const v = parseFloat((num || range || {}).value);
        return isNaN(v) ? 0 : v;
    }

    function write(w, k, tab, v) {
        const [range, num] = inputs(w, k, tab);
        v = Math.round(v * 100) / 100;
        for (const el of [num, range]) {
            if (!el || parseFloat(el.value) === v) continue;
            el.value = v;
            if (typeof updateInput === "function") updateInput(el);
            else el.dispatchEvent(new Event("input", {bubbles: true}));
        }
    }

    function draw(cell, hue, amt) {
        const disc = cell.querySelector(".dm-wheel-disc");
        const puck = cell.querySelector(".dm-wheel-puck");
        const r = disc.clientWidth / 2;
        const a = hue * 2 * Math.PI;
        const d = Math.min(Math.max(amt, 0), 1) * (r - 6);
        puck.style.left = (r + Math.sin(a) * d) + "px";
        puck.style.top = (r - Math.cos(a) * d) + "px";
        puck.style.background = amt > 0.005 ? "hsl(" + Math.round(hue * 360) + ",90%,55%)" : "#ddd";
        cell.querySelector(".dm-wheel-val").textContent = hue.toFixed(2) + " · " + amt.toFixed(2);
    }

    function sync() {
        app().querySelectorAll(".dm-wheels").forEach((box) => {
            if (!box.offsetParent || box.dataset.dragging) return;   // hidden tab, or being dragged
            const tab = box.dataset.tab;
            box.querySelectorAll(".dm-wheel").forEach((cell) => {
                const w = cell.dataset.w;
                draw(cell, read(w, "hue", tab), read(w, "amt", tab));
            });
        });
    }

    function at(cell, e) {
        const disc = cell.querySelector(".dm-wheel-disc").getBoundingClientRect();
        const r = disc.width / 2;
        const x = e.clientX - disc.left - r, y = e.clientY - disc.top - r;
        let hue = Math.atan2(x, -y) / (2 * Math.PI);
        if (hue < 0) hue += 1;
        const amt = Math.min(Math.hypot(x, y) / (r - 6), 1);
        // At the very centre the angle means nothing: keep the colour, clear the amount.
        if (amt < 0.03) return [read(cell.dataset.w, "hue", cell.closest(".dm-wheels").dataset.tab), 0];
        return [hue, amt];
    }

    function apply(box, cell, hue, amt) {
        const tab = box.dataset.tab, w = cell.dataset.w;
        draw(cell, hue, amt);
        write(w, "hue", tab, hue);
        write(w, "amt", tab, amt);
    }

    document.addEventListener("pointerdown", function (e) {
        const t = e.composedPath ? e.composedPath()[0] : e.target;
        if (!(t instanceof Element)) return;
        const disc = t.closest(".dm-wheel-disc");
        if (!disc) return;
        const cell = disc.closest(".dm-wheel"), box = cell.closest(".dm-wheels");
        e.preventDefault();
        box.dataset.dragging = "1";
        disc.setPointerCapture(e.pointerId);
        apply(box, cell, ...at(cell, e));
        const move = (ev) => apply(box, cell, ...at(cell, ev));
        const up = () => {
            delete box.dataset.dragging;
            disc.removeEventListener("pointermove", move);
            disc.removeEventListener("pointerup", up);
            disc.removeEventListener("pointercancel", up);
        };
        disc.addEventListener("pointermove", move);
        disc.addEventListener("pointerup", up);
        disc.addEventListener("pointercancel", up);
    });

    document.addEventListener("dblclick", function (e) {
        const t = e.composedPath ? e.composedPath()[0] : e.target;
        if (!(t instanceof Element)) return;
        const disc = t.closest(".dm-wheel-disc");
        if (!disc) return;
        const cell = disc.closest(".dm-wheel"), box = cell.closest(".dm-wheels");
        apply(box, cell, read(cell.dataset.w, "hue", box.dataset.tab), 0);
    });

    // Presets, Reset and PNG-info paste change the sliders from Python: follow them.
    setInterval(sync, 250);
})();
