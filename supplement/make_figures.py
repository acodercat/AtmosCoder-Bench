"""Generate F0–F22 from the CSVs in supplement/figure_data/.

    uv run --with matplotlib python supplement/make_figures.py            # all
    uv run --with matplotlib python supplement/make_figures.py F0 F4      # a subset

Palette: the Nature Publishing Group (ggsci `npg`) categorical set, restricted to the four
hues that survive a colour-vision check — simulating deuteranopia, protanopia and tritanopia
and measuring pairwise CIELAB separation gives a worst-case ΔE of 12.1 with an L* band of
36–71, so no pair collapses under any common CVD and none is too light for a white surface.
Sequential panels use a single-hue ramp built from the same deep blue (never red–green).

Conventions
- one claim per figure, stated in the title; effect sizes with uncertainty over raw endpoints;
- colour semantics are fixed everywhere: NAVY = reasoning, CYAN = non-reasoning,
  SAND = domain-specialised, RED = emphasis only; model order = core leaderboard order;
- every series is direct-labelled (no numbered keys); gpt-5.5 (reasoning) is marked †
  wherever tokens appear (chain-of-thought not returned, count understated);
- NO statistic is hard-coded into a title or caption — everything is computed from the CSVs
  at render time, so a data refresh can never leave a stale number in a figure.

Figures go to supplement/figures/ as PDF (vector) and PNG at 400 dpi.
"""
import csv
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle
import matplotlib.patheffects as pe

# --- Nature page geometry and type scale ---------------------------------------
# Nature accepts two column widths and nothing in between; a figure delivered at an
# intermediate width is rescaled at typesetting, which silently rescales the type with it.
# save() therefore writes a FIXED canvas (no tight bbox), so the output width is exactly
# figsize[0] and the type scale below is the type scale the reader sees.
WIDTH_1COL, WIDTH_2COL = 89 / 25.4, 183 / 25.4
FS_PANEL, FS_LABEL, FS_TICK, FS_ANNOT = 8, 7, 6.5, 6      # panel letter / axis / ticks / marks
GRID_LW = 0.4

DATA = os.path.join(os.path.dirname(__file__), "figure_data")
OUT = os.path.join(os.path.dirname(__file__), "figures")
os.makedirs(OUT, exist_ok=True)

# --- NPG (Nature) palette, CVD-validated subset -----------------------------
RED, CYAN, NAVY, TEAL = "#E64B35", "#4DBBD5", "#3C5488", "#00A087"
GREY, SAND = "#8491B4", "#B09C85"
INK, MUTED, GRID = "#20242c", "#7b8290", "#e4e7ec"
TXT = "#5b6270"   # secondary TEXT only — 6.1:1 on white (Nature asks >4.5:1); MUTED/GREY stay for graphics
RED_TXT = "#B03A26"  # RED darkened for TEXT use — RED itself is only 3.87:1 on white, RED_TXT is 6.0:1
CYAN_TXT = "#26788D"  # likewise for CYAN, which is 2.2:1 as ink; CYAN_TXT is 5.1:1
SEQ = LinearSegmentedColormap.from_list("npg_blue", ["#f7f9fb", "#c6d3e3", "#7f9cc0", NAVY])

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "Liberation Sans", "Nimbus Sans", "DejaVu Sans"],
    "font.size": 7, "axes.titlesize": 8, "axes.labelsize": 7,
    "xtick.labelsize": 6.5, "ytick.labelsize": 6.5, "legend.fontsize": 6.5,
    "axes.edgecolor": MUTED, "axes.linewidth": 0.6, "axes.labelcolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK,
    "xtick.labelcolor": INK, "ytick.labelcolor": INK,
    "xtick.major.width": 0.6, "ytick.major.width": 0.6,
    "xtick.major.size": 2.5, "ytick.major.size": 2.5,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 160, "savefig.dpi": 400,
})


def load(name):
    with open(os.path.join(DATA, name)) as fh:
        return list(csv.DictReader(fh))


def save(fig, stem):
    for ext in ("pdf", "png"):
        # no tight bbox: the canvas IS the deliverable, so width == figsize[0] exactly
        fig.savefig(os.path.join(OUT, f"{stem}.{ext}"), facecolor="white")
    plt.close(fig)
    print(f"  figures/{stem}.pdf + .png")


NOTES_PATH = os.path.join(OUT, "_captions.json")
MD_PATH = os.path.join(os.path.dirname(__file__), "FIGURES.md")
FIG_ORDER = ["F0_core_composition", "F0b_category_treemap", "F1_category_by_model", "F2_F3_protocol", "F2b_tokens_absolute", "F2c_protocol_spend", "F4_token_accuracy_frontier", "F4b_efficiency_map", "F4c_token_length_decay", "F4d_spend_profile",
             "F5_main_results", "F5_composite", "F6_1a_trap_gradient", "F6_1b_trap_family", "F6_1c_shortcut_capture",
             "F6_1d_trap_family_matrix", "F6_2_variant_robustness",
             "F6_3_prompt_sensitivity", "F7_mcq_inflation", "F8_three_axes",
             "F9_scaffolding_ablation", "F10_cross_domain", "F11_discrimination",
             "F12_echo_funnel", "F17_solvability_atlas", "F18_trap_verdicts",
             "F19_answer_space", "F20_mcq_verdict_atlas", "F21_unit_rescue", "F22_fragility_map", "F24_difficulty_category_trellis"]


def note(stem, claim, caption, data):
    """Register the figure's description; flush_notes() writes FIGURES.md after a run.
    Captions live HERE (not inside the figure) so panels stay clean, while any statistic
    in the text is still computed from the CSVs at render time."""
    import json as _json
    old = {}
    if os.path.exists(NOTES_PATH):
        old = _json.load(open(NOTES_PATH))
    old[stem] = {"claim": claim, "caption": " ".join(caption.split()), "data": data}
    _json.dump(old, open(NOTES_PATH, "w"), indent=1, ensure_ascii=False)


def flush_notes():
    import json as _json
    if not os.path.exists(NOTES_PATH):
        return
    old = _json.load(open(NOTES_PATH))
    with open(MD_PATH, "w") as fh:
        fh.write("# Figure descriptions\n\n"
                 "*Auto-generated by `make_figures.py` — edit the `note()` calls there, not this file. "
                 "Every statistic below is computed from `figure_data/` at render time, so a data refresh "
                 "regenerates both the figures and this text.*\n\n")
        for stem in FIG_ORDER:
            if stem not in old:
                continue
            e = old[stem]
            fh.write(f"## `{stem}`\n\n**Claim.** {e['claim']}\n\n"
                     f"**Caption.** {e['caption']}\n\n**Data.** {e['data']}\n\n")
    print(f"  FIGURES.md ({len(old)} entries)")


def panel(ax, letter, title=""):
    """Titles are NOT drawn; the claim lives in FIGURES.md and figures carry data only.

    Panel letters (Nature: 8 pt bold) go on genuine multi-panel figures, meaning panels the
    caption addresses separately and that carry their own axis. A marginal annotation strip
    sharing the main axis (the difficulty band above F17) is part of its panel, not a panel of
    its own, and is deliberately left unlettered."""
    del title
    if letter:
        ax.text(-0.02, 1.06, letter, transform=ax.transAxes, fontsize=FS_PANEL,
                fontweight="bold", va="bottom", ha="right")


def declutter(vals, gap):
    """Nudge label y-positions apart, preserving order — no leader lines needed."""
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    out = list(vals)
    for k in range(1, len(order)):
        i, j = order[k - 1], order[k]
        if out[j] - out[i] < gap:
            out[j] = out[i] + gap
    return out


def slope(ax, rows, key_a, key_b, labels, colors, gap, sd=None):
    """Two-column slope chart with de-cluttered right-hand labels (used where a slope
    is genuinely the right form: few series, visible movement)."""
    ys = [float(r[key_b]) for r in rows]
    placed = declutter(ys, gap)
    for r, y_lab, col in zip(rows, placed, colors):
        a, b = float(r[key_a]), float(r[key_b])
        if sd:
            ax.errorbar([0, 1], [a, b], yerr=[float(r[sd[0]]), float(r[sd[1]])], fmt="none",
                        ecolor=col, elinewidth=0.6, capsize=1.6, capthick=0.6, alpha=0.85)
        ax.plot([0, 1], [a, b], "-", color=col, lw=1.0, zorder=2)
        ax.plot([0, 1], [a, b], "o", color=col, ms=3.0, zorder=3,
                markeredgecolor="white", markeredgewidth=0.5)
        ax.annotate("", xy=(1.05, y_lab), xytext=(1.005, b), textcoords="data",
                    arrowprops=dict(arrowstyle="-", color=col, lw=0.45, alpha=0.55))
    for r, y_lab, col in zip(rows, placed, colors):
        ax.text(1.07, y_lab, labels(r), fontsize=FS_TICK, va="center", color=INK)
    ax.set_xticks([0, 1]); ax.set_xlim(-0.08, 1.06)
    ax.grid(axis="y", color=GRID, lw=GRID_LW, zorder=0)
    ax.set_axisbelow(True)


def mfmt(text):
    """True minus (U+2212) for negative value labels — apply to formatted numbers only,
    never to model names (which contain hyphens)."""
    return text.replace("-", "\u2212")


def dag(name):
    return name + " †" if name.startswith("gpt-5.5 (reasoning)") else name


# Core leaderboard order (accuracy desc), the shared row order for every model-list figure.
MODEL_ORDER = [r["model"] for r in load("F4_token_accuracy.csv")]


def ordered(rows, key="model"):
    idx = {m: i for i, m in enumerate(MODEL_ORDER)}
    return sorted(rows, key=lambda r: idx.get(r[key], 99))


# ---------------------------------------------------------------- F0b (category treemap)
def _columns(vals, W, H, k):
    """Full-height columns of stacked cells: every vertical edge runs the whole height, so the
    layout has no T-junctions on the vertical axis at all.

    A squarified treemap packs better but its strips do not share boundaries, and a row-based
    mosaic puts a different set of vertical splits in every row; with ten cells that is half a
    dozen T-junctions in a small area, which is what makes a generated treemap look accidental
    next to a hand-composed one. Constraining the split to full-height columns costs some aspect
    quality and buys an unbroken vertical rhythm. Areas stay exactly proportional to the values.
    """
    total = sum(vals)
    target = total / k
    cols, cur, acc = [], [], 0.0
    for v in vals:                                   # vals arrive largest-first
        if cur and abs(acc + v - target) > abs(acc - target) and len(cols) < k - 1:
            cols.append(cur); cur, acc = [], 0.0
        cur.append(v); acc += v
    cols.append(cur)
    place, x = [None] * len(vals), 0.0            # output order == input order
    idx = 0
    for col in cols:
        cw = W * sum(col) / total
        y = 0.0
        for v in col:
            ch = H * v / sum(col)
            place[idx] = (x, y, cw, ch)
            idx += 1
            y += ch
        x += cw
    return place


TAB_R = 2.3                           # one tab per shared edge, as in a hand-cut puzzle:
                                      # repeating tabs along a long edge turns a two-piece
                                      # join into a zip and reads as several separate links


def _jigsaw(tile, tabs):
    """Rectangle path carrying interlocking tabs.

    `tabs[edge]` is a list of (position along the edge, +1 accept / -1 protrude). Tabs are laid
    out at a fixed pitch rather than one per edge, so a long edge carries several and a short
    edge one: constant tab DENSITY is what reads as a puzzle, whereas one tab per edge makes a
    tall cell look like a plain rectangle next to a small one that looks like a piece."""
    import numpy as np
    x, y, w, h = tile
    corners = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    pts = []
    for e in range(4):
        p0, p1 = corners[e], corners[(e + 1) % 4]
        ex, ey = p1[0] - p0[0], p1[1] - p0[1]
        L = (ex * ex + ey * ey) ** 0.5
        ux, uy = ex / L, ey / L
        pts.append(p0)
        for c, d in sorted(tabs.get(e, [])):
            nx, ny = -uy * d, ux * d
            for a in np.linspace(-np.pi / 2, np.pi / 2, 26):
                pts.append((p0[0] + ux * (c + TAB_R * np.sin(a)) + nx * TAB_R * np.cos(a),
                            p0[1] + uy * (c + TAB_R * np.sin(a)) + ny * TAB_R * np.cos(a)))
    return pts


def _tab_positions(lo, hi):
    """The single tab centre for one shared edge, at the middle of the overlap."""
    return [((lo + hi) / 2, -1)]


def f0b():
    """The corpus as a treemap: area is how many problems a category holds, colour is how
    hard they are. Companion to F0, which carries the exact per-stratum counts."""
    import numpy as np
    from matplotlib.patches import Polygon
    rows = [r for r in load("F0_core_composition.csv") if r["category"] != "ALL"]
    allr = next(r for r in load("F0_core_composition.csv") if r["category"] == "ALL")
    N = int(allr["n_total"])
    rows.sort(key=lambda r: -int(r["n_total"]))
    W, H = 100.0, 58.0
    vals = [int(r["n_total"]) for r in rows]
    # pick the column count that gives the least extreme cell shapes
    tiles = min((_columns(vals, W, H, k) for k in (3, 4, 5)),
                key=lambda t: max(max(w / h, h / w) for _x, _y, w, h in t))

    # tabs live on genuinely shared edges; the tile listed first bumps out, its partner in
    # a tab on EVERY shared edge: a tile with tabs on some edges and plain corners on others
    # reads as accidental, which was the second thing making this look unlike a real puzzle
    G = 0.22                                   # half of the white channel between tiles
    eps, tabs = 1e-6, {i: {e: [] for e in range(4)} for i in range(len(tiles))}
    for i, (x0, y0, w0, h0) in enumerate(tiles):
        for j, (x1, y1, w1, h1) in enumerate(tiles):
            if i >= j:
                continue
            if abs(x0 + w0 - x1) < eps:                       # i's right edge = j's left edge
                lo, hi = max(y0, y1), min(y0 + h0, y1 + h1)
                if hi - lo > 3 * TAB_R:
                    for m, d in _tab_positions(lo, hi):
                        tabs[i][1].append((m - y0 - G, d))            # measured from the INNER corner
                        tabs[j][3].append((y1 + h1 - m - G, -d))      # mirrored, same inner-corner basis
            if abs(y0 + h0 - y1) < eps:                       # i's top edge = j's bottom edge
                lo, hi = max(x0, x1), min(x0 + w0, x1 + w1)
                if hi - lo > 3 * TAB_R:
                    for m, d in _tab_positions(lo, hi):
                        tabs[i][2].append((x0 + w0 - m - G, d))       # measured from the INNER corner
                        tabs[j][0].append((m - x1 - G, -d))           # mirrored, same inner-corner basis

    fig, ax = plt.subplots(figsize=(WIDTH_2COL, 3.95), layout="constrained")
    shares = [100 * int(r["n_high"]) / int(r["n_total"]) for r in rows]
    # tiles use only the middle of the ramp: the palest end is invisible against the page and
    # the deepest end swallows the label. The colourbar must be cut from the SAME sub-range,
    # or a reader matching a tile to the key lands on the wrong percentage.
    from matplotlib.colors import LinearSegmentedColormap as _LSC
    SEQ_TILE = _LSC.from_list("seq_tile", SEQ(np.linspace(0.18, 0.90, 256)))
    for i, (r, t) in enumerate(zip(rows, tiles)):
        x, y, w, h = t
        inner = (x + G, y + G, w - 2 * G, h - 2 * G)
        sh = shares[i]
        col = SEQ_TILE((sh - min(shares)) / (max(shares) - min(shares)))
        ax.add_patch(Polygon(_jigsaw(inner, tabs[i]), closed=True, facecolor=col,
                             edgecolor="white", lw=0.8, joinstyle="round", zorder=3))
    ax.set_xlim(-0.6, W + 0.6); ax.set_ylim(-0.6, H + 0.6)
    ax.set_aspect("equal")
    ax.set_xticks([]); ax.set_yticks([])          # not axis("off"): that would also kill the
    for sp in ax.spines.values():                 # xlabel, which carries the encoding legend
        sp.set_visible(False)
    # labels are measured against the settled layout: draw ONCE here, then place text with a
    # live renderer. Drawing during label placement would re-run constrained_layout mid-build
    # and collapse the axes, which is exactly the bug that broke the first attempt.
    fig.canvas.draw()
    rnd = fig.canvas.get_renderer()
    inv = ax.transData.inverted()

    def _tw(txt, size):
        probe = ax.text(0, 0, txt, fontsize=size, alpha=0)
        bb = probe.get_window_extent(rnd)
        probe.remove()
        return abs(inv.transform((bb.x1, 0))[0] - inv.transform((bb.x0, 0))[0])

    pt_per_unit = (ax.bbox.height / fig.dpi * 72) / (ax.get_ylim()[1] - ax.get_ylim()[0])
    for i, (r, t) in enumerate(zip(rows, tiles)):
        x, y, w, h = t
        sh = shares[i]
        col = SEQ_TILE((sh - min(shares)) / (max(shares) - min(shares)))
        n = int(r["n_total"])
        name = r["category"].replace("_", " ").capitalize()
        # wrap by measurement, not by a width threshold: the usable width is the cell minus
        # the white channel and whatever a side tab eats into it. thermodynamics is WIDER than
        # its own cell on one line, so no tab placement could have saved it unwrapped.
        avail = w - 2 * G - TAB_R * (bool(tabs[i].get(1)) + bool(tabs[i].get(3))) - 1.2
        if " " in name and _tw(name, FS_TICK) > avail:
            name = name.replace(" ", "\n")
        # text colour from the tile's measured luminance, not a guess: white only where it
        # actually clears the contrast bar, ink otherwise (WCAG relative-luminance formula)
        cr, cg, cb_, _ca = col
        lum = sum(k * (v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4)
                  for k, v in ((0.2126, cr), (0.7152, cg), (0.0722, cb_)))
        dark = (1.05 / (lum + 0.05)) >= ((lum + 0.05) / 0.065)
        main = "white" if dark else INK
        # the secondary line must ALSO clear the contrast bar on its own tile: TXT grey is a
        # white-background colour and drops to ~2:1 on the mid-blue tiles, so fall back to the
        # main ink whenever muted grey cannot reach 4.5:1 against this tile
        if dark:
            sub = (1, 1, 1, 0.85)
        else:
            txt_lum = 0.117
            sub = TXT if (lum + 0.05) / (txt_lum + 0.05) >= 4.5 else INK
        lines = name.count("\n") + 1
        # every shared edge carries its tab at the midpoint, which is also where a centred
        # label sits; nudge the label away from whichever side actually protrudes into the
        # tile. Horizontal only: moving it vertically would push short labels out of the cell.
        cx, cy = x + w / 2, y + h / 2
        # the name grows upward from cy and the count hangs below it, so a wrapped name lifts
        # the pair's visual centre; drop cy by half the extra name height to re-centre
        cy -= name.count("\n") * 0.5 * FS_TICK * 1.3 / pt_per_unit
        ax.text(cx, cy + 0.55, name, ha="center", va="bottom", fontsize=FS_TICK,
                color=main, linespacing=1.3, zorder=4)
        ax.text(cx, cy - 0.55, f"{n} ({100 * n / N:.0f}%)", ha="center", va="top",
                fontsize=FS_ANNOT, color=sub, zorder=4)

    # the treemap has no axis, so the encoding and the unit have to be stated somewhere on the
    # figure itself; one line does it, whereas prefixing every tile with "N =" would relabel the
    # plotted value as a sample size (which is what N means on the rate figures, e.g. F6.1b)
    ax.set_xlabel(f"Tile area is proportional to the number of core problems\n"
                  f"(N = {N} problems across {len(rows)} categories)")

    sm = plt.cm.ScalarMappable(cmap=SEQ_TILE, norm=plt.Normalize(min(shares), max(shares)))
    cb = fig.colorbar(sm, ax=ax, fraction=0.018, pad=0.012, shrink=0.72, aspect=26)
    cb.outline.set_visible(False); cb.ax.tick_params(length=0, labelsize=FS_ANNOT)
    cb.set_label("High-difficulty share of the category (%)", fontsize=FS_LABEL)

    big, small = rows[0], rows[-1]
    hardest = max(rows, key=lambda r: int(r["n_high"]) / int(r["n_total"]))
    note("F0b_category_treemap",
         f"The corpus is uneven by design and its size and its difficulty are unrelated: "
         f"{big['category'].replace('_', ' ')} holds {100 * int(big['n_total']) / N:.0f}% of the "
         f"set but is not among the hardest, while "
         f"{hardest['category'].replace('_', ' ')} is the hardest at "
         f"{100 * int(hardest['n_high']) / int(hardest['n_total']):.0f}% high-difficulty "
         f"problems on {100 * int(hardest['n_total']) / N:.0f}% of the set.",
         f"""Treemap of the {N}-problem core set. Tile area is the number of problems in a
         category, so the whole rectangle is the corpus; tile colour is the share of that
         category graded high difficulty by the rubric classifier, which was applied before any
         model was run. Tiles are laid out as full-height columns of stacked cells, so every vertical edge runs
         unbroken through the figure, and each pair of neighbouring tiles interlocks through a
         single tab at the midpoint of its shared edge; areas remain exactly proportional to
         the counts. Category sizes follow the source material rather than a quota,
         which is why they span {int(small['n_total'])} to {int(big['n_total'])} problems. Size
         and difficulty are close to independent: the two largest categories sit in the middle of
         the colour range while the hardest,
         {hardest['category'].replace('_', ' ')} at
         {100 * int(hardest['n_high']) / int(hardest['n_total']):.0f}%, is only the
         {sorted(range(len(rows)), key=lambda i: -int(rows[i]['n_total'])).index(rows.index(hardest)) + 1}th
         largest. F0 carries the same data with exact per-stratum counts; this view is for the
         shape of the corpus rather than for reading numbers off.""",
         "`F0_core_composition.csv`")
    save(fig, "F0b_category_treemap")


# ---------------------------------------------------------------- F1
def f1():
    rows = load("F1_category_matrix.csv")
    cats = ["Rad", "Thermo", "Clim", "BL", "Dyn", "Obs", "Aero", "Chem", "AQ", "Cloud"]
    sizes = {r["category"]: r["n"] for r in load("F1_category_sizes.csv")}
    M = [[float(r[f"{c}_mean"]) for c in cats] for r in rows]
    fig, ax = plt.subplots(figsize=(WIDTH_2COL, 4.97), layout="constrained")
    im = ax.imshow(M, cmap=SEQ, vmin=25, vmax=100, aspect="auto")
    ax.set_xticks(range(len(cats)))
    ax.set_xticklabels([f"{c}\n(N = {sizes[c]})" for c in cats])
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r["model"] for r in rows])
    ax.tick_params(length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    for i, r in enumerate(rows):
        for j, c in enumerate(cats):
            v = float(r[f"{c}_mean"])
            ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=FS_ANNOT,
                    color="white" if v > 84 else INK)
    ax.set_xlabel("Subject category (N = problems in the category)", labelpad=6)
    panel(ax, "", "Accuracy by category, code mode (3-run mean, %)")
    cb = fig.colorbar(im, ax=ax, fraction=0.022, pad=0.015)
    cb.outline.set_visible(False); cb.ax.tick_params(length=0)
    cb.set_label("Accuracy (%)")
    note("F1_category_by_model",
         "Difficulty has a stable category structure that runs through every capability tier.",
         """Accuracy by subject category under the code protocol. Rows: the 16 leaderboard
         configurations, ordered by overall core-set accuracy; columns: the 10-class subject
         taxonomy, ordered easiest to hardest by cross-model mean, with the number of problems
         under each label. Each cell is the configuration's mean accuracy over 3 runs (%) on
         that category; the single-hue scale avoids red-green contrast. The four right-most
         columns (aerosols, chemistry, air quality, cloud physics) stay the lightest across all
         tiers on a scale where dark is high accuracy, i.e. the hard cluster is a property of the material, not of any one model.""",
         "`F1_category_matrix.csv`, `F1_category_sizes.csv`")
    save(fig, "F1_category_by_model")


# ---------------------------------------------------------------- F2/F3 (protocol comparison)
def f23():
    """Effect-size panels instead of slope charts: (a) Δ accuracy about zero,
    (b) token ratio about 1×. The claims ARE the reference lines."""
    rows = sorted(load("F2_F3_direct_vs_code.csv"),
                  key=lambda r: -float(r["delta_code_minus_direct"]))
    n = len(rows)
    ys = list(range(n))[::-1]
    deltas = [float(r["delta_code_minus_direct"]) for r in rows]
    mean_d = sum(deltas) / n
    ratios = [float(r["token_ratio_direct_over_code"]) for r in rows]

    fig, (a, b) = plt.subplots(1, 2, figsize=(WIDTH_2COL, 2.65),
                               gridspec_kw=dict(width_ratios=[1.15, 1], wspace=0.12), layout="constrained")
    # (a) accuracy difference, code − direct
    a.axvline(0, color=MUTED, lw=0.8, zorder=1)
    for y, r, d in zip(ys, rows, deltas):
        err = (float(r["code_sd"]) ** 2 + float(r["direct_sd"]) ** 2) ** 0.5
        a.errorbar(d, y, xerr=err, fmt="o", ms=4, color=NAVY, ecolor=NAVY,
                   elinewidth=0.7, capsize=1.8, capthick=0.7,
                   markeredgecolor="white", markeredgewidth=0.5, zorder=3)
        a.text(d + (0.32 if d >= 0 else -0.32) + err * (1 if d >= 0 else -1), y, mfmt(f"{d:+.1f}"),
               fontsize=FS_ANNOT, color=TXT, va="center", ha="left" if d >= 0 else "right")
    a.set_yticks(ys); a.set_yticklabels([r["model"] for r in rows])
    a.tick_params(axis="y", length=0)
    a.set_xlabel(f"Accuracy difference, code − direct (pt)\n"
                 f"(N = {len(rows)} configurations, 3 runs of 436 problems each)")
    a.set_xlim(-4.6, 5.6)
    a.grid(axis="x", color=GRID, lw=GRID_LW, zorder=0); a.set_axisbelow(True)
    panel(a, "a", "Accuracy: near-tied, sign is model-dependent")

    # (b) token cost ratio, direct / code
    b.axvline(1, color=MUTED, lw=0.8, zorder=1)
    for y, r, ratio in zip(ys, rows, ratios):
        und = r["tokens_understated_dagger"] == "yes"
        b.plot([1, ratio], [y, y], color=GRID, lw=1.6, zorder=1, solid_capstyle="butt")
        b.plot(ratio, y, "o", ms=4.4, zorder=3,
               markerfacecolor="white" if und else NAVY,
               markeredgecolor=NAVY, markeredgewidth=0.9)
        b.text(ratio + 0.045, y, f'{ratio:.2f}×' + (" †" if und else ""),
               fontsize=FS_ANNOT, color=TXT, va="center")
    b.set_yticks(ys); b.set_yticklabels([])
    b.tick_params(axis="y", length=0)
    b.set_xlabel("Token cost ratio, direct/code")
    b.set_xlim(0.88, 2.55)
    b.set_xticks([1.0, 1.5, 2.0, 2.5])
    b.grid(axis="x", color=GRID, lw=GRID_LW, zorder=0); b.set_axisbelow(True)
    panel(b, "b", "Cost: direct is never cheaper")
    cens = [r["model"] for r in rows if r["tokens_understated_dagger"] == "yes"]
    dagnote = ("" if not cens else
               " Open markers with a dagger, " + " and ".join(cens) + ", run on endpoints that "
               "return only a summary of the chain of thought, so those counts are lower bounds "
               "and the configurations are excluded from efficiency claims.")
    note("F2_F3_protocol",
         "Code vs direct: accuracy is near-tied with a model-dependent sign; direct never costs fewer tokens.",
         f"""Protocol comparison over the six configurations run under both protocols on the
         436-problem core set (3 runs each). (a) Accuracy difference, code − direct, in points;
         error bars are quadrature-combined 3-run s.d.; the mean gap is {mean_d:+.2f} pt. Both signs occur, so neither protocol dominates on accuracy.
         (b) Token cost ratio, direct/code, on a log axis anchored at 1x: every model sits right
         of 1x.{dagnote}""",
         "`F2_F3_direct_vs_code.csv`")
    save(fig, "F2_F3_protocol")


# ---------------------------------------------------------------- F2b (absolute tokens)
def f2b():
    """Companion to F2_F3_protocol panel b: the same six models, but absolute per-run
    token totals as paired bars — no ratios, just the two quantities side by side."""
    rows = sorted(load("F2_F3_direct_vs_code.csv"),
                  key=lambda r: -float(r["direct_tokens_M"]))
    fig, ax = plt.subplots(figsize=(WIDTH_2COL, 3.71), layout="constrained")
    xs = list(range(len(rows)))
    for x, r in zip(xs, rows):
        c, d = float(r["code_tokens_M"]), float(r["direct_tokens_M"])
        und = r["tokens_understated_dagger"] == "yes"
        ax.bar(x - 0.19, c, width=0.34, color=NAVY, alpha=0.45, zorder=3)
        ax.bar(x + 0.19, d, width=0.34, color=NAVY, zorder=3)
        ax.text(x - 0.19, c + 0.16, f"{c:.2f}" + ("†" if und else ""),
                fontsize=FS_ANNOT, ha="center", va="bottom", color=TXT)
        ax.text(x + 0.19, d + 0.16, f"{d:.2f}" + ("†" if und else ""),
                fontsize=FS_ANNOT, ha="center", va="bottom", color=INK)
    ax.set_xticks(xs)
    ax.set_xticklabels([r["model"].replace(" (reasoning)", "\n(reasoning)") for r in rows],
                       fontsize=FS_ANNOT, linespacing=1.25)
    ax.tick_params(axis="x", length=0)
    ax.set_xlim(-0.65, len(rows) - 0.35)
    ax.set_ylim(0, 11)
    ax.set_ylabel("Tokens per full core-set run (M, o200k)")
    ax.set_xlabel(f"(N = {len(rows)} configurations run under both protocols, 3 runs each)")
    ax.legend(handles=[Line2D([], [], color=NAVY, alpha=0.45, lw=5, label="Code"),
                       Line2D([], [], color=NAVY, lw=5, label="Direct")],
              loc="upper right", frameon=False, handlelength=1.2)
    ax.grid(axis="y", color=GRID, lw=GRID_LW, zorder=0); ax.set_axisbelow(True)
    panel(ax, "", "Direct always spends more tokens than code")
    tmax = max(max(float(r["code_tokens_M"]), float(r["direct_tokens_M"])) for r in rows)
    cens = [r["model"] for r in rows if r["tokens_understated_dagger"] == "yes"]
    dagnote = ("" if not cens else
               " Open markers with a dagger, " + " and ".join(cens) + ", run on endpoints that "
               "return only a summary of the chain of thought, so those counts are lower bounds "
               "and the configurations are excluded from efficiency claims.")
    note("F2b_tokens_absolute",
         "In absolute terms, the direct protocol spends more tokens than code for every model.",
         f"""Per-run token totals for the six configurations run under both protocols
         (uniform o200k count over the stored text of every call, over the full 436-problem core
         set, mean of 3 runs; companion to the ratio panel of F2_F3_protocol), on a common linear
         axis so the absolute spread across configurations is preserved; every bar is labelled
         because the smaller pairs are short against the {tmax:.2f} M maximum. Light bar: code protocol;
         dark bar: direct. The dark bar is taller in every pair: prose must verbalise
         the working that code delegates to the interpreter, and the gap is widest for
         the reasoning settings. Both arms are counted the same way, so the comparison is
         internally consistent{dagnote}.""",
         "`F2_F3_direct_vs_code.csv`")
    save(fig, "F2b_tokens_absolute")


# ---------------------------------------------------------------- F0
DIFF = [("n_low", "Low", "#c6d3e3"), ("n_medium", "Medium", "#7f9cc0"), ("n_high", "High", NAVY)]


def f0():
    """The corpus itself: how the 436 core problems distribute over the ten categories,
    and how each category's own difficulty mix compares with the corpus-wide mix."""
    rows = [r for r in load("F0_core_composition.csv") if r["category"] != "ALL"]
    allr = next(r for r in load("F0_core_composition.csv") if r["category"] == "ALL")
    N, ncat = int(allr["n_total"]), len(rows)
    pooled_high = int(allr["n_high"]) / N * 100
    xmax = max(int(r["n_total"]) for r in rows) * 1.13   # axis follows the data, never hard-coded

    fig, axes = plt.subplots(1, 2, figsize=(WIDTH_2COL, 3.3), sharey=True,
                             gridspec_kw={"width_ratios": [1.35, 1], "wspace": 0.06}, layout="constrained")
    ys = list(range(ncat))[::-1]
    names = [r["category"].replace("_", " ").capitalize() for r in rows]

    # (a) absolute counts, stacked low -> high
    ax = axes[0]
    for y, r in zip(ys, rows):
        left = 0
        for key, _lab, col in DIFF:
            v = int(r[key])
            ax.barh(y, v, left=left, height=0.66, color=col, zorder=3)
            if v >= 8:      # only label a segment wide enough to hold the digits
                ax.text(left + v / 2, y, str(v), fontsize=FS_ANNOT, ha="center", va="center",
                        color="white" if col == NAVY else INK, zorder=4)
            left += v
        ax.text(left + xmax * 0.016, y, str(left), fontsize=FS_TICK, va="center", color=INK)
    ax.set_yticks(ys); ax.set_yticklabels(names)
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, xmax); ax.set_ylim(-0.7, ncat + 0.05)   # headroom for the panel-b annotation
    ax.set_xlabel(f"Problems per category\n(N = {N} problems, {ncat} categories)")
    panel(ax, "a")
    ax.grid(axis="x", color=GRID, lw=GRID_LW, zorder=0); ax.set_axisbelow(True)
    ax.spines["bottom"].set_bounds(0, max(t for t in ax.get_xticks() if t <= xmax))
    ax.legend(handles=[Line2D([], [], color=c, lw=5, label=l) for _k, l, c in DIFF],
              loc="lower right", frameon=False, handlelength=1.2, ncol=1,
              title="Difficulty", title_fontsize=FS_TICK)

    # (b) same rows normalised, so the mix is comparable across very different sizes
    ax = axes[1]
    for y, r in zip(ys, rows):
        tot, left = int(r["n_total"]), 0.0
        for key, _lab, col in DIFF:
            w = int(r[key]) / tot * 100
            ax.barh(y, w, left=left, height=0.66, color=col, zorder=3)
            left += w
        hi = int(r["n_high"]) / tot * 100
        ax.text(102, y, f"{hi:.0f}%", fontsize=FS_ANNOT, va="center",
                color=RED_TXT if hi > pooled_high else TXT)
    ax.axvline(100 - pooled_high, color=INK, lw=0.8, ls=(0, (3, 2)), zorder=5)
    ax.text(100 - pooled_high - 1.5, ncat - 0.32,
            f"corpus-wide high share {pooled_high:.0f}%", fontsize=FS_ANNOT,
            ha="right", va="center", color=INK)
    ax.set_xlim(0, 112); ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xticklabels(["0", "25", "50", "75", "100"])
    ax.spines["bottom"].set_bounds(0, 100)          # no rule beyond the last meaningful tick
    ax.set_xlabel("Difficulty composition within category (%)\nred = high-difficulty share "
                  "above the corpus-wide share")
    panel(ax, "b")
    ax.grid(axis="x", color=GRID, lw=GRID_LW, zorder=0); ax.set_axisbelow(True)
    ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)

    top, bot = names[0], names[-1]
    note("F0_core_composition",
         f"The core set spans {ncat} categories that are deliberately uneven in size, "
         f"but every category carries all three difficulty strata.",
         f"""Composition of the {N}-problem core set. a, Problems per category, stacked by the
         intrinsic difficulty stratum assigned by the rubric classifier (low, medium, high);
         the number at the end of each bar is the category total. b, The same rows
         normalised to 100%, so the difficulty mix can be compared across categories that
         differ by almost an order of magnitude in size; the dashed line marks the corpus-wide
         high-difficulty share ({pooled_high:.0f}%, {allr['n_high']}/{N}) and the percentage at
         each row is that category's own high share, printed in red where it exceeds the
         corpus-wide value. Category sizes follow the source material rather than a quota:
         {top} is the largest at {rows[0]['n_total']} problems and {bot} the smallest at
         {rows[-1]['n_total']}. Difficulty is an intrinsic rubric score computed before any
         model was run, not an observed pass rate, so it cannot inherit a model's weaknesses.""",
         "`F0_core_composition.csv` (extracted from `benchmark/core.json`, not from any run)")
    save(fig, "F0_core_composition")


# --------------------------------------------------------------- ridgeline helpers
def _kde(pts, grid, h=0.11):
    """Gaussian kernel density over log10(tokens), evaluated from the stored histogram: each
    bin contributes its count at the bin centre. Bandwidth h is in log10 units (about a
    quarter of a decade at the half-width), chosen once and used by every ridge so shapes are
    comparable; it smooths the bin edges without inventing structure."""
    import numpy as np
    c = np.array([b for b, _n in pts]); w = np.array([n for _b, n in pts], dtype=float)
    if w.sum() <= 0:
        return np.zeros_like(grid)
    d = (grid[:, None] - c[None, :]) / h
    return (np.exp(-0.5 * d * d) * w[None, :]).sum(axis=1)


def _ridge(ax, grid, y0, dens, height, col, z, fill=0.30):
    """One ridge: pale fill, crisp outline, and a white halo under the outline so overlapping
    ridges stay separable — the detail that makes a stacked density read as data rather than
    decoration."""
    import matplotlib.patheffects as _pe
    y = y0 + dens / dens.max() * height
    ax.fill_between(grid, y0, y, color=col, alpha=fill, lw=0, zorder=z)
    ax.plot(grid, y, color=col, lw=0.9, zorder=z + 0.1,
            path_effects=[_pe.withStroke(linewidth=2.2, foreground="white")])


def _qstrip(ax, y0, p10, p50, p90, col, z):
    """The baseline doubles as a quantile strip: a heavier segment spanning P10-P90 and a dot
    at the median, so the exact numbers are recoverable from a shape that is otherwise smoothed."""
    import numpy as np
    ax.plot([np.log10(p10), np.log10(p90)], [y0, y0], color=col, lw=2.2, solid_capstyle="butt",
            zorder=z + 0.2, alpha=0.85)
    ax.plot([np.log10(p50)], [y0], marker="o", ms=3.0, mfc="white", mec=col, mew=1.0,
            zorder=z + 0.3)


# ---------------------------------------------------------------- F2c
def f2c(into=None):
    """The protocol cost comparison as two distributions per model rather than two bars: it
    shows whether prose shifts the whole distribution or only stretches its tail."""
    import numpy as np
    hist = load("F4d_spend_hist.csv")
    qs = {(r["model"], r["protocol"]): r for r in load("F4d_spend_quantiles.csv")}
    both = sorted({m for m, _p in qs} & {m for m, p in qs if p == "direct"},
                  key=lambda m: float(qs[(m, "code")]["p50"]))
    by = {}
    for r in hist:
        by.setdefault((r["model"], r["protocol"]), []).append(
            (float(r["log10_lo"]), int(r["n_problem_runs"])))
    grid = np.linspace(1.72, 5.28, 500)

    if into is None:
        fig, ax = plt.subplots(figsize=(WIDTH_2COL, 4.29), layout="constrained")
    else:
        fig, ax = into, into.add_subplot()
    OVER = 1.45
    for i, m in enumerate(both):
        for prot, col in (("code", CYAN), ("direct", NAVY)):
            dens = _kde(sorted(by[(m, prot)]), grid)
            if dens.max() <= 0:
                continue
            _ridge(ax, grid, i, dens, OVER, col, 100 - i)
            r = qs[(m, prot)]
            _qstrip(ax, i, float(r["p10"]), float(r["p50"]), float(r["p90"]), col, 100 - i)
        rc, rd = float(qs[(m, "code")]["p50"]), float(qs[(m, "direct")]["p50"])
        ax.text(5.46, i + 0.02, f"{rd / rc:.1f}\u00d7", fontsize=FS_TICK, va="center", ha="right",
                color=INK, zorder=200,
                path_effects=[pe.withStroke(linewidth=2.4, foreground="white")])
        disp_m = m.replace(" (reasoning)", " (R)") if into is not None else m
        ax.text(1.68, i + 0.02, disp_m, fontsize=FS_TICK, va="center", ha="right", color=INK, zorder=200,
                path_effects=[pe.withStroke(linewidth=2.4, foreground="white")])

    ax.set_xlim(1.63, 5.52); ax.set_ylim(-0.5, len(both) + OVER - 0.5)
    ax.set_xticks([2, 3, 4, 5]); ax.set_xticklabels(["100", "1k", "10k", "100k"])
    ax.set_yticks([]); ax.spines["left"].set_visible(False)
    if into is None:
        ax.set_xlabel("Output tokens spent on one problem (o200k, log scale)\n"
                      f"(N = {int(qs[(both[0], 'code')]['n_problem_runs']):,} problem-runs per "
                      "configuration and protocol; bar spans P10\u2013P90, dot marks the median)")
    else:                       # half width: the long form runs off the canvas edge
        ax.set_xlabel("Output tokens per problem (o200k, log scale)\n"
                      f"(N = {int(qs[(both[0], 'code')]['n_problem_runs']):,} problem-runs "
                      "per configuration and protocol)")
    ax.text(5.46, len(both) + OVER - 0.72, "median\ndirect / code", fontsize=FS_ANNOT, ha="right",
            va="center", color=INK, style="italic", linespacing=1.25)
    ax.text(1.68, len(both) + OVER - 0.62, "code", fontsize=FS_TICK, ha="right", va="center",
            color=CYAN_TXT, style="italic",
            path_effects=[pe.withStroke(linewidth=2.0, foreground="white")])
    ax.text(1.68, len(both) + OVER - 1.02, "direct", fontsize=FS_TICK, ha="right", va="center",
            color=NAVY, style="italic",
            path_effects=[pe.withStroke(linewidth=2.0, foreground="white")])
    ax.grid(axis="x", color=GRID, lw=GRID_LW, zorder=0); ax.set_axisbelow(True)

    if into is not None:
        return
    ratios = {m: float(qs[(m, "direct")]["p50"]) / float(qs[(m, "code")]["p50"]) for m in both}
    means = {r["model"]: float(r["token_ratio_direct_over_code"])
             for r in load("F2_F3_direct_vs_code.csv")}
    mean_lo, mean_hi = min(means.values()), max(means.values())
    gap_m = max(both, key=lambda m: ratios[m] - means[m])
    gap_mean, gap_med = means[gap_m], ratios[gap_m]
    tails = {m: float(qs[(m, "direct")]["p90_over_p50"]) - float(qs[(m, "code")]["p90_over_p50"])
             for m in both}
    up = sum(1 for v in ratios.values() if v > 1)
    note("F2c_protocol_spend",
         f"Prose does not merely add a long tail, it moves the whole distribution: the median "
         f"problem costs more under the direct protocol for {up} of {len(both)} configurations, "
         f"by {min(ratios.values()):.1f}x to {max(ratios.values()):.1f}x.",
         f"""Distribution of the output tokens spent on a single problem, for the
         {len(both)} configurations run under both protocols on the 436-problem core set, three
         runs each. Light ridges are the code protocol, dark ridges the direct protocol, each
         scaled to its own peak so that shape rather than height carries the comparison, with the
         median marked by a tick in the matching colour and the ratio of the two medians printed
         at the right. Rows are ordered by code-protocol median. The comparison that a per-run
         mean cannot make is visible here: the dark ridge is displaced to the right of the light
         one along its whole body rather than only in the tail, so the extra cost of answering in
         prose is paid on the ordinary problem and not just on the few hard ones. Output tokens
         are completion plus reasoning under the repo's own o200k accounting, identical on both
         sides. The ratios here are ratios of medians and are systematically larger than the
         ratios of per-run means quoted in the result tables ({mean_lo:.2f}x to {mean_hi:.2f}x),
         because the code protocol carries the heavier tail of the two on four of the
         {len(both)} configurations, which lifts its mean and so shrinks a ratio of means: the
         starkest case is {gap_m}, {gap_mean:.2f}x by mean against {gap_med:.1f}x by median. The
         median is the fairer summary of what the ordinary problem costs; the mean is the fairer
         summary of what a full run costs.""",
         "`F4d_spend_hist.csv`, `F4d_spend_quantiles.csv` (`extract_figure_data.py spend_dist`)")
    save(fig, "F2c_protocol_spend")


# ---------------------------------------------------------------- F4
# label placement: (dx pt, dy pt, ha); pairs are labelled once, at the non-reasoning twin
F4_LABEL = {
    "gpt-5.5": (-4, -9, "right"), "Qwen-3.5-397B": (0, 7, "center"),
    "Kimi K2.6": (5, -8, "left"), "DeepSeek-V4-pro": (6, -2, "left"),
    "DeepSeek-V4-flash": (-6, -2, "right"), "Qwen-3.6-27B": (0, -11, "center"),
    "Qwen-3.5-9B": (6, -2, "left"), "Qwen-2.5-72B": (6, -2, "left"),
    "Gemini-3.1-Pro (reasoning)": (9, 8, "left"),
    "gpt-5.5 (reasoning)": (0, 8, "center"),
}


def f4():
    """Frontier as a vector field: each backbone's arrow is 'what turning thinking on buys'."""
    rows = load("F4_token_accuracy.csv")
    pt = {r["model"]: (float(r["tokens_M_per_run"]), float(r["accuracy"])) for r in rows}
    fig, ax = plt.subplots(figsize=(WIDTH_2COL, 4.26), layout="constrained")

    by_back = {}
    for r in rows:
        if r["backbone_pair"]:
            by_back.setdefault(r["backbone_pair"], []).append(r)
    for rs in by_back.values():
        if len(rs) != 2:
            continue
        nr = next(r for r in rs if r["setting"] == "non-reasoning")
        re = next(r for r in rs if r["setting"] == "reasoning")
        (x0, y0), (x1, y1) = pt[nr["model"]], pt[re["model"]]
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0), zorder=2,
                    arrowprops=dict(arrowstyle="->,head_width=0.18,head_length=0.32",
                                    color=GREY, lw=0.9, shrinkA=4, shrinkB=5, alpha=0.85))
        gain = y1 - y0
        xm, ym = (x0 * x1) ** 0.5, (y0 + y1) / 2   # geometric mid on the log axis
        ax.annotate(f"+{gain:.1f}", (xm, ym), xytext=(4, 2), textcoords="offset points",
                    fontsize=FS_ANNOT, color=TXT, style="italic", ha="left", zorder=2)

    # Pareto frontier over honestly-counted points († excluded)
    hon = sorted((pt[r["model"]] for r in rows if r["tokens_understated_dagger"] == "no"))
    front, best = [], -1
    for x, y in hon:
        if y > best:
            front.append((x, y)); best = y
    ax.plot([p[0] for p in front], [p[1] for p in front], drawstyle="steps-post",
            color=RED, ls="--", lw=0.9, zorder=2)

    for r in rows:
        x, y = pt[r["model"]]
        und = r["tokens_understated_dagger"] == "yes"
        ax.scatter(x, y, marker="o" if r["setting"] == "reasoning" else "s", s=42, zorder=4,
                   facecolor="white" if und else (NAVY if r["setting"] == "reasoning" else CYAN),
                   edgecolor=GREY if und else "white", lw=0.8)
        if und:      # censored: only a lower bound on the token count, true value lies right
            ax.annotate("", xy=(x * 1.40, y), xytext=(x, y), zorder=3,
                        arrowprops=dict(arrowstyle="->,head_width=0.14,head_length=0.28",
                                        color=GREY, lw=0.8, shrinkA=4, shrinkB=0))
    short = {"Gemini-3.1-Pro (reasoning)": "Gemini-3.1-Pro (R) \u2020",
             "gpt-5.5 (reasoning)": "gpt-5.5 (R) \u2020"}
    for label, (dx, dy, ha) in F4_LABEL.items():
        x, y = pt[label]
        ax.annotate(short.get(label, label), (x, y), xytext=(dx, dy),
                    textcoords="offset points", fontsize=FS_ANNOT, ha=ha, va="center",
                    color=INK, zorder=5)

    ax.set_xscale("log"); ax.set_xlim(0.2, 30); ax.set_ylim(38, 101)
    ax.set_xlabel("Tokens per run (M, o200k over the stored text, log scale)\n"
                  f"(N = {len(rows)} configurations, 3 runs of 436 problems each)")
    ax.set_ylabel("Accuracy (%)")
    keys = [Line2D([], [], ls="none", marker="o", ms=5, mfc=NAVY, mec="white", label="Reasoning"),
            Line2D([], [], ls="none", marker="s", ms=5, mfc=CYAN, mec="white", label="Non-reasoning"),
            Line2D([], [], color=GREY, lw=0.9, marker=">", ms=3, mfc=GREY, label="Thinking on (+pt)")]
    if any(r["tokens_understated_dagger"] == "yes" for r in rows):
        keys.append(Line2D([], [], ls="-", marker="o", ms=5, mfc="white", mec=GREY, color=GREY,
                           lw=0.8, label="Tokens a lower bound (†)"))
    keys.append(Line2D([], [], color=RED, ls="--", lw=1.0, label="Pareto frontier"))
    ax.legend(handles=keys, loc="lower right", frameon=False, handlelength=1.6)
    ax.grid(color=GRID, lw=GRID_LW, zorder=0); ax.set_axisbelow(True)
    panel(ax, "")
    fnames = [m for m, (x, y) in pt.items() if (x, y) in front]
    cens = [r["model"] for r in rows if r["tokens_understated_dagger"] == "yes"]
    note("F4_token_accuracy_frontier",
         f"Reasoning buys points at a token price, and the efficiency frontier is "
         f"{len(front)} configurations wide.",
         f"""Core-set accuracy against tokens per full run (log axis), code protocol,
         {len(rows)} configurations. Arrows connect each backbone's non-reasoning
         setting to its reasoning twin and are labelled with the accuracy gain (+pt): enabling
         thinking always moves up and to the right, with the largest gains on the weakest
         backbones. The dashed step is the Pareto frontier: {", ".join(fnames)}. Tokens are the
         provider's own usage accounting summed over the self-repair attempts, not a recount of
         the stored text, so reasoning that a provider generates but does not echo is still
         counted; this matters most for gpt-5.5 (reasoning) and Gemini-3.1-Pro, whose endpoints
         return only a summary of the chain of thought and whose totals a text recount would
         halve.""",
         "`F4_token_accuracy.csv`")
    save(fig, "F4_token_accuracy_frontier")


# ---------------------------------------------------------------- F4b
# label anchors for the efficiency map: (dx pt, dy pt, ha) at the non-reasoning twin
F4B_LABEL = {
    "gpt-5.5": (0, 8, "center"), "DeepSeek-V4-flash": (-3, -11, "center"),
    "DeepSeek-V4-pro": (5, 5, "left"), "Qwen-3.6-27B": (0, -11, "center"),
    "Qwen-3.5-397B": (0, -11, "center"), "Kimi K2.6": (0, -11, "center"),
    "Qwen-3.5-9B": (-2, -11, "center"), "Qwen-2.5-72B": (7, -2, "left"),
    "Gemini-3.1-Pro": (11, -8, "left"),
}
ISO = [1000, 3000, 10000, 30000]          # tokens spent per correct answer


def f4b(into=None):
    """Cost-efficiency map: the same (tokens, accuracy) measurements as F4, but drawn over a
    field of constant tokens-per-correct-answer, so efficiency is read off the background
    instead of being inferred from two coordinates."""
    import numpy as np
    rows = load("F4_token_accuracy.csv")
    NPROB = 436
    xs = [float(r["tokens_M_per_run"]) for r in rows]
    lo, hi = min(xs) * 0.62, max(xs) * 1.65
    ylo, yhi = 35, 100.5

    if into is None:
        fig, ax = plt.subplots(figsize=(WIDTH_2COL, 4.54), layout="constrained")
    else:
        fig, ax = into, into.add_subplot()
    ax.set_xscale("log")

    # --- background: tokens spent per correct answer, everywhere in the plane -------------
    gx = np.logspace(np.log10(lo), np.log10(hi), 500)
    gy = np.linspace(ylo, yhi, 400)
    GX, GY = np.meshgrid(gx, gy)
    cost = GX * 1e6 / (GY / 100 * NPROB)
    # contours only, no shaded field: the field would double-encode the same quantity, and a
    # navy wash collides with the repo's colour semantics (navy = reasoning, dark = accurate)
    cs = ax.contour(GX, GY, np.log10(cost), levels=[np.log10(v) for v in ISO],
                    colors=MUTED, linewidths=0.6, linestyles="dashed", zorder=1)
    # per-level label heights: standalone keeps one row at 52; at 3:2 the legend swallows
    # 52, and 3k at the shared height lands under the Qwen-3.6-27B label's halo
    ypos = {v: 52 for v in ISO} if into is None else {1000: 75, 3000: 68, 10000: 75, 30000: 75}
    ax.clabel(cs, fmt={lev: f"{v // 1000}k" for lev, v in zip(cs.levels, ISO)},
              manual=[(v * NPROB * ypos[v] / 100 / 1e6, ypos[v]) for v in ISO],
              fontsize=FS_ANNOT, colors=TXT, inline=True, inline_spacing=3)
    ax.text(lo * 1.04, ylo + 1.2,
            "contours: tokens per correct answer" if into is not None
            else "dashed contours: tokens spent per correct answer",
            fontsize=FS_ANNOT, color=TXT, ha="left", va="bottom", style="italic", zorder=6)

    # --- twin connectors, then the points ------------------------------------------------
    by_pair = {}
    for r in rows:
        if r["backbone_pair"]:
            by_pair.setdefault(r["backbone_pair"], {})[r["setting"]] = r
    for pair in by_pair.values():
        a, b = pair.get("non-reasoning"), pair.get("reasoning")
        if a and b:
            ax.annotate("", xy=(float(b["tokens_M_per_run"]), float(b["accuracy"])),
                        xytext=(float(a["tokens_M_per_run"]), float(a["accuracy"])),
                        arrowprops=dict(arrowstyle="-|>", lw=0.55, color=GREY,
                                        shrinkA=5 if into is None else 2.5,
                                        shrinkB=5 if into is None else 2.5,
                                        alpha=0.55), zorder=2)
    for r in rows:
        x, y = float(r["tokens_M_per_run"]), float(r["accuracy"])
        rea = r["setting"] == "reasoning"
        dag = r["tokens_understated_dagger"] == "yes"
        ms = 46 if into is None else 16        # half width: full-size markers occlude
        ax.scatter([x], [y], s=ms, marker="o" if rea else "s", zorder=4,
                   facecolor="white" if dag else (NAVY if rea else CYAN),
                   edgecolor=NAVY if rea else CYAN, linewidth=1.0 if dag else 0.7)
        if dag:      # censored: the count is a lower bound, the true point lies to the right
            grow = (1.38, 1.44) if into is None else (1.26, 1.30)
            ax.annotate("", xy=(x * grow[0], y), xytext=(x, y), zorder=3,
                        arrowprops=dict(arrowstyle="->,head_width=0.13,head_length=0.26",
                                        color=NAVY, lw=0.8,
                                        shrinkA=4 if into is None else 3, shrinkB=0, alpha=0.8))
            ax.text(x * grow[1], y, "\u2020", fontsize=FS_TICK, ha="left", va="center",
                    color=NAVY, zorder=5)
        key = r["model"].replace(" (reasoning)", "")
        # pairs are labelled once; WHICH twin carries the label is free, and at half width the
        # non-reasoning cluster around 0.3-0.9 M has no room left for Qwen-3.5-397B (every side
        # is taken: right hits Kimi's square, left swallowed gpt-5.5's, above is Gemini's text,
        # below is DeepSeek-V4-pro's) -- so its label rides the reasoning twin instead, whose
        # right side is open water
        swap = into is not None and key == "Qwen-3.5-397B"
        if key in F4B_LABEL and ((rea if swap else not rea) or not r["backbone_pair"]):
            over = {} if into is None else {"Qwen-3.5-397B": (7, -1, "left")}
            dx, dy, ha = over.get(key, F4B_LABEL[key])
            ax.annotate(key, (x, y), textcoords="offset points", xytext=(dx, dy),
                        ha=ha, fontsize=FS_TICK, color=INK, zorder=5,
                        path_effects=[pe.withStroke(linewidth=1.8, foreground="white")])

    ax.set_xlim(lo, hi); ax.set_ylim(ylo, yhi)
    ax.set_xticks([0.2, 0.3, 0.5, 1, 2, 5, 10, 20])
    ax.set_xticklabels(["0.2", "0.3", "0.5", "1", "2", "5", "10", "20"])
    ax.tick_params(axis="x", which="minor", length=0)
    ax.set_xlabel("Tokens per full core-set run (M, o200k over the stored text, log scale)")
    ax.set_ylabel("Accuracy (%)")
    ax.grid(axis="y", color=GRID, lw=GRID_LW, zorder=0); ax.set_axisbelow(True)
    hs = 5 if into is None else 4              # legend handles track the data-marker size
    keys = [Line2D([], [], ls="", marker="o", mfc=NAVY, mec=NAVY, ms=hs, label="Reasoning"),
            Line2D([], [], ls="", marker="s", mfc=CYAN, mec=CYAN, ms=hs, label="Non-reasoning"),
            Line2D([], [], color=GREY, lw=0.8, label="Same backbone, thinking on")]
    if any(r["tokens_understated_dagger"] == "yes" for r in rows):
        keys.append(Line2D([], [], ls="-", marker="o", mfc="white", mec=NAVY, color=NAVY, lw=0.8,
                           ms=hs, label="Tokens a lower bound (†)"))
    ax.legend(handles=keys, loc="lower right", frameon=False, handlelength=1.4, borderpad=0.2,
              fontsize=None if into is None else FS_ANNOT, handletextpad=0.5)

    if into is not None:
        return
    # cheapest/dearest are quoted only over fully measured configurations: a censored count
    # could win the "cheapest" title purely by being incomplete
    meas = [r for r in rows if r["tokens_understated_dagger"] == "no"]
    cheap = min(meas, key=lambda r: float(r["tokens_M_per_run"]) * 1e6
                / (float(r["accuracy"]) / 100 * NPROB))
    c_cost = float(cheap["tokens_M_per_run"]) * 1e6 / (float(cheap["accuracy"]) / 100 * NPROB)
    dear = max(meas, key=lambda r: float(r["tokens_M_per_run"]) * 1e6
               / (float(r["accuracy"]) / 100 * NPROB))
    d_cost = float(dear["tokens_M_per_run"]) * 1e6 / (float(dear["accuracy"]) / 100 * NPROB)
    note("F4b_efficiency_map",
         f"Accuracy and inference cost are not proportional: the cheapest configuration per "
         f"correct answer ({cheap['model']}, {c_cost:,.0f} tokens) is also one of the most "
         f"accurate, while the dearest ({dear['model']}, {d_cost:,.0f} tokens) is "
         f"{d_cost / c_cost:.0f} times costlier for a lower score; both figures are quoted over "
         f"the {len(meas)} configurations whose token count is fully measured.",
         f"""Cost-efficiency map of the {len(rows)} configurations evaluated on the core set under
         the code protocol. Axes carry the same two measurements as the frontier figure, tokens
         per run against accuracy, overlaid with the quantity that matters when the two are
         traded against each other: dashed contours of constant tokens spent per correct answer,
         defined as tokens per run divided by accuracy times {NPROB} problems. Any two
         configurations lying on the same contour are equally efficient regardless of where they
         sit on either axis, cost rises monotonically from the 1k contour to the 30k contour,
         and the upper left is both cheaper and more accurate. Circles are reasoning settings, squares non-reasoning, and a
         grey arrow joins the two settings of one backbone. Tokens are the provider's own usage
         accounting summed over the self-repair attempts rather than a recount of the stored
         text, so reasoning that a provider generates but does not echo is still priced; a text
         recount would halve gpt-5.5 (reasoning) and Gemini-3.1-Pro and move both into a
         cheaper contour band than they belong in. Accuracy is the mean of three runs.""",
         "`F4_token_accuracy.csv` (same table as the frontier figure; the cost field is derived, "
         "not an extra measurement)")
    save(fig, "F4b_efficiency_map")



# ---------------------------------------------------------------- F4c
MIN_BIN_N = 25          # a bin thinner than this is not used
STRATA = [("low", "Low", "#c6d3e3"), ("medium", "Medium", "#7f9cc0"), ("high", "High", NAVY)]
# the cheapest FULLY COUNTED reasoning configuration: the two summary-only endpoints cannot
# appear here at all, because the horizontal axis is the token measurement itself
EXEMPLAR = "DeepSeek-V4-flash (reasoning)"


def _wslope(pts):
    """Weighted least-squares slope of accuracy on log2(output tokens): points per doubling."""
    W = sum(w for _, _, w in pts)
    mx = sum(x * w for x, _, w in pts) / W
    my = sum(y * w for _, y, w in pts) / W
    den = sum(w * (x - mx) ** 2 for x, _, w in pts)
    return sum(w * (x - mx) * (y - my) for x, y, w in pts) / den if den else None


def f4c():
    """Does a model's own verbosity predict its failures once the two confounds are removed?
    Tokens come from the repo's own o200k count, only single-attempt records are used (the loop
    would otherwise couple tokens to failure by construction), and every comparison is made
    inside one intrinsic difficulty stratum."""
    rows = [r for r in load("F4c_token_bins.csv") if int(r["n_problem_runs"]) >= MIN_BIN_N]
    # a summary-only endpoint gives a lower bound on the spend, which would place its points in
    # the wrong bins; the horizontal axis here IS the measurement, so those configurations are
    # dropped rather than flagged
    censored = {r["model"] for r in load("F4_token_accuracy.csv")
                if r["tokens_understated_dagger"] == "yes"}
    rows = [r for r in rows if r["model"] not in censored]
    order = [r["model"] for r in load("F1_category_matrix.csv") if r["model"] not in censored]
    cell = {}
    for r in rows:
        cell.setdefault((r["model"], r["difficulty"]), []).append(
            (int(r["log2_bin"]), float(r["accuracy_pct"]), int(r["n_problem_runs"])))
    models = [m for m in order if any((m, lv) in cell for lv, _, _ in STRATA)]
    slopes = {k: _wslope(sorted(v)) for k, v in cell.items() if len(v) >= 2}
    nruns = sum(int(r["n_problem_runs"]) for r in rows)

    fig, axes = plt.subplots(1, 2, figsize=(WIDTH_2COL, 4.15),
                             gridspec_kw={"width_ratios": [1, 1.45], "wspace": 0.12}, layout="constrained")

    # (left) what a slope is, on the strongest configuration in the set
    ax = axes[0]
    for lv, lab, col in STRATA:
        pts = sorted(cell.get((EXEMPLAR, lv), []))
        if len(pts) < 2:
            continue
        ax.plot([p[0] for p in pts], [p[1] for p in pts], color=col, lw=1.4, marker="o",
                ms=3.2, mew=0, zorder=3)
        ax.annotate(lab, (pts[-1][0], pts[-1][1]), textcoords="offset points",
                    xytext=(5, 7 if lv == "low" else 0),
                    va="center", fontsize=FS_ANNOT, color=col if col != "#c6d3e3" else TXT,
                    path_effects=[pe.withStroke(linewidth=2.0, foreground="white")])
    xs = sorted({p[0] for lv, _, _ in STRATA for p in cell.get((EXEMPLAR, lv), [])})
    ax.set_xticks(xs)
    ax.set_xticklabels([f"{2 ** b // 1024}k" if b >= 10 else str(2 ** b) for b in xs])
    ax.set_xlim(min(xs) - 0.3, max(xs) + 1.5)
    yv = [p[1] for lv, _l, _c in STRATA for p in cell.get((EXEMPLAR, lv), [])]
    ylo = min(yv) - 0.08 * (max(yv) - min(yv)); ax.set_ylim(ylo, 101.5)
    ax.set_yticks([t for t in range(0, 101, 10 if max(yv) - min(yv) > 25 else 5) if t >= ylo])
    ax.set_xlabel(f"Output tokens spent on the problem\n({EXEMPLAR}, by difficulty stratum)")
    ax.set_ylabel("Accuracy within the bin (%)")
    ax.grid(axis="y", color=GRID, lw=GRID_LW, zorder=0); ax.set_axisbelow(True)
    panel(ax, "a")

    # (right) the same slope for every configuration and stratum
    ax = axes[1]
    ys = list(range(len(models)))[::-1]
    off = {"low": 0.26, "medium": 0.0, "high": -0.26}
    for y, m in zip(ys, models):
        for lv, _lab, col in STRATA:
            sl = slopes.get((m, lv))
            if sl is None:
                continue
            solid = len(cell[(m, lv)]) >= 3
            ax.scatter([sl], [y + off[lv]], s=22, marker="o", zorder=4,
                       facecolor=col if solid else "white", edgecolor=col, lw=0.9)
    ax.axvline(0, color=INK, lw=0.7, zorder=2)
    ax.set_yticks(ys); ax.set_yticklabels(models); ax.tick_params(axis="y", length=0)
    ax.yaxis.tick_right()
    ax.set_ylim(-1.9, len(models) - 0.4)
    means = {}
    for k, (lv, lab, col) in enumerate(STRATA):
        v = [s for (m, l), s in slopes.items() if l == lv]
        means[lv] = (sum(v) / len(v), len(v), sum(1 for x in v if x < 0))
        ax.scatter([means[lv][0]], [-1.15 + off[lv]], s=34, marker="D", color=col, zorder=5)
    ax.axhline(-0.62, color=GRID, lw=0.8, zorder=1)
    ax.text(1.005, 0.06, "Mean", transform=ax.transAxes, fontsize=FS_TICK, ha="left",
            va="center", color=INK)
    ax.set_xlabel("Accuracy change per doubling of output length (pt)\n"
                  f"(N = {len(models)} configurations x 3 difficulty strata; "
                  "filled = 3 or more bins, open = 2)")
    ax.grid(axis="x", color=GRID, lw=GRID_LW, zorder=0); ax.set_axisbelow(True)
    panel(ax, "b")

    lo, med, hi = (means[k][0] for k in ("low", "medium", "high"))
    note("F4c_token_length_decay",
         f"Output length predicts failure only where the problem is hard: averaged over "
         f"configurations, accuracy changes by {lo:+.1f} points per doubling of output on "
         f"low-difficulty problems, {med:+.1f} on medium and {hi:+.1f} on high, with the "
         f"high-difficulty slope negative for {means['high'][2]} of {means['high'][1]} "
         f"configurations.",
         f"""Accuracy against the number of output tokens a configuration spent on a problem,
         measured inside each intrinsic difficulty stratum. a, The three curves for
         {EXEMPLAR}, the cheapest configuration whose token count is fully measured, which is
         flat on easy problems and falls steeply on hard ones. b, The weighted least-squares slope of that
         relationship, in accuracy points per doubling of output length, for every configuration
         and stratum; filled markers rest on three or more bins, open markers on two, and the
         diamonds below the rule are the means over configurations. Three deliberate choices
         make this a within-model measurement rather than a restatement of difficulty. Output
         tokens are the repo's own uniform o200k count of the answer text, the same accounting
         used everywhere else here and in the result tables. Only
         records solved on the first attempt are used, because tokens are summed over the
         self-repair loop, so a record that needed several attempts would carry several times
         the tokens and be far likelier to have failed, manufacturing the very decline the
         figure asks about. And every comparison is made inside one stratum of the rubric
         difficulty label, which was assigned before any model was run, so a long answer is
         compared only against other answers to problems of the same graded difficulty. A bin
         holding fewer than {MIN_BIN_N} problem-runs is discarded and a stratum with fewer than
         two usable bins yields no slope, leaving {nruns:,} problem-runs behind the figure.
         Two configurations are absent by construction: gpt-5.5 (reasoning) and Gemini-3.1-Pro
         run on endpoints that return only a summary of the chain of thought, so the horizontal
         axis, which is the measurement here rather than a label, cannot be computed for them.""",
         "`F4c_token_bins.csv` (`extract_figure_data.py token_bins`, from "
         "`experiments/core_code/` usage plus the difficulty labels in `benchmark/core.json`)")
    save(fig, "F4c_token_length_decay")


# ---------------------------------------------------------------- F4d
def f4d():
    """How much a configuration spends on ONE problem, as a distribution rather than a mean.
    Every other token figure here reports a per-run mean; for a heavy-tailed spender that is a
    poor summary, and the spread turns out to be a model property in its own right."""
    import numpy as np
    hist = [r for r in load("F4d_spend_hist.csv") if r["protocol"] == "code"]
    q = {r["model"]: r for r in load("F4d_spend_quantiles.csv") if r["protocol"] == "code"}
    censored = {r["model"] for r in load("F4_token_accuracy.csv")
                if r["tokens_understated_dagger"] == "yes"}
    by = {}
    for r in hist:
        by.setdefault(r["model"], []).append((float(r["log10_lo"]), int(r["n_problem_runs"])))
    models = sorted(by, key=lambda m: float(q[m]["p50"]))          # quietest at the bottom
    grid = np.linspace(1.70, 5.42, 500)

    fig, ax = plt.subplots(figsize=(WIDTH_2COL, 5.45), layout="constrained")
    OVER = 2.1
    for i, m in enumerate(models):
        rea = q[m]["setting"] == "reasoning"
        col = NAVY if rea else CYAN
        dens = _kde(sorted(by[m]), grid)
        if dens.max() <= 0:
            continue
        _ridge(ax, grid, i, dens, OVER, col, 100 - i)
        _qstrip(ax, i, float(q[m]["p10"]), float(q[m]["p50"]), float(q[m]["p90"]), col, 100 - i)
        d = float(q[m]["p90_over_p50"])
        ax.text(5.62, i + 0.02, f"{d:.1f}", fontsize=FS_ANNOT, va="center", ha="right",
                color=RED_TXT if d >= 5 else TXT, zorder=200,
                path_effects=[pe.withStroke(linewidth=2.4, foreground="white")])
        ax.text(1.66, i + 0.02, m + (" \u2020" if m in censored else ""), fontsize=FS_TICK,
                va="center", ha="right", color=NAVY if rea else CYAN_TXT, zorder=200,
                path_effects=[pe.withStroke(linewidth=2.4, foreground="white")])

    ax.set_xlim(1.62, 5.68); ax.set_ylim(-0.5, len(models) + OVER - 0.5)
    ax.set_xticks([2, 3, 4, 5]); ax.set_xticklabels(["100", "1k", "10k", "100k"])
    ax.set_yticks([]); ax.spines["left"].set_visible(False)
    ax.set_xlabel("Output tokens spent on one problem (o200k, log scale)\n"
                  f"(N = {int(q[models[0]]['n_problem_runs']):,} problem-runs per configuration; "
                  "bar spans P10\u2013P90, dot marks the median)")
    ax.text(5.62, len(models) + OVER - 0.95, "P90\n/median", fontsize=FS_ANNOT, ha="right",
            va="center", color=INK, style="italic", linespacing=1.25)
    ax.text(1.66, len(models) + OVER - 0.95, "reasoning", fontsize=FS_ANNOT, ha="right",
            va="center", color=NAVY, style="italic")
    ax.text(1.66, len(models) + OVER - 1.45, "non-reasoning", fontsize=FS_ANNOT, ha="right",
            va="center", color=CYAN_TXT, style="italic")
    ax.grid(axis="x", color=GRID, lw=GRID_LW, zorder=0); ax.set_axisbelow(True)

    tight = min(q, key=lambda m: float(q[m]["p90_over_p50"]))
    wide = max(q, key=lambda m: float(q[m]["p90_over_p50"]))
    worst = max(q, key=lambda m: float(q[m]["mean_over_p50"]))
    note("F4d_spend_profile",
         f"How much a model spends on one problem is a distribution, not a number: the spread "
         f"between a typical problem and an expensive one ranges from {float(q[tight]['p90_over_p50']):.1f}x "
         f"({tight}) to {float(q[wide]['p90_over_p50']):.1f}x ({wide}), so the per-run means "
         f"reported elsewhere overstate the typical problem by as much as "
         f"{float(q[worst]['mean_over_p50']):.1f}x ({worst}).",
         f"""Distribution of the output tokens each configuration spent on a single problem,
         under the code protocol. The unit of observation is one problem-run, the 436-problem
         core set evaluated three times, and output tokens are completion plus reasoning from the
         repo's own o200k accounting. Rows are ordered by median spend, quietest at the bottom,
         and each ridge is scaled to its own peak so that shape rather than height carries the
         comparison; the white tick is the median and the figure at the right is the ratio of the
         90th percentile to the median, printed in red where a configuration's expensive problems
         cost five times its typical one or more. The horizontal axis is logarithmic because the
         medians alone span two orders of magnitude. The distributions differ in shape and not
         only in position, which is the point: {tight} is almost deterministic
         ({float(q[tight]['p90_over_p50']):.1f}x), while {wide} carries a tail
         {float(q[wide]['p90_over_p50']):.1f}x beyond its median, so a per-run mean, the summary
         used in every other token figure here, sits {float(q[worst]['mean_over_p50']):.1f}x above
         the median problem for {worst}. Daggered configurations return only a summary of the
         chain of thought, so their ridges sit further left than the spend they actually
         incurred.""",
         "`F4d_spend_hist.csv`, `F4d_spend_quantiles.csv` (`extract_figure_data.py spend_dist`)")
    save(fig, "F4d_spend_profile")


# ---------------------------------------------------------------- F5
def f5(into=None):
    rows = load("F5a_main_accuracy.csv")
    col = {"reasoning": NAVY, "non-reasoning": CYAN, "out-of-distribution": SAND}
    if into is None:
        fig, ax = plt.subplots(figsize=(WIDTH_2COL, 4.91), layout="constrained")
    else:
        fig, ax = into, into.add_subplot()
    ys = list(range(len(rows)))
    ax.barh(ys, [float(r["accuracy"]) for r in rows], height=0.68,
            color=[col[r["group"]] for r in rows], zorder=2)
    # error bars with a white casing so they stay visible on the dark reasoning bars
    for y, r in zip(ys, rows):
        v, sd = float(r["accuracy"]), float(r["sd"])
        ax.errorbar(v, y, xerr=sd, fmt="none", ecolor="white", elinewidth=1.8,
                    capsize=2.4, capthick=1.8, zorder=3)
        ax.errorbar(v, y, xerr=sd, fmt="none", ecolor=INK, elinewidth=0.6,
                    capsize=1.7, capthick=0.6, zorder=4)
        ax.text(v + max(sd, 0.4) + 1.1, y, f'{v:.1f}',
                va="center", fontsize=FS_ANNOT, color=INK)
    names = [r["model"] for r in rows]
    if into is not None:                       # composite: (R) buys the bars an extra ~11 mm
        names = [m.replace(" (reasoning)", " (R)") for m in names]
    ax.set_yticks(ys); ax.set_yticklabels(names)
    ax.tick_params(axis="y", length=0)
    ax.invert_yaxis(); ax.set_xlim(0, 108)
    ax.set_xlabel(f"Accuracy (%), mean ± s.d. of 3 runs\n"
                  f"(N = {len(rows)} configurations x 436 problems)")
    disp = {"reasoning": "Reasoning", "non-reasoning": "Non-reasoning",
            "out-of-distribution": "Out-of-distribution"}
    ax.legend(handles=[Line2D([], [], color=v, lw=5, label=disp[k]) for k, v in col.items()],
              loc="lower right", frameon=False, handlelength=1.1)
    ax.grid(axis="x", color=GRID, lw=GRID_LW, zorder=0); ax.set_axisbelow(True)
    panel(ax, "", "Core-set accuracy, code mode (18 configurations)")
    if into is not None:
        return
    note("F5_main_results",
         "Core-set leaderboard, code protocol, 18 configurations.",
         """Accuracy on the 436-problem core set (mean ± s.d. of 3 independent runs; white-cased
         error bars). Navy: reasoning settings; cyan: non-reasoning; sand: the two
         domain-specialised ClimateGPT models, reported as an out-of-distribution reference -
         their near-zero scores show the benchmark measures quantitative reasoning, not
         climate-text familiarity. Accuracy = passed / (passed + failed); infrastructure errors
         are excluded from the denominator (all runs here finished with zero).""",
         "`F5a_main_accuracy.csv`")
    save(fig, "F5_main_results")


# ---------------------------------------------------------------- F24 (difficulty trellis)
SHORT_CAT = {"atmospheric_radiation": "Atmospheric radiation", "climate_dynamics": "Climate dynamics",
             "atmospheric_thermodynamics": "Atmospheric thermodynamics", "boundary_layer": "Boundary layer",
             "atmospheric_dynamics": "Atmospheric dynamics", "observation_and_modeling": "Observation and modeling",
             "atmospheric_chemistry": "Atmospheric chemistry", "air_quality": "Air quality",
             "atmospheric_aerosols": "Atmospheric aerosols", "cloud_physics": "Cloud physics"}
TIERS = ["Frontier", "Strong", "Mid", "Weak"]
# ordinal capability ramp drawn from the repo's CVD-validated NPG set rather than the
# ColorBrewer blue-orange-red the request named: those two warm hues are 3.2:1 and 4.4:1 on
# white, below the 4.5:1 the rest of this supplement holds itself to
TIER_COL = [NAVY, CYAN, SAND, RED]
SPARSE_N = 5                     # a stratum thinner than this is shaded, not read as a measurement


def f24(into=None, order="by_high"):
    """Difficulty-stratified category trellis on the three-run-mean basis.

    Every accuracy in docs/results/ is a mean over the three runs; F17_solve_matrix.csv can only
    yield majority-of-three rates, which run up to 1.6 points higher because a majority absorbs
    one flaky run. This reads the per-run long table instead, which is also what makes the
    run-to-run s.d. on each tier median computable."""
    import numpy as np
    rows = load("F24_run_outcomes.csv")
    D = ["low", "medium", "high"]
    seen, cats = {}, {}
    for r in rows:
        seen[(r["model"], int(r["run"]), r["id"])] = int(r["passed"])
        cats[r["id"]] = (r["category"], r["difficulty"])
    models = sorted({r["model"] for r in rows})

    def per_run(ids, m):                               # the three per-run rates for one cell
        return [100 * sum(seen[(m, n, i)] for i in ids) / len(ids) for n in (1, 2, 3)]

    def acc(ids, m):                                   # mean of the three per-run rates
        return sum(per_run(ids, m)) / 3 if ids else None

    ids_all = list(cats)
    overall = {m: acc(ids_all, m) for m in models}
    ranked = sorted(models, key=lambda m: -overall[m])   # tiers computed on THIS basis
    tier_of = {m: i // 4 for i, m in enumerate(ranked)}

    cat_ids = {c: [i for i in cats if cats[i][0] == c] for c in SHORT_CAT}
    cell = {(c, d): [i for i in cat_ids[c] if cats[i][1] == d] for c in SHORT_CAT for d in D}
    high_acc = {c: sum(acc(cell[(c, "high")], m) for m in models) / len(models) for c in SHORT_CAT}
    keys = {"by_high": lambda c: -high_acc[c],
            "by_overall": lambda c: -sum(acc(cat_ids[c], m) for m in models) / len(models),
            "by_n": lambda c: -len(cat_ids[c])}
    cat_order = sorted(SHORT_CAT, key=keys[order])

    if into is None:
        fig = plt.figure(figsize=(WIDTH_2COL, 3.95), layout="constrained")
    else:
        fig = into
    axes = fig.subplots(2, 5, sharey=True)             # sharex stays FALSE: each panel prints
    axes = axes.ravel()                                # its own stratum sizes under the ticks
    xs = [0, 1, 2]
    for k, c in enumerate(cat_order):
        ax = axes[k]
        ns = [len(cell[(c, d)]) for d in D]
        for j, n in enumerate(ns):                     # thin strata are flagged, not read
            if n < SPARSE_N:
                # a band under the axis rather than a full-height wash: shading the whole column
                # made panels with two thin strata (Observation and modeling) read as greyed out
                ax.add_patch(Rectangle((j - 0.34, -6), 0.68, 4.0, facecolor="#dfe3e8",
                                       edgecolor="none", zorder=1, clip_on=False))
        for m in models:
            ax.plot(xs, [acc(cell[(c, d)], m) for d in D], color=TIER_COL[tier_of[m]],
                    lw=0.55, alpha=0.4, zorder=2)
        for t in range(4):
            group = [m for m in models if tier_of[m] == t]
            med = [float(np.median([acc(cell[(c, d)], m) for m in group])) for d in D]
            # RUN-to-run s.d., not between-configuration spread: take the tier median within
            # each run, then the sample s.d. of those three. The two differ sharply (23.7 vs
            # 0.7 points on one cell), and it is the run-to-run quantity the three-run basis
            # buys us and that this figure claims to show.
            sd = [float(np.std([float(np.median([per_run(cell[(c, d)], m)[n] for m in group]))
                                for n in range(3)], ddof=1)) for d in D]
            ax.plot(xs, med, color=TIER_COL[t], lw=1.5, zorder=4)
            for j in range(3):
                ax.errorbar(j, med[j], yerr=sd[j], fmt="none", ecolor=TIER_COL[t],
                            elinewidth=0.7, capsize=1.4, capthick=0.7, zorder=4)
                thin = ns[j] < SPARSE_N
                ax.plot([j], [med[j]], marker="o", ms=3.0, zorder=5, color=TIER_COL[t],
                        mfc="white" if thin else TIER_COL[t], mew=0.9)
        hi = 100 * len(cell[(c, "high")]) / len(cat_ids[c])
        ax.set_title(f"{SHORT_CAT[c]}\nn = {len(cat_ids[c])} ({hi:.0f}% high)",
                     fontsize=FS_ANNOT, linespacing=1.25, pad=5)
        ax.set_xticks(xs)
        ax.set_xticklabels([f"{lab}\n{n}" for lab, n in zip("LMH", ns)], fontsize=FS_ANNOT,
                           linespacing=1.2)
        # the axis floor sits below zero so the one error bar whose lower arm reaches -2.6
        # (Observation and modeling, high, weak tier) is shown whole rather than sliced by the
        # spine; ticks stay on the meaningful 0-100 range
        ax.set_xlim(-0.38, 2.38); ax.set_ylim(-6, 104)
        ax.set_yticks([0, 25, 50, 75, 100])
        ax.tick_params(length=0)
        ax.grid(axis="y", color=GRID, lw=GRID_LW, zorder=1); ax.set_axisbelow(True)
        if k % 5:
            ax.tick_params(labelleft=False)
        else:
            ax.set_ylabel("Accuracy (%)", fontsize=FS_LABEL)

    # gridspec hspace is a multiple of the axes height under constrained_layout and blows the
    # rows apart; the layout engine takes a figure fraction, which is what we want here
    if into is None:
        fig.get_layout_engine().set(hspace=0.06, wspace=0.03, h_pad=0.02, w_pad=0.02)
    keysL = [Line2D([], [], color=TIER_COL[t], lw=1.5, marker="o", ms=3, label=TIERS[t])
             for t in range(4)]
    keysL += [Line2D([], [], color=MUTED, lw=0.55, alpha=0.6, label="individual configuration"),
              Patch(fc="#dfe3e8", ec="none", label=f"stratum < {SPARSE_N} problems"),
              Line2D([], [], color=MUTED, lw=0.7, marker="|", ms=6, markeredgewidth=0.7,
                     label="\u00b1 1 s.d. over the 3 runs")]
    fig.legend(handles=keysL, loc="outside upper center", ncol=7, frameon=False,
               fontsize=FS_ANNOT, handlelength=1.2, columnspacing=1.1, handletextpad=0.5)
    fig.supxlabel("Intrinsic difficulty stratum (L / M / H), with the number of problems in each\n"
                  f"(N = {len(ids_all)} problems x {len(models)} configurations x 3 runs; "
                  "tier medians computed on the three-run mean)", fontsize=FS_LABEL)
    if into is not None:
        return

    lo = [acc([i for i in cats if cats[i][1] == "low"], m) for m in models]
    hg = [acc([i for i in cats if cats[i][1] == "high"], m) for m in models]
    pen = {t: sum(hg[i] - lo[i] for i, m in enumerate(models) if tier_of[m] == t) / 4
           for t in range(4)}
    spread = {t: float(np.std([sum(acc(cell[(c, "high")], m) for m in models if tier_of[m] == t) / 4
                               for c in SHORT_CAT], ddof=1)) for t in (0, 3)}
    note("F24_difficulty_category_trellis",
         f"Difficulty dominates subject: the high-difficulty penalty deepens from "
         f"{pen[0]:+.1f} points for the frontier tier to {pen[3]:+.1f} for the weak tier, and its "
         f"spread across the ten categories widens from s.d. {spread[0]:.1f} to {spread[3]:.1f}.",
         f"""Accuracy against intrinsic difficulty, one panel per subject category, on the same
         three-run-mean basis as every accuracy in the result tables: a cell value is the mean of
         the three per-run rates over the problems in that (category, difficulty) cell, and the
         error bar on each tier median is the run-to-run sample s.d. (n-1): the tier median is
         taken within each run and the s.d. is over those three values, so the bar shows how much
         the median moves between repetitions rather than how far the four configurations sit
         apart. Thin lines are the {len(models)} individual configurations, thick lines the median
         of the four in each capability tier; tiers are quartiles of overall core-set accuracy
         computed on this basis rather than carried over, which moves two configurations across
         the frontier/strong boundary relative to a majority-of-three ranking. Ticks read L / M /
         H with that panel's stratum size beneath, and axes are deliberately not shared in x so
         each panel shows its own sizes. Eight of the thirty cells hold fewer than
         {SPARSE_N} problems and one holds a single problem: those columns are shaded and their
         tier-median markers drawn hollow, because a rate over one problem is not a measurement.
         Panels run left to right, top to bottom in descending high-difficulty accuracy, so the
         panel order is itself the ranking that matters.""",
         "`F24_run_outcomes.csv` (`extract_figure_data.py run_outcomes`)")
    save(fig, "F24_difficulty_category_trellis")


# ---------------------------------------------------------------- F5 composite
def f5comp():
    """The three headline figures on one canvas for the paper's main figure: the leaderboard
    at the left, the per-problem protocol cost and the efficiency field stacked at the right.
    Each panel is re-drawn live into its subfigure, so this is a vector recomposition at the
    final type size, not a scaled paste-up of the standalone exports."""
    fig = plt.figure(figsize=(WIDTH_2COL, WIDTH_2COL * 2 / 3), layout="constrained")   # 3:2 canvas
    # the third, empty column is a right margin: a centred xlabel overhangs its axes
    # horizontally and constrained_layout reserves no room for that overhang
    left, right, _pad = fig.subfigures(1, 3, width_ratios=[1.14, 1.0, 0.012], wspace=0.02)
    rtop, rbot = right.subfigures(2, 1, height_ratios=[1.0, 1.1], hspace=0.02)
    f5(into=left)
    f2c(into=rtop)
    f4b(into=rbot)
    for sf, letter in ((left, "a"), (rtop, "b"), (rbot, "c")):
        # 12 pt on the 183 mm canvas ~= 9 pt at the typeset \textwidth.
        sf.text(0.012, 0.995, letter, fontsize=12, fontweight="bold", va="top")
    note("F5_composite",
         "Main-figure composite: the leaderboard, the per-problem cost of answering in prose, "
         "and the token-efficiency field, on one canvas.",
         """Composite of the three headline panels at print size. a, Core-set leaderboard
         (as F5_main_results). b, Distribution of output tokens spent on a single problem under
         the code and direct protocols (as F2c_protocol_spend). c, Cost-efficiency map over the
         tokens-per-correct-answer field (as F4b_efficiency_map). Every panel is drawn from the
         same CSVs as its standalone counterpart at identical type size; (R) abbreviates a
         reasoning setting, spelt out by the panel-a legend. See those entries for the full
         captions.""",
         "`F5a_main_accuracy.csv`, `F4d_spend_hist.csv`, `F4d_spend_quantiles.csv`, "
         "`F4_token_accuracy.csv`")
    save(fig, "F5_composite")


# ---------------------------------------------------------------- F6.1 (traps)
def f61a():
    """Standalone: capability gradient of the Trap Gap, with reasoning-twin arrows."""
    rows = load("F6_1_trap_gradient.csv")
    pt = {r["model"]: (float(r["core_accuracy"]), float(r["trap_gap_pp"])) for r in rows}
    pairs = [("gpt-5.5", "gpt-5.5 (reasoning)"),
             ("DeepSeek-V4-flash", "DeepSeek-V4-flash (reasoning)"),
             ("Qwen-3.6-27B", "Qwen-3.6-27B (reasoning)"),
             ("Qwen-3.5-9B", "Qwen-3.5-9B (reasoning)")]
    fig, ax = plt.subplots(figsize=(WIDTH_2COL, 3.98), layout="constrained")
    for nr, re_ in pairs:
        (x0, y0), (x1, y1) = pt[nr], pt[re_]
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0), zorder=2,
                    arrowprops=dict(arrowstyle="->,head_width=0.2,head_length=0.36",
                                    color=GREY, lw=1.0, shrinkA=5, shrinkB=6, alpha=0.9))
        ax.text((x0 + x1) / 2 + 0.5, (y0 + y1) / 2 + 0.7, mfmt(f"-{y0 - y1:.0f}"),
                fontsize=FS_TICK, color=TXT, style="italic", ha="left", va="bottom")
    for r in rows:
        x, y = pt[r["model"]]
        ax.scatter(x, y, marker="o" if r["setting"] == "reasoning" else "s", s=40, zorder=4,
                   facecolor=NAVY if r["setting"] == "reasoning" else CYAN,
                   edgecolor="white", lw=0.8)
    # point offsets so spacing is independent of the figure size
    lab = {"Qwen-3.5-9B": (7, 3, "left"), "Qwen-3.6-27B": (-6, 5, "right"),
           "DeepSeek-V4-flash": (7, 4, "left"), "gpt-5.5": (-8, 1, "right"),
           "Gemini-3.1-Pro (reasoning)": (0, -10, "center")}
    for m, (dx, dy, ha) in lab.items():
        name = "Gemini-3.1-Pro (R)" if m.startswith("Gemini") else m
        ax.annotate(name, pt[m], xytext=(dx, dy), textcoords="offset points",
                    fontsize=FS_TICK, ha=ha, va="center", color=INK, zorder=5)
    ax.set_xlabel(f"Core-set accuracy (%)\n(N = {len(rows)} configurations)"); ax.set_ylabel("Trap Gap (pp)")
    ax.set_xlim(57, 103); ax.set_ylim(-4, 41)
    ax.legend(handles=[
        Line2D([], [], ls="none", marker="o", ms=4.5, mfc=NAVY, mec="white", label="Reasoning"),
        Line2D([], [], ls="none", marker="s", ms=4.5, mfc=CYAN, mec="white", label="Non-reasoning"),
        Line2D([], [], color=GREY, lw=1.0, marker=">", ms=3.5, mfc=GREY, label="Thinking on (−pp)")],
        loc="lower left", frameon=False, handlelength=1.4, borderaxespad=0.2)
    ax.grid(color=GRID, lw=GRID_LW, zorder=0); ax.set_axisbelow(True)
    panel(ax, "")
    gaps = {m: pt[m][1] for m in pt}
    note("F6_1a_trap_gradient",
         "Susceptibility to the trap shortcut falls with capability, and enabling reasoning "
         "shrinks it further without ever closing it.",
         f"""Trap Gap against core-set accuracy for the nine configurations evaluated on the
         67-trap diagnostic set (three runs each). The Trap Gap is the failure rate on traps
         restricted to those whose untouched parent problem the same model solves in the
         run-matched core experiment, so it measures susceptibility to the trigger rather than
         general incompetence. Grey arrows connect each backbone's non-reasoning setting to its
         reasoning twin and are labelled with the reduction in points. The gap falls from
         {max(gaps.values()):.0f} pp at the weakest configuration to {min(gaps.values()):.0f} pp
         at the strongest, and every arrow points down, but none reaches zero.""",
         "`F6_1_trap_gradient.csv`")
    save(fig, "F6_1a_trap_gradient")


def f61b():
    """Standalone: pooled solve rate by trap mechanism family."""
    fam = load("F6_1b_trap_family.csv")
    fig, ax = plt.subplots(figsize=(WIDTH_1COL, 2.4), layout="constrained")
    ys = list(range(len(fam)))[::-1]
    ax.barh(ys, [float(r["solve_rate_pct"]) for r in fam], height=0.62, color=NAVY, zorder=3)
    for y, r in zip(ys, fam):
        ax.text(float(r["solve_rate_pct"]) + 1.5, y, f'{float(r["solve_rate_pct"]):.0f}%',
                fontsize=FS_TICK, va="center", color=INK)
        ax.text(1.5, y, f'N = {r["total"]}', fontsize=FS_ANNOT, va="center", color="white", zorder=4)
    ax.set_yticks(ys)
    ax.set_yticklabels([r["family"].replace("_", " ").capitalize() for r in fam])
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Pooled solve rate (%)   (N = model-runs in the family)")
    ax.grid(axis="x", color=GRID, lw=GRID_LW, zorder=0); ax.set_axisbelow(True)
    panel(ax, "")
    hardest, easiest = fam[0], fam[-1]
    note("F6_1b_trap_family",
         "Traps are hardest where a stated condition silently invalidates the default regime.",
         f"""Pooled solve rate for each trap mechanism family over all nine configurations and
         three runs (n is the number of model-runs contributing to the family). Regime-boundary
         triggers, where a parameter sits just past the validity threshold of the canonical
         formula, are solved in only {float(hardest["solve_rate_pct"]):.0f}% of runs, against
         {float(easiest["solve_rate_pct"]):.0f}% for {easiest["family"].replace("_", " ")}
         triggers. Models therefore reproduce named formulae and unit conventions reliably and
         fail most often when a condition in the text silently removes the default regime.
         The per-configuration resolution of the same measurement is given separately.""",
         "`F6_1b_trap_family.csv` (regenerate: `uv run python supplement/extract_figure_data.py trap_family`)")
    save(fig, "F6_1b_trap_family")


def f61c():
    """Standalone: convergence of failures onto the exact predicted shortcut."""
    cap = load("F6_1c_shortcut_capture.csv")[:5][::-1]
    fig, ax = plt.subplots(figsize=(WIDTH_1COL, 2.18), layout="constrained")
    ys = list(range(len(cap)))
    ax.barh(ys, [int(r["capture_runs"]) for r in cap], height=0.62, color=NAVY, zorder=3)
    for y, r in zip(ys, cap):
        star = " *" if r["includes_frontier"] == "yes" else ""
        ax.text(int(r["capture_runs"]) + 0.4, y,
                f'{r["capture_runs"]}/27 · {r["capture_configs"]} models{star}',
                fontsize=FS_ANNOT, va="center", color=INK)
    ax.set_yticks(ys); ax.set_yticklabels([r["trap"] for r in cap])
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, 27); ax.set_xticks([0, 9, 18, 27])
    ax.set_xlabel("Runs emitting the exact predicted shortcut value\n"
                  f"(N = {int(cap[0]['total_runs'])} model-runs per trap)")
    ax.grid(axis="x", color=GRID, lw=GRID_LW, zorder=0); ax.set_axisbelow(True)
    panel(ax, "")
    top = cap[-1]
    note("F6_1c_shortcut_capture",
         "Trap failures are not idiosyncratic: independent models converge on the one wrong "
         "value the trap predicts.",
         f"""The five traps with the highest shortcut capture, counted over 9 configurations x 3
         runs = 27 model-runs each. A run counts as captured only when it failed and every
         sub-answer it returned matches the corresponding output of the trap's stored
         shortcut solver within 2%, so a capture is the trap's exact predicted wrong answer
         rather than any wrong answer. The leading case, {top["trap"]}, captures
         {top["capture_runs"]} of 27 runs across {top["capture_configs"]} distinct
         configurations. An asterisk marks traps whose capturers include a frontier
         configuration, showing that these shortcuts are not an artefact of low capability.""",
         "`F6_1c_shortcut_capture.csv` (regenerate: `uv run python supplement/extract_figure_data.py trap_capture`); capture rule per `docs/results/TRAP_RESULTS.md` Table 4")
    save(fig, "F6_1c_shortcut_capture")


def f61d():
    """The same verdicts as the trap raster, but with the columns grouped by mechanism
    family, so family difficulty appears as vertical bands across every model-run."""
    import numpy as np
    from matplotlib.colors import ListedColormap
    from matplotlib.patches import Patch
    rows = load("F18_trap_matrix.csv")
    fam_order = [r["family"] for r in load("F6_1b_trap_family.csv")]   # hardest to easiest
    sizes = {r["family"]: int(r["n_traps"]) for r in load("F6_1b_family_sizes.csv")}

    by_trap = {}
    for r in rows:
        e = by_trap.setdefault(r["trap"], {"family": r["family"], "cells": {}, "fail": 0})
        e["cells"][(r["model"], r["run"])] = r["state"]
        if r["state"] != "pass":
            e["fail"] += 1

    configs = ["gemini-3.1-pro", "gpt55-reasoning", "gpt55", "deepseek-v4-flash-reasoning",
               "qwen3.6-27b-reasoning", "qwen3.6-27b", "deepseek-v4-flash",
               "qwen3.5-9b-reasoning", "qwen3.5-9b"]
    disp = {"gemini-3.1-pro": "Gemini-3.1-Pro (R)", "gpt55-reasoning": "gpt-5.5 (R)",
            "gpt55": "gpt-5.5", "deepseek-v4-flash-reasoning": "DeepSeek-V4-flash (R)",
            "qwen3.6-27b-reasoning": "Qwen-3.6-27B (R)", "qwen3.6-27b": "Qwen-3.6-27B",
            "deepseek-v4-flash": "DeepSeek-V4-flash", "qwen3.5-9b-reasoning": "Qwen-3.5-9B (R)",
            "qwen3.5-9b": "Qwen-3.5-9B"}
    state_ix = {"pass": 0, "fail": 1, "captured": 2}

    GAP = 2
    cols, bands = [], []          # cols: trap id or None (gap); bands: (centre, family)
    for f in fam_order:
        members = sorted([t for t in by_trap if by_trap[t]["family"] == f],
                         key=lambda t: (-by_trap[t]["fail"], t))
        start_ix = len(cols)
        cols += members
        bands.append(((start_ix + len(cols) - 1) / 2, f, len(members)))
        cols += [None] * GAP
    cols = cols[:-GAP]

    M = np.full((len(configs) * 3, len(cols)), -1)
    for j, t in enumerate(cols):
        if t is None:
            continue
        for i, m in enumerate(configs):
            for k, run in enumerate("123"):
                M[i * 3 + k, j] = state_ix[by_trap[t]["cells"][(m, run)]]
    Mm = np.ma.masked_equal(M, -1)

    fig, ax = plt.subplots(figsize=(WIDTH_2COL, 3.43), layout="constrained")
    cmap = ListedColormap(["#eef1f6", "#a9b4c6", RED])
    cmap.set_bad("white")
    ax.imshow(Mm, aspect="auto", interpolation="nearest", cmap=cmap, vmin=0, vmax=2)
    for g in range(1, len(configs)):
        ax.axhline(g * 3 - 0.5, color="white", lw=1.4)
    ax.set_yticks([i * 3 + 1 for i in range(len(configs))])
    ax.set_yticklabels([disp[c] for c in configs], fontsize=FS_ANNOT)
    ax.tick_params(length=0)
    ax.set_xticks([c for c, _, _ in bands])
    ax.set_xticklabels([f'{f.replace("_", chr(10)).capitalize()}\n(N = {n})' for _, f, n in bands],
                       fontsize=FS_ANNOT)
    ax.set_xlabel("Trap mechanism family, hardest to easiest (N = traps in the family)",
                  labelpad=6)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.legend(handles=[Patch(fc="#eef1f6", ec=GRID, label="Solved"),
                       Patch(fc="#a9b4c6", label="Failed, other error"),
                       Patch(fc=RED, label="Failed with the exact predicted shortcut")],
              loc="lower left", frameon=False, ncol=3, fontsize=FS_ANNOT,
              handlelength=1.1, handleheight=0.9, bbox_to_anchor=(0.0, -0.30))

    pooled = {r["family"]: float(r["solve_rate_pct"]) for r in load("F6_1b_trap_family.csv")}
    hardest, easiest = fam_order[0], fam_order[-1]
    note("F6_1d_trap_family_matrix",
         "Family difficulty is a vertical band that survives every capability level: the "
         "hardest mechanism stays hardest for the strongest model.",
         f"""Every trap verdict, arranged as in the trap raster but with the 67 columns grouped
         by mechanism family rather than by capture count. Rows are the nine configurations,
         three runs each, ordered by overall trap accuracy; families run hardest to easiest by
         pooled solve rate, with the count of traps under each label and blank columns
         separating the bands. Colour encodes the verdict: solved, failed for some other
         reason, or failed with the exact value predicted by the trap's stored shortcut solver
         (every returned sub-answer within 2% of it). The {hardest.replace("_", " ")} band is
         visibly darker than every other band in every row, from
         {pooled[hardest]:.0f}% pooled solve rate against {pooled[easiest]:.0f}% for
         {easiest.replace("_", " ")}, and the darkness does not thin out towards the top rows,
         so the difficulty belongs to the trigger mechanism rather than to weak models. The
         per-configuration and per-family rates behind this raster are tabulated in
         `F6_1b_matrix.csv`.""",
         "`F18_trap_matrix.csv`, `F6_1b_trap_family.csv`, `F6_1b_family_sizes.csv` (regenerate: `uv run python supplement/extract_figure_data.py trap_matrix trap_family trap_family_matrix`)")
    save(fig, "F6_1d_trap_family_matrix")


# ---------------------------------------------------------------- F6.2 (forest)
def f62():
    """The contamination claim as it actually is: paired effect sizes with 95% CIs
    straddling zero, per family — not sixteen flat slope lines."""
    rows = load("F6_2_forest.csv")
    fam = {f: ordered([r for r in rows if r["family"] == f]) for f in ("numeric", "paraphrase")}
    n = len(fam["numeric"])
    ys = list(range(n))[::-1]
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH_2COL, 3.82), sharey=True,
                             gridspec_kw=dict(wspace=0.08), layout="constrained")
    min_holm = min(float(r["p_holm"]) for r in rows)
    npar = {r["family"]: int(r["n_parents"]) for r in rows}
    for ax, family in zip(axes, ("numeric", "paraphrase")):
        ax.axvline(0, color=MUTED, lw=0.8, zorder=1)
        for y, r in zip(ys, fam[family]):
            d, lo, hi = (float(r[k]) for k in ("delta_pt", "ci_lo_pt", "ci_hi_pt"))
            sig = float(r["mcnemar_p"]) < 0.05
            colr = RED if sig else NAVY
            ax.plot([lo, hi], [y, y], color=colr, lw=1.0, zorder=2,
                    solid_capstyle="butt", alpha=0.9)
            ax.plot(d, y, "o", ms=3.6, color=colr, zorder=3,
                    markeredgecolor="white", markeredgewidth=0.5)
            if sig:
                ax.text(hi + 0.35, y, f'p={float(r["mcnemar_p"]):.3f}',
                        fontsize=FS_ANNOT, color=INK, va="center")
        ax.set_xlim(-7.2, 8.6)
        ax.set_xlabel("Δ parent-level accuracy, core − "
                      f"{family} variants (pt)\npaired over N = {npar[family]} parent problems")
        ax.grid(axis="x", color=GRID, lw=GRID_LW, zorder=0); ax.set_axisbelow(True)
        panel(ax, "ab"[axes.tolist().index(ax)] if hasattr(axes, "tolist") else "")
    axes[0].set_yticks(ys)
    axes[0].set_yticklabels([r["model"] for r in fam["numeric"]])
    axes[0].tick_params(axis="y", length=0)
    note("F6_2_variant_robustness",
         "Numeric and paraphrase perturbation move accuracy by about zero - no detectable contamination.",
         f"""Forest plot of the paired shift Delta per model, with analytic 95% CIs. The unit of
         analysis is the parent problem, not the individual variant: for each of the
         {npar["numeric"]} perturbable parents (numeric family) and {npar["paraphrase"]} parents
         (paraphrase family), the model either solves the parent problem itself, counted on a
         majority of its three runs, or holds the parent's variant family, counted when at least
         three of its five variants are solved on the same majority rule. Delta is the difference
         between those two accuracies over the identical set of parents, which is what makes the
         comparison paired and the exact McNemar test applicable. Red rows are the only tests with
         uncorrected McNemar p < 0.05; none survives Holm correction across the 16 tests per family
         (smallest Holm-adjusted p = {min_holm:.2f}). CIs come from the analysis module itself
         (eval.analysis.robustness), so figure and analysis cannot drift apart.""",
         "`F6_2_forest.csv` (regenerate: `uv run python supplement/extract_figure_data.py forest`)")
    save(fig, "F6_2_variant_robustness")


# ---------------------------------------------------------------- F6.3 (prompt sensitivity)
def f63():
    rows = load("F6_3_prompt_sensitivity.csv")
    disp = {"Gemini-3.1-Pro (reasoning)": "Gemini-3.1-Pro (R)"}
    hue = dict(zip([r["model"] for r in rows], [NAVY, TEAL, CYAN, RED]))
    fig, (a, b) = plt.subplots(1, 2, figsize=(WIDTH_2COL, 2.9),
                               gridspec_kw=dict(width_ratios=[1.35, 1], wspace=0.30), layout="constrained")
    slope(a, rows, "permissive_acc", "codeonly_acc",
          lambda r: f'{disp.get(r["model"], r["model"])}  '
                    + mfmt(f'{float(r["codeonly_acc"]) - float(r["permissive_acc"]):+.1f}'),
          [hue[r["model"]] for r in rows], gap=2.6)
    a.set_xticklabels(["Permissive", "Code-only"])
    a.set_ylabel("Accuracy (%)")
    panel(a, "a", "Accuracy")

    ys = list(range(len(rows)))[::-1]
    for y, r in zip(ys, rows):
        p, c = float(r["unrecoverable_permissive"]), float(r["unrecoverable_codeonly"])
        b.barh(y + 0.19, p, height=0.34, color=hue[r["model"]], alpha=0.45, zorder=3)
        b.barh(y - 0.19, c, height=0.34, color=hue[r["model"]], zorder=3)
        b.text(p + 0.7, y + 0.19, f"{p:.0f}", fontsize=FS_ANNOT, va="center", color=TXT)
        b.text(c + 0.7, y - 0.19, f"{c:.0f}", fontsize=FS_ANNOT, va="center", color=INK)
    b.set_yticks(ys)
    b.set_yticklabels([disp.get(r["model"], r["model"]) for r in rows], fontsize=FS_ANNOT)
    b.tick_params(axis="y", length=0)
    b.set_xlim(0, 42)
    b.set_xlabel("Problems whose code never runs\n(of 436)")
    b.legend(handles=[Line2D([], [], color=GREY, alpha=0.45, lw=5, label="Permissive"),
                      Line2D([], [], color=GREY, lw=5, label="Code-only")],
             loc="upper right", frameon=False, handlelength=1.1)
    b.grid(axis="x", color=GRID, lw=GRID_LW, zorder=0); b.set_axisbelow(True)
    panel(b, "b", "Code that never runs")
    mv = sorted(rows, key=lambda r: float(r["delta"]))[:2]   # the two that move furthest down
    note("F6_3_prompt_sensitivity",
         "A reasonable prompt rewording moves frontier models within noise but collapses the small model - through non-executable code, not physics.",
         f"""Core-set accuracy under two functionally equivalent code-mode prompts: the default
         reasoning-permissive template vs a code-only variant that forbids prose before the code
         block ({len(rows)} models x 3 runs x 436 problems; same hue = same model in both panels).
         (a) Accuracy: the two frontier configurations shift within run noise, while the two that
         move furthest are {mv[0]["model"]} by {float(mv[0]["delta"]):+.1f} and {mv[1]["model"]}
         by {float(mv[1]["delta"]):+.1f} points. (b) Mechanism: problems whose code never runs
         even after the five-attempt repair loop, per run. The count for {mv[0]["model"]} rises
         from {int(mv[0]["unrecoverable_permissive"])} to {int(mv[0]["unrecoverable_codeonly"])};
         every other model stays at
         {max(int(r["unrecoverable_codeonly"]) for r in rows if r is not mv[0])}.
         The accuracy swing is an executability artefact, not a change in scientific
         ability.""",
         "`F6_3_prompt_sensitivity.csv`")
    save(fig, "F6_3_prompt_sensitivity")


def f6():
    f61a(); f61b(); f61c(); f61d(); f62(); f63()


# ---------------------------------------------------------------- F7 (MCQ inflation)
def f7():
    rows = load("F7_mcq_inflation.csv")   # already ordered by code accuracy desc
    inh = [r for r in rows if r["option_source"] == "in-house"]
    d_all = [float(r["delta_all670"]) for r in rows]
    d_cln = [float(r["delta_clean480"]) for r in inh]
    fig, (a, b) = plt.subplots(1, 2, figsize=(WIDTH_2COL, 2.83),
                               gridspec_kw=dict(width_ratios=[1.7, 1], wspace=0.35), layout="constrained")
    ys = list(range(len(rows)))[::-1]
    for y, r in zip(ys, rows):
        code, opt = float(r["code_all670"]), float(r["option_all670"])
        paper = r["option_source"] == "paper"
        a.plot([code, opt], [y, y], color=GRID, lw=1.6, zorder=1, solid_capstyle="butt")
        a.plot(code, y, "o", ms=4.6, color=NAVY, zorder=3,
               markeredgecolor="white", markeredgewidth=0.6)
        a.plot(opt, y, "o", ms=4.6, zorder=3, markerfacecolor="white",
               markeredgecolor=GREY if paper else NAVY, markeredgewidth=1.0)
        a.text((code + opt) / 2, y + 0.22, f'+{opt - code:.0f}', fontsize=FS_ANNOT,
               color=TXT, ha="center", va="bottom")
        if not paper:   # clean-480 residual pair, lighter, slightly below
            cc, oc = float(r["code_clean480"]), float(r["option_clean480"])
            a.plot([cc, oc], [y - 0.26, y - 0.26], color=TEAL, lw=1.0, alpha=0.55, zorder=2)
            a.plot([cc, oc], [y - 0.26, y - 0.26], "o", ms=2.4, color=TEAL, alpha=0.8, zorder=3)
    a.set_yticks(ys)
    a.set_yticklabels([r["model"] + (" ‡" if r["option_source"] == "paper" else "")
                       for r in rows])
    a.tick_params(axis="y", length=0)
    a.set_xlim(0, 100); a.set_xlabel("Accuracy on the same 670 problems (%)")
    a.legend(handles=[
        Line2D([], [], ls="none", marker="o", ms=5, mfc=NAVY, mec="white", label="Compute (code)"),
        Line2D([], [], ls="none", marker="o", ms=5, mfc="white", mec=NAVY, label="Pick a letter (option)"),
        Line2D([], [], color=TEAL, lw=1.2, marker="o", ms=3, alpha=0.7, label="Defect-free 480 only")],
        loc="upper left", bbox_to_anchor=(0.0, 0.98), frameon=False, handlelength=1.4)
    a.grid(axis="x", color=GRID, lw=GRID_LW, zorder=0); a.set_axisbelow(True)
    panel(a, "a", f"Letters inflate accuracy by {min(d_all):.0f}–{max(d_all):.0f} pt")

    ys_b = list(range(len(inh)))[::-1]
    b.barh(ys_b, [float(r["rescue_pct"]) for r in inh], height=0.58, color=NAVY, zorder=3)
    b.axvline(25, color=MUTED, lw=0.8, ls="--", zorder=2)
    b.text(25.8, -0.42, "Random (25%)", fontsize=FS_ANNOT, color=TXT, va="center", ha="left")
    b.set_ylim(-0.7, len(inh) - 0.4)
    for y, r in zip(ys_b, inh):
        b.text(float(r["rescue_pct"]) - 2, y,
               f'{float(r["rescue_pct"]):.0f}%  ({r["rescue_correct"]}/{r["rescue_total"]})',
               fontsize=FS_ANNOT, va="center", ha="right", color="white", zorder=4)
    b.set_yticks(ys_b); b.set_yticklabels([r["model"] for r in inh])
    b.tick_params(axis="y", length=0)
    b.set_xlim(0, 100); b.set_xlabel("Code-mode failures scored correct\nby letter choice (%)")
    b.grid(axis="x", color=GRID, lw=GRID_LW, zorder=0); b.set_axisbelow(True)
    panel(b, "b", "Options rescue failed computations")
    note("F7_mcq_inflation",
         f"Picking a letter scores {min(d_all):.0f}-{max(d_all):.0f} points above computing the answer on the same problems.",
         f"""The external AtmosSci-Bench MCQ10 set (670 problems). (a) Per model: accuracy when
         required to compute the answer (filled; code protocol, 5% tolerance) vs when choosing
         among four printed options (open; letter-match). Grey pairs use the full 670; teal pairs
         restrict to the 480 problems on non-defective templates, where the residual gap is still
         +{min(d_cln):.0f}-{max(d_cln):.0f} pt - about half the raw inflation is defective answer
         keys punishing correct derivations, the rest is the option shortcut itself. Double-dagger
         rows: option accuracy as published by the AtmosSci-Bench authors on the same set.
         (b) Of the problems each model failed to compute, the share it nonetheless answered with
         the correct letter (vs the 25% random line): options carry most of the signal.""",
         "`F7_mcq_inflation.csv` (regenerate: `uv run python supplement/extract_figure_data.py mcq`)")
    save(fig, "F7_mcq_inflation")


# ---------------------------------------------------------------- F8 (three axes)
def f8():
    """Construct-validity overview: how much each evaluation choice moves the measured
    score. Fabrication is deliberately an annotation, not a bar — the finding is
    existence made inert, not a rate."""
    mcq = load("F7_mcq_inflation.csv")
    d_all = [float(r["delta_all670"]) for r in mcq]
    proto = [float(r["delta_code_minus_direct"]) for r in load("F2_F3_direct_vs_code.csv")]
    proto_mean = sum(proto) / len(proto)

    fig, ax = plt.subplots(figsize=(WIDTH_1COL, 1.59), layout="constrained")
    # format axis
    ax.plot([min(d_all), max(d_all)], [2, 2], color=NAVY, lw=5, solid_capstyle="butt", zorder=3)
    ax.text(max(d_all) + 1.2, 2, f"+{min(d_all):.0f} to +{max(d_all):.0f} pt",
            fontsize=FS_TICK, va="center", color=INK)
    # protocol axis
    ax.plot([min(proto), max(proto)], [1, 1], color=NAVY, lw=1.2, alpha=0.45,
            solid_capstyle="butt", zorder=2)
    ax.plot(proto_mean, 1, "o", ms=5.5, color=NAVY, zorder=3,
            markeredgecolor="white", markeredgewidth=0.6)
    ax.text(max(proto) + 1.2, 1, mfmt(f"mean {proto_mean:+.1f} pt (range {min(proto):+.1f} to {max(proto):+.1f})"),
            fontsize=FS_TICK, va="center", color=INK)
    # fabrication axis — existence, never a frequency
    ax.plot(0, 0, marker="D", ms=5, color=SAND, zorder=3, markeredgecolor="white")
    ax.text(1.2, 0, "10 confirmed records, score shift 0 pt",
            fontsize=FS_TICK, va="center", color=INK, style="italic")
    ax.axvline(0, color=MUTED, lw=0.8, zorder=1)
    ax.set_yticks([2, 1, 0])
    ax.set_yticklabels(["Format\n(option letter vs computed)",
                        "Protocol\n(code vs direct prose)",
                        "Fabricated execution\n(claimed but never run)"], fontsize=FS_TICK)
    ax.tick_params(axis="y", length=0)
    ax.set_ylim(-0.55, 2.6); ax.set_xlim(-6, 52)
    ax.set_xlabel("Shift in measured accuracy (pt)\n(N = 3 evaluation choices)")
    ax.grid(axis="x", color=GRID, lw=GRID_LW, zorder=0); ax.set_axisbelow(True)
    panel(ax, "", "What the evaluation format does to the measured score")
    note("F8_three_axes",
         "What each evaluation-format choice does to the measured score.",
         f"""Construct-validity summary. Format (option letter vs computed answer, same MCQ10
         problems, 6 models): +{min(d_all):.0f} to +{max(d_all):.0f} points. Protocol (code vs
         direct prose, core set, 6 paired configurations): mean {proto_mean:+.1f} pt, range
         {min(proto):+.1f} to {max(proto):+.1f} - negligible next to format. Fabricated execution
         (a model asserting a computation that never ran): occurs (10 confirmed records) but is
         inert under execution grounding - the graded value is recomputed from the model's own
         program, so the score shift is 0 pt. Deliberately annotated, not plotted as a rate: the
         finding is existence made harmless, not frequency.""",
         "`F7_mcq_inflation.csv`, `F2_F3_direct_vs_code.csv`; fabrication records in `docs/results/FABRICATION_TRACES.md`")
    save(fig, "F8_three_axes")




# ---------------------------------------------------------------- F9 (scaffolding)
def f9():
    rows = load("F9_scaffolding.csv")
    fig, (a, b) = plt.subplots(1, 2, figsize=(WIDTH_2COL, 2.53),
                               gridspec_kw=dict(width_ratios=[1.7, 1], wspace=0.35), layout="constrained")
    ys = list(range(len(rows)))[::-1]
    for y, r in zip(ys, rows):
        w, s = float(r["with_acc"]), float(r["stripped_acc"])
        a.plot([s, w], [y, y], color=GRID, lw=1.6, zorder=1, solid_capstyle="butt")
        a.errorbar(w, y, xerr=float(r["with_sd"]), fmt="o", ms=4.6, color=NAVY,
                   ecolor=NAVY, elinewidth=0.6, capsize=1.6, zorder=3,
                   markeredgecolor="white", markeredgewidth=0.6)
        a.errorbar(s, y, xerr=float(r["stripped_sd"]), fmt="o", ms=4.6, zorder=3,
                   markerfacecolor="white", markeredgecolor=NAVY, markeredgewidth=1.0,
                   ecolor=NAVY, elinewidth=0.6, capsize=1.6)
        a.text((w + s) / 2, y + 0.18, mfmt(f'{float(r["delta"]):+.1f}'), fontsize=FS_ANNOT,
               color=TXT, ha="center", va="bottom")
        a.text(s - float(r["stripped_sd"]) - 1.2, y, f'{r["lost_maj3"]} lost',
               fontsize=FS_ANNOT, color=TXT, ha="right", va="center")
    a.set_yticks(ys); a.set_yticklabels([r["model"] for r in rows])
    a.tick_params(axis="y", length=0)
    a.set_xlim(58, 102); a.set_ylim(-0.55, 3.75)
    a.set_xlabel("Accuracy on the 169 paired problems (%)")
    a.legend(handles=[
        Line2D([], [], ls="none", marker="o", ms=5, mfc=NAVY, mec="white", label="With scaffolding"),
        Line2D([], [], ls="none", marker="o", ms=5, mfc="white", mec=NAVY, label="Scaffolding removed")],
        loc="upper left", frameon=False, handlelength=1.2)
    a.grid(axis="x", color=GRID, lw=GRID_LW, zorder=0); a.set_axisbelow(True)
    panel(a, "a", "Removing handed-over knowledge costs small models most")

    spread_w = max(float(r["with_acc"]) for r in rows) - min(float(r["with_acc"]) for r in rows)
    spread_s = max(float(r["stripped_acc"]) for r in rows) - min(float(r["stripped_acc"]) for r in rows)
    b.bar([0, 1], [spread_w, spread_s], width=0.55, color=[GREY, NAVY], zorder=3)
    for x, v in ((0, spread_w), (1, spread_s)):
        b.text(x, v + 0.7, f"{v:.1f} pt", ha="center", fontsize=FS_TICK, color=INK)
    b.annotate(f"×{spread_s / spread_w:.1f}", (0.5, spread_s * 0.82), ha="center",
               fontsize=FS_LABEL, color=INK, fontweight="bold")
    b.set_xticks([0, 1]); b.set_xticklabels(["With\nscaffolding", "Scaffolding\nremoved"])
    b.tick_params(axis="x", length=0)
    b.set_ylim(0, spread_s * 1.18)
    b.set_ylabel("Model separation, max − min (pt)")
    b.grid(axis="y", color=GRID, lw=GRID_LW, zorder=0); b.set_axisbelow(True)
    panel(b, "b", "Separation more than doubles")
    note("F9_scaffolding_ablation",
         "Removing handed-over knowledge costs small models most and more than doubles model separation.",
         f"""The scaffolding ablation: 169 core problems whose original statements handed over
         recallable formulas or constants, evaluated in both forms (4 models x 3 runs; identical
         reference solver and answers, so only the statement differs). (a) Accuracy with the
         scaffolding (filled) vs with it removed (open), ± 3-run s.d.; the drop grows
         monotonically as model scale falls, and 'lost' counts problems solved with scaffolding
         but not without (majority-of-3). (b) The max-min spread across the four models widens
         from {spread_w:.1f} to {spread_s:.1f} pt (x{spread_s / spread_w:.1f}): converting
         'apply the supplied relation' into 'recall it, then apply it' is what exposes capability
         differences.""",
         "`F9_scaffolding.csv` (regenerate: `uv run python supplement/extract_figure_data.py scaffold`)")
    save(fig, "F9_scaffolding_ablation")


# ---------------------------------------------------------------- F10 (cross-domain)
def f10():
    rows = load("F10_cross_domain.csv")
    core = {r["model"]: float(r["accuracy"]) for r in load("F4_token_accuracy.csv")}
    # wspace 0.5 dated from the floating-canvas era; on a fixed 183 mm canvas it opened a dead
    # white channel between the panels. b's y labels are long, so the gap it needs is set by
    # those, not by a hand-tuned fraction: constrained_layout finds it from wspace 0.06.
    fig, (a, b) = plt.subplots(1, 2, figsize=(WIDTH_2COL, 2.75),
                               gridspec_kw=dict(width_ratios=[1.0, 1.12], wspace=0.06),
                               layout="constrained")
    a.plot([30, 100], [30, 100], color=MUTED, lw=0.8, ls="--", zorder=1)
    a.text(53.5, 50.0, "y = x", fontsize=FS_ANNOT, color=TXT, style="italic",
           ha="left", rotation=45, rotation_mode="anchor")
    off = {"gpt-5.5": (-1.2, 2.4, "right"), "Kimi K2.6": (2.2, -0.8, "left"),
           "DeepSeek-V4-flash": (-2.2, 0.2, "right"), "Qwen-3.6-27B": (0.4, -3.4, "left"),
           "Qwen-2.5-72B": (2.2, -0.8, "left")}
    for r in rows:
        x, y = core[r["model"]], float(r["overall"])
        # ms=4.6 matches panel b's dumbbell dots: scatter takes AREA in pt^2, so the
        # equivalent of a 4.6 pt diameter is 4.6^2, not the 34 this used to carry
        a.scatter(x, y, s=4.6 ** 2, color=NAVY, zorder=3, edgecolor="white", lw=0.6)
        dx, dy, ha = off[r["model"]]
        a.text(x + dx, y + dy, r["model"], fontsize=FS_ANNOT, ha=ha, va="center", color=INK)
    a.set_xlim(30, 100); a.set_ylim(30, 100)
    a.set_xlabel("Core-set accuracy (atmospheric, %)")
    a.set_ylabel("Cross-domain accuracy\n(131 problems, 4 fields, %)")
    a.grid(color=GRID, lw=GRID_LW, zorder=0); a.set_axisbelow(True)
    a.set_aspect("equal")
    panel(a, "a", "Scores transfer across fields")

    gaps = sorted(load("F10b_domain_gaps.csv"), key=lambda r: float(r["gap"]))
    ys = list(range(len(gaps)))
    for y, r in zip(ys, gaps):
        s, w = float(r["strong4_mean"]), float(r["weak"])
        b.plot([w, s], [y, y], color=GRID, lw=1.6, zorder=1, solid_capstyle="butt")
        b.plot(s, y, "o", ms=4.6, color=NAVY, zorder=3, markeredgecolor="white", markeredgewidth=0.6)
        b.plot(w, y, "s", ms=4.4, color=CYAN, zorder=3, markeredgecolor="white", markeredgewidth=0.6)
        b.text((s + w) / 2, y + 0.16, f'{float(r["gap"]):.0f} pt', fontsize=FS_ANNOT,
               color=TXT, ha="center", va="bottom")
    b.set_yticks(ys)
    # every label stays on ONE line: a wrapped tick label is centred on its tick, so the
    # dumbbell for the wrapped row landed in the gap BETWEEN the two lines while the unwrapped
    # rows sat flush with theirs. Abbreviating is cheaper than the 12 mm a full second word
    # would take out of the plotting areas on a fixed 183 mm canvas.
    ABBR = {"environmental_chemistry": "Env. chemistry"}

    def dom_label(r):
        name = ABBR.get(r["domain"], r["domain"].replace("_", " ").capitalize())
        return f'{name} (N = {r["n"]})'
    b.set_yticklabels([dom_label(r) for r in gaps])
    b.tick_params(axis="y", length=0)
    b.set_xlim(0, 100); b.set_ylim(-0.6, 3.65); b.set_xlabel("Accuracy (%)")
    b.legend(handles=[
        Line2D([], [], ls="none", marker="o", ms=4.6, mfc=NAVY, mec="white", label="Strong-4 mean"),
        Line2D([], [], ls="none", marker="s", ms=4.6, mfc=CYAN, mec="white", label="Qwen-2.5-72B")],
        loc="lower left", frameon=False, handlelength=1.2)
    b.grid(axis="x", color=GRID, lw=GRID_LW, zorder=0); b.set_axisbelow(True)
    panel(b, "b", "Multi-step domains discriminate most")
    weak = min(rows, key=lambda r: float(r["overall"]))
    weak_cross = float(weak["overall"])
    weak_core = float(next(r["accuracy"] for r in load("F4_token_accuracy.csv")
                           if r["model"] == weak["model"]))
    note("F10_cross_domain",
         "The construction protocol, not the subject matter, sets the score.",
         f"""(a) Accuracy on the atmospheric core set (x; 3-run mean) against the 131-problem
         cross-domain suite built by the identical pipeline for hydrology, environmental
         chemistry, ecology and soil mechanics (y; single run). All five models hug the y = x
         diagonal and keep their exact ordering; the weakest model scores {weak_core:.1f}% in
         atmospheric science and {weak_cross:.1f}% across four unrelated fields. (b) Per-domain gap between the four
         strong models' mean and the weak reference: long multi-step reactor/treatment chains
         (environmental chemistry) discriminate hardest, short budget-style problems (ecology)
         least - a guide for what to mine when extending the benchmark.""",
         "`F10_cross_domain.csv`, `F10b_domain_gaps.csv` + core accuracies from `F4_token_accuracy.csv`")
    save(fig, "F10_cross_domain")


# ---------------------------------------------------------------- F11 (discrimination)
def f11():
    rows = load("F11_discrimination.csv")
    counts = {d: [0] * 17 for d in ("low", "medium", "high")}
    for r in rows:
        counts[r["difficulty"]][int(r["solved_by_n_of_16"])] += 1
    xs = list(range(17))
    fig, ax = plt.subplots(figsize=(WIDTH_1COL, 2.58), layout="constrained")
    dcol = {"low": "#c6d3e3", "medium": "#7f9cc0", "high": NAVY}
    bottom = [0] * 17
    for d in ("low", "medium", "high"):
        ax.bar(xs, counts[d], width=0.8, bottom=bottom, color=dcol[d], zorder=3,
               label=f"{d.capitalize()} difficulty")
        bottom = [b + c for b, c in zip(bottom, counts[d])]
    total = {x: bottom[x] for x in xs}
    unsolved = [r["id"] for r in rows if r["solved_by_n_of_16"] == "0"]
    tail = sum(total[x] for x in range(4))
    ax.set_xticks(xs)
    ax.set_xlabel("Configurations solving the problem (of 16)")
    ax.set_ylabel("Core problems")
    ax.legend(frameon=False, loc="upper left", handlelength=1.1)
    ax.grid(axis="y", color=GRID, lw=GRID_LW, zorder=0); ax.set_axisbelow(True)
    panel(ax, "", "Difficulty is a long live tail, not a saturated block")
    note("F11_discrimination",
         "Difficulty is a long live tail: one problem defeats every configuration, none is dead weight, and the label tracks solvability.",
         f"""Item-discrimination profile of the core set: each of the 436 problems is placed by
         how many of the 16 leaderboard configurations solve it (majority-of-3 runs), stacked by
         the intrinsic difficulty label. {total[16]} problems are solved by all 16 (the shared
         easy mass), {tail} by three or fewer (the tail that separates frontier models), and
         exactly one ({unsolved[0]}) by none. High-difficulty problems (dark) dominate the tail
         while low-difficulty ones (light) sit almost entirely at 15-16, so the rubric-based
         label agrees with realised solvability.""",
         "`F11_discrimination.csv` (regenerate: `uv run python supplement/extract_figure_data.py discrimination`)")
    save(fig, "F11_discrimination")


# ---------------------------------------------------------------- F12 (echo funnel)
def f12():
    rows = load("F12_echo_funnel.csv")
    fig, ax = plt.subplots(figsize=(WIDTH_1COL, 1.97), layout="constrained")
    ys = list(range(len(rows)))[::-1]
    prev = None
    for y, r in zip(ys, rows):
        n = int(r["count"])
        last = r is rows[-1]
        ax.barh(y, n, height=0.62, color=SAND if last else NAVY, zorder=3)
        share = f"  ({100 * n / prev:.1f}%)" if prev else ""
        ax.text(n * 1.25, y, f"{n:,}{share}", fontsize=FS_ANNOT, va="center", color=INK)
        prev = n
    ax.set_xscale("log"); ax.set_xlim(0.8, 3e5)
    ax.set_yticks(ys)
    ax.set_yticklabels([r["stage"][:1].upper() + r["stage"][1:] for r in rows])
    ax.tick_params(axis="y", length=0)
    ax.set_xlabel(f"Count (log scale)\n(N = {int(rows[0]['count']):,} variant instance-runs at the funnel mouth)")
    ax.grid(axis="x", color=GRID, lw=GRID_LW, zorder=0); ax.set_axisbelow(True)
    panel(ax, "", "Hunting contamination: 83,040 runs distil to 12 nameable problems")
    cap = " → ".join(f'{r["stage"]}: {r["criterion"]}' for r in rows[2:])
    note("F12_echo_funnel",
         "Hunting contamination end-to-end: 83,040 variant runs distil to 12 nameable problems.",
         f"""The contamination evidence chain over the numeric-variant experiments
         ({int(rows[0]["count"]):,} instance-runs = 1,730 variants x 16 configurations x 3 runs),
         log-scale counts; the percentage beside each count is the share of the previous stage retained. Each stage applies a strictly narrower criterion, fixed in the
         analysis code: a failed run counts as a parent-echo only if its answer matches the
         parent's on every graded discriminative sub-answer (parent and variant expected answers
         >5% apart); an echo counts as strict memorisation only if the model also solves the
         parent on the core set; a problem is confirmed leaked only when >=2 independent models
         show strict memorisation. The endpoint (sand; problems, not runs) is released as a
         per-problem flagged list rather than left as an aggregate suspicion.""",
         "`F12_echo_funnel.csv`; stages from `eval.analysis.echo_forensics --json` + `pipeline/reports/contamination_final.json`")
    save(fig, "F12_echo_funnel")






# ---------------------------------------------------------------- F17 (solvability atlas)
def f17():
    """The whole benchmark in one raster: 16 configurations x 436 problems."""
    import numpy as np
    from matplotlib.colors import ListedColormap
    from matplotlib.patches import Patch
    rows = load("F17_solve_matrix.csv")           # already sorted most- to least-solved
    models = MODEL_ORDER                          # leaderboard order, best first
    M = np.array([[int(r[m]) for r in rows] for m in models])
    diff_ix = {"low": 0, "medium": 1, "high": 2}
    D = np.array([[diff_ix[r["difficulty"]] for r in rows]])

    fig, (st, ax) = plt.subplots(2, 1, figsize=(WIDTH_2COL, 3.4), sharex=True,
                                 gridspec_kw=dict(height_ratios=[1, 18], hspace=0.06), layout="constrained")
    st.imshow(D, aspect="auto", cmap=ListedColormap(["#b9e5f2", CYAN, "#177f9c"]),
              interpolation="nearest")
    st.set_yticks([0]); st.set_yticklabels(["Difficulty"], fontsize=FS_ANNOT)
    st.tick_params(length=0)
    for sp in st.spines.values():
        sp.set_visible(False)
    ax.imshow(M, aspect="auto", cmap=ListedColormap(["#eef1f6", NAVY]),
              interpolation="nearest")
    ax.set_yticks(range(len(models)))
    ax.set_yticklabels(models, fontsize=FS_ANNOT)
    ax.tick_params(length=0)
    ax.set_xticks([])
    ax.set_xlabel("436 core problems, sorted from most- to least-solved")
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.legend(handles=[Patch(fc=NAVY, label="Solved (majority-of-3)"),
                       Patch(fc="#eef1f6", ec=GRID, label="Not solved"),
                       Patch(fc="#b9e5f2", label="Low difficulty"),
                       Patch(fc=CYAN, label="Medium"),
                       Patch(fc="#177f9c", label="High")],
              loc="lower left", frameon=False, ncol=5, fontsize=FS_ANNOT,
              handlelength=1.1, handleheight=0.9, columnspacing=1.0,
              bbox_to_anchor=(0.0, -0.22))

    # Guttman-style reproducibility: how close is the raster to perfectly nested?
    errors = 0
    for j, r in enumerate(rows):
        k = int(r["solved_by"])
        ideal = [1] * k + [0] * (len(models) - k)
        errors += sum(1 for a, b in zip(M[:, j], ideal) if a != b)
    rep = 1 - errors / M.size
    n_all = sum(1 for r in rows if int(r["solved_by"]) == len(models))
    n_none = sum(1 for r in rows if int(r["solved_by"]) == 0)
    note("F17_solvability_atlas",
         "The whole benchmark in one picture: capability is a near-nested hierarchy over a "
         "long live tail.",
         f"""Every problem-model outcome in the core evaluation: rows are the 16 leaderboard
         configurations (best on top), columns the 436 problems sorted from most- to
         least-solved (majority-of-3 runs); navy = solved. The raster is close to perfectly
         nested: filling in each column top-down reproduces {100 * rep:.1f}% of the
         {M.size:,} cells, so what separates models is almost entirely *how far down the
         shared difficulty ordering they reach*, not idiosyncratic strengths. The top strip
         marks the intrinsic difficulty label: high-difficulty problems (dark) pile up in the
         sparsely-solved tail. {n_all} problems are solved by every configuration and
         {n_none} by none.""",
         "`F17_solve_matrix.csv` (regenerate: `uv run python supplement/extract_figure_data.py solve_matrix`)")
    save(fig, "F17_solvability_atlas")


# ---------------------------------------------------------------- F18 (trap verdict raster)
def f18():
    """67 traps x 27 model-runs, three states — convergent shortcuts appear as red
    vertical stripes."""
    import numpy as np
    from matplotlib.colors import ListedColormap
    from matplotlib.patches import Patch
    rows = load("F18_trap_matrix.csv")
    by_trap = {}
    for r in rows:
        e = by_trap.setdefault(r["trap"], {"cap": 0, "fail": 0, "cells": {}})
        e["cells"][(r["model"], r["run"])] = r["state"]
        if r["state"] == "captured":
            e["cap"] += 1
        elif r["state"] == "fail":
            e["fail"] += 1
    traps = sorted(by_trap, key=lambda t: (-by_trap[t]["cap"], -by_trap[t]["fail"], t))
    raw2disp = {v: k for k, v in
                {"gpt-5.5 (reasoning)": "gpt55-reasoning",
                 "Gemini-3.1-Pro (reasoning)": "gemini-3.1-pro",
                 "gpt-5.5": "gpt55",
                 "DeepSeek-V4-flash (reasoning)": "deepseek-v4-flash-reasoning",
                 "Qwen-3.6-27B (reasoning)": "qwen3.6-27b-reasoning",
                 "Qwen-3.6-27B": "qwen3.6-27b",
                 "DeepSeek-V4-flash": "deepseek-v4-flash",
                 "Qwen-3.5-9B (reasoning)": "qwen3.5-9b-reasoning",
                 "Qwen-3.5-9B": "qwen3.5-9b"}.items()}
    configs = ["gpt55-reasoning", "gemini-3.1-pro", "gpt55", "deepseek-v4-flash-reasoning",
               "qwen3.6-27b-reasoning", "qwen3.6-27b", "deepseek-v4-flash",
               "qwen3.5-9b-reasoning", "qwen3.5-9b"]
    state_ix = {"pass": 0, "fail": 1, "captured": 2}
    M = np.array([[state_ix[by_trap[t]["cells"][(m, run)]] for t in traps]
                  for m in configs for run in "123"])

    fig, ax = plt.subplots(figsize=(WIDTH_2COL, 3.3), layout="constrained")
    ax.imshow(M, aspect="auto", interpolation="nearest",
              cmap=ListedColormap(["#eef1f6", "#a9b4c6", RED]))
    for g in range(1, len(configs)):
        ax.axhline(g * 3 - 0.5, color="white", lw=1.4)
    ax.set_yticks([i * 3 + 1 for i in range(len(configs))])
    ax.set_yticklabels([raw2disp[c] for c in configs], fontsize=FS_ANNOT)
    ax.tick_params(length=0)
    top = [t for t in traps if by_trap[t]["cap"] >= 4]
    ax.set_xticks([traps.index(t) for t in top])
    ax.set_xticklabels(top, fontsize=FS_ANNOT, rotation=90)
    ax.set_xlabel("67 traps, sorted by shortcut capture")
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.legend(handles=[Patch(fc="#eef1f6", ec=GRID, label="Solved"),
                       Patch(fc="#a9b4c6", label="Failed, other error"),
                       Patch(fc=RED, label="Failed with the exact predicted shortcut")],
              loc="lower left", frameon=False, ncol=3, fontsize=FS_ANNOT,
              handlelength=1.1, handleheight=0.9, bbox_to_anchor=(0.0, -0.34))
    n_cap = sum(e["cap"] for e in by_trap.values())
    note("F18_trap_verdicts",
         "Trap failures are not noise: they line up in columns, on the exact wrong value the "
         "trap predicted.",
         f"""Every trap-set verdict: 9 configurations (rows, 3 runs each, best on top) x 67
         traps (columns, sorted by shortcut capture). Red marks runs whose entire answer vector
         matches the trap's stored shortcut-solver output within 2%: of {sum(e["cap"] + e["fail"] for e in by_trap.values())}
         failures, {n_cap} are such captures, and they concentrate in vertical stripes, with many
         independent models and runs falling into the same predicted hole (labelled columns), rather than scattering. The stripes reach the top rows: even frontier configurations
         take the shortcut on {top[0]}. Grey cells are ordinary wrong answers; the light field
         shows the traps are solvable ({100 * (M == 0).mean():.0f}% of all runs pass).""",
         "`F18_trap_matrix.csv` (regenerate: `uv run python supplement/extract_figure_data.py trap_matrix`)")
    save(fig, "F18_trap_verdicts")


# ---------------------------------------------------------------- F19 (answer space)
def f19():
    """48 real answers to one problem, laid on the answer axis: consensus on the wrong
    value vs collapse across forty orders of magnitude."""
    import math
    rows = load("F19_answer_space.csv")
    fig, (a, b) = plt.subplots(1, 2, figsize=(WIDTH_2COL, 3.4), sharey=True,
                               gridspec_kw=dict(wspace=0.08), layout="constrained")
    ys = {m: i for i, m in enumerate(MODEL_ORDER)}

    def dots(ax, pid, xf):
        pts = [r for r in rows if r["problem"] == pid and r["actual"] != ""]
        for r in pts:
            x = xf(float(r["actual"]))
            if x is None:
                continue
            ok = r["sub_passed"] == "1"
            ax.plot(x, ys[r["model"]], "o", ms=3.6, zorder=3,
                    markerfacecolor=NAVY if ok else "white",
                    markeredgecolor=NAVY if ok else GREY, markeredgewidth=0.9,
                    alpha=0.9)
        return pts

    # (a) 4.5 — the answer is printed in the problem, and half of it is the attractor
    exp45 = float(next(r["expected"] for r in rows if r["problem"] == "4.5"))
    a.axvline(exp45, color=MUTED, lw=0.8, ls="--", zorder=1)
    dots(a, "4.5", lambda v: v if 0.2 <= v <= 1.1 else None)
    a.set_xlim(0.25, 1.08)
    a.set_xticks([0.345, 0.5, 0.7, 0.87, 1.0])
    a.set_xticklabels(["0.345", "0.5", "0.7", "0.87", "1.0"])
    a.set_xlabel("Reported value for problem 4.5,\nequatorial gravity deficit (%)")
    a.set_yticks(range(len(MODEL_ORDER)))
    a.set_yticklabels(MODEL_ORDER, fontsize=FS_ANNOT)
    a.tick_params(axis="y", length=0)
    a.invert_yaxis()
    a.grid(axis="x", color=GRID, lw=GRID_LW, zorder=0); a.set_axisbelow(True)
    panel(a, "a")

    # (b) ry_7.7 — orders of magnitude from the reference
    expb = float(next(r["expected"] for r in rows if r["problem"] == "ry_7.7"))
    b.axvline(0, color=MUTED, lw=0.8, ls="--", zorder=1)

    def to_oom(v):
        if v == 0:
            return -23.5           # parked at the left edge (true zero, off the log axis)
        return math.log10(abs(v) / expb)

    dots(b, "ry_7.7", to_oom)
    b.set_xlim(-25.5, 23)
    b.set_xticks([-20, -10, 0, 10, 20])
    b.set_xlabel("Orders of magnitude from the reference,\nproblem ry_7.7 (log₁₀ |answer / truth|)")
    b.tick_params(axis="y", length=0)
    b.grid(axis="x", color=GRID, lw=GRID_LW, zorder=0); b.set_axisbelow(True)
    b.legend(handles=[Line2D([], [], ls="none", marker="o", ms=4.5, mfc=NAVY, mec=NAVY, label="Within tolerance"),
                      Line2D([], [], ls="none", marker="o", ms=4.5, mfc="white", mec=GREY, label="Failed")],
             loc="lower right", frameon=False, handlelength=1.2, fontsize=FS_ANNOT)
    panel(b, "b")

    n345 = sum(1 for r in rows if r["problem"] == "4.5" and r["actual"] != ""
               and abs(float(r["actual"]) - 0.345) < 0.02)
    note("F19_answer_space",
         "Two ways to be wrong: forty-six answers that agree on the wrong value, and "
         "forty-eight that agree on nothing.",
         f"""Every run's answer to two hand-verified case problems (16 configurations x 3 runs;
         rows in leaderboard order, filled = within the 5% tolerance). (a) Problem 4.5 asks to
         show that effective gravity is ~0.7% weaker at the equator; the target is printed in
         the problem text (dashed line), yet {n345} of 46 gradable runs return 0.345%, exactly
         half of it: the rigid-sphere shortcut that skips the equipotential-bulge term. The
         error is a consensus, cutting across every capability tier: cross-model agreement is
         not correctness. (b) Problem ry_7.7 (collision-coalescence growth) shows the opposite
         failure: below the frontier, answers scatter across forty orders of magnitude with no
         repeated wrong value (two literal zeros are parked at the left edge; one negative
         answer is plotted by magnitude). Structured shortcut versus unstructured collapse: the
         two failure modes that execution grounding exposes but cannot repair.""",
         "`F19_answer_space.csv` (regenerate: `uv run python supplement/extract_figure_data.py answer_space`); cases verified in `docs/results/FAILURE_CASES.md`")
    save(fig, "F19_answer_space")


# ---------------------------------------------------------------- F20 (MCQ verdict atlas)
def f20():
    """670 problems x 3 dual-mode models, four states, split defective | clean."""
    import numpy as np
    from matplotlib.colors import ListedColormap
    from matplotlib.patches import Patch
    rows = load("F20_mcq_verdicts.csv")
    models = ["Gemini-3.1-Pro", "gpt-5.5", "DeepSeek-V4-flash"]   # code accuracy desc
    st = {}
    for r in rows:
        st.setdefault(r["id"], {})[r["model"]] = r["state"]
    defect = {r["id"]: r["defective"] for r in rows}
    state_ix = {"neither": 0, "option-only": 1, "code-only": 2, "both": 3}

    def key(i):
        ss = [st[i][m] for m in models]
        return (-sum(x == "option-only" for x in ss), -sum(x == "neither" for x in ss),
                sum(x == "both" for x in ss), i)

    bad = sorted((i for i in st if defect[i] == "yes"), key=key)
    good = sorted((i for i in st if defect[i] == "no"), key=key)
    GAP = 5
    M = np.full((len(models), len(bad) + GAP + len(good)), -1)
    for j, i in enumerate(bad):
        for y, m in enumerate(models):
            M[y, j] = state_ix[st[i][m]]
    for j, i in enumerate(good):
        for y, m in enumerate(models):
            M[y, len(bad) + GAP + j] = state_ix[st[i][m]]
    Mm = np.ma.masked_equal(M, -1)

    fig, ax = plt.subplots(figsize=(WIDTH_2COL, 2.2), layout="constrained")
    cmap = ListedColormap(["#eef1f6", SAND, TEAL, NAVY])
    cmap.set_bad("white")
    ax.imshow(Mm, aspect="auto", interpolation="nearest", cmap=cmap, vmin=0, vmax=3)
    for g in range(1, len(models)):
        ax.axhline(g - 0.5, color="white", lw=1.2)
    ax.set_yticks(range(len(models)))
    ax.set_yticklabels(models, fontsize=FS_ANNOT)
    ax.set_xticks([len(bad) / 2, len(bad) + GAP + len(good) / 2])
    ax.set_xticklabels([f"{len(bad)} problems on defective templates",
                        f"{len(good)} problems on clean templates"], fontsize=FS_TICK)
    ax.tick_params(length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.legend(handles=[Patch(fc=NAVY, label="Both protocols correct"),
                       Patch(fc=SAND, label="Option letter only"),
                       Patch(fc=TEAL, label="Computed answer only"),
                       Patch(fc="#eef1f6", ec=GRID, label="Neither")],
              loc="lower left", frameon=False, ncol=4, fontsize=FS_ANNOT,
              handlelength=1.1, handleheight=0.9, bbox_to_anchor=(0.0, -0.38))
    n_codeonly_bad = sum(1 for i in bad for m in models if st[i][m] == "code-only")
    sh = [100 * sum(1 for i in bad if st[i][m] == "option-only") / len(bad) for m in models]
    note("F20_mcq_verdict_atlas",
         "On defective answer keys a correct derivation cannot score: the defective block "
         "contains not a single computed-only cell, while the option letter keeps scoring.",
         f"""Every problem-model outcome on the external MCQ10 set for the three models run
         under both protocols (rows, by code accuracy), split into the {len(bad)} problems on
         audit-confirmed defective templates and the {len(good)} on clean ones (columns sorted
         within each block). In the defective block, computed-only (teal) occurs exactly
         {n_codeonly_bad} times across all three models, because the option distractors are generated
         from the stored key, so when the key is wrong a correct derivation is structurally
         unmatchable, while the letter alone still scores on {min(sh):.0f}-{max(sh):.0f}% of
         these problems. The few both-correct columns inside the defective block are templates
         whose specific defect (an unstated sign convention, a misread unit) a model can happen
         to reproduce in code as well. The clean block shows the residual pattern: mostly
         both-correct, with an option-only fringe that is the genuine selection shortcut.""",
         "`F20_mcq_verdicts.csv` (regenerate: `uv run python supplement/extract_figure_data.py mcq_verdicts`)")
    save(fig, "F20_mcq_verdict_atlas")


# ---------------------------------------------------------------- F21 (unit rescue)
def f21():
    rows = load("F21_unit_rescue.csv")[:10]
    totals = {r["model"]: int(r["rescued"]) for r in load("F21b_unit_totals.csv")}
    tot_pass, tot_resc = totals.pop("__total_passing__"), totals.pop("__total_rescued__")
    fig, ax = plt.subplots(figsize=(WIDTH_1COL, 2.6), layout="constrained")
    ys = list(range(len(rows)))[::-1]
    for y, r in zip(ys, rows):
        n = int(r["count"])
        ax.barh(y, n, height=0.6, color=NAVY, zorder=3)
        ax.text(n + 4, y, str(n), fontsize=FS_ANNOT, va="center", color=INK)
    ax.set_yticks(ys)
    ax.set_yticklabels([f'{r["expected_unit"]} → {r["answered_unit"]}' for r in rows],
                       fontsize=FS_ANNOT)
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, 440)
    ax.set_xlabel("Passing sub-answers rescued by unit reconciliation\n"
                  f"(N = {tot_pass:,} passing sub-answers)")
    ax.grid(axis="x", color=GRID, lw=GRID_LW, zorder=0); ax.set_axisbelow(True)
    panel(ax, "")
    note("F21_unit_rescue",
         "A unit-blind grader would mis-mark one in seventeen correct sub-answers.",
         f"""The ten most frequent unit conversions behind passes that a bare numeric compare
         would reject (label: reference unit → the unit the model answered in; the
         dimensionless family, comprising fraction, unitless and empty, is grouped). Across the 16
         leaderboard configurations x 3 runs, {tot_resc:,} of {tot_pass:,} passing sub-answers
         ({100 * tot_resc / tot_pass:.1f}%) pass only through the engine's unit reconciliation,
         and the load is nearly uniform per configuration
         ({min(totals.values())}-{max(totals.values())} each), so it is a property of the
         problems, not of any model's formatting. Unit-aware grading is therefore not leniency
         but a correctness requirement; the same check caught the two false positives in the
         external MCQ audit (km vs m keys).""",
         "`F21_unit_rescue.csv`, `F21b_unit_totals.csv` (regenerate: `uv run python supplement/extract_figure_data.py unit_rescue`); exact replay of `eval.engine.compare_values`")
    save(fig, "F21_unit_rescue")


# ---------------------------------------------------------------- F22 (fragility map)
def f22():
    """346 parents x 16 models: where solving the original but losing the variants
    happens — the picture contamination would have to paint, showing no structure."""
    import numpy as np
    from matplotlib.colors import ListedColormap
    from matplotlib.patches import Patch
    rows = load("F22_fragility.csv")
    st = {}
    for r in rows:
        st.setdefault(r["parent"], {})[r["model"]] = r["state"]
    leaked = {r["parent"] for r in rows if r["leaked"] == "yes"}
    frag = {p: sum(1 for m in st[p].values() if m == "fragile") for p in st}
    parents = sorted(st, key=lambda p: (-frag[p], sum(1 for m in st[p].values() if m == "neither"), p))
    state_ix = {"neither": 0, "gained": 1, "fragile": 2, "both": 3}
    M = np.array([[state_ix[st[p][m]] for p in parents] for m in MODEL_ORDER])

    fig, ax = plt.subplots(figsize=(WIDTH_2COL, 3.2), layout="constrained")
    ax.imshow(M, aspect="auto", interpolation="nearest",
              cmap=ListedColormap(["#eef1f6", CYAN, RED, NAVY]), vmin=0, vmax=3)
    lx = [parents.index(p) for p in leaked]
    ax.scatter(lx, [-1.0] * len(lx), marker="v", s=14, color=INK, clip_on=False, zorder=5)
    ax.set_ylim(len(MODEL_ORDER) - 0.5, -1.6)
    ax.set_yticks(range(len(MODEL_ORDER)))
    ax.set_yticklabels(MODEL_ORDER, fontsize=FS_ANNOT)
    ax.set_xticks([])
    ax.set_xlabel("346 numeric-variantable parents, sorted by fragility")
    ax.tick_params(length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.legend(handles=[Patch(fc=NAVY, label="Core and variants solved"),
                       Patch(fc=RED, label="Fragile: core solved, variants lost"),
                       Patch(fc=CYAN, label="Variants only"),
                       Patch(fc="#eef1f6", ec=GRID, label="Neither"),
                       Line2D([], [], ls="none", marker="v", ms=4, color=INK,
                              label="Confirmed-leaked parent")],
              loc="lower left", frameon=False, ncol=5, fontsize=FS_ANNOT,
              handlelength=1.1, handleheight=0.9, bbox_to_anchor=(-0.02, -0.30))
    n_frag = sum(frag.values())
    on_leaked = sum(frag[p] for p in leaked)
    note("F22_fragility_map",
         "The picture contamination would paint, solved originals collapsing under "
         "perturbation, shows no structure: fragility is sparse, scattered, and not where "
         "the identified leakage sits.",
         f"""Parent-level outcomes over the numeric-variant family (a parent's variants count
         as held if ≥3 of 5 are solved, majority-of-3 runs; columns sorted by how many models
         are fragile on the parent). Fragile cells (red), the signature memorisation would
         produce at scale, number {n_frag} of {M.size:,} ({100 * n_frag / M.size:.1f}%), the
         worst column catches only {max(frag.values())} of 16 models, and just {on_leaked} of
         the {n_frag} sit on the {len(leaked)} echo-confirmed leaked parents (markers): the
         nameable leakage does not explain the residual fragility, which behaves like noise.
         Read against the trap raster, where convergent failure forms solid stripes, this is
         the instrument's negative control: it shows structure where structure exists, and
         none here.""",
         "`F22_fragility.csv` (regenerate: `uv run python supplement/extract_figure_data.py fragility`)")
    save(fig, "F22_fragility_map")


FIGS = {"F0": f0, "F0B": f0b, "F1": f1, "F23": f23, "F2B": f2b, "F2C": f2c, "F4": f4, "F4B": f4b, "F4C": f4c, "F4D": f4d, "F5": f5, "F5C": f5comp, "F6": f6, "F7": f7, "F8": f8,
        "F9": f9, "F10": f10, "F11": f11, "F12": f12,
        "F17": f17, "F18": f18, "F19": f19, "F20": f20, "F21": f21, "F22": f22, "F24": f24}

if __name__ == "__main__":
    for k in (sys.argv[1:] or list(FIGS)):
        print(f"{k}:")
        FIGS[k]()
    flush_notes()
