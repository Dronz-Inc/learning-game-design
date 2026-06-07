#!/usr/bin/env python3
"""
Find TIDY, THEMATIC 3-set options.

Each set is drawn from a single coherent theme (curated, clean criteria). We pair
TWO independent themes (name / flag / capital / culture) with ONE geography theme
(location / borders / terrain / size) -- the structure that reliably yields zero
impossible combinations. For each theme-trio we hill-climb the 6+6+6 pick to:
  1) zero impossible combos      (hard requirement)
  2) easy band (>=10 answers) under 20%
  3) as many hard (==1) combos as possible
Then we print the best options and chart the top three.
"""
import itertools
import os
import random

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import build_criteria as B
from traits_matrix import trait_masks

M = trait_masks()                     # key -> (group, label, bitmask)
pc = B.popcount
def lbl(k): return M[k][1]

# ---- curated tidy theme pools (trait keys) ---------------------------------
THEMES = {
    "Name & spelling": ["nm_starts_vowel", "nm_ends_vowel", "nm_ends_a", "nm_ends_n",
                         "nm_has_o", "nm_has_r", "nm_double", "nm_two_words",
                         "len_le5", "len_6_7", "len_8_9", "len_ge10"],
    "Flag": ["fc_green", "fc_yellow", "fc_black", "fc_blue", "fc_4plus",
             "fs_star", "fs_sun", "fs_crescent", "fs_emblem", "fs_animal", "fs_none"],
    "Capital city": ["cap_starts_vowel", "cap_le5", "cap_ge9", "cap_two_words",
                     "cap_same_initial", "ms_cap_not_largest"],
    "Culture & trivia": ["g_drives_left", "g_monarchy", "g_commonwealth", "g_eu",
                         "l_english", "l_french", "l_arabic", "cur_dollar", "cur_euro",
                         "ms_bigcat", "ms_eagle", "ms_multitz"],
    "Location": ["loc_africa", "loc_asia", "loc_europe", "loc_americas",
                 "loc_na", "loc_sa", "loc_south", "loc_oceania"],
    "Borders & shape": ["b_landlocked", "b_island", "b_archipelago", "b_one",
                        "b_le2", "b_ge4", "b_ge5"],
    "Terrain & climate": ["cl_tropical", "cl_arid", "cl_temperate", "cl_contin", "cl_med",
                         "px_volcano", "px_desert", "p_ge3000", "p_ge4000", "px_below0", "gl_tropic"],
    "Size & people": ["a_ge1m", "a_lt50k", "a_lt20k", "pop_ge50m", "pop_ge20m",
                      "pop_lt5m", "pop_lt1m"],
}
INDEP = ["Name & spelling", "Flag", "Capital city", "Culture & trivia"]
GEO = ["Location", "Borders & shape", "Terrain & climate", "Size & people"]


def report(counts):
    t = len(counts)
    return dict(n0=sum(c == 0 for c in counts), n1=sum(c == 1 for c in counts),
                nge10=sum(c >= 10 for c in counts), mx=max(counts),
                mean=sum(counts) / t)


def key(r):
    return (r["n0"], max(0, r["nge10"] - 43), -r["n1"], abs(r["mean"] - 3.2))


def evalsel(a, b, c):
    return [pc(M[ka][2] & M[kb][2] & M[kc][2]) for ka in a for kb in b for kc in c]


def climb(poolA, poolB, poolC, rng, restarts=40):
    best, bestk = None, None
    for _ in range(restarts):
        sets = [rng.sample(poolA, 6), rng.sample(poolB, 6), rng.sample(poolC, 6)]
        pools = [poolA, poolB, poolC]
        counts = evalsel(*sets); k = key(report(counts))
        improved = True
        while improved:
            improved = False
            for si in range(3):
                for pos in range(6):
                    cur = sets[si][pos]
                    for cand in pools[si]:
                        if cand in sets[si]:
                            continue
                        sets[si][pos] = cand
                        nk = key(report(evalsel(*sets)))
                        if nk < k:
                            k = nk; cur = cand; improved = True
                        else:
                            sets[si][pos] = cur
        if bestk is None or k < bestk:
            bestk = k; best = ([list(s) for s in sets], report(evalsel(*sets)), evalsel(*sets))
    return best


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    rng = random.Random(3)
    results = []
    for (i1, i2) in itertools.combinations(INDEP, 2):
        for g in GEO:
            names = [i1, i2, g]
            sets, rep, counts = climb(THEMES[i1], THEMES[i2], THEMES[g], rng)
            results.append((key(rep), names, sets, rep, counts))
    results.sort(key=lambda x: x[0])

    print(f"Explored {len(results)} theme-trios (2 independent + 1 geography).\n")
    for rank, (k, names, sets, rep, counts) in enumerate(results[:6], 1):
        print("=" * 74)
        print(f"#{rank}  {names[0]}  +  {names[1]}  +  {names[2]}")
        print(f"     impossible={rep['n0']}  hard(=1)={rep['n1']} ({rep['n1']/216*100:.0f}%)"
              f"  easy>=10={rep['nge10']} ({rep['nge10']/216*100:.0f}%)  max={rep['mx']}")
        for tname, s in zip(names, sets):
            print(f"     [{tname}] " + "; ".join(lbl(x) for x in s))

    # chart top 3
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.8), sharey=True)
    for i, (k, names, sets, rep, counts) in enumerate(results[:3]):
        h = {}
        for c in counts:
            h[c] = h.get(c, 0) + 1
        xs = list(range(0, max(h) + 1)); ys = [h.get(x, 0) for x in xs]
        colors = ["#c0392b" if x == 0 else "#e67e22" if x == 1
                  else "#2e86c1" if x <= 10 else "#95a5a6" for x in xs]
        ax = axes[i]
        ax.bar(xs, ys, color=colors)
        ax.set_title("  +  ".join(names) +
                     f"\nimpossible={rep['n0']}  hard={rep['n1']}  easy>=10={rep['nge10']}",
                     fontsize=9)
        ax.set_xlabel("answers per combo"); ax.set_xticks(xs)
        if i == 0:
            ax.set_ylabel("number of dice combos")
        ax.grid(axis="y", alpha=0.3)
    fig.suptitle("Tidy thematic options — answer-count frequency over 216 combos "
                 "(red=impossible, orange=hard '1', grey=>10)", fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.91])
    out = os.path.join(here, "thematic_options.png")
    fig.savefig(out, dpi=130)
    print("\nChart written:", out)


if __name__ == "__main__":
    main()
