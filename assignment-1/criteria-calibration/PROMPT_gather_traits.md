# Delegation prompt — gather more country traits for "Roll Call"

Copy everything in the box below to the other agent.

---

You are extending the candidate-trait pool for a one-player geography dice game called **Roll Call**.

**Repo:** `dronz-inc/learning-game-design`  ·  **Branch:** `claude/geography-game-plan-ddj7E`
**Work in:** `assignment-1/criteria-calibration/`

## The game (context)
The universe is the **193 UN member states**. A game uses **3 sets of 6 criteria**. Each round the player rolls a die three times (one criterion per set) and must name a country satisfying **all three**, from memory; the goal is the longest streak. A later step picks the final 3×6 from a large candidate pool and proves the difficulty distribution by exhaustively evaluating all 6×6×6 = 216 combinations.

**Your job is ONLY to expand the candidate-trait pool with accurate per-country data — do NOT pick the final 18 criteria.** Get a big, varied, well-sourced set of traits so the selection step has lots to work with.

## Hard requirement that shapes what to add
The selection must be able to produce **zero impossible combinations** (every round has ≥1 valid answer). Two *geographic* axes together (e.g. continent × border-type) create unavoidable empty intersections (Oceania has no landlocked states, Europe almost no islands…). So **prioritise dimensions that are INDEPENDENT of geography**, because they combine cleanly:
- name spelling, name length, **capital-city** properties, **flag** colours/symbols, **official language**, **currency**, **population**, **driving side**, **calling code / TLD**, organisation membership.
Geographic/physical traits (oceans, mountains, climate, regions, shape) are still welcome — but the pool needs to be rich in *independent* axes so a 0-impossible trio exists.

## The data structure (follow it exactly)
- `traits_matrix.py` — the **canonical trait registry**. Each trait is a tuple `(key, group, label, predicate)` where `predicate(country_name) -> bool` returns True/False for all 193 countries. Running `python3 traits_matrix.py` regenerates `traits_matrix.csv` (193 rows × every trait, Y/blank) and prints each trait's breadth.
- `country_ext.json` — committed snapshot of authoritative attributes (capital, population, area, languages, currency) keyed by the exact country names used in the game. **Add new raw data here** (extend each country's object) when a trait needs data the name alone can't provide.
- `build_criteria.py` — base dataset (`COUNTRIES`: continent, landlocked, neighbours, equator, southern) and the bitmask evaluator. The 193 canonical country names are `build_criteria.NAMES`.
- Helpers already present: `letters(name)`, `has_double(name)`; ext accessors `_cap`, `_pop`, `_area`, `_langs`, `_has_lang`, `_curname`, `_curcode`.

## What to add (aim for 40–70 NEW traits)
Brainstorm widely, then implement. Strong categories:
- **Flags** *(needs new data → add a `flag` field to `country_ext.json`)*: has red / blue / green / yellow / white / black; has a star / crescent / cross / sun-or-disc / coat-of-arms-or-seal / animal; horizontal vs vertical stripes; is a tricolour; contains a Union Jack.
- **Physical geography** *(new data)*: borders the Atlantic / Pacific / Indian Ocean / Mediterranean / Arctic; is an archipelago; has a peak above 3,000 m / 4,000 m; mostly desert; on the Pacific Ring of Fire; crossed by the equator (already have) / a tropic line; entirely within the tropics.
- **Region (finer than continent)** *(new data)*: Caribbean, Central America, South America, Nordic, Balkans, Middle East, Horn of Africa, Sahel, Central Asia, Southeast Asia, etc.
- **Capital extras**: capital is a coastal/port city *(new data)*; capital is NOT the largest city *(new data)*; capital ends in a vowel; capital has 3+ words.
- **Political / membership** *(new data, online-checkable)*: drives on the left; EU member; Commonwealth member; NATO; OPEC; landlocked-and-… ; is a monarchy; uses a non-Latin script name.
- **Name extras (no new data — derive from the name)**: contains a Q / X / K / J / W; first and last letter the same; has 3+ of the same letter; contains two words that both start with the same letter; is an adjective-form demonym match — be creative but keep them objective.

## Rules for every trait
1. **Objective & checkable** — resolves to a clear True/False for all 193 countries from a citable source (Wikipedia, CIA World Factbook, Natural Earth, etc.). A player must be able to verify it on a map or one lookup.
2. **Breadth target** — aim for traits matching **roughly 8%–45% of countries (≈15–87 of 193)**. Avoid <5% (causes impossible combos) and >55% (causes trivially-easy rounds). Spread breadths within each category.
3. **Accurate data** — when adding raw data to `country_ext.json`, fill **all 193** countries; do not leave gaps. Spot-check at least 8 countries per new data field against your source and note the source in a comment or in `SOURCES.md`.
4. **No duplicates** — don't add a trait that's ~95% identical to an existing one.
5. **Stable keys** — `key` is a short snake_case id, unique, never reused for a different meaning.

## Deliverables
1. Updated `traits_matrix.py` (new traits appended to `TRAITS`) and any new data merged into `country_ext.json` (or a new committed snapshot file if a different source is used).
2. Regenerated `traits_matrix.csv` (run `python3 traits_matrix.py` — it must run with **no network and no extra pip packages at runtime**; if you used a package to gather data, snapshot the results to JSON and commit the JSON, like `country_ext.json`).
3. A `SOURCES.md` listing each new data field and where it came from, and noting which fields are best-effort.
4. A short summary in your final message: how many traits added, by category, with their breadths (the script prints these), and any data you were unsure about.
5. Commit and push to the branch with a clear message. **Do not** select the final 18 criteria or change `build_criteria.py`'s base `COUNTRIES` facts — only add traits/data.

## Verify before you finish
- `python3 traits_matrix.py` runs clean and reports the new traits.
- Every new trait's breadth is printed and within (or near) the 8%–45% target; flag any that aren't.
- Spot-check a handful of countries per new data field against your source.

---
