"""
Athlete cardiac remodeling by sport, drawn as mean +/- 1 SD ellipses.

Each sport is a semi-transparent ellipse centered on its mean
(LV end-diastolic dimension, wall thickness); the ellipse half-axes are one
standard deviation in each direction. Fill color encodes the Mitchell /
Task Force 8 classification of the sport.

Data source
-----------
Spirito P, Pelliccia A, Proschan MA, et al. "Morphology of the 'athlete's
heart' assessed by echocardiography in 947 elite athletes representing 27
sports." Am J Cardiol 1994;74(8):802-806. doi:10.1016/0002-9149(94)90439-1

Means, SDs and athlete counts are from Table I of that paper. The paper lists
27 sports; this figure uses the 25-sport grouping from the project README,
which merges two pairs of Table I rows:
  * "Cycling" = endurance cycling (n=50) + sprint cycling (n=15)  -> n=65
  * "Track"   = long-distance track (n=49) + sprint track (n=40)  -> n=89
All 25 counts below sum to 947, matching the full cohort.

Output: sport_heart_ellipses.pdf (vector). All text is typeset with LaTeX.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")  # gives a renderer for text measurement; savefig(.pdf) still uses the PDF backend
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Ellipse

# Typeset every label with LaTeX (Computer Modern serif).
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.size": 18,          # presentation-scale base size
    "axes.edgecolor": "#555555",
})

# --- Mitchell classification -> fill color -------------------------------
# blue = high dynamic, red = high static, green = high dynamic + static,
# gray = low both
sport_color = {
    "Rowing": "green",
    "Track": "blue",
    "Cycling": "green",
    "Soccer": "blue",
    "Canoeing": "green",
    "Roller-skating": "green",
    "Swimming": "blue",
    "Volleyball": "blue",
    "Pentathlon": "blue",
    "Tennis": "blue",
    "Fencing": "gray",
    "Alpine skiing": "green",
    "Cross-country skiing": "green",
    "Equestrianism": "red",
    "Team handball": "blue",
    "Yachting": "red",
    "Roller hockey": "blue",
    "Water polo": "blue",
    "Tae kwon do": "blue",
    "Wrestling and judo": "red",
    "Bobsledding": "green",
    "Boxing": "blue",
    "Diving": "red",
    "Field weight events": "red",
    "Weightlifting": "red",
}

sports = [
    "Rowing", "Track", "Cycling", "Soccer", "Canoeing", "Roller-skating",
    "Swimming", "Volleyball", "Pentathlon", "Tennis", "Fencing",
    "Alpine skiing", "Cross-country skiing", "Equestrianism", "Team handball",
    "Yachting", "Roller hockey", "Water polo", "Tae kwon do",
    "Wrestling and judo", "Bobsledding", "Boxing", "Diving",
    "Field weight events", "Weightlifting",
]

# LV end-diastolic dimension (mm): mean and SD
lved_mean = [56.0, 51.4, 54.8, 54.9, 54.5, 49.0, 53.0, 53.7, 52.4, 50.0,
             51.7, 52.0, 54.5, 50.4, 51.8, 51.2, 53.4, 54.7, 50.6, 52.6,
             55.1, 52.5, 49.6, 55.5, 53.2]
lved_sd = [3, 4, 5, 4, 3, 4, 4, 3, 4, 3, 5, 3, 4, 3, 4, 4, 3, 3, 4, 5, 2,
           3, 3, 4, 3]

# Wall thickness (mm): mean and SD
wt_mean = [11.3, 9.8, 10.4, 9.9, 10.5, 9.0, 9.3, 9.4, 9.2, 9.1, 9.2, 8.9,
           9.6, 9.0, 8.5, 9.0, 9.7, 10.7, 8.7, 10.2, 9.6, 9.8, 8.7, 10.0,
           10.4]
wt_sd = [1.3, 1.2, 1.1, 0.7, 1.5, 1.0, 1.2, 1.0, 0.9, 1.0, 1.3, 0.9, 0.8,
         0.8, 0.9, 0.8, 0.9, 0.6, 1.2, 0.9, 0.5, 1.0, 1.1, 0.5, 0.7]

# Number of athletes per sport, from Spirito 1994 Table I (sums to 947).
n_athletes = {
    "Rowing": 95,
    "Track": 89,             # long-distance (49) + sprint (40)
    "Cycling": 65,           # endurance (50) + sprint (15)
    "Soccer": 62,
    "Canoeing": 59,
    "Roller-skating": 58,
    "Swimming": 55,
    "Volleyball": 51,
    "Pentathlon": 50,
    "Tennis": 46,
    "Fencing": 42,
    "Alpine skiing": 32,
    "Cross-country skiing": 31,
    "Equestrianism": 28,
    "Team handball": 26,
    "Yachting": 24,
    "Roller hockey": 23,
    "Water polo": 21,
    "Tae kwon do": 17,
    "Wrestling and judo": 16,
    "Bobsledding": 16,
    "Boxing": 14,
    "Diving": 11,
    "Field weight events": 9,
    "Weightlifting": 7,
}
assert sum(n_athletes.values()) == 947, sum(n_athletes.values())

# Shorten a few long names so labels stay compact (LaTeX-safe text)
abbrev = {
    "Cross-country skiing": "XC Ski",
    "Wrestling and judo": "Wrest/Judo",
    "Field weight events": "Throws",
    "Roller-skating": "Roller",
    "Team handball": "Handball",
    "Water polo": "Water Polo",
    "Alpine skiing": "Alpine",
    "Tae kwon do": "TKD",
    "Roller hockey": "R.\\ Hockey",
    "Equestrianism": "Equestrian",
}

# Darker shades for edges/text so overlapping fills stay readable
edge_color = {
    "blue": "#1f4e9c",
    "red": "#a01f2e",
    "green": "#1f7a34",
    "gray": "#4d4d4d",
}
fill_color = {
    "blue": "#4f8ff0",
    "red": "#e2564f",
    "green": "#43b364",
    "gray": "#9a9a9a",
}


def make_label(sport):
    short = abbrev.get(sport, sport)
    n = n_athletes.get(sport)
    if n is not None:
        return f"{short}\n($n={n}$)"
    return short


# One record per sport
records = []
for sport, xm, xs, ym, ys in zip(sports, lved_mean, lved_sd, wt_mean, wt_sd):
    c = sport_color[sport]
    records.append({
        "sport": sport,
        "x": xm, "xs": xs, "y": ym, "ys": ys,
        "color": c,
        "label": make_label(sport),
        "area": xs * ys,  # only used for draw order (big ellipses first)
    })

# --- Plot ----------------------------------------------------------------
fig, ax = plt.subplots(figsize=(18, 8))

for row in sorted(records, key=lambda r: r["area"], reverse=True):
    c = row["color"]
    ax.add_patch(Ellipse(
        (row["x"], row["y"]),
        width=2 * row["xs"],   # +/- 1 SD along x
        height=2 * row["ys"],  # +/- 1 SD along y
        facecolor=fill_color[c], edgecolor=edge_color[c],
        alpha=0.30, linewidth=1.4, zorder=2,
    ))
    ax.plot(row["x"], row["y"], marker="o", markersize=8,
            color=edge_color[c], zorder=6)

# Axis limits: tight around the ellipse extents (all ellipses stay inside)
x_lo = min(r["x"] - r["xs"] for r in records) - 0.5
x_hi = max(r["x"] + r["xs"] for r in records) + 0.5
y_lo = min(r["y"] - r["ys"] for r in records) - 0.25
y_hi = max(r["y"] + r["ys"] for r in records) + 0.3
ax.set_xlim(x_lo, x_hi)
ax.set_ylim(y_lo, y_hi)

ax.set_xlabel(r"LV end-diastolic dimension (mm)", fontsize=24)
ax.set_ylabel(r"LV wall thickness (mm)", fontsize=24)
ax.tick_params(axis="both", labelsize=18)
ax.grid(True, color="#dddddd", linewidth=0.8, zorder=0)
ax.set_axisbelow(True)

# --- Non-overlapping label placement -------------------------------------
# Create the label texts, then push them apart in display (pixel) space with
# a simple force model (repel overlapping labels, spring each toward its own
# point), and finally draw a thin leader line from each point to its label.
fig.canvas.draw()
renderer = fig.canvas.get_renderer()

texts, half, anchor_px = [], [], []
for row in records:
    t = ax.annotate(
        row["label"], (row["x"], row["y"]),
        ha="center", va="center", fontsize=15,
        color=edge_color[row["color"]], zorder=7,
        bbox=dict(boxstyle="round,pad=0.28", facecolor="white",
                  edgecolor=edge_color[row["color"]], linewidth=1.0,
                  alpha=0.9),
    )
    bb = t.get_window_extent(renderer)
    texts.append(t)
    half.append((bb.width / 2.0, bb.height / 2.0))
    anchor_px.append(ax.transData.transform((row["x"], row["y"])))

half = np.array(half)
anchor_px = np.array(anchor_px)
# Start each label a little up-and-right of its point
pos = anchor_px + np.array([0.0, 14.0])
target = anchor_px + np.array([0.0, 14.0])   # spring rest position
ax_bb = ax.get_window_extent(renderer)
# get_window_extent covers the text glyphs but not the rounded box padding,
# so add enough margin to keep the drawn chips (and a small gap) apart.
pad = 13.0
n = len(records)

for _it in range(8000):
    # Anneal the spring to zero so repulsion fully clears residual overlaps
    spring = 0.02 if _it < 2000 else 0.0
    force = np.zeros((n, 2))
    # Repel overlapping label boxes. Push apart along the center-to-center
    # direction (diagonal escape) so wedged clusters don't ping-pong.
    for i in range(n):
        for j in range(i + 1, n):
            d = pos[i] - pos[j]
            ox = (half[i, 0] + half[j, 0] + pad) - abs(d[0])
            oy = (half[i, 1] + half[j, 1] + pad) - abs(d[1])
            if ox > 0 and oy > 0:
                push = min(ox, oy)
                dist = np.hypot(*d)
                if dist < 1e-6:
                    # Exactly stacked: separate deterministically by index
                    u = np.array([1.0, 0.0]) if (i + j) % 2 else np.array([0.0, 1.0])
                else:
                    u = d / dist
                force[i] += 0.55 * push * u
                force[j] -= 0.55 * push * u
    # Keep labels off every data point (so the mean markers stay visible)
    for i in range(n):
        for a in anchor_px:
            d = pos[i] - a
            ox = (half[i, 0] + pad) - abs(d[0])
            oy = (half[i, 1] + pad) - abs(d[1])
            if ox > 0 and oy > 0:
                s = np.sign(d[1]) or 1.0
                force[i, 1] += 0.3 * oy * s
    # Weak spring back toward each label's rest position
    force += spring * (target - pos)
    pos += force
    # Stay inside the axes
    pos[:, 0] = np.clip(pos[:, 0], ax_bb.x0 + half[:, 0], ax_bb.x1 - half[:, 0])
    pos[:, 1] = np.clip(pos[:, 1], ax_bb.y0 + half[:, 1], ax_bb.y1 - half[:, 1])

# Report any label boxes that still overlap after layout
overlaps = []
for i in range(n):
    for j in range(i + 1, n):
        d = pos[i] - pos[j]
        if (abs(d[0]) < half[i, 0] + half[j, 0]) and \
           (abs(d[1]) < half[i, 1] + half[j, 1]):
            overlaps.append((records[i]["sport"], records[j]["sport"]))
print(f"Remaining label overlaps: {len(overlaps)}" +
      (f" -> {overlaps}" if overlaps else ""))

inv = ax.transData.inverted()
for i, (row, t) in enumerate(zip(records, texts)):
    t.set_position(inv.transform(pos[i]))
    # Leader line from the point to the label box edge, if the label moved
    d = pos[i] - anchor_px[i]
    dist = np.hypot(*d)
    if dist > half[i, 1] + 6:
        with np.errstate(divide="ignore", invalid="ignore"):
            sx = half[i, 0] / abs(d[0]) if d[0] else np.inf
            sy = half[i, 1] / abs(d[1]) if d[1] else np.inf
        s = min(sx, sy)
        edge_px = pos[i] - d * s              # box boundary toward the point
        p0 = inv.transform(anchor_px[i])
        p1 = inv.transform(edge_px)
        ax.plot([p0[0], p1[0]], [p0[1], p1[1]],
                color=edge_color[row["color"]], linewidth=1.4,
                alpha=0.8, zorder=5)

# Legend for the Mitchell categories
legend_handles = [
    Line2D([0], [0], marker="o", linestyle="", markersize=11, alpha=0.75,
           markerfacecolor=fill_color[k], markeredgecolor=edge_color[k],
           label=lab)
    for k, lab in [("blue", "High dynamic"), ("red", "High static"),
                   ("green", "High dynamic $+$ static"), ("gray", "Low both")]
]
ax.legend(handles=legend_handles, title=r"Mitchell classification",
          fontsize=17, title_fontsize=19, loc="upper left", framealpha=0.95)

fig.tight_layout()
fig.savefig("sport_heart_ellipses.pdf", bbox_inches="tight")
fig.savefig("sport_heart_ellipses.png", dpi=200, bbox_inches="tight")
print("Saved sport_heart_ellipses.pdf and sport_heart_ellipses.png")
