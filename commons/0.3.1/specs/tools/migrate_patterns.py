#!/usr/bin/env python3
"""migrate_patterns.py — moves pattern files of the earlier form into the form of LIBRARY-PATTERNS part 5
(R1, R2, R9, R10; Holger, commons.core#110 6627102753, X-1 to X-3). A help: it prints what it would do, and writes
only with `--apply`.

It changes the form, never the content: no text of a section is written, no orbit changes (R3), no status is
raised, and no id is made. What it does to each file:
- the front matter keeps the fields of part 5; every other field is dropped and named in the output, never silently;
- a hub `{hub_id, influence}` becomes its `hub_id`, and the influence is dropped (decided in the KISS pass); with
  `--principles FOLDER`, a hub that names its principle by title, `{principle: "<title>[: …| (…)]"}`, becomes the slug of
  the one principle of orbit 1 in FOLDER whose title equals the part before `:` or `(`, trimmed and in any case, and a
  hub that names none or more than one is dropped and named, never guessed (A-1, HB);
- a curated relation `{typeid, slug, weight, ...}` becomes its id, `requires`, `complementary` and `alternatives`
  kept, every other kind dropped and named (R9);
- a status R10 does not know is read as `candidate`, and `draft` and `observed` likewise (R10); none is raised;
- a section heading that begins with its section's name is cut to that name, `Cognitive Era Considerations` to
  `Cognitive Era` (part 5), and `### 1. Context` or `## Section 1: Context` is written `### Section 1: Context`;
- a known use written as a list item, `1.  **Place:** …` or `*   **Place:** …`, loses its list mark, so that it is the
  paragraph beginning with its place in bold that part 5 reads (R6); its words stay as they are;
- a file whose id is not `pat_` followed by letters, digits or underscores is not moved: an id is never made (R2).
What then passes `check_library.py --patterns` is for the human accountable to select (X-3); this help selects nothing.

Usage:  migrate_patterns.py SOURCE TARGET [--apply] [--principles FOLDER]
        SOURCE and TARGET are folders; each file keeps its path below them, `<orbit folder>/<slug>.md`.
"""
import argparse
import os
import re
import sys

import yaml

sys.dont_write_bytecode = True
SECTIONS = ["Context", "Problem", "Solution", "Implementation", "Consequences", "Known Uses", "Cognitive Era", "Vitality"]
CURATED = ("requires", "complementary", "alternatives")
KEPT = ("id", "slug", "title", "summary", "aliases", "orbital_layer", "gravitational_hubs", "ontology", "lifecycle",
        "relationships", "value_model", "contributors", "sources", "license", "attribution")
ONTOLOGY = ("domain", "cross_domains", "search_hints")
LIFECYCLE = ("status", "version", "confidence")
STATUS = ("candidate", "stable", "archived")
ADDRESS = ("slug", "weight", "status", "reason")
HEADING = re.compile(r"^#{2,3}\s+(?:Section\s+(\d+):|(\d+)\.)\s*(.+?)\s*$")
ITEM = re.compile(r"^(?:[-*]|\d+\.)\s+(\*\*[^*]+\*\*)")


def split(text):
    """the front matter and the body of a pattern file, or (None, text)"""
    t = text.replace("\r\n", "\n")
    if not t.startswith("---\n"):
        return None, t
    end = t.find("\n---", 4)
    if end < 0:
        return None, t
    try:
        fm = yaml.safe_load(t[4:end])
    except yaml.YAMLError:
        return None, t
    return (fm if isinstance(fm, dict) else None), t[end + 4:].lstrip("\n")


def ref(x):
    """a curated relation's id, else its slug"""
    if isinstance(x, dict):
        return x.get("typeid") or x.get("id") or x.get("slug")
    return x


def principles_of(folder):
    """{title in lower case: [slug, ...]}: the principles of orbit 1 in a folder, by their title"""
    out = {}
    for p in sorted(os.listdir(folder)) if folder and os.path.isdir(folder) else []:
        if p.endswith(".md"):
            fm, _ = split(open(os.path.join(folder, p), encoding="utf-8", errors="replace").read())
            if fm and fm.get("orbital_layer") == 1 and fm.get("title") and fm.get("slug"):
                out.setdefault(str(fm["title"]).strip().lower(), []).append(fm["slug"])
    return out


def hub_slugs(hubs, principles, said):
    """the principles a pattern's hubs name by title, as their slugs, each once; a hub naming none or more than one is
    dropped and named in `said` (A-1, HB: exact, never fuzzy)"""
    out = []
    for h in hubs or []:
        title = h.get("principle") if isinstance(h, dict) else None
        key = re.split(r"[:(]", str(title or ""))[0].strip().lower()
        hit = principles.get(key) or []
        if len(hit) == 1:
            if hit[0] not in out:
                out.append(hit[0])
        else:
            hid = h.get("hub_id") if isinstance(h, dict) else h
            said.append(f"dropped the hub `{hid}` (`{title}`): it names " + ("no principle of orbit 1" if not hit else f"{len(hit)} principles"))
    return out


def front(fm, said, principles=None):
    """the front matter in the form of part 5, and what changed said in `said`; with `principles`, a hub by the
    principle its title names"""
    out = {}
    for k in fm:
        if k not in KEPT:
            said.append(f"dropped `{k}`")
    for k in KEPT:
        if k in fm and fm[k] is not None:
            out[k] = fm[k]
    hubs = out.get("gravitational_hubs")
    if principles is not None and isinstance(hubs, list) and any(isinstance(h, dict) and h.get("principle") for h in hubs):
        out["gravitational_hubs"] = hub_slugs(hubs, principles, said)
        said.append("hubs by the principle their title names")
    elif isinstance(hubs, list) and any(isinstance(h, dict) for h in hubs):
        out["gravitational_hubs"] = [h.get("hub_id") if isinstance(h, dict) else h for h in hubs]
        said.append("hubs by id, their influence dropped")
    on = out.get("ontology")
    if isinstance(on, dict):
        for k in [k for k in on if k not in ONTOLOGY]:
            said.append(f"dropped `ontology.{k}`")
        out["ontology"] = {k: on[k] for k in ONTOLOGY if k in on}
        hints = out["ontology"].get("search_hints")
        if isinstance(hints, dict):
            for k in [k for k in hints if k != "primary_tension"]:
                said.append(f"dropped `ontology.search_hints.{k}`")
            out["ontology"]["search_hints"] = {k: hints[k] for k in ("primary_tension",) if k in hints}
    lc = out.get("lifecycle")
    if isinstance(lc, dict):
        for k in [k for k in lc if k not in LIFECYCLE]:
            said.append(f"dropped `lifecycle.{k}`")
        out["lifecycle"] = {k: lc[k] for k in LIFECYCLE if k in lc}
        st = out["lifecycle"].get("status")
        if st not in STATUS:
            out["lifecycle"]["status"] = "candidate"
            said.append(f"status `{st}` read as `candidate` (R10)")
    rel = out.get("relationships")
    if isinstance(rel, dict):
        for k in [k for k in rel if k not in CURATED]:
            said.append(f"dropped the relation kind `{k}`")
        kept = {k: [ref(x) for x in rel.get(k) or [] if ref(x)] for k in CURATED if rel.get(k)}
        if any(isinstance(x, dict) for k in CURATED for x in rel.get(k) or []):
            said.append("curated relations by id, their weights dropped")
        if kept:
            out["relationships"] = kept
        else:
            out.pop("relationships")
    vm = out.get("value_model")
    if isinstance(vm, dict):
        for k in [k for k in vm if k not in ("vsd", "vsf", "unaddressed")]:
            said.append(f"dropped `value_model.{k}`")
        keep = {}
        for k in ("vsd", "vsf"):
            if isinstance(vm.get(k), list):
                keep[k] = [{f: a[f] for f in ADDRESS if f in a} for a in vm[k] if isinstance(a, dict) and a.get("slug")]
                if any(set(a) - set(ADDRESS) for a in vm[k] if isinstance(a, dict)):
                    said.append(f"`value_model.{k}`: each address keeps its slug, weight, status and reason")
        if "unaddressed" in vm:
            keep["unaddressed"] = vm["unaddressed"]
        out["value_model"] = keep
    return out


def body(text, said):
    """the body with each section heading in part 5's form, and the known uses as paragraphs"""
    lines, cur, items = [], None, 0
    for line in text.split("\n"):
        m = HEADING.match(line)
        n = int(m[1] or m[2]) if m else 0
        if m and 1 <= n <= len(SECTIONS) and m[3].startswith(SECTIONS[n - 1]):
            cur = SECTIONS[n - 1]
            if m[3] != cur:
                said.append(f"heading `{m[3]}` cut to `{cur}`")
            if m[2] or not line.startswith("### "):
                said.append(f"heading `{line.strip()}` written `### Section {n}: {cur}`")
            line = f"### Section {n}: {cur}"
        elif line.startswith("#"):
            cur = None
        elif cur == "Known Uses" and ITEM.match(line):
            line = line[ITEM.match(line).start(1):]
            items += 1
            if lines and lines[-1].strip():   # a paragraph of its own
                lines.append("")
        lines.append(line)
    if items:
        said.append(f"{items} known use(s) written as paragraphs, not list items")
    return "\n".join(lines)


def migrate(text, principles=None):
    """(the file in the form of part 5, or None, and what changed)"""
    said = []
    fm, rest = split(text)
    if fm is None:
        return None, ["no front matter: not moved"]
    if not re.fullmatch(r"pat_[a-z0-9_]+", str(fm.get("id") or "")):
        return None, [f"the id `{fm.get('id')}` is not `pat_…`, and an id is never made (R2): not moved"]
    out = front(fm, said, principles)
    head = yaml.safe_dump(out, sort_keys=False, allow_unicode=True, width=120)
    return f"---\n{head}---\n\n{body(rest, said)}", said


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("target")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--principles", metavar="FOLDER", help="the principles of orbit 1 a hub's title is matched against (HB)")
    a = ap.parse_args()
    principles = principles_of(a.principles) if a.principles else None
    moved = skipped = 0
    for root, dirs, files in os.walk(a.source):
        dirs[:] = sorted(d for d in dirs if not d.startswith("."))
        for f in sorted(files):
            if not f.endswith(".md") or f in ("README.md", "LICENSE.md"):
                continue
            p = os.path.join(root, f)
            rp = os.path.relpath(p, a.source).replace(os.sep, "/")
            new, said = migrate(open(p, encoding="utf-8", errors="replace").read(), principles)
            print(f"{'move' if new else 'skip'}: {rp}" + (f": {'; '.join(said)}" if said else ""))
            if new is None:
                skipped += 1
                continue
            moved += 1
            if a.apply:
                t = os.path.join(a.target, rp)
                os.makedirs(os.path.dirname(t), exist_ok=True)
                open(t, "w", encoding="utf-8", newline="\n").write(new)
    print(f"# {moved} moved, {skipped} not moved" + ("" if a.apply else "; run with --apply to write them"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
