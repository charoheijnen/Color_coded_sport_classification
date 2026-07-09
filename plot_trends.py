"""
Publication-ready figure of the trends quantified in analyze_trends.py.

Two panels (LV end-diastolic dimension, LV wall thickness) show the athlete-
weighted category mean +/- 95% CI for each Mitchell exercise class, ordered by
training load. Significance brackets compare the standout class (high dynamic +
static) with each of the others (Welch t-test); each panel notes the one-way
ANOVA result.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from analyze_trends import DATA, CAT_NAME, pooled, anova, welch, stars

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.size": 18,
    "axes.edgecolor": "#555555",
})

edge_color = {"blue": "#1f4e9c", "red": "#a01f2e",
              "green": "#1f7a34", "gray": "#4d4d4d"}
fill_color = {"blue": "#4f8ff0", "red": "#e2564f",
              "green": "#43b364", "gray": "#9a9a9a"}

# Categories ordered by training load (low -> combined endurance+power)
ORDER = ["gray", "red", "blue", "green"]
XLABEL = {
    "gray": "Low\nboth",
    "red": "High\nstatic",
    "blue": "High\ndynamic",
    "green": r"High dyn." + "\n" + r"$+$ static",
}


def category_stats(idx_mean, idx_sd):
    """Return {cat: (N, mean, sd, ci)} for one measure."""
    out = {}
    for c in ORDER:
        rows = [(r[2], r[idx_mean], r[idx_sd]) for r in DATA if r[1] == c]
        N, m, sd, ss = pooled(rows, idx_mean, idx_sd)
        out[c] = (N, m, sd, 1.96 * sd / np.sqrt(N))
    return out


def bracket(ax, x1, x2, y, h, text):
    ax.plot([x1, x1, x2, x2], [y, y + h, y + h, y],
            lw=1.6, color="#333333", zorder=5)
    ax.text((x1 + x2) / 2.0, y + h, text, ha="center", va="bottom",
            fontsize=17, color="#333333")


def panel(ax, idx_mean, idx_sd, ylabel, ylim, bstep):
    st = category_stats(idx_mean, idx_sd)
    xs = np.arange(len(ORDER))
    means = [st[c][1] for c in ORDER]
    cis = [st[c][3] for c in ORDER]

    # Trend line through the ordered means, then colored points on top
    ax.plot(xs, means, color="#999999", lw=1.6, zorder=2)
    for x, c in zip(xs, ORDER):
        N, m, sd, ci = st[c]
        ax.errorbar(x, m, yerr=ci, fmt="o", markersize=15,
                    markerfacecolor=fill_color[c], markeredgecolor=edge_color[c],
                    markeredgewidth=2.0, ecolor=edge_color[c], elinewidth=2.2,
                    capsize=7, capthick=2.2, zorder=4)

    ax.set_xticks(xs)
    ax.set_xticklabels([XLABEL[c] for c in ORDER], fontsize=17)
    ax.set_xlim(-0.6, len(ORDER) - 0.4)
    ax.set_ylim(*ylim)
    ax.set_ylabel(ylabel, fontsize=22)
    ax.tick_params(axis="y", labelsize=17)
    ax.grid(True, axis="y", color="#dddddd", linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)

    # ANOVA note
    groups = [pooled([(r[2], r[idx_mean], r[idx_sd])
                      for r in DATA if r[1] == c], idx_mean, idx_sd)
              for c in ORDER]
    F, dfb, dfw, p = anova(groups)
    ax.text(0.03, 0.96,
            rf"ANOVA: $F({dfb},{dfw})={F:.1f}$, $p={_sci(p)}$",
            transform=ax.transAxes, ha="left", va="top", fontsize=16)

    # Significance brackets: green (rightmost, index 3) vs each other class
    gi = ORDER.index("green")
    top = max(m + c for m, c in zip(means, cis))
    y = top + bstep
    for other in ["blue", "red", "gray"]:
        oi = ORDER.index(other)
        _, _, p2, _ = welch(st["green"][:3], st[other][:3])
        bracket(ax, oi, gi, y, bstep * 0.28, stars(p2))
        y += bstep


def _sci(p):
    """LaTeX scientific notation like 1.3\\times10^{-16}."""
    exp = int(np.floor(np.log10(p)))
    mant = p / 10 ** exp
    return rf"{mant:.1f}\times10^{{{exp}}}"


fig, axes = plt.subplots(1, 2, figsize=(16, 7))
panel(axes[0], 3, 4, r"LV end-diastolic dimension (mm)", (49.5, 57.0), 0.75)
panel(axes[1], 5, 6, r"LV wall thickness (mm)", (8.7, 11.9), 0.32)

fig.text(0.5, 0.005,
         r"Points: athlete-weighted category mean $\pm$ 95\% CI\quad"
         r"$\cdot$\quad brackets: Welch $t$-test vs.\ high dynamic $+$ static "
         r"($^{*}p{<}0.05$, $^{**}p{<}0.01$, $^{***}p{<}0.001$)",
         ha="center", va="bottom", fontsize=15)

fig.tight_layout(rect=(0, 0.045, 1, 1))
fig.savefig("trends_by_classification.pdf", bbox_inches="tight")
fig.savefig("trends_by_classification.png", dpi=200, bbox_inches="tight")
print("Saved trends_by_classification.pdf and trends_by_classification.png")
