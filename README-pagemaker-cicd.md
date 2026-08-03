# PageMaker headless build: a frictionless CLI alternative to the GUI

This documents how the site can be rebuilt from the command line, without
opening PageMaker's Tkinter GUI. It replaces an earlier attempt at fully
automated GitHub Actions CI/CD, which turned out to add more complexity than
it saved for a single-maintainer site with an already-fast GUI workflow —
see "Why this isn't GitHub Actions" at the bottom.

## The layout

| Location | Contents |
|---|---|
| **PageMaker repo** | `main.pyw` (the GUI, unchanged), `pagemaker_core.py`, `build_site.py`, `html_reformat.py` — the engine, headless-safe and callable from the CLI — plus a `configs/` subfolder holding saved PageMaker JSON configs (e.g. `full-site.json`). |
| **Site repo** (`mikeverwer.github.io`, at `D:\Projects\Code\Website\mikeverwer.github.io`) | All site content/assets, and the template pages (e.g. `page.html`, `teaching.html`) that `--template` points at. |
| **`D:\Scripts`** (on PATH) | `build-site.ps1` — the build trigger. Lives here rather than in either repo, so it's runnable from anywhere. |

`build_site.py` imports `pagemaker_core`, which imports `html_reformat` —
plain module imports, no path in the `import` statement. Python adds the
*invoked script's own directory* to the module search path automatically,
so keeping all three `.py` files together in the PageMaker repo is what
makes those imports resolve correctly even though `build-site.ps1` calls
`build_site.py` from yet another directory entirely.

## Running a build

From anywhere, since `D:\Scripts` is on PATH:

```powershell
build-site.ps1
build-site.ps1 -config full-site.json -template page.html   # defaults shown
build-site.ps1 -template teaching.html                       # only override what differs
```

`-config` and `-template` are filenames only, not paths — the script
resolves them itself: `-config` against the PageMaker repo's `configs/`
folder, `-template` against the site root. It checks all three resolved
paths (the build script itself, the config, the template) up front and
errors out clearly if any is missing, rather than failing partway through.

One-time setup before the first run:
1. `pip install beautifulsoup4`
2. Open `build-site.ps1` and set `$PageMakerRepo` at the top to your local
   PageMaker repo path (it's a placeholder right now).

It rebuilds every page and regenerates `sitemap.xml`/`robots.txt` in place —
review the changes, then commit and push yourself. Nothing here touches git
automatically.

## How PageMaker actually builds pages

There's no separate "build output" folder — `PersonalSitePage` writes each
page directly into the site tree using one formula:

```
output_file_path = f"{root}{path_to_page}{output_filename}.html"
```

- `root` = `project_data.root` in the config — for this project, the entire
  site repo, not a staging subfolder.
- `path_to_page` = a row's `"path -insert"`, cleaned to always start/end
  with `/` (an empty string becomes just `/`).
- `output_filename` = a row's `"html filename -insert"`.

Examples traced from the real config against the repo tree:

| `path -insert` | `html filename -insert` | Resulting file |
|---|---|---|
| `/apps/` | `coin_flip` | `apps/coin_flip.html` |
| `""` (→ `/`) | `index` | `index.html` |
| `/projects/ad_posting_db/` | `ad_posting_procedures` | `projects/ad_posting_db/ad_posting_procedures.html` |

**Because `mikeverwer.github.io` is a user-page repo, the file tree *is* the
URL tree** — GitHub serves the repo root as `https://mikeverwer.github.io/`
directly, with no translation step.

One more dependency worth knowing: `change_article()` doesn't embed markdown
content at build time — it writes a `src="/assets/docs/..."`-style attribute
into the HTML, and something client-side fetches that `.md` file in the
browser. The deployed site needs `assets/docs/*.md` alongside the generated
HTML, not just the `.html` files themselves.

## The two footer dates, and why nothing automatic tracks them

Every page has `#last-modified` (footer, bottom right) — meant to reflect
when PageMaker last *structurally* rebuilt the page. Most pages also have
`#article-date` — when that page's own `.md` content last changed.

`#article-date` is authoritative and manual: it comes straight from the
`md_filename` config field (an optional `"<name>, <date>"` pair you set
yourself when you edit an article), untouched by the build process. This
was never a problem.

`#last-modified` is `datetime.date.today()`, stamped fresh every time
`PersonalSitePage` runs — meaning every page gets today's date on every
full rebuild, structural or not. This is correct precisely *because* you're
the one deciding when to run a full rebuild, the same way opening PageMaker's
GUI and clicking build always has been. It only becomes a problem if
something automated triggers a full rebuild on every content change without
your judgment in the loop — which is exactly what the GitHub Actions
version did, and exactly why it doesn't anymore.

## Fixes made to `PersonalSitePage` for headless compatibility

- **`ctypes.windll.shell32...` (main.pyw, module level):** Windows-only API
  called at import time — would crash on import outside Windows. Not an
  issue here since `pagemaker_core.py` never imports `main.pyw`, only the
  extracted `PersonalSitePage` class.
- **`PersonalSitePage.log()`:** originally assumed `self.logging_text` was a
  live Tkinter `Text` widget and was called on every build step, not just
  errors — passing `logger=None` crashed immediately. Patched to skip the
  widget calls when `logger` is `None`, while still printing either way and
  still working identically from the GUI. This is the one permanent,
  intentional difference from the class body in `main.pyw` — worth
  reapplying there too if you ever want a single canonical copy (see below).
- **Hardcoded path separators:** the original `make_sitemap` used a literal
  backslash (`f"{root_path}\\sitemap.xml"`) while `robots.txt` used a forward
  slash. `build_site.py`'s `make_sitemap()`/`write_robots()` use
  `pathlib.Path` instead, which works the same on Windows and Linux.

## `pagemaker_core.py` is still a separate copy from `main.pyw`

`PersonalSitePage` currently exists twice: inline inside `main.pyw`, and as
this extracted copy (identical except the `log()` fix above). Now that both
live in the same repo, keeping them in sync is at least a simple copy/paste
when the class changes, rather than a cross-repo one. If it ever becomes
worth the effort, `main.pyw` could import `PersonalSitePage` from
`pagemaker_core.py` instead of defining it inline, making this file the one
canonical source both the GUI and the CLI actually use — but that's a
separate, optional refactor, not something this setup requires.

## Why this isn't GitHub Actions

An earlier version of this ran the build automatically on every push via a
GitHub Actions workflow. It worked, but the actual friction it removed was
small — PageMaker's GUI already makes a full rebuild a few clicks — while
what it added kept growing: a headless port, a deploy pipeline, an artifact
staging/exclude step, and eventually a real design conflict where an
automatic full-rebuild-on-every-push made `#last-modified` bump on pages
that hadn't structurally changed, which needed git-history heuristics to
even partially work around.

Moving the trigger back to a deliberate, manual `.\build-site.ps1` run
removes that conflict entirely, for free — you already know whether a
change is structural or content-only when you decide to run it, which is
exactly the judgment call that was hard to reconstruct automatically from a
git diff after the fact.
