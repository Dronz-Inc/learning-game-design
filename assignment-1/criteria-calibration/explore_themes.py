#!/usr/bin/env python3
"""
Explore alternative SET THEMES for Roll Call:
  Set 1 = NAME (letter categories + length, kept tidy)
  Set 2 = LOCATION (continent / hemisphere / equator)
  Set 3 = GEOGRAPHIC VARIANT (borders, shape, size)

Relaxed objective (per latest direction):
  - minimise impossible rounds (answer count == 0)
  - it's OK to have some combos with >10 answers, but not too many
  - PREFER more "hard" combos (exactly 1 answer)

Tries every 6-of-pool selection per set, ranks them, prints the top 3, and
renders a bar chart of the answer-count frequency for each.
"""
import csv
import itertools
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import build_criteria as B   # reuse the 193-country dataset + helpers

attrs, letters, has_double = B.attrs, B.letters, B.has_double
NAMES, IDX, popcount = B.NAMES, B.IDX, B.popcount

# ---- a couple of area tiers (well-known; approximate, verify in table) -------
LARGE_AREA = {  # ~30 largest by area
    "Russia", "Canada", "United States", "China", "Brazil", "Australia", "India",
    "Argentina", "Kazakhstan", "Algeria", "Democratic Republic of the Congo",
    "Saudi Arabia", "Mexico", "Indonesia", "Sudan", "Libya", "Iran", "Mongolia",
    "Peru", "Chad", "Niger", "Angola", "Mali", "South Africa", "Colombia",
    "Ethiopia", "Bolivia", "Mauritania", "Egypt", "Tanzania",
}
SMALL_AREA = {  # ~30 smallest by area
    "Monaco", "Nauru", "Tuvalu", "San Marino", "Liechtenstein", "Marshall Islands",
    "Saint Kitts and Nevis", "Maldives", "Malta", "Grenada",
    "Saint Vincent and the Grenadines", "Barbados", "Antigua and Barbuda",
    "Seychelles", "Palau", "Andorra", "Saint Lucia", "Singapore", "Micronesia",
    "Tonga", "Dominica", "Bahrain", "Kiribati", "Sao Tome and Principe", "Comoros",
    "Luxembourg", "Samoa", "Cabo Verde", "Brunei", "Trinidad and Tobago",
}

def _len_le(k):
    return lambda nm: len(letters(nm)) <= k
def _len_rng(lo, hi):
    return lambda nm: lo <= len(letters(nm)) <= hi

POOL_NAME = [   # Set 1 — tidy: vowel/consonant categories + length
    ("starts_vowel", "Starts with a vowel",          lambda nm: letters(nm)[0] in "aeiou"),
    ("ends_vowel",   "Ends in a vowel",              lambda nm: letters(nm)[-1] in "aeiou"),
    ("ends_cons",    "Ends in a consonant",          lambda nm: letters(nm)[-1] not in "aeiou"),
    ("double",       "Has a double letter",          has_double),
    ("two_words",    "Is more than one word",        lambda nm: " " in nm.strip()),
    ("len_le5",      "5 letters or fewer",           _len_le(5)),
    ("len_le6",      "6 letters or fewer",           _len_le(6)),
    ("len_7_8",      "7 or 8 letters",               _len_rng(7, 8)),
    ("len_ge9",      "9 letters or more",            lambda nm: len(letters(nm)) >= 9),
    ("len_ge10",     "10 letters or more",           lambda nm: len(letters(nm)) >= 10),
]

POOL_LOC = [    # Set 2 — location
    ("africa",   "In Africa",                 lambda nm: attrs(nm)["continent"] == "AF"),
    ("asia",     "In Asia",                   lambda nm: attrs(nm)["continent"] == "AS"),
    ("europe",   "In Europe",                 lambda nm: attrs(nm)["continent"] == "EU"),
    ("americas", "In the Americas",           lambda nm: attrs(nm)["continent"] == "AM"),
    ("oceania",  "In Oceania",                lambda nm: attrs(nm)["continent"] == "OC"),
    ("southern", "Entirely south of equator", lambda nm: attrs(nm)["southern"]),
    ("equator",  "Equator passes through it", lambda nm: attrs(nm)["equator"]),
    ("northern", "Entirely north of equator", lambda nm: not attrs(nm)["southern"] and not attrs(nm)["equator"]),
]

POOL_GEO = [    # Set 3 — geographic variant (borders / shape / size)
    ("landlocked", "Landlocked",                  lambda nm: attrs(nm)["landlocked"]),
    ("island",     "Island (no land borders)",    lambda nm: attrs(nm)["neighbours"] == 0),
    ("one_nbr",    "Borders exactly one country",  lambda nm: attrs(nm)["neighbours"] == 1),
    ("le2_nbr",    "Borders 1 or 2 countries",     lambda nm: 1 <= attrs(nm)["neighbours"] <= 2),
    ("ge4_nbr",    "Borders 4+ countries",         lambda nm: attrs(nm)["neighbours"] >= 4),
    ("ge5_nbr",    "Borders 5+ countries",         lambda nm: attrs(nm)["neighbours"] >= 5),
    ("large",      "Among the ~30 largest by area",lambda nm: nm in LARGE_AREA),
    ("small",      "Among the ~30 smallest by area",lambda nm: nm in SMALL_AREA),
]

def masks(pool):
    return {k: (lbl, B.mask_of(pred)) for k, lbl, pred in pool}
MN, ML, MG = masks(POOL_NAME), masks(POOL_LOC), masks(POOL_GEO)


def report(counts):
    t = len(counts)
    n0 = sum(c == 0 for c in counts)
    nov = sum(c > 10 for c in counts)
    n1 = sum(c == 1 for c in counts)
    nge10 = sum(c >= 10 for c in counts)
    return dict(t=t, mn=min(counts), mx=max(counts), n0=n0, nov=nov, n1=n1,
                nge10=nge10, mean=sum(counts) / t)


def key(rep):
    # 1) fewest impossible rounds; 2) keep >10 combos under ~25; 3) MORE hard (==1)
    return (rep["n0"], max(0, rep["nov"] - 25), -rep["n1"], abs(rep["mean"] - 3.5))


def evaluate(a, b, c):
    counts = []
    for ka in a:
        ma = MN[ka][1]
        for kb in b:
            mab = ma & ML[kb][1]
            for kc in c:
                counts.append(popcount(mab & MG[kc][1]))
    return counts


def search_all():
    keysN = [k for k, *_ in POOL_NAME]
    keysL = [k for k, *_ in POOL_LOC]
    keysG = [k for k, *_ in POOL_GEO]
    results = []
    for a in itertools.combinations(keysN, 6):
        for b in itertools.combinations(keysL, 6):
            for c in itertools.combinations(keysG, 6):
                counts = evaluate(a, b, c)
                rep = report(counts)
                results.append((a, b, c, rep, counts))
    return results


def pick(results, sort_key):
    return min(results, key=sort_key)


def hist(counts):
    h = {}
    for c in counts:
        h[c] = h.get(c, 0) + 1
    return h


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    results = search_all()
    min0 = min(r[3]["n0"] for r in results)
    print(f"(evaluated {len(results)} selections; fewest possible impossible combos = {min0})\n")

    # three trade-off points along the frontier
    opt_safe = pick(results, lambda r: (r[3]["n0"], -r[3]["n1"], abs(r[3]["mean"] - 3.5)))
    opt_hard = pick(results, lambda r: (-r[3]["n1"], r[3]["n0"], max(0, r[3]["nov"] - 30)))
    # B: a harder middle -- fewest impossible among selections with >=62 hard combos
    mid = [r for r in results if r[3]["n1"] >= 62]
    opt_bal = pick(mid, lambda r: (r[3]["n0"], -r[3]["n1"])) if mid else opt_safe
    labelled = [("A — fewest impossible", opt_safe),
                ("B — balanced", opt_bal),
                ("C — most hard (=1) combos", opt_hard)]

    fig, axes = plt.subplots(1, 3, figsize=(16, 4.8), sharey=True)
    for i, (title, (a, b, c, rep, counts)) in enumerate(labelled):
        print("=" * 72)
        print(f"OPTION {title}")
        print("  Set 1 NAME    :", ", ".join(MN[x][0] for x in a))
        print("  Set 2 LOCATION:", ", ".join(ML[x][0] for x in b))
        print("  Set 3 GEO     :", ", ".join(MG[x][0] for x in c))
        print(f"  -> min/max={rep['mn']}/{rep['mx']}  impossible(0)={rep['n0']} "
              f"({rep['n0']/216*100:.1f}%)  >10={rep['nov']}  ==1 hard={rep['n1']} "
              f"({rep['n1']/216*100:.1f}%)  >=10 easy band={rep['nge10']} ({rep['nge10']/216*100:.1f}%)")

        h = hist(counts)
        xs = list(range(0, max(h) + 1))
        ys = [h.get(x, 0) for x in xs]
        colors = ["#c0392b" if x == 0 else "#e67e22" if x == 1
                  else "#2e86c1" if x <= 10 else "#95a5a6" for x in xs]
        ax = axes[i]
        ax.bar(xs, ys, color=colors)
        ax.set_title(f"{title}\nimpossible={rep['n0']}  hard(=1)={rep['n1']}  >10={rep['nov']}",
                     fontsize=10)
        ax.set_xlabel("answers per combo (# matching countries)")
        if i == 0:
            ax.set_ylabel("number of dice combos")
        ax.set_xticks(xs)
        ax.grid(axis="y", alpha=0.3)
    fig.suptitle("Roll Call — name + location + geographic-variant: answer-count frequency over 216 combos\n"
                 "(red = impossible '0', orange = hard '1', grey = >10 easy)", fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.90])
    out = os.path.join(here, "theme_options.png")
    fig.savefig(out, dpi=130)
    print("\nChart written:", out)


if __name__ == "__main__":
    main()

