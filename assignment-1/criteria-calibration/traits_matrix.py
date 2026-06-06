#!/usr/bin/env python3
"""
Master TRAITS MATRIX for Roll Call.

One canonical registry of EVERY candidate trait we are exploring as a possible
game criterion, evaluated Y/N for all 193 countries. Re-run to regenerate
`traits_matrix.csv` whenever traits are added or the dataset changes.

This is the single source for combo exploration: open the CSV in a spreadsheet,
or load it / this registry in a script, and test any 3-set selection without
re-deriving country facts each time.

    python3 traits_matrix.py        # regenerates traits_matrix.csv

To add a trait: append one (key, group, label, predicate) row to TRAITS below
and re-run. Keep `group` consistent so the columns stay organised.
"""
import csv
import os

import build_criteria as B

attrs, letters, has_double = B.attrs, B.letters, B.has_double
NAMES, IDX = B.NAMES, B.IDX

# Area tiers (well-known; approximate -- verify against this very table).
LARGE_AREA = {
    "Russia", "Canada", "United States", "China", "Brazil", "Australia", "India",
    "Argentina", "Kazakhstan", "Algeria", "Democratic Republic of the Congo",
    "Saudi Arabia", "Mexico", "Indonesia", "Sudan", "Libya", "Iran", "Mongolia",
    "Peru", "Chad", "Niger", "Angola", "Mali", "South Africa", "Colombia",
    "Ethiopia", "Bolivia", "Mauritania", "Egypt", "Tanzania",
}
SMALL_AREA = {
    "Monaco", "Nauru", "Tuvalu", "San Marino", "Liechtenstein", "Marshall Islands",
    "Saint Kitts and Nevis", "Maldives", "Malta", "Grenada",
    "Saint Vincent and the Grenadines", "Barbados", "Antigua and Barbuda",
    "Seychelles", "Palau", "Andorra", "Saint Lucia", "Singapore", "Micronesia",
    "Tonga", "Dominica", "Bahrain", "Kiribati", "Sao Tome and Principe", "Comoros",
    "Luxembourg", "Samoa", "Cabo Verde", "Brunei", "Trinidad and Tobago",
}

def L(nm):
    return len(letters(nm))

# (key, group, human label, predicate)
TRAITS = [
    # --- NAME: letters ---
    ("starts_vowel", "name-letters", "Starts with a vowel",        lambda n: letters(n)[0] in "aeiou"),
    ("ends_vowel",   "name-letters", "Ends in a vowel",            lambda n: letters(n)[-1] in "aeiou"),
    ("ends_cons",    "name-letters", "Ends in a consonant",        lambda n: letters(n)[-1] not in "aeiou"),
    ("ends_a",       "name-letters", "Ends in A",                  lambda n: letters(n).endswith("a")),
    ("ends_n",       "name-letters", "Ends in N",                  lambda n: letters(n).endswith("n")),
    ("ends_ia",      "name-letters", "Ends in -IA",                lambda n: letters(n).endswith("ia")),
    ("ends_land",    "name-letters", "Ends in -LAND",              lambda n: letters(n).endswith("land")),
    ("ends_stan",    "name-letters", "Ends in -STAN",              lambda n: letters(n).endswith("stan")),
    ("has_double",   "name-letters", "Has a double letter",        has_double),
    ("has_no_a",     "name-letters", "Contains no A",              lambda n: "a" not in letters(n)),
    ("has_no_e",     "name-letters", "Contains no E",              lambda n: "e" not in letters(n)),
    ("has_o",        "name-letters", "Contains an O",              lambda n: "o" in letters(n)),
    ("has_r",        "name-letters", "Contains an R",              lambda n: "r" in letters(n)),
    ("has_z",        "name-letters", "Contains a Z",               lambda n: "z" in letters(n)),
    ("all_vowels",   "name-letters", "Uses all five vowels",       lambda n: set("aeiou") <= set(letters(n))),
    ("starts_a_g",   "name-letters", "Starts with A-G",            lambda n: letters(n)[0] <= "g"),
    ("starts_m_z",   "name-letters", "Starts with M-Z",            lambda n: letters(n)[0] >= "m"),
    # --- NAME: structure ---
    ("two_words",    "name-structure", "More than one word",       lambda n: " " in n.strip()),
    ("one_word",     "name-structure", "Single word",              lambda n: " " not in n.strip()),
    # --- NAME: length ---
    ("len_le4",  "name-length", "4 letters or fewer", lambda n: L(n) <= 4),
    ("len_le5",  "name-length", "5 letters or fewer", lambda n: L(n) <= 5),
    ("len_le6",  "name-length", "6 letters or fewer", lambda n: L(n) <= 6),
    ("len_le7",  "name-length", "7 letters or fewer", lambda n: L(n) <= 7),
    ("len_5_6",  "name-length", "5 or 6 letters",     lambda n: 5 <= L(n) <= 6),
    ("len_6_7",  "name-length", "6 or 7 letters",     lambda n: 6 <= L(n) <= 7),
    ("len_7_8",  "name-length", "7 or 8 letters",     lambda n: 7 <= L(n) <= 8),
    ("len_8_9",  "name-length", "8 or 9 letters",     lambda n: 8 <= L(n) <= 9),
    ("len_ge8",  "name-length", "8 letters or more",  lambda n: L(n) >= 8),
    ("len_ge9",  "name-length", "9 letters or more",  lambda n: L(n) >= 9),
    ("len_ge10", "name-length", "10 letters or more", lambda n: L(n) >= 10),
    ("len_ge11", "name-length", "11 letters or more", lambda n: L(n) >= 11),
    # --- LOCATION ---
    ("africa",   "location", "In Africa",                 lambda n: attrs(n)["continent"] == "AF"),
    ("asia",     "location", "In Asia",                   lambda n: attrs(n)["continent"] == "AS"),
    ("europe",   "location", "In Europe",                 lambda n: attrs(n)["continent"] == "EU"),
    ("americas", "location", "In the Americas",           lambda n: attrs(n)["continent"] == "AM"),
    ("oceania",  "location", "In Oceania",                lambda n: attrs(n)["continent"] == "OC"),
    ("afr_or_am","location", "In Africa or the Americas", lambda n: attrs(n)["continent"] in ("AF", "AM")),
    ("eu_or_as", "location", "In Europe or Asia",         lambda n: attrs(n)["continent"] in ("EU", "AS")),
    ("southern", "location", "Entirely south of equator", lambda n: attrs(n)["southern"]),
    ("northern", "location", "Entirely north of equator", lambda n: not attrs(n)["southern"] and not attrs(n)["equator"]),
    ("equator",  "location", "Equator passes through it",  lambda n: attrs(n)["equator"]),
    # --- BORDERS / SHAPE ---
    ("landlocked", "borders", "Landlocked",                 lambda n: attrs(n)["landlocked"]),
    ("coast",      "borders", "Has a sea coastline",        lambda n: not attrs(n)["landlocked"]),
    ("island",     "borders", "Island (no land borders)",   lambda n: attrs(n)["neighbours"] == 0),
    ("has_border", "borders", "Has at least one land border",lambda n: attrs(n)["neighbours"] >= 1),
    ("one_nbr",    "borders", "Borders exactly one country", lambda n: attrs(n)["neighbours"] == 1),
    ("le2_nbr",    "borders", "Borders 1 or 2 countries",    lambda n: 1 <= attrs(n)["neighbours"] <= 2),
    ("mid_nbr",    "borders", "Borders 2 to 4 countries",    lambda n: 2 <= attrs(n)["neighbours"] <= 4),
    ("ge3_nbr",    "borders", "Borders 3 or more countries", lambda n: attrs(n)["neighbours"] >= 3),
    ("ge4_nbr",    "borders", "Borders 4 or more countries", lambda n: attrs(n)["neighbours"] >= 4),
    ("ge5_nbr",    "borders", "Borders 5 or more countries", lambda n: attrs(n)["neighbours"] >= 5),
    # --- SIZE ---
    ("large", "size", "Among the ~30 largest by area",  lambda n: n in LARGE_AREA),
    ("small", "size", "Among the ~30 smallest by area", lambda n: n in SMALL_AREA),
]


def trait_masks():
    """Return {key: (group, label, bitmask)} for use by exploration scripts."""
    out = {}
    for key, group, label, pred in TRAITS:
        out[key] = (group, label, B.mask_of(pred))
    return out


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "traits_matrix.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        header = (["Country", "Continent", "Landlocked", "Neighbours", "Equator", "Southern"]
                  + [f"[{g}] {lbl}" for (_, g, lbl, _) in TRAITS])
        w.writerow(header)
        for nm in NAMES:
            at = attrs(nm)
            row = [nm, at["continent"], at["landlocked"], at["neighbours"],
                   at["equator"], at["southern"]]
            row += ["Y" if pred(nm) else "" for (_, _, _, pred) in TRAITS]
            w.writerow(row)
    # breadth summary
    print(f"Wrote {path}  ({len(NAMES)} countries x {len(TRAITS)} traits)")
    print("\nTrait breadths (how many countries match):")
    grp = None
    for key, group, label, pred in TRAITS:
        if group != grp:
            grp = group
            print(f"  -- {group} --")
        cnt = sum(1 for n in NAMES if pred(n))
        print(f"     {label:34s} {cnt:3d}  ({cnt/len(NAMES)*100:.0f}%)")


if __name__ == "__main__":
    main()
