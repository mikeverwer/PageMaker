#!/usr/bin/env python3
"""
Migrate old PageMaker config JSON files to the new format.

Changes applied:
  - Top-level "rows" → "num_rows"
  - Top-level "input_data" → "pages"
  - In each page: "link labels -insert" + "links -insert" (paired CSV strings)
    → "links" (list of {"label": ..., "url": ...[, "target": ...]} dicts)

The "target=_blank" suffix occasionally found in old link URLs is split out
into a separate "target" key on the link dict, when present.

Usage:
    python migrate_config.py path/to/config.json [more.json ...]

Each input file is migrated to a sibling file with `.migrated` inserted
before the `.json` extension. Originals are never modified.
"""

import json
import sys
import glob
from pathlib import Path


def parse_link_target(raw_url):
    """
    Split an optional `target=...` suffix out of a URL string.

        "/foo.html target=_blank" → ("/foo.html", "_blank")
        "/foo.html"               → ("/foo.html", None)
    """
    parts = raw_url.strip().split(maxsplit=1)
    if len(parts) == 2 and parts[1].startswith("target="):
        return parts[0], parts[1].split("=", 1)[1]
    return raw_url.strip(), None


def migrate_links(labels_csv, urls_csv):
    """Convert paired comma-separated strings into a list of link dicts."""
    labels = [s.strip() for s in labels_csv.split(",") if s.strip()]
    urls   = [s.strip() for s in urls_csv.split(",")   if s.strip()]

    if not labels and not urls:
        return []

    if len(labels) != len(urls):
        print(
            f"  Warning: {len(urls)} URLs vs {len(labels)} labels; "
            f"pairing up to the shorter list.",
            file=sys.stderr,
        )

    links = []
    for label, raw_url in zip(labels, urls):
        url, target = parse_link_target(raw_url)
        link = {"label": label, "url": url}
        if target is not None:
            link["target"] = target
        links.append(link)
    return links


def migrate_page(old_page):
    """
    Rebuild a single page entry in the new format. Preserves the order of
    fields in the old format, inserts `links` immediately after `type -set`,
    and drops the legacy `link labels -insert` / `links -insert` fields.
    """
    new_links = migrate_links(
        old_page.get("link labels -insert", ""),
        old_page.get("links -insert", ""),
    )

    new_page = {}
    inserted_links = False
    for key, value in old_page.items():
        if key in ("link labels -insert", "links -insert"):
            continue
        new_page[key] = value
        if key == "type -set":
            new_page["links"] = new_links
            inserted_links = True

    # Fallback: if the page had no `type -set` (unexpected), append at the end
    if not inserted_links:
        new_page["links"] = new_links

    return new_page


def migrate_config(old):
    """Transform a full config dictionary from old format to new."""
    if "input_data" not in old or "rows" not in old:
        raise ValueError(
            "Doesn't look like an old-format config "
            "(missing 'rows' or 'input_data' at top level)."
        )

    return {
        "num_rows":     old["rows"],
        "pages":        [migrate_page(p) for p in old["input_data"]],
        "project_data": old.get("project_data", {}),
    }


def migrate_file(path):
    """Migrate one file; write to <stem>.migrated.json beside it."""
    with open(path, encoding="utf-8") as f:
        old = json.load(f)

    new = migrate_config(old)

    out_path = path.with_name(f"{path.stem}.migrated.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(new, f, indent=2)
        f.write("\n")
    return out_path


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip(), file=sys.stderr)
        sys.exit(1)

    paths = []
    for path_str in sys.argv[1:]:
        matches = glob.glob(path_str)
        if matches:
            paths.extend(matches)
        else:
            paths.append(path_str)

    failures = 0
    for path_str in paths:
        path = Path(path_str)
        if not path.is_file():
            print(f"Skipping {path}: not a file.", file=sys.stderr)
            failures += 1
            continue

        print(f"Migrating {path}...")
        try:
            out = migrate_file(path)
            print(f"  → {out}")
        except (ValueError, KeyError, json.JSONDecodeError) as e:
            print(f"  Failed: {type(e).__name__}: {e}", file=sys.stderr)
            failures += 1

    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()