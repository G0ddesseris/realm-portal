#!/usr/bin/env python3
"""Sequentially number and sanitize Bunny CDN feed files.

Numbers are birth order, not display order. Next Core = 138, next Elite = 080.
Catalog ids 135, 136, and 137 are already live (dashboard or Outbox filenames, not all local prefixes).
The portal sorts the episode index newest-first (highest id on top).
Never rename a file that is already on Bunny — that would break the live URL.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path

MEDIA_EXTS = {".mp4", ".mov", ".webm", ".mkv"}
PREFIX_RE = re.compile(r"^(\d{3,})_")
SAFE_RE = re.compile(r"[^A-Za-z0-9_-]+")
MULTI_UNDERSCORE_RE = re.compile(r"_+")

DEFAULT_DIRS = [
    Path(r"D:\RealmOfChaos\Veblen_Portal\Bunny Videos\Core"),
    Path(r"D:\RealmOfChaos\Veblen_Portal\Bunny Videos\Elite"),
]


def is_media(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in MEDIA_EXTS


def highest_prefix(files: list[Path]) -> int:
    highest = 0
    for path in files:
        match = PREFIX_RE.match(path.name)
        if match:
            highest = max(highest, int(match.group(1)))
    return highest


def catalog_floor(folder_name: str) -> int:
    catalog = Path(r"D:\RealmOfChaos\Veblen_Portal\vault_catalog.json")
    if not catalog.is_file():
        return 0
    key = "elite" if folder_name.lower() == "elite" else "core"
    try:
        rows = json.loads(catalog.read_text(encoding="utf-8")).get(key) or []
    except (OSError, json.JSONDecodeError):
        return 0
    highest = 0
    for row in rows:
        try:
            highest = max(highest, int(row.get("id") or 0))
        except (TypeError, ValueError):
            continue
    return highest


def sanitize_stem(stem: str) -> str:
    cleaned = stem.replace(" ", "_").replace("&", "and")
    cleaned = SAFE_RE.sub("_", cleaned)
    cleaned = MULTI_UNDERSCORE_RE.sub("_", cleaned).strip("_-")
    return cleaned or "clip"


def unique_target(folder: Path, filename: str, reserved: set[str]) -> str:
    path = folder / filename
    if filename.lower() not in reserved and not path.exists():
        reserved.add(filename.lower())
        return filename
    stem = Path(filename).stem
    suffix = Path(filename).suffix
    n = 2
    while True:
        candidate = f"{stem}_{n}{suffix}"
        if candidate.lower() not in reserved and not (folder / candidate).exists():
            reserved.add(candidate.lower())
            return candidate
        n += 1


def plan_folder(folder: Path) -> list[tuple[Path, Path]]:
    files = sorted((p for p in folder.iterdir() if is_media(p)), key=lambda p: p.name.lower())
    pending = [p for p in files if not PREFIX_RE.match(p.name)]
    pending.sort(key=lambda p: (p.stat().st_ctime, p.name.lower()))
    next_index = max(highest_prefix(files), catalog_floor(folder.name)) + 1
    reserved = {p.name.lower() for p in files}
    planned: list[tuple[Path, Path]] = []
    for source in pending:
        stem = sanitize_stem(PREFIX_RE.sub("", source.stem))
        filename = unique_target(
            folder, f"{next_index:03d}_{stem}{source.suffix.lower()}", reserved
        )
        planned.append((source, folder / filename))
        next_index += 1
    return planned


def apply_plan(planned: list[tuple[Path, Path]], dry_run: bool) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for source, dest in planned:
        rows.append((source.name, dest.name))
        if dry_run or source == dest:
            continue
        source.rename(dest)
    return rows


def write_log(rows: list[tuple[str, str, str]], log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    new_file = not log_path.exists()
    with log_path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        if new_file:
            writer.writerow(["folder", "from", "to", "utc"])
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        for folder, src, dest in rows:
            writer.writerow([folder, src, dest, stamp])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--log",
        default=r"D:\RealmOfChaos\Veblen_Portal\Bunny Videos\rename_log.csv",
    )
    args = parser.parse_args()

    all_rows: list[tuple[str, str, str]] = []
    for folder in DEFAULT_DIRS:
        if not folder.is_dir():
            print(f"SKIP missing folder: {folder}")
            continue
        planned = plan_folder(folder)
        print(f"\n[{folder.name}] {len(planned)} file(s) to index")
        applied = apply_plan(planned, dry_run=args.dry_run)
        for src, dest in applied:
            print(f"  {src} -> {dest}")
            all_rows.append((folder.name, src, dest))

    if all_rows and not args.dry_run:
        write_log(all_rows, Path(args.log))
        print(f"\nWrote {len(all_rows)} rename(s) to {args.log}")
    elif args.dry_run:
        print("\nDry run only. No files renamed.")
    else:
        print("\nNothing to index.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
