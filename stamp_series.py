#!/usr/bin/env python
"""STAMP SERIES FIELDS ONTO THE CATALOG — the step that makes a file part of a series.

    py stamp_series.py            # dry run: show what would change
    py stamp_series.py --write    # apply, additive only

Why this exists:
  vault_catalog.json is a flat list — one row per file. The front end reads it that way and
  must keep doing so. Series identity lives in series_register.json and gets copied onto
  matching rows as flat additive fields. Nothing is ever renumbered, re-titled or removed.

What it does NOT do:
  * it does not add new rows — build_catalog.py does that by reading Bunny storage
  * it does not publish anything — a row appears to members only when it is in the catalog
  * it does not set series_ep on a row whose file_name it cannot match

Order of operations when a new episode ships:
  1  bunny_put.py            upload + verify served size
  2  build_catalog.py --write  append the row (title comes from catalog_title_overrides.json)
  3  stamp_series.py --write    copy the series fields onto it
  4  build_catalog.py --bump    only if the front end should refresh
"""
import argparse, json, os, sys

PORTAL = r"D:\RealmOfChaos\Veblen_Portal"
CAT = os.path.join(PORTAL, "vault_catalog.json")
REG = os.path.join(PORTAL, "series_register.json")
FIELDS = ("series_id", "series_name", "series_ep", "series_status", "series_tier")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()

    if not os.path.exists(REG):
        sys.exit(f"no register: {REG}")
    reg = json.load(open(REG, encoding="utf-8"))
    cat = json.load(open(CAT, encoding="utf-8"))

    # file_name -> series fields, built from every series in the register
    want = {}
    for s in reg.get("series", []):
        for ep in s.get("episodes", []):
            want[ep["file_name"]] = {
                "series_id": s["series_id"],
                "series_name": s["name"],
                "series_ep": ep["ep"],
                "series_status": s["status"],
                "series_tier": s["tier"],
            }

    rows = [r for tier in ("core", "elite") for r in cat.get(tier, [])]
    by_name = {r.get("file_name"): r for r in rows}

    changed = 0
    print(f"register: {len(want)} episode(s) marked")
    for fn, fields in want.items():
        row = by_name.get(fn)
        if row is None:
            print(f"  ~ {fn:<24} not in catalog yet — build_catalog.py has not added it")
            continue
        diff = {k: v for k, v in fields.items() if row.get(k) != v}
        if not diff:
            print(f"  = {fn:<24} already stamped")
            continue
        print(f"  + {fn:<24} {', '.join(f'{k}={v}' for k, v in diff.items())}")
        if a.write:
            for k, v in fields.items():
                row[k] = v
        changed += 1

    # report anything in the catalog that claims a series but is not in the register
    stray = [r["file_name"] for r in rows if r.get("series_id") and r["file_name"] not in want]
    if stray:
        print(f"  ! stamped in catalog but absent from register ({len(stray)}): {', '.join(stray[:5])}")

    if not a.write:
        print(f"\ndry run — {changed} row(s) would change. re-run with --write.")
        return
    if changed:
        json.dump(cat, open(CAT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        print(f"\nwrote {CAT} ({changed} row(s) stamped)")
    else:
        print("\nnothing to change")


if __name__ == "__main__":
    main()
