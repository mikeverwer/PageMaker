# Feature Ideas

- display image/text on hover over markdown text.
- convert to more non-static site that changes the variables with javascript


## Potential Changes

- The "everything rebuilds" concern is more theoretical than practical. With ~12 pages, full regeneration is fast. The real cost is the manual last-modified-date field in the UI — which is the thing actually creating friction. A modest improvement: have the tool stat the source markdown file's mtime and offer that as a default for the date field, with manual override. That way the date is correct by construction unless you explicitly want to lie about it (e.g., to suppress a "modified" date for trivial typo fixes). Implementation-wise this is a `os.path.getmtime` call when the row's MD filename changes, populating the date input automatically.

- One actual bug worth flagging: mutable default arguments. `links: list[str] = None` is fine because you're using None as the sentinel. But if you ever change those defaults to `links: list[str] = []` (a tempting "improvement"), every PersonalSitePage instance would share the same list object across calls. Worth keeping a comment explaining why None is intentional, since this is the kind of thing a future-you might "clean up" without realizing.

- The exception flow in `__init__`. You catch `FileNotFoundError` and log without re-raising, but catch generic `Exception` and re-raise. That means a missing template file silently produces a half-constructed object that subsequent code might try to use, while any other error propagates. Probably you want both to re-raise (or both to fail-and-skip via a class-level "valid" flag). The current asymmetry could lead to confusing downstream behavior on a missing template.

- On change_meta(index, follow, ...) taking integer flags. Those look like booleans-as-ints from the GUI checkbox state. If they're literal 0/1, that's fine; if they're using truthiness elsewhere, type-hinting them as bool would document intent. Minor.

- On the "remove row" feature. Worth pairing with row reordering (drag-handles or up/down buttons), since once you have remove, "remove and re-add at end" is the workaround for ordering and that's awkward. If you're already in there adding remove, ordering is probably one extra method.

- A larger architectural question, since you mentioned you might revisit the structure: have you considered separating the config from the generation? Right now your GUI tool is doing both — config editing and HTML production. If the config were a JSON/YAML file the GUI just reads and writes, then generation could happen from the CLI too. That'd let you wire up a file watcher (watchdog library) that regenerates on markdown changes without opening the GUI, while keeping the GUI as the canonical way to edit structure. The split is roughly: GUI = "what pages exist and how are they configured", CLI/watcher = "build the HTML from the current config". This is the model Hugo and Jekyll use, but with a custom GUI front-end you'd retain the visibility-into-the-whole-site advantage that off-the-shelf tools don't have.