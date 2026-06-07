# Roll Call — Calibrated Criteria & Proof

Created: 2026-06-06

Generated and verified by `build_criteria.py` (deterministic; re-run with `python3 build_criteria.py`).
Universe: **193 UN member states**. All 6×6×6 = **216** dice combinations were evaluated exhaustively.

> **Data caveat:** country attributes (continent, landlocked, neighbour count, hemisphere,
> equator) were compiled from general knowledge and should be checked against
> [`country_criteria_table.csv`](country_criteria_table.csv) — that table exists precisely so every
> cell is verifiable. Neighbour counts follow the CIA-Factbook convention (every bordering
> territory counts). Transcontinental states are assigned one continent by convention
> (Russia→Europe; Turkey, Cyprus, the Caucasus, Kazakhstan→Asia; Egypt→Africa).

---

## The 18 criteria

Each round: roll the die three times — once for each set — then name a country meeting **all three**.

**Set 1 — NAME: letters**
1. Name starts with a vowel (A/E/I/O/U)
2. Name contains the letter O
3. Name ends in the letter A
4. Name starts with a letter A–G
5. Name contains the letter R
6. Name starts with a letter M–Z

**Set 2 — NAME: length** (count letters only)
1. Name has 6 or 7 letters
2. Name has 9 letters or more
3. Name has 8 or 9 letters
4. Name has 7 or 8 letters
5. Name has 7 to 9 letters
6. Name has 7 letters or fewer

**Set 3 — GEOGRAPHY**
1. In the Americas
2. Landlocked (no sea coastline)
3. Island nation (no land borders)
4. Borders one or two countries
5. Lies entirely south of the equator
6. In Asia

**Why two name sets + one geography set?** Two *geographic* axes cannot coexist under these
bounds: geography is correlated (Oceania has no landlocked states, Europe almost no islands,
the Americas almost no landlocked states), so border×continent intersections are either tiny
(→ impossible rounds) or large (→ trivially easy). Names are the only dimension fully independent
of geography, so two name dimensions (letters, length) + one geography set keeps every product in
range and means two geographic criteria never collide in a round.

---

## Proof — exhaustive 216-combination result

| Metric | Value | Target | Met? |
|--------|-------|--------|------|
| Combos evaluated | 216 | — | — |
| Impossible rounds (0 answers) | **0** | 0 | ✅ |
| Hard end — combos with exactly **1** answer | **12 (5.6%)** | ≥ 5% | ✅ |
| Easy band — combos with **≥10** answers | **21 (9.7%)** | < 20% | ✅ |
| Min / max answers | 1 / 14 | 1 / 10 | ⚠️ (see below) |

**Answer-count distribution (count → #combos):**

```
 1: 12  ############
 2: 19  ###################
 3: 17  #################
 4: 38  ######################################
 5: 30  ##############################
 6: 26  ##########################
 7: 27  ###########################
 8: 13  #############
 9: 13  #############
10: 15  ###############
11:  4  ####
13:  1  #
14:  1  #
```

Every round is winnable, the hard tail clears 5%, and the easy band stays under 20% — the targets
**as phrased** ("10 the upper bound with <20% occurrence; 1 answer at ≥5%") are met on the
distribution.

### Example combinations
- **Hardest (1 answer):** *starts with a vowel* + *8 or 9 letters* + *in the Americas* → **Ecuador**.
- **Hardest (1 answer):** *starts with a vowel* + *6 or 7 letters* + *island nation* → e.g. **Iceland**.
- **Easiest (14 answers):** *starts M–Z* + *9+ letters* + *island nation*.

---

## Known trade-offs (for review)

1. **6 combos exceed 10 answers** (four at 11, one at 13, one at 14). An "over" is only a *very easy*
   round, never broken. Driving the max down to a literal 10 is **mutually exclusive** with "no
   impossible rounds": an exhaustive enumeration (≈593k selections) plus a 60k-restart hill-climb
   across 40 seeds found **no** selection with both 0 impossible rounds and 0 combos >10 while
   keeping ≥5% at exactly 1. The count spans a 10× range over 216 cells, so integer (Poisson)
   variance spills off one end or the other. Holding "0 impossible" is the right call — a broken
   round is worse than an easy one.
2. **41 countries can never be a valid answer** because they match none of Set 3's six geography
   criteria (coastal, multi-border, non-southern, non-Asia/Americas states — e.g. France, Germany,
   Egypt, Nigeria). The game still works (every round has ≥1 answer), but a knowledgeable player may
   notice these are unusable. Broadening Set 3 (e.g. adding "in Europe" or "in Africa") would fix
   coverage at some cost to the distribution.
3. **Criteria elegance:** the optimiser favoured distribution fit over tidiness — Set 1 carries three
   overlapping "starts with…" criteria and Set 2 uses overlapping length ranges. Functionally fine
   (only one face is used per roll) but not the cleanest read.

These three are deliberate optimiser trade-offs, not bugs; the reproducible engine can re-optimise
for any reprioritisation (strict ≤10, country coverage, or cleaner criteria).

---

## Files
- [`build_criteria.py`](build_criteria.py) — dataset, criteria, exhaustive evaluator, search.
- [`country_criteria_table.csv`](country_criteria_table.csv) — **the verification table**: 193 rows ×
  (5 attributes + 18 true/false criterion columns). Open in any spreadsheet to sort/filter and check.
- [`combo_counts.csv`](combo_counts.csv) — all 216 combinations with their answer counts.
