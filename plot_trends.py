"""
Summary of sport_heart_ellipses.py: the same LV end-diastolic dimension vs.
wall-thickness axes, but with the 25 per-sport ellipses collapsed into one
ellipse per Mitchell exercise class.

Each ellipse is centered on the athlete-weighted category mean with half-axes
of +/- 1 SD (pooled across the sports in that class, i.e. the spread of the
individual athletes) -- exactly the convention used for the per-sport ellipses,
so this reads as the summary of that plot. Ellipses are labeled by exercise
form and athlete count.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse

from analyze_trends import DATA, CAT_NAME, pooled

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
CATS = ["green", "blue", "red", "gray"]

# Where to place each category label (data coords) + its leader line to the mean
LABEL_POS = {
    "green": (56.9, 12.1),
    "blue": (56.2, 8.15),
    "red": (46.6, 10.5),
    "gray": (47.0, 8.05),
}


def cat_stats(cat):
    rows_x = [(r[2], r[3], r[4]) for r in DATA if r[1] == cat]
    rows_y = [(r[2], r[5], r[6]) for r in DATA if r[1] == cat]
    N, mx, sdx, _ = pooled(rows_x, 3, 4)
    _, my, sdy, _ = pooled(rows_y, 5, 6)
    return int(N), mx, sdx, my, sdy


stats = {c: cat_stats(c) for c in CATS}

fig, ax = plt.subplots(figsize=(18, 8))

# Draw larger ellipses first so smaller ones stay visible on top
for c in sorted(CATS, key=lambda c: stats[c][2] * stats[c][4], reverse=True):
    N, mx, sdx, my, sdy = stats[c]
    ax.add_patch(Ellipse(
        (mx, my), width=2 * sdx, height=2 * sdy,
        facecolor=fill_color[c], edgecolor=edge_color[c],
        alpha=0.30, linewidth=1.6, zorder=2,
    ))
    ax.plot(mx, my, marker="o", markersize=11, color=edge_color[c], zorder=6)

# Labels (exercise form + athlete count) with a leader line to the mean
for c in CATS:
    N, mx, my = stats[c][0], stats[c][1], stats[c][3]
    name = CAT_NAME[c].replace("+", r"$+$")
    ax.annotate(
        rf"{name}" + "\n" + rf"($n={N}$)",
        xy=(mx, my), xytext=LABEL_POS[c], textcoords="data",
        ha="center", va="center", fontsize=18, color=edge_color[c], zorder=7,
        bbox=dict(boxstyle="round,pad=0.32", facecolor="white",
                  edgecolor=edge_color[c], linewidth=1.2, alpha=0.92),
        arrowprops=dict(arrowstyle="-", color=edge_color[c], linewidth=1.6,
                        shrinkA=2, shrinkB=6),
    )

# Same axes as sport_heart_ellipses.py (tight around the per-sport ellipses)
x_lo = min(r[3] - r[4] for r in DATA) - 0.5
x_hi = max(r[3] + r[4] for r in DATA) + 0.5
y_lo = min(r[5] - r[6] for r in DATA) - 0.25
y_hi = max(r[5] + r[6] for r in DATA) + 0.3
ax.set_xlim(x_lo, x_hi)
ax.set_ylim(y_lo, y_hi)

ax.set_xlabel(r"LV end-diastolic dimension (mm)", fontsize=24)
ax.set_ylabel(r"LV wall thickness (mm)", fontsize=24)
ax.tick_params(axis="both", labelsize=18)
ax.grid(True, color="#dddddd", linewidth=0.8, zorder=0)
ax.set_axisbelow(True)

fig.tight_layout()
fig.savefig("trends_by_classification.pdf", bbox_inches="tight")
fig.savefig("trends_by_classification.png", dpi=200, bbox_inches="tight")
print("Saved trends_by_classification.pdf and trends_by_classification.png")
