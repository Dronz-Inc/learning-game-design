#!/usr/bin/env python3
"""
FINAL locked criteria for Roll Call (Option 1: Name + Flag + Terrain).

Deterministic: evaluates exactly these 18 criteria across all 216 dice combos,
writes the verification table + 216-combo grid + distribution chart, and prints
the proof. Re-run any time: python3 final_criteria.py
"""
import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import build_criteria as B
from traits_matrix import trait_masks

M = trait_masks()
pc, NAMES, IDX = B.popcount, B.NAMES, B.IDX
HERE = os.path.dirname(os.path.abspath(__file__))

# page wording -> trait key
SETS = [
    ("Set 1 - NAME & SPELLING", [
        ("Name has fewer than 8 letters", "len_le7"),
        ("Name has more than 8 letters", "len_ge9"),
        ("Name starts with a vowel", "nm_starts_vowel"),
        ("Name ends in the letter A", "nm_ends_a"),
        ("Name contains the letter O", "nm_has_o"),
        ("Name contains the letter R", "nm_has_r"),
    ]),
    ("Set 2 - FLAG", [
        ("Flag has 4 or more colours", "fc_4plus"),
        ("Flag has green", "fc_green"),
        ("Flag has yellow", "fc_yellow"),
        ("Flag has a star", "fs_star"),
        ("Flag has a coat of arms / emblem", "fs_emblem"),
        ("Flag has no symbol (colours only)", "fs_none"),
    ]),
    ("Set 3 - TERRAIN & CLIMATE", [
        ("Crossed by a tropic line", "gl_tropic"),
        ("Mainly arid climate", "cl_arid"),
        ("Has a major desert", "px_desert"),
        ("Has a peak above 4,000 m", "p_ge4000"),
        ("Mainly tropical climate", "cl_tropical"),
        ("Has active volcanoes", "px_volcano"),
    ]),
]

A = SETS[0][1]; Bb = SETS[1][1]; C = SETS[2][1]


def counts_all():
    out = []
    for la, ka in A:
        ma = M[ka][2]
        for lb, kb in Bb:
            mab = ma & M[kb][2]
            for lc, kc in C:
                out.append((la, lb, lc, pc(mab & M[kc][2])))
    return out


def members(ka, kb, kc):
    m = M[ka][2] & M[kb][2] & M[kc][2]
    return [n for n in NAMES if (m >> IDX[n]) & 1]


def main():
    rows = counts_all()
    cs = [r[3] for r in rows]
    t = len(cs)
    n0 = sum(c == 0 for c in cs); n1 = sum(c == 1 for c in cs)
    nge10 = sum(c >= 10 for c in cs)
    print("=" * 70)
    print("OPTION 1 - FINAL PROOF (216 dice combinations)")
    print("=" * 70)
    print(f"  impossible (0 answers) : {n0}  ({n0/t*100:.1f}%)   target 0")
    print(f"  hard (exactly 1)       : {n1}  ({n1/t*100:.1f}%)   target >= 5%")
    print(f"  easy band (>= 10)      : {nge10}  ({nge10/t*100:.1f}%)   target < 20%")
    print(f"  min / max answers      : {min(cs)} / {max(cs)}   mean {sum(cs)/t:.1f}")
    h = {}
    for c in cs:
        h[c] = h.get(c, 0) + 1
    print("\n  histogram (answers -> #combos):")
    for kk in range(0, max(h) + 1):
        if kk in h:
            print(f"    {kk:2d}: {h[kk]:3d}  {'#'*h[kk]}")

    # per-criterion breadth
    print("\n  per-criterion breadth (countries matching):")
    for title, items in SETS:
        print(f"   {title}")
        for lbl, k in items:
            print(f"     {lbl:38s} {pc(M[k][2]):3d}")

    # example hardest combos (==1)
    print("\n  sample hardest combos (exactly 1 answer):")
    shown = 0
    for la, ka in A:
        for lb, kb in Bb:
            for lc, kc in C:
                if pc(M[ka][2] & M[kb][2] & M[kc][2]) == 1 and shown < 6:
                    who = members(ka, kb, kc)[0]
                    print(f"     {la} + {lb} + {lc}  ->  {who}")
                    shown += 1

    # ---- verification table (193 x 18) ----
    flat = [(t_, l_, k_) for (t_, items) in SETS for (l_, k_) in items]
    with open(os.path.join(HERE, "final_verification_table.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Country"] + [l for (_, l, _) in flat])
        for n in NAMES:
            w.writerow([n] + ["Y" if (M[k][2] >> IDX[n]) & 1 else "" for (_, _, k) in flat])

    # ---- 216 combo grid ----
    with open(os.path.join(HERE, "final_combo_counts.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Set1_name", "Set2_flag", "Set3_terrain", "answers", "example_countries"])
        for la, ka in A:
            for lb, kb in Bb:
                for lc, kc in C:
                    mem = members(ka, kb, kc)
                    w.writerow([la, lb, lc, len(mem), "; ".join(mem[:5])])

    # ---- distribution chart ----
    xs = list(range(0, max(h) + 1)); ys = [h.get(x, 0) for x in xs]
    colors = ["#c0392b" if x == 0 else "#e67e22" if x == 1
              else "#2e86c1" if x <= 10 else "#95a5a6" for x in xs]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(xs, ys, color=colors)
    ax.set_title("Roll Call - Option 1 (Name + Flag + Terrain)\n"
                 f"216 combos: 0 impossible, {n1} hard (=1), {nge10} easy (>=10)")
    ax.set_xlabel("answers per combo (# matching countries)")
    ax.set_ylabel("number of dice combos")
    ax.set_xticks(xs); ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "final_distribution.png"), dpi=130)
    print("\nWrote final_verification_table.csv, final_combo_counts.csv, final_distribution.png")


if __name__ == "__main__":
    main()
