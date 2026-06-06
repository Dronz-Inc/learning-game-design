#!/usr/bin/env python3
"""Parse raw_table.md (pasted research table) into the canonical country_data.csv,
mapping country names to the game's canonical 193 and validating completeness."""
import csv
import os

import build_criteria as B

HERE = os.path.dirname(os.path.abspath(__file__))

# table name -> canonical game name
ALIAS = {
    "Ivory Coast": "Cote d'Ivoire",
    "Republic of the Congo": "Congo",
}

COLS = ["Country", "Capital", "Population", "Area_km2", "Continent", "Subregion",
        "Landlocked", "Bordering_countries", "Coasts", "Highest_peak_m", "Drives_on",
        "Official_languages", "Currency", "Government", "Hemisphere", "Flag_colors",
        "Flag_symbols", "Archipelago", "EU_member", "Commonwealth_member"]


def parse():
    rows = []
    with open(os.path.join(HERE, "raw_table.md")) as f:
        for line in f:
            line = line.strip()
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if cells[0] in ("Country", "") or set(cells[0]) <= set("-: "):
                continue
            rows.append(cells)
    return rows


def main():
    rows = parse()
    out = []
    for cells in rows:
        rec = dict(zip(COLS, cells))
        rec["Country"] = ALIAS.get(rec["Country"], rec["Country"])
        out.append(rec)

    names = {r["Country"] for r in out}
    canon = set(B.NAMES)
    missing = canon - names
    extra = names - canon
    print(f"parsed {len(out)} rows; missing={sorted(missing)}; extra={sorted(extra)}")
    assert not missing and not extra, "name mismatch -- fix ALIAS or raw_table.md"
    assert len(out) == 193, f"expected 193, got {len(out)}"

    with open(os.path.join(HERE, "country_data.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(COLS)
        for nm in B.NAMES:                       # write in canonical order
            r = next(x for x in out if x["Country"] == nm)
            w.writerow([r[c] for c in COLS])
    print("wrote country_data.csv")


if __name__ == "__main__":
    main()
