#!/usr/bin/env python3
"""Parse raw_table.md + raw_table2.md (pasted research tables) into the canonical
country_data.csv, mapping names to the game's 193 and validating completeness."""
import csv
import os

import build_criteria as B

HERE = os.path.dirname(os.path.abspath(__file__))
ALIAS = {"Ivory Coast": "Cote d'Ivoire", "Republic of the Congo": "Congo"}


def parse(path):
    """Return (header, list-of-rowdicts) from a markdown pipe table."""
    header, rows = None, []
    with open(os.path.join(HERE, path)) as f:
        for line in f:
            line = line.strip()
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if set("".join(cells)) <= set("-: "):     # separator row
                continue
            if header is None:
                header = cells
                continue
            rec = dict(zip(header, cells))
            rec["Country"] = ALIAS.get(rec["Country"], rec["Country"])
            rows.append(rec)
    return header, rows


def main():
    h1, t1 = parse("raw_table.md")
    h2, t2 = parse("raw_table2.md")
    d2 = {r["Country"]: r for r in t2}

    # merged column order: all of table1, then table2's new columns
    new_cols = [c for c in h2 if c not in h1]
    cols = h1 + new_cols

    by_name = {}
    for r in t1:
        merged = dict(r)
        extra = d2.get(r["Country"], {})
        for c in new_cols:
            merged[c] = extra.get(c, "")
        by_name[r["Country"]] = merged

    canon = set(B.NAMES)
    names = set(by_name)
    assert names == canon, f"name mismatch: missing={canon-names} extra={names-canon}"
    assert len(by_name) == 193, f"expected 193, got {len(by_name)}"

    with open(os.path.join(HERE, "country_data.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for nm in B.NAMES:
            r = by_name[nm]
            w.writerow([r.get(c, "") for c in cols])
    print(f"wrote country_data.csv ({len(by_name)} countries x {len(cols)} columns)")


if __name__ == "__main__":
    main()
