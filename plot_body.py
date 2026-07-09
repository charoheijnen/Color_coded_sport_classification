"""
Summary ellipse plot for the upper/lower/whole-body classification, drawn on
the same axes as sport_heart_ellipses.py / plot_trends.py so it can be compared
directly with the Mitchell-classification summary. One +/- 1 SD ellipse per body
region (athlete-weighted mean, pooled SD), labeled by region and athlete count.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse

from analyze_trends import DATA
from analyze_body import GROUPS, GROUP_NAME, group_stats

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.size": 18,
    "axes.edgecolor": "#555555",
})

# Distinct palette (not the Mitchell colors) so the two schemes aren't confused
edge_color = {"lower": "#b25a12", "upper": "#6a2f9e", "whole": "#12776e"}
fill_color = {"lower": "#f0a24e", "upper": "#b085d6", "whole": "#4fbfb0"}

LABEL_POS = {
    "lower": (46.7, 10.7),
    "upper": (56.4, 8.15),
    "whole": (56.9, 12.1),
}

stats = {g: group_stats(g) for g in GROUPS}

fig, ax = plt.subplots(figsize=(18, 8))

for g in sorted(GROUPS, key=lambda g: stats[g][2] * stats[g][4], reverse=True):
    N, mx, sdx, my, sdy = stats[g]
    ax.add_patch(Ellipse(
        (mx, my), width=2 * sdx, height=2 * sdy,
        facecolor=fill_color[g], edgecolor=edge_color[g],
        alpha=0.32, linewidth=1.6, zorder=2,
    ))
    ax.plot(mx, my, marker="o", markersize=11, color=edge_color[g], zorder=6)

for g in GROUPS:
    N, mx, my = stats[g][0], stats[g][1], stats[g][3]
    ax.annotate(
        rf"{GROUP_NAME[g]}" + "\n" + rf"($n={N}$)",
        xy=(mx, my), xytext=LABEL_POS[g], textcoords="data",
        ha="center", va="center", fontsize=18, color=edge_color[g], zorder=7,
        bbox=dict(boxstyle="round,pad=0.32", facecolor="white",
                  edgecolor=edge_color[g], linewidth=1.2, alpha=0.92),
        arrowprops=dict(arrowstyle="-", color=edge_color[g], linewidth=1.6,
                        shrinkA=2, shrinkB=6),
    )

# Same axes as the per-sport / Mitchell summary figures
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
fig.savefig("trends_by_body_region.pdf", bbox_inches="tight")
fig.savefig("trends_by_body_region.png", dpi=200, bbox_inches="tight")
print("Saved trends_by_body_region.pdf and trends_by_body_region.png")
