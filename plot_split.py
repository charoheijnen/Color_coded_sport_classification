"""
The data-driven two-group split (analyze_split.py) drawn on the same axes as
the other summary figures: the 25 sport means as dots colored by cluster, one
+/- 1 SD ellipse per cluster, and the k-means decision boundary. This is the
cleanest two-group separation of the sports in the (LVEDd, wall thickness)
plane -- far sharper than the Mitchell or body-region cuts.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse

from analyze_trends import DATA
from analyze_split import assign, group_pooled, boundary_x

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.size": 18,
    "axes.edgecolor": "#555555",
})

# larger-hearts cluster = 1, smaller = 0
edge_color = {1: "#b0202e", 0: "#20558f"}
fill_color = {1: "#e0796f", 0: "#79a8dd"}

fig, ax = plt.subplots(figsize=(18, 8))

# Cluster ellipses (+/- 1 SD on each axis)
ell = {}
for g in (1, 0):
    _, mx, sdx, _ = group_pooled(g, 3, 4)
    _, my, sdy, _ = group_pooled(g, 5, 6)
    ell[g] = (mx, my, sdx, sdy)
for g in sorted(ell, key=lambda g: ell[g][2] * ell[g][3], reverse=True):
    mx, my, sdx, sdy = ell[g]
    ax.add_patch(Ellipse((mx, my), 2 * sdx, 2 * sdy,
                         facecolor=fill_color[g], edgecolor=edge_color[g],
                         alpha=0.25, linewidth=1.6, zorder=2))

# Individual sport means as dots colored by cluster
for i, r in enumerate(DATA):
    g = assign[i]
    ax.plot(r[3], r[5], marker="o", markersize=11, markerfacecolor=fill_color[g],
            markeredgecolor=edge_color[g], markeredgewidth=1.8, zorder=5)
# Cluster centroids as large diamonds
for g in (1, 0):
    mx, my = ell[g][0], ell[g][1]
    ax.plot(mx, my, marker="D", markersize=15, markerfacecolor=edge_color[g],
            markeredgecolor="white", markeredgewidth=1.8, zorder=6)

# Same axes as the other summary figures
x_lo = min(r[3] - r[4] for r in DATA) - 0.5
x_hi = max(r[3] + r[4] for r in DATA) + 0.5
y_lo = min(r[5] - r[6] for r in DATA) - 0.25
y_hi = max(r[5] + r[6] for r in DATA) + 0.3
ax.set_xlim(x_lo, x_hi)
ax.set_ylim(y_lo, y_hi)

# k-means decision boundary (a straight line in this plane)
yy = np.array([y_lo, y_hi])
ax.plot(boundary_x(yy), yy, ls="--", color="#444444", linewidth=2.0, zorder=4)

# Group labels
ax.annotate(r"\textbf{Larger hearts}" + "\n" + r"13 sports, $n=469$",
            xy=(57.3, 12.1), ha="center", va="center", fontsize=19,
            color=edge_color[1], zorder=7,
            bbox=dict(boxstyle="round,pad=0.35", facecolor="white",
                      edgecolor=edge_color[1], linewidth=1.4, alpha=0.95))
ax.annotate(r"\textbf{Smaller hearts}" + "\n" + r"12 sports, $n=478$",
            xy=(46.6, 8.0), ha="center", va="center", fontsize=19,
            color=edge_color[0], zorder=7,
            bbox=dict(boxstyle="round,pad=0.35", facecolor="white",
                      edgecolor=edge_color[0], linewidth=1.4, alpha=0.95))
ax.text(boundary_x(y_hi) - 0.2, y_hi - 0.15, r"k-means boundary",
        ha="right", va="top", fontsize=15, color="#444444")

ax.set_xlabel(r"LV end-diastolic dimension (mm)", fontsize=24)
ax.set_ylabel(r"LV wall thickness (mm)", fontsize=24)
ax.tick_params(axis="both", labelsize=18)
ax.grid(True, color="#dddddd", linewidth=0.8, zorder=0)
ax.set_axisbelow(True)

fig.tight_layout()
fig.savefig("best_two_group_split.pdf", bbox_inches="tight")
fig.savefig("best_two_group_split.png", dpi=200, bbox_inches="tight")
print("Saved best_two_group_split.pdf and best_two_group_split.png")
