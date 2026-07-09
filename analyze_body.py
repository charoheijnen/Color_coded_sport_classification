"""
An alternative classification: which muscle groups drive the sport?

This is a judgment-based grouping into upper-body-dominant, lower-body-dominant,
and whole-body sports, as a complement to the Mitchell (static/dynamic)
classification. It reuses the same Spirito 1994 data and the same pooled-
summary-statistics machinery as analyze_trends.py, and quantifies how the LV
dimensions differ between body regions (one-way ANOVA + Welch pairwise tests).
"""

import numpy as np
from itertools import combinations

from analyze_trends import DATA, pooled, anova, welch, stars

GROUP_NAME = {
    "upper": "Upper-body",
    "lower": "Lower-body",
    "whole": "Whole-body",
}
GROUPS = ["lower", "upper", "whole"]

# Sport -> dominant working muscle region
BODY = {
    # Lower-body dominant (legs are the engine)
    "Track": "lower",
    "Cycling": "lower",
    "Roller-skating": "lower",
    "Soccer": "lower",
    "Alpine skiing": "lower",
    "Bobsledding": "lower",
    "Tae kwon do": "lower",
    "Equestrianism": "lower",
    # Upper-body dominant (arms / shoulders / trunk drive the action)
    "Canoeing": "upper",
    "Swimming": "upper",
    "Water polo": "upper",
    "Tennis": "upper",
    "Boxing": "upper",
    "Team handball": "upper",
    "Fencing": "upper",
    "Yachting": "upper",
    "Volleyball": "upper",
    "Wrestling and judo": "upper",
    "Field weight events": "upper",
    # Whole-body (arms and legs contribute comparably)
    "Rowing": "whole",
    "Cross-country skiing": "whole",
    "Pentathlon": "whole",
    "Weightlifting": "whole",
    "Diving": "whole",
    "Roller hockey": "whole",
}

assert set(BODY) == {r[0] for r in DATA}, "every sport must be classified"


def rows_for(group, idx_mean, idx_sd):
    return [(r[2], r[idx_mean], r[idx_sd]) for r in DATA if BODY[r[0]] == group]


def group_stats(group):
    """Return (N, mean_x, sd_x, mean_y, sd_y) for LVEDd (x) and wall thick (y)."""
    N, mx, sdx, _ = pooled(rows_for(group, 3, 4), 3, 4)
    _, my, sdy, _ = pooled(rows_for(group, 5, 6), 5, 6)
    return int(N), mx, sdx, my, sdy


def analyze(idx_mean, idx_sd, label):
    print(f"\n{'='*70}\n{label}\n{'='*70}")
    summ, groups = {}, []
    for g in GROUPS:
        rows = rows_for(g, idx_mean, idx_sd)
        N, m, sd, ss = pooled(rows, idx_mean, idx_sd)
        summ[g] = (N, m, sd)
        groups.append((N, m, sd, ss))
        print(f"  {GROUP_NAME[g]:<12} n={int(N):>3}  mean={m:5.2f}  "
              f"SD={sd:4.2f}  ({len(rows)} sports)")
    F, dfb, dfw, p = anova(groups)
    print(f"\n  One-way ANOVA: F({dfb},{dfw}) = {F:.2f}, p = {p:.2e} {stars(p)}")
    print("\n  Pairwise (Welch t-test, Cohen's d):")
    for a, b in combinations(GROUPS, 2):
        t, df, pp, d = welch(summ[a], summ[b])
        print(f"    {GROUP_NAME[a]:<11} vs {GROUP_NAME[b]:<11} "
              f"Δ={summ[a][1]-summ[b][1]:+5.2f}  t={t:6.2f}  "
              f"p={pp:.2e} {stars(pp):<3}  d={d:+.2f}")


if __name__ == "__main__":
    analyze(3, 4, "LV END-DIASTOLIC DIMENSION (mm) by body region")
    analyze(5, 6, "LV WALL THICKNESS (mm) by body region")
