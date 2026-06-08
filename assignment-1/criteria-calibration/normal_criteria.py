#!/usr/bin/env python3
"""
Design + verify the EASY ("normal") mode criteria for Roll Call.

Three thematic sets, in line with the brief:
  Set 1 - Name    : letters / length of the country name (kept simple & fun)
  Set 2 - Location: where it sits - continent, hemisphere, tropics
  Set 3 - Geography: physical traits - volcanoes, landlocked, island, neighbours

Goal: EASIER than hard mode, but never trivial and never impossible. Every one
of the 216 dice rolls must have at least one valid country (zero impossible
rolls); we maximise the *minimum* cell so most rounds offer several answers
while still allowing a few tight single-answer rolls.

Countries are encoded as 193-bit masks per predicate so a full 216-cell
evaluation is just bit-AND + popcount. A randomized + greedy search picks the
best feasible 6/6/6 selection.

Run:  python3 normal_criteria.py
"""
import csv, json, os, re, random, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "country_data.csv")
ROWS = list(csv.DictReader(open(DATA)))
N = len(ROWS)

def letters(name): return re.sub(r"[^a-z]", "", name.lower())
def americas(r):   return r["Continent"] in ("North America", "South America")

# ---- candidate predicate pools (label -> predicate) ------------------------
NAME_POOL = {
    "Name has fewer than 7 letters":   lambda r: len(letters(r["Country"])) < 7,
    "Name has more than 9 letters":    lambda r: len(letters(r["Country"])) > 9,
    "Name starts with a vowel":        lambda r: letters(r["Country"])[:1] in tuple("aeiou"),
    "Name ends in the letter A":       lambda r: letters(r["Country"]).endswith("a"),
    "Name contains the letter N":      lambda r: "n" in letters(r["Country"]),
    "Name contains the letter I":      lambda r: "i" in letters(r["Country"]),
    "Name contains the letter R":      lambda r: "r" in letters(r["Country"]),
    "Name contains the letter O":      lambda r: "o" in letters(r["Country"]),
    "Name is a single word":           lambda r: " " not in r["Country"].strip(),
}
LOC_POOL = {
    "Located in Africa":               lambda r: r["Continent"] == "Africa",
    "Located in Asia":                 lambda r: r["Continent"] == "Asia",
    "Located in Europe":               lambda r: r["Continent"] == "Europe",
    "Located in the Americas":         americas,
    "Located in Africa or Europe":     lambda r: r["Continent"] in ("Africa", "Europe"),
    "Located in Asia or Oceania":      lambda r: r["Continent"] in ("Asia", "Oceania"),
    "Lies north of the equator":       lambda r: r["Hemisphere"] in ("Northern", "Both"),
    "Lies south of the equator":       lambda r: r["Hemisphere"] in ("Southern", "Both"),
    "Crossed by the equator or a tropic line": lambda r: "Yes" in (
        r["Crosses_equator"], r["Crosses_tropic_of_cancer"], r["Crosses_tropic_of_capricorn"]),
    "Lies entirely in the tropics or south of them": lambda r: r["Hemisphere"] in ("Southern", "Both")
        or "Yes" in (r["Crosses_tropic_of_cancer"], r["Crosses_equator"]),
}
GEO_POOL = {
    "Has active volcanoes":            lambda r: r["Has_active_volcanoes"] == "Yes",
    "Is landlocked (no sea coast)":    lambda r: r["Landlocked"] == "Yes",
    "Is an island nation":             lambda r: r["Archipelago"] == "Yes",
    "Has a sea or ocean coastline":    lambda r: r["Landlocked"] == "No",
    "Borders only one country":        lambda r: r["Bordering_countries"] == "1",
    "Borders four or more countries":  lambda r: int(r["Bordering_countries"]) >= 4,
    "Larger than 1,000,000 km":        lambda r: int(r["Area_km2"]) >= 1_000_000,
    "Smaller than 100,000 km":         lambda r: int(r["Area_km2"]) < 100_000,
}

# thematic anchors we *want* to appear (keeps the sets readable & on-brief).
# These are the signature "easy mode" physical traits the brief calls out.
NAME_ANCHOR = []   # name set is free
LOC_ANCHOR  = []   # location set is free
GEO_ANCHOR  = ["Has active volcanoes", "Is landlocked (no sea coast)", "Is an island nation"]

def mask(pred):
    m = 0
    for i, r in enumerate(ROWS):
        if pred(r): m |= (1 << i)
    return m

NAME_M = {k: mask(v) for k, v in NAME_POOL.items()}
LOC_M  = {k: mask(v) for k, v in LOC_POOL.items()}
GEO_M  = {k: mask(v) for k, v in GEO_POOL.items()}

def counts_for(name6, loc6, geo6):
    nm = [NAME_M[k] for k in name6]
    lm = [LOC_M[k] for k in loc6]
    gm = [GEO_M[k] for k in geo6]
    out = []
    for a in nm:
        for b in lm:
            nl = a & b
            if nl == 0:
                out.extend([0] * 6)
                continue
            for c in gm:
                out.append(bin(nl & c).count("1"))
    return out

def score(counts):
    # feasible first (no zeros), then push up the floor, fewer ones, more total
    return (counts.count(0) == 0, min(counts), -counts.count(1), sum(counts))

def pick(pool_keys, anchors, k=6, rng=random):
    chosen = list(anchors)
    rest = [x for x in pool_keys if x not in chosen]
    rng.shuffle(rest)
    chosen += rest[: k - len(chosen)]
    return chosen

def neighbours(name6, loc6, geo6):
    """Yield configs one single-criterion swap away, respecting anchors."""
    for idx, (cur, pool, anchor) in enumerate([
            (name6, NAME_POOL, NAME_ANCHOR),
            (loc6,  LOC_POOL,  LOC_ANCHOR),
            (geo6,  GEO_POOL,  GEO_ANCHOR)]):
        for i, slot in enumerate(cur):
            if slot in anchor:
                continue
            for cand in pool:
                if cand in cur:
                    continue
                new = list(cur); new[i] = cand
                if idx == 0: yield new, loc6, geo6
                elif idx == 1: yield name6, new, geo6
                else: yield name6, loc6, new

def hill_climb(name6, loc6, geo6):
    best = (score(counts_for(name6, loc6, geo6)), name6, loc6, geo6)
    improved = True
    while improved:
        improved = False
        for n, l, g in neighbours(best[1], best[2], best[3]):
            s = score(counts_for(n, l, g))
            if s > best[0]:
                best = (s, n, l, g); improved = True; break
    return best

def search(restarts=400):
    rng = random.Random(7)
    nk, lk, gk = list(NAME_POOL), list(LOC_POOL), list(GEO_POOL)
    best = None
    for _ in range(restarts):
        n0 = pick(nk, NAME_ANCHOR, 6, rng)
        l0 = pick(lk, LOC_ANCHOR, 6, rng)
        g0 = pick(gk, GEO_ANCHOR, 6, rng)
        s, n, l, g = hill_climb(n0, l0, g0)
        if best is None or s > best[0]:
            best = (s, n, l, g)
    s, n, l, g = best
    return s, n, l, g, counts_for(n, l, g)

if __name__ == "__main__":
    s, name6, loc6, geo6, counts = search()
    feasible, mn, neg_ones, total = s
    print(f"feasible(no impossible roll)={feasible}  min-cell={mn}  "
          f"ones={-neg_ones}  total={total}  median={statistics.median(counts)}  "
          f"max={max(counts)}")
    print("\nSet 1 - Name:");    [print("  ", k) for k in name6]
    print("Set 2 - Location:");  [print("  ", k) for k in loc6]
    print("Set 3 - Geography:"); [print("  ", k) for k in geo6]
    json.dump({"sets": [name6, loc6, geo6]},
              open(os.path.join(HERE, "normal_sets.json"), "w"), indent=2)
    print("\nwrote normal_sets.json")
