"""
Find the cleanest two-group split of the 25 sports in the (LV end-diastolic
dimension, wall thickness) plane, rather than imposing a classification.

We standardize the two axes, run a deterministic 2-means clustering on the 25
sport means (seeded from the top principal component so there is no randomness),
and then characterize the resulting groups: which sports fall where, the
athlete-pooled means, Welch tests, Cohen's d, and separation metrics
(silhouette; overlap of the two athlete distributions along the discriminant).

Importing this module gives you the clustering (names, assign, GROUP, the
standardized centroids C0/C1 and scalers MU/SD, and group_pooled/boundary_x);
running it prints the report.
"""

import numpy as np
from analyze_trends import DATA, pooled, welch, stars

names = [r[0] for r in DATA]
_x = np.array([r[3] for r in DATA], float)   # LVEDd mean
_y = np.array([r[5] for r in DATA], float)   # wall thickness mean

# Standardize both axes (unweighted across the 25 sports)
_X = np.column_stack([_x, _y])
MU, SD = _X.mean(0), _X.std(0)
_Z = (_X - MU) / SD

# Seed 2-means from the top principal component (deterministic; no RNG)
_evals, _evecs = np.linalg.eigh(np.cov(_Z.T))
_proj = _Z @ _evecs[:, -1]
assign = (_proj > np.median(_proj)).astype(int)
for _ in range(100):
    _c0, _c1 = _Z[assign == 0].mean(0), _Z[assign == 1].mean(0)
    _new = (((_Z - _c1) ** 2).sum(1) < ((_Z - _c0) ** 2).sum(1)).astype(int)
    if np.array_equal(_new, assign):
        break
    assign = _new

# Order groups so group 1 = larger hearts (higher along the remodeling diagonal)
if _Z[assign == 1].mean(0).sum() < _Z[assign == 0].mean(0).sum():
    assign = 1 - assign

C0, C1 = _Z[assign == 0].mean(0), _Z[assign == 1].mean(0)  # standardized centroids
GROUP = {names[i]: int(assign[i]) for i in range(len(names))}


def group_pooled(g, idx_mean, idx_sd):
    """(N, mean, sd, ss) pooled over all athletes in cluster g for one axis."""
    rows = [(r[2], r[idx_mean], r[idx_sd])
            for i, r in enumerate(DATA) if assign[i] == g]
    return pooled(rows, idx_mean, idx_sd)


def boundary_x(y_orig):
    """LVEDd on the k-means decision boundary for a given wall thickness.

    Boundary: points equidistant to C0/C1 in standardized space, i.e.
    2 z . (C1 - C0) = |C1|^2 - |C0|^2. Solve for the LVEDd coordinate.
    """
    w = C1 - C0
    rhs = (C1 @ C1 - C0 @ C0) / 2.0
    zy = (y_orig - MU[1]) / SD[1]
    zx = (rhs - w[1] * zy) / w[0]
    return zx * SD[0] + MU[0]


def _report():
    print("=" * 72)
    print("DATA-DRIVEN TWO-GROUP SPLIT (2-means on standardized sport means)")
    print("=" * 72)
    for g, tag in [(1, "GROUP A  (larger hearts)"),
                   (0, "GROUP B  (smaller hearts)")]:
        members = [names[i] for i in range(len(names)) if assign[i] == g]
        Nx, mx, sdx, _ = group_pooled(g, 3, 4)
        _, my, sdy, _ = group_pooled(g, 5, 6)
        print(f"\n{tag}: {len(members)} sports, n={int(Nx)} athletes")
        print(f"  LVEDd {mx:5.2f} ± {sdx:.2f} mm   wall {my:5.2f} ± {sdy:.2f} mm")
        print("  " + ", ".join(members))

    print("\n" + "-" * 72 + "\nHow big is the difference?")
    for im, isd, lab in [(3, 4, "LVEDd"), (5, 6, "wall thickness")]:
        a, b = group_pooled(1, im, isd)[:3], group_pooled(0, im, isd)[:3]
        t, df, p, d = welch(a, b)
        print(f"  {lab:<15} Δ = {a[1]-b[1]:+.2f} mm   t={t:5.2f}  "
              f"p={p:.2e} {stars(p)}   Cohen's d={d:+.2f}")

    # Mean silhouette of the sport-level clustering
    sil = []
    for i in range(len(names)):
        same = [j for j in range(len(names)) if assign[j] == assign[i] and j != i]
        other = [j for j in range(len(names)) if assign[j] != assign[i]]
        ai = np.mean([np.linalg.norm(_Z[i] - _Z[j]) for j in same])
        bi = np.mean([np.linalg.norm(_Z[i] - _Z[j]) for j in other])
        sil.append((bi - ai) / max(ai, bi))
    print(f"\n  Mean silhouette (sport level) = {np.mean(sil):.2f}")

    # Overlap of the two athlete distributions along the discriminant
    from scipy import stats as sstats
    trapz = getattr(np, "trapezoid", getattr(np, "trapz", None))
    w = (C1 - C0) / np.linalg.norm(C1 - C0)

    def proj_stats(g):
        _, mx, sdx, _ = group_pooled(g, 3, 4)
        _, my, sdy, _ = group_pooled(g, 5, 6)
        m = w[0] * (mx - MU[0]) / SD[0] + w[1] * (my - MU[1]) / SD[1]
        s = np.sqrt((w[0] * sdx / SD[0]) ** 2 + (w[1] * sdy / SD[1]) ** 2)
        return m, s

    mA, sA = proj_stats(1)
    mB, sB = proj_stats(0)
    lo = min(mA, mB) - 6 * max(sA, sB)
    hi = max(mA, mB) + 6 * max(sA, sB)
    grid = np.linspace(lo, hi, 4000)
    ov = trapz(np.minimum(sstats.norm.pdf(grid, mA, sA),
                          sstats.norm.pdf(grid, mB, sB)), grid)
    dsep = abs(mA - mB) / np.sqrt((sA ** 2 + sB ** 2) / 2)
    print(f"  Athlete-distribution overlap along discriminant = {ov*100:.0f}% "
          f"(separation d = {dsep:.2f})")


if __name__ == "__main__":
    _report()
