"""
Do cardiac dimensions differ by Mitchell exercise classification?

We only have per-sport summary statistics (n, mean, SD) from Spirito 1994
Table I, not individual athlete data. That is enough to reconstruct exact
group-level statistics: pooling the sports within a Mitchell category gives
the category mean and the total (within-sport + between-sport) variance of
the individual athletes in that category.

For each of LV end-diastolic dimension (LVEDd) and LV wall thickness we then:
  * report the athlete-weighted category mean +/- pooled SD,
  * run a one-way ANOVA across the four categories (F test), and
  * run Welch two-sample t-tests for every pair of categories.

The classification colors are the ones assigned in the project README.
"""

import numpy as np
from itertools import combinations
from scipy import stats

# (sport, category, n, LVEDd_mean, LVEDd_sd, WT_mean, WT_sd) from Spirito 1994
DATA = [
    ("Rowing", "green", 95, 56.0, 3, 11.3, 1.3),
    ("Track", "blue", 89, 51.4, 4, 9.8, 1.2),
    ("Cycling", "green", 65, 54.8, 5, 10.4, 1.1),
    ("Soccer", "blue", 62, 54.9, 4, 9.9, 0.7),
    ("Canoeing", "green", 59, 54.5, 3, 10.5, 1.5),
    ("Roller-skating", "green", 58, 49.0, 4, 9.0, 1.0),
    ("Swimming", "blue", 55, 53.0, 4, 9.3, 1.2),
    ("Volleyball", "blue", 51, 53.7, 3, 9.4, 1.0),
    ("Pentathlon", "blue", 50, 52.4, 4, 9.2, 0.9),
    ("Tennis", "blue", 46, 50.0, 3, 9.1, 1.0),
    ("Fencing", "gray", 42, 51.7, 5, 9.2, 1.3),
    ("Alpine skiing", "green", 32, 52.0, 3, 8.9, 0.9),
    ("Cross-country skiing", "green", 31, 54.5, 4, 9.6, 0.8),
    ("Equestrianism", "red", 28, 50.4, 3, 9.0, 0.8),
    ("Team handball", "blue", 26, 51.8, 4, 8.5, 0.9),
    ("Yachting", "red", 24, 51.2, 4, 9.0, 0.8),
    ("Roller hockey", "blue", 23, 53.4, 3, 9.7, 0.9),
    ("Water polo", "blue", 21, 54.7, 3, 10.7, 0.6),
    ("Tae kwon do", "blue", 17, 50.6, 4, 8.7, 1.2),
    ("Wrestling and judo", "red", 16, 52.6, 5, 10.2, 0.9),
    ("Bobsledding", "green", 16, 55.1, 2, 9.6, 0.5),
    ("Boxing", "blue", 14, 52.5, 3, 9.8, 1.0),
    ("Diving", "red", 11, 49.6, 3, 8.7, 1.1),
    ("Field weight events", "red", 9, 55.5, 4, 10.0, 0.5),
    ("Weightlifting", "red", 7, 53.2, 3, 10.4, 0.7),
]

CATS = ["green", "blue", "red", "gray"]
CAT_NAME = {
    "green": "High dynamic + static",
    "blue": "High dynamic",
    "red": "High static",
    "gray": "Low both",
}


def pooled(rows, mi, si):
    """Exact N, weighted mean and pooled SD of individuals from summary stats.

    rows: list of (n, mean, sd). mi/si unused placeholder kept for clarity.
    Total SS = sum[(n_i-1) sd_i^2 + n_i (mean_i - grand)^2].
    """
    n = np.array([r[0] for r in rows], float)
    m = np.array([r[1] for r in rows], float)
    s = np.array([r[2] for r in rows], float)
    N = n.sum()
    grand = (n * m).sum() / N
    ss = ((n - 1) * s**2 + n * (m - grand) ** 2).sum()
    sd = np.sqrt(ss / (N - 1))
    return N, grand, sd, ss


def anova(groups):
    """One-way ANOVA from per-group (N, mean, within-SS)."""
    Ns = np.array([g[0] for g in groups], float)
    Ms = np.array([g[1] for g in groups], float)
    SSw = sum(g[3] for g in groups)
    Ntot = Ns.sum()
    grand = (Ns * Ms).sum() / Ntot
    SSb = (Ns * (Ms - grand) ** 2).sum()
    k = len(groups)
    dfb, dfw = k - 1, Ntot - k
    F = (SSb / dfb) / (SSw / dfw)
    p = stats.f.sf(F, dfb, dfw)
    return F, dfb, int(dfw), p


def welch(a, b):
    """Welch t-test between two groups given (N, mean, SD)."""
    (na, ma, sa), (nb, mb, sb) = a, b
    se = np.sqrt(sa**2 / na + sb**2 / nb)
    t = (ma - mb) / se
    df = se**4 / ((sa**2 / na) ** 2 / (na - 1) + (sb**2 / nb) ** 2 / (nb - 1))
    p = 2 * stats.t.sf(abs(t), df)
    d = (ma - mb) / np.sqrt((sa**2 + sb**2) / 2)  # Cohen's d
    return t, df, p, d


def stars(p):
    return ("***" if p < 1e-3 else "**" if p < 1e-2 else
            "*" if p < 0.05 else "ns")


def analyze(idx_mean, idx_sd, label):
    print(f"\n{'='*70}\n{label}\n{'='*70}")
    groups, summ = {}, {}
    for c in CATS:
        rows = [(r[2], r[idx_mean], r[idx_sd]) for r in DATA if r[1] == c]
        N, m, sd, ss = pooled(rows, idx_mean, idx_sd)
        groups[c] = (N, m, sd, ss)
        summ[c] = (N, m, sd)
        print(f"  {CAT_NAME[c]:<24} n={int(N):>3}  "
              f"mean={m:5.2f}  SD={sd:4.2f}  ({len(rows)} sports)")

    F, dfb, dfw, p = anova([groups[c] for c in CATS])
    print(f"\n  One-way ANOVA: F({dfb},{dfw}) = {F:.2f}, p = {p:.2e} {stars(p)}")

    print("\n  Pairwise (Welch t-test, Cohen's d):")
    for a, b in combinations(CATS, 2):
        t, df, pp, d = welch(summ[a], summ[b])
        print(f"    {CAT_NAME[a]:<22} vs {CAT_NAME[b]:<22} "
              f"Δ={summ[a][1]-summ[b][1]:+5.2f}  "
              f"t={t:6.2f}  p={pp:.2e} {stars(pp):<3}  d={d:+.2f}")


analyze(3, 4, "LV END-DIASTOLIC DIMENSION (mm)")
analyze(5, 6, "LV WALL THICKNESS (mm)")

# Correlation of the two dimensions across sports (athlete-weighted)
n = np.array([r[2] for r in DATA], float)
x = np.array([r[3] for r in DATA], float)
y = np.array([r[5] for r in DATA], float)
w = n / n.sum()
xm, ym = (w * x).sum(), (w * y).sum()
cov = (w * (x - xm) * (y - ym)).sum()
r = cov / np.sqrt((w * (x - xm) ** 2).sum() * (w * (y - ym) ** 2).sum())
print(f"\n{'='*70}\nAcross the 25 sports: weighted corr(LVEDd, wall thickness) "
      f"r = {r:.2f}\n{'='*70}")
