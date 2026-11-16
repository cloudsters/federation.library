#!/usr/bin/env python3
"""check_library.py — a library holds releases that can be relied on (library.md), and its patterns are well formed
(library-patterns.md). Read-only.

Reports each finding as fail (a MUST), should (a SHOULD) or gap (missing or unverifiable, not wrong), and exits with
1 only on a fail. The check ids are those of the two specifications, part 6, and unique across them:

  library           layout  release  immutable  index  private  licence  where-used
  library-patterns  form  anchor  ip  relations  lifecycle  extract

One code checks a release copy wherever it lies (`check_copy`): in its library, alone with --release, and at install,
where catalogue.py --core calls it. It reads the copy alone and never the private maker: its record, its parts
and their digests, its licence and its text, its private data, and its profile's mandatory content, the offer's checks
of EXTENSION or the specifications of Commons Essentials for an extension, the checks of library-patterns for an
extract. Whether the copy is the release its pin names is read against the record digest the pin gives (--expect);
whether a record was generated from its source's event, and by whom it was authorised, is not verified by any code yet.

Whether a released version stayed as it was first released, and whether one has left the library, is read from git;
outside git, a gap. The names a release is checked against come from --names, a file kept outside git; without it,
that part of `private` and `form` is a gap. Third-party codes and trademarks come from --terms. A list finds
the names on it; it proves no text anonymous. With --core, the commons reads the library as it does: the lines of
its bill that a withholding touches, each a `should` for the commons to decide on, and nothing written to the library.

Usage:  check_library.py LIBRARY [--names FILE] [--terms FILE] [--today YYYY-MM-DD]
        check_library.py --release FOLDER [--expect sha256:...] [--names FILE] [--terms FILE]
        check_library.py --patterns FOLDER [--names FILE] [--terms FILE]
        check_library.py LIBRARY --core CORE
"""
import argparse
import datetime
import glob
import hashlib
import json
import os
import re
import subprocess
import sys

import jsonschema
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA = json.load(open(os.path.join(HERE, "..", "schemas", "library.schema.json"), encoding="utf-8"))
PATTERNS = json.load(open(os.path.join(HERE, "..", "schemas", "library-patterns.schema.json"), encoding="utf-8"))
sys.dont_write_bytecode = True   # the tools never write into the install they lie in (SPECIFICATION R29; `extension` R12)
sys.path.insert(0, HERE)
import catalogue  # noqa: E402
import rejected as rejected_words  # noqa: E402
import layout  # noqa: E402
import check_model  # noqa: E402
from check_core import PHONE, Report  # noqa: E402
from catalogue import source_terms, term_rx, unbound  # noqa: E402

SPECS = {"library": ["layout", "release", "model", "immutable", "index", "private", "licence", "where-used"],
         "library-patterns": ["form", "anchor", "ip", "relations", "lifecycle", "extract"]}
ROOT = {"library.yml", "index.yml", "patterns", "README.md", "CONTRIBUTING.md",
        "LICENSE", ".github", ".git", ".gitignore", ".gitattributes"}
SEMVER = re.compile(SCHEMA["$defs"]["semver"]["pattern"])
CALVER = re.compile(SCHEMA["$defs"]["extract"]["properties"]["version"]["pattern"])
MODEL_PARTS = {"registry", "loops", "views"} | set(layout.record_folders())   # a model's records, either layout
INSTALLED = {"model": "model", "extension": "model", "extract": "patterns"}   # the one part a copy holds (R3); `extension`, the earlier value of `model`
EARLIER_PART = {"model": "essentials"}                           # the earlier name of a model's part (LIBRARY part 5)
NEVER = ("knowledge", "workshop", "_authoring", "overlays")       # never in a release copy (EXTENSION R12, R29, R31)
ESSENTIALS = layout.ESSENTIALS[0]                                # the Commons model's release, `commons-essentials` its earlier id (D4-3)
MAKER = {"carry-over"}   # read against the maker's estate at its own gate; a copy holds no superseded text
TESTS = "tools/tests/"   # the checks' own tests stay with the maker: their fixtures carry contact data by design
SECTIONS = ["Context", "Problem", "Solution", "Implementation", "Consequences", "Cognitive Era", "Vitality"]
EARLIER = "Known Uses"   # the earlier form's sixth section, read as written and never required (library-patterns R5, R6)
PROVENANCE = ("contributors", "sources", "license", "attribution")   # the only fields that name anyone (library R10)
EMAIL = re.compile(r"(?<![\w.+/-])[\w.+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}(?![\w-])")   # never `<id>@<version>`
PLACEHOLDER = re.compile(r"\[TODO\]|TODO:|INSERT HERE|\[\.\.\.\]|lorem ipsum|^\s*(TODO|TBD|FIXME)\.?\s*$", re.I | re.M)
# QA-1 (Holger, commons.core#110 6886059574): what an independent review found and no gate failed
PIPELINE = re.compile(r"derived from GraphRAG analysis", re.I)                 # a note of the tool that made it
MOJIBAKE = re.compile("\u00c3[\u0080-\u00bf\u00a2]|\u00e2\u20ac|\u00ef\u00bf\u00bd|\ufffd")   # UTF-8 read as a single-byte code page
OWN_SOURCE = re.compile(r"founder-led practice|a founder's essay|chat history", re.I)   # our own practice's papers (E3-2i')
SECOND_PERSON = re.compile(r"^\s*(You are|You're|You have)\b")                  # a persona text, not the pattern form
CREDENTIAL = re.compile(r"(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----|xox[bp]-[A-Za-z0-9-]{10,})")
CURATED = ("requires", "complementary", "alternatives")
ACYCLIC = ("requires",)   # a dependency in a circle explains nothing; complementary and alternatives may be mutual
UNBUILT = ("that each record was generated from its source's `release` event, and that this event was authorised, is "
           "unverified: the release tool is not built, and a well-formed `event` with `gate.result: pass` is the "
           "maker's statement, not a proof (R3)")


def defs(name):
    if name == "pattern":
        return PATTERNS
    if name in PATTERNS["$defs"]:
        return {**PATTERNS["$defs"][name], "$defs": PATTERNS["$defs"]}
    return {**SCHEMA["$defs"][name], "$defs": SCHEMA["$defs"]}


def validate(r, check, sch, doc, where):
    for e in sorted(jsonschema.Draft202012Validator(sch).iter_errors(doc), key=lambda e: list(e.path)):
        r.fail(check, f"{where}: {'/'.join(str(p) for p in e.path) or 'root'}: {e.message}")


def yml(p):
    try:
        return yaml.safe_load(open(p, encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return None


def sha(b):
    return hashlib.sha256(b.replace(b"\r\n", b"\n")).hexdigest()


def day(v):
    """an ISO date `YYYY-MM-DD`, or None where it is none"""
    try:
        return datetime.date.fromisoformat(str(v)) if re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(v)) else None
    except ValueError:
        return None


def git(d, *args):
    try:
        out = subprocess.run(["git", "-C", d, *args], capture_output=True)
        return out.stdout if out.returncode == 0 else None
    except OSError:
        return None


def files(d):
    return sorted(os.path.join(top, f) for top, _, fs in os.walk(d) for f in fs)


def rel(p, base):
    return os.path.relpath(p, base).replace(os.sep, "/")


def contained(p, d):
    """whether a path, every link and junction on it resolved, lies inside a copy (R2, R9)"""
    root, real = (os.path.normcase(os.path.realpath(x)) for x in (d, p))
    return real == root or real.startswith(root.rstrip(os.sep) + os.sep)


def inside(d, path):
    """whether a path a record or an index names is one inside the copy: relative, never climbing out, and contained
    once resolved (R2, R9)"""
    s = str(path or "")
    return bool(s) and not os.path.isabs(s) and not re.match(r"^[A-Za-z]:", s) \
        and ".." not in re.split(r"[\\/]", s) and contained(os.path.join(d, s), d)


def wordlist(path):
    if not path:
        return None
    return [w.strip() for w in open(path, encoding="utf-8") if w.strip() and not w.startswith("#")]


FAST = getattr(yaml, "CSafeLoader", yaml.SafeLoader)


def front(path):
    t = open(path, encoding="utf-8", errors="replace").read()
    if not t.startswith("---"):
        return None, t
    parts = t.split("---", 2)
    try:
        fm = yaml.load(parts[1], Loader=FAST)       # the safe loader, in C where PyYAML has it: the same documents, faster
    except yaml.YAMLError:
        return None, t
    return (fm if isinstance(fm, dict) else None), (parts[2] if len(parts) > 2 else "")


def sections(body):
    """the body's sections by name: `### Section <n>: <name>`"""
    out, cur = {}, None
    for line in body.splitlines():
        m = re.match(r"^###\s+Section\s+(\d+):\s*(.+?)\s*$", line)
        if m:
            cur = m[2]
            out[cur] = []
        elif cur is not None:
            out[cur].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}


def cycles(edges):
    """the cycles of a directed graph {node: [node]}, each once, from its smallest node"""
    found, state = set(), {}

    def walk(n, path):
        state[n] = 1
        path.append(n)
        for m in edges.get(n, []):
            if state.get(m) == 1:
                c = path[path.index(m):]
                i = c.index(min(c))
                found.add(tuple(c[i:] + c[:i]))
            elif m in edges and state.get(m) is None:
                walk(m, path)
        path.pop()
        state[n] = 2

    for n in sorted(edges):
        if n not in state:
            walk(n, [])
    return sorted(found)


def complete(text):
    """whether a section ends where something ends: a sentence, a closed code fence, a URL or a closed emphasis
    (R4; Holger, commons.core#110 6867369350, CK); a section cut off mid-sentence does not"""
    last = (text.strip().splitlines() or ["."])[-1].rstrip("-").strip() or "."
    if last.startswith("```") and text.count("```") % 2 == 0:      # a diagram or code block, closed
        return True
    if re.search(r"https?://\S+$", last):                          # a reference that ends in its address
        return True
    if re.search(r"\S(\*\*|__|\*|_)+$", last):                     # a closed emphasis, `**_` and `_**` among them
        return True
    return bool(re.search(r"[.!?\"')*:”’]\s*$", last))


def check_patterns(r, folder, base, names, terms, released=False):
    """the checks of library-patterns on every pattern file of a folder; returns {id: (front matter, path)}. QA-1's
    checks fail a stock and an extract being cut; in a copy already released, immutable and retired by a newer
    extract, they are a `should` (`released`)"""
    qa = r.should if released else r.fail
    pats, slugs, live_slugs, bodies, unnamed, ents_once = {}, {}, {}, {}, 0, []
    forms = set()
    for p in files(folder):
        if not p.endswith(".md") or os.path.basename(p) in ("README.md", "LICENSE.md"):
            continue
        w = f"`{rel(p, base)}`"
        fm, body = front(p)
        if fm is None:
            r.fail("form", f"{w}: no front matter (R1)")
            continue
        for e in jsonschema.Draft202012Validator(defs("pattern")).iter_errors(fm):
            r.fail("form", f"{w}: {'/'.join(str(x) for x in e.path) or 'root'}: {e.message} (R1, R2; library R10)")
        pid = fm.get("id")
        if pid in pats:
            r.fail("form", f"{w}: the id `{pid}` is taken by another pattern (R2)")
        live = (fm.get("lifecycle") or {}).get("status") != "archived"   # an archived copy keeps its name as history
        if live and fm.get("slug") in live_slugs:
            qa("form", f"{w}: the slug `{fm.get('slug')}` is taken by `{live_slugs[fm.get('slug')]}` (R2)")
        key = re.sub(r"\s+", " ", body).strip()
        if live and key and key in bodies:
            qa("form", f"{w}: its text is that of `{bodies[key]}` (R2)")
        if live:
            live_slugs.setdefault(fm.get("slug"), rel(p, base))
            bodies.setdefault(key, rel(p, base))
        pats[pid] = (fm, p)
        slugs[fm.get("slug")] = pid
        raw = open(p, encoding="utf-8", errors="replace").read()
        if MOJIBAKE.search(raw):
            qa("form", f"{w}: it holds text decoded in the wrong code page, e.g. `{MOJIBAKE.search(raw).group(0)}` (R4)")
        if PIPELINE.search(body):
            qa("form", f"{w}: it carries a note of the tool that made it, `{PIPELINE.search(body).group(0)}`, which is no part of a pattern (R4)")
        summary = re.sub(r"\s+", " ", str(fm.get("summary") or "")).strip()
        quote = next((m[1].strip() for m in re.finditer(r"(?m)^> (?!\[!)(.*?)\s*$", body[:2000])), None)
        if summary and quote and quote != summary and summary.startswith(quote):
            qa("form", f"{w}: the summary quoted under its title is cut at {len(quote)} of {len(summary)} characters (R4)")
        for s in fm.get("sources") or []:
            if OWN_SOURCE.search(str(s)):
                qa("form", f"{w}: its sources name a paper of our own practice, `{str(s)[:60]}`, which no public extract carries (library R10; E3-2i')")
        if re.search(r"[a-z]\.\.\*\*", body):
            qa("form", f"{w}: a sentence ends in `..**` (R4)")
        forms.add(str((fm.get("lifecycle") or {}).get("form") or fm.get("form") or "1"))
        sec = sections(body)
        heads = re.findall(r"(?m)^(#{1,6})\s+Section\s+\d+:\s*(.+?)\s*$", body)
        for s in sorted({n for _, n in heads if [x for _, x in heads].count(n) > 1}):
            r.fail("form", f"{w}: the section `{s}` stands twice; a pattern holds each section once (R4)")
        for lvl, s in heads:
            if lvl != "###":
                r.fail("form", f"{w}: the section `{s}` is headed `{lvl} Section`, where every section is `### Section n:` (R4)")
        nums = [(int(n), s) for n, s in re.findall(r"(?m)^###\s+Section\s+(\d+):\s*(.+?)\s*$", body)]
        order = SECTIONS[:5] + [EARLIER] * any(s == EARLIER for _, s in nums) + SECTIONS[5:]   # the earlier form numbers 1 to 8
        want = [(order.index(s) + 1, s) for _, s in nums if s in order]
        if [x for x in nums if x[1] in order] != want:
            qa("form", f"{w}: its sections are numbered {[n for n, _ in nums]}, where the seven are numbered 1 to 7 (R4)")
        if SECOND_PERSON.match(sections(body).get("Context") or ""):
            qa("form", f"{w}: its Context opens in the second person, a persona text rather than the pattern form (R4; E3-2f)")
        for s in SECTIONS:
            text = sec.get(s)
            if text is None:
                r.fail("form", f"{w}: no section `{s}` (R4)")
            elif not text.strip("-* \n>"):
                r.fail("form", f"{w}: the section `{s}` is empty (R4)")
            elif PLACEHOLDER.search(text):
                r.fail("form", f"{w}: the section `{s}` holds a placeholder (R4)")
            elif not complete(text):
                r.fail("form", f"{w}: the section `{s}` ends mid-sentence (R4)")
        named = SECTIONS + [EARLIER] * (EARLIER in sec)
        if names is None:
            unnamed += 1                                  # said once for the folder, below
        else:
            for n in names:
                if any(term_rx(n).search(sec.get(s) or "") for s in named):
                    r.fail("form", f"{w}: its sections name `{n}`, which only its provenance fields may name (library R10)")
        prose = "\n".join(sec.get(s) or "" for s in named)
        for t in terms or []:
            if t and term_rx(t).search(prose):
                r.fail("ip", f"{w}: names `{t}` in its sections, which belongs only in its sources (R8)")
        ents = ents_once or ents_once.extend(rejected_words.entries()) or ents_once   # the glossary, read once
        for level, msg in rejected_words.findings("sections.md", prose, f"{w}: its sections", ents):
            if released and level == "should":            # a released copy is read-only: the hint is its maker's
                continue
            (r.should if released else getattr(r, level))("ip", msg.replace("(R14)", "(R8)"))
        st = (fm.get("lifecycle") or {}).get("status")
        heads = {k: v for k, v in fm.items() if k not in PROVENANCE}   # the front matter and file name, its sources exempt
        for level, msg in rejected_words.findings(os.path.splitext(p)[0] + ".yml", yaml.safe_dump(heads, allow_unicode=True),
                                                  f"{w}: its front matter", ents) if st != "archived" else ():   # history
            if released and level == "should":
                continue
            (r.should if released else getattr(r, level))("ip", msg.replace("(R14)", "(R8)").replace(".yml`", ".md`"))
        if st not in ("candidate", "stable", "archived", "draft", "observed"):
            r.fail("lifecycle", f"{w}: the status `{st}` is none of R10's (R10)")
        if "graph_garden" in fm or any(k not in CURATED for k in (fm.get("relationships") or {})):
            r.fail("relations", f"{w}: holds a relation outside the curated kinds, or a garden block (R9)")
    if len(forms) > 1:
        r.fail("form", f"`{rel(folder, base)}`: its patterns follow {len(forms)} versions of the form (R1)")
    principles = {fm.get("slug") for fm, _ in pats.values() if fm.get("orbital_layer") == 1} | \
                 {pid for pid, (fm, _) in pats.items() if fm.get("orbital_layer") == 1}
    edges = {k: {} for k in ACYCLIC}
    for pid, (fm, p) in pats.items():
        w = f"`{rel(p, base)}`"
        if fm.get("orbital_layer") in (2, 3, 4):
            hubs = [h.get("hub_id") if isinstance(h, dict) else h for h in fm.get("gravitational_hubs") or []]
            if not hubs:
                r.fail("anchor", f"{w}: orbit {fm['orbital_layer']}, and no principle it rests on (R4)")
            elif principles and not any(h in principles for h in hubs):
                r.fail("anchor", f"{w}: none of its hubs is a principle of orbit 1 here (R4)")
            elif not principles:
                r.gap("anchor", f"{w}: no principle of orbit 1 in this release to resolve its hubs (R4)")
        rels = fm.get("relationships") or {}
        for k in CURATED:
            for t in rels.get(k) or []:
                ref = t.get("id") or t.get("slug") if isinstance(t, dict) else t
                if ref not in pats and ref not in slugs:
                    r.gap("relations", f"{w}: its `{k}` names `{ref}`, which is not in this release (R9)")
                elif k in ACYCLIC:
                    edges[k].setdefault(pid, []).append(ref if ref in pats else slugs[ref])
    for k in ACYCLIC:
        for c in cycles(edges[k]):
            r.fail("relations", f"`{k}` runs in a circle: {' → '.join(c + (c[0],))} (R9)")
    if unnamed:
        r.gap("form", f"no list of names given (--names): the sections of {unnamed} pattern(s) are unchecked for names, "
                      f"which only the maker's gate, given its list, reads (library R10)")
    return pats


def check_extract(r, lid, pd, rec, w):
    """an extract's release: its index against its record and its patterns (library-patterns R17, R18)"""
    ix = os.path.join(pd, "index.jsonl")
    if not os.path.isfile(ix):
        r.fail("extract", f"{w}: no `index.jsonl` (R3)")
        return
    if rec.get("digest") != f"sha256:{sha(open(ix, 'rb').read())}":
        r.fail("extract", f"{w}: `index.jsonl` differs from the digest in its record (R3)")
    lines = [json.loads(x) for x in open(ix, encoding="utf-8") if x.strip()]
    head = lines[0] if lines else {}
    if head.get("kind") != "index":
        r.fail("extract", f"{w}: the index does not begin with its `kind: index` line (R3)")
    for k in ("graph_run", "extractor", "policy", "scope"):
        if head.get(k) != rec.get(k):
            r.fail("extract", f"{w}: the index gives the {k} `{head.get(k)}`, its record `{rec.get(k)}` (R3)")
    ids = {x.get("id") for x in lines[1:]}
    for x in lines[1:]:
        at = f"{w}, index line `{x.get('id')}`"
        for e in jsonschema.Draft202012Validator(defs("index_line")).iter_errors(x):
            r.fail("extract", f"{at}: {'/'.join(str(p) for p in e.path) or 'root'}: {e.message} (R3, R18)")
        if not str(x.get("id", "")).startswith(f"{lid}/"):
            r.fail("extract", f"{at}: not qualified by this library's id `{lid}` (R2)")
        if x.get("file") and not inside(pd, x["file"]):
            r.fail("extract", f"{at}: its file `{x.get('file')}` is no path inside the extract; the pin covers only the copy (R2, R3)")
            continue
        f = os.path.join(pd, str(x.get("file") or ""))
        fm, _ = front(f) if x.get("file") and os.path.isfile(f) else (None, "")
        if fm is None:
            r.fail("extract", f"{at}: its file `{x.get('file')}` is not in the extract (R3)")
            continue
        if f"{lid}/{fm.get('id')}" != x.get("id") or fm.get("orbital_layer") != x.get("orbit"):
            r.fail("extract", f"{at}: its file has another id or orbit (R3)")
        ratified = {f"vsf:{v.get('slug')}" for v in ((fm.get("value_model") or {}).get("vsf") or []) if isinstance(v, dict) and v.get("status") == "ratified"}
        for fam in (x.get("context") or {}).get("families") or []:
            if fam not in ratified:
                r.fail("extract", f"{at}: `{fam}` is no family the pattern is ratified for (R18; model R18)")
        for l in x.get("links") or []:
            if l.get("to") not in ids:
                r.fail("extract", f"{at}: the link to `{l.get('to')}` leads out of the extract (R3)")
    for p in files(pd):
        if p.endswith(".md") and rel(p, pd) not in {x.get("file") for x in lines[1:]}:
            r.fail("extract", f"{w}: `{rel(p, pd)}` is in the extract, but not in its index (R3)")
    n = rec.get("count")   # the cut counted against the whole stock (R17; the Office, GO-3, on the count of v2026.11.3)
    if not isinstance(n, dict):
        r.gap("extract", f"{w}: its record gives no `count` of the stock and the cut; a record states it since Commons 0.3.0 (R17)")
        return
    by = n.get("by_folder") or {}
    sums = lambda x: x.get("archived", 0) + x.get("left_out", 0) + x.get("cut", 0)
    folders = {}
    for x in lines[1:]:
        folders[str(x.get("file", "")).split("/", 1)[0]] = folders.get(str(x.get("file", "")).split("/", 1)[0], 0) + 1
    if n.get("cut") != len(lines) - 1:
        r.fail("extract", f"{w}: its record counts {n.get('cut')} patterns cut, its index holds {len(lines) - 1} (R17)")
    if n.get("stock") != sums(n):
        r.fail("extract", f"{w}: its record counts a stock of {n.get('stock')}, not archived + left out + cut = {sums(n)} (R17)")
    for k in ("stock", "archived", "left_out", "cut"):
        if n.get(k) != sum(x.get(k, 0) for x in by.values()):
            r.fail("extract", f"{w}: its record's `{k}` is not the sum of its folders' (R17)")
    for f, x in by.items():
        if x.get("stock") != sums(x) or x.get("cut") != folders.get(f, 0):
            r.fail("extract", f"{w}: its record's count of `{f}` does not add up, or is not the {folders.get(f, 0)} patterns its index holds there (R17)")


def recs_of(d):
    """the record ids an extension release offers, `<kind>:<slug>`"""
    out = set()
    for p in glob.glob(os.path.join(layout.records(d), "*", "*.y*ml")):
        x = yml(p) or {}
        if isinstance(x, dict) and x.get("kind") and x.get("slug"):
            out.add(f"{x['kind']}:{x['slug']}")
    return out


def part_digest(d):
    """sha256 over every file of a copy but its record, path by path, whatever the line endings (R3)"""
    return digest_of((rel(p, d), lambda p=p: open(p, "rb").read()) for p in files(d))


def digest_of(held):
    """the part digest over `(path inside the copy, read)` pairs, wherever the copy is read from: its folder, or a
    revision of the CORE that installed it (R3; GRAPH and MCP read an installed extract only where it holds)"""
    h = hashlib.sha256()
    for rp, read in sorted(held, key=lambda x: x[0]):
        if rp != "release.yml":
            h.update(f"{rp}\0{sha(read())}\n".encode())
    return "sha256:" + h.hexdigest()


def offered(r, d, w, names, held=False):
    """a model's release, read from the copy alone: its form (`release`), and what may leave a CORE (`model`, R19): cut
    from an emulation, no word in the sense the glossary rejects, no term of a source outside its sources and bindings,
    only `global` sources bound (R10, R19)"""
    rec = yml(os.path.join(d, "release.yml")) or {}
    src, now = str(rec.get("source") or ""), rec.get("kind") == "model"
    if not src:                                  # a record of kind `model` names both; one before 0.4.0 neither (O-1)
        (r.fail if now else r.gap)("model", f"{w}: its record names no `source`" + (": a model is released only from an emulation (R19)" if now
                                   else ": cut before 0.4.0, from an offer, not from an emulation (R19)"))
    elif ":models/emulation/" not in src:
        r.fail("model", f"{w}: its `source` `{src}` is no emulation; a model is released only from one (R19)")
    if now and not rec.get("written_in"):
        r.fail("model", f"{w}: its record names no `written_in`, the Commons model it is written in (part 5)")
    mf = layout.model_file(d)
    off = yml(mf)
    if off is None:
        r.fail("release", f"{w}: no `model.yml`, nor its earlier `offer.yml` (LIBRARY R19)")
    else:
        catalogue.valid(r, "release", f"{w}/{os.path.basename(mf)}", off, None)
    attr = yml(os.path.join(d, "sources.yml"))
    if attr is None:
        r.fail("release", f"{w}: no attribution list `sources.yml` (EXTENSION R31)")
    srcs = {s.get("id"): s for s in (attr or {}).get("sources") or [] if isinstance(s, dict)}
    reg = layout.records(d)
    recs = catalogue.records(reg)
    if not any(k.startswith("value-stream:") and "/" not in k for k in recs):
        r.fail("release", f"{w}: offers no value stream in `registry/` (EXTENSION R4)")
    else:
        # a release the library holds is read against today's grammar as a should; a commons installing it, as a fail
        for o, c, t in check_model.check(check_model.load(reg), extension=True).items:
            if o == "fail":
                (r.should if held else r.fail)("release", f"{w}/registry: {c}: {t}")
    have = catalogue.loops(os.path.join(d, "loops"))
    for fam in sorted({rec.get("family") for k, (rec, _) in recs.items() if k.startswith("value-stream:") and "/" not in k} - {None}):
        if f"_family.{fam}" not in have:
            r.fail("release", f"{w}: offers streams of `{fam}` and no steering loop `loops/_family.{fam}.loop.yml` (EXTENSION R12)")
    for k, f, b in catalogue.binds_of(recs):
        if not isinstance(b, dict) or b.get("source") not in srcs:
            r.fail("release", f"{w}: `{k}` binds `{b}`, which the release does not attribute in `sources.yml` (R19)")
        elif catalogue.jurisdictional((srcs[b["source"]] or {}).get("jurisdiction")):
            r.fail("model", f"{w}: `{k}` binds `{b['source']}`, a source of one jurisdiction; a model binds only `global` sources (R19)")
    tl = sorted({x for s in srcs.values() for x in source_terms(s)}, key=len, reverse=True)
    for p in files(d):
        rp = rel(p, d)
        if rp.split("/")[0] not in MODEL_PARTS - {"views"} or not p.endswith((".yml", ".yaml", ".md")):
            continue
        body = unbound(p, open(p, encoding="utf-8", errors="replace").read(), set(srcs))
        for t in tl:
            if term_rx(t).search(body):
                r.fail("model", f"{w}/{rp} names `{t}`, which belongs only in the attribution list (R19)")
        for n in names or []:
            if term_rx(n).search(body):
                r.fail("private", f"{w}/{rp} names `{n}` outside the attribution list (R10)")
    rejected = catalogue.rejected_terms()
    for p in files(d):
        rp = rel(p, d)
        if rp.split("/")[0] in MODEL_PARTS or rp in ("model.yml", "offer.yml"):
            catalogue.rejected_in(r, "model", p, open(p, encoding="utf-8", errors="replace").read(), f"{w}/{rp}", rejected,
                                        r.should if held else None)


def specified(r, d, w):
    """the copy of Commons Essentials, profile `specifications`: the discipline's `specs/` and nothing else (EXTENSION
    R9)"""
    import check_spec  # noqa: E402
    for x in sorted(os.listdir(d)):
        if x not in ("release.yml", "LICENSES", "specs"):
            r.fail("release", f"{w}: `{x}` in a release of the profile `specifications`, which holds only `specs/` (EXTENSION R9)")
    if os.path.isdir(os.path.join(d, "specs", *TESTS.split("/"))):
        r.fail("release", f"{w}: `specs/{TESTS}` in a release; the checks' own tests stay with the maker (R10, part 6)")
    own = sorted(glob.glob(os.path.join(d, "specs", "*.md")))
    if not own:
        r.fail("release", f"{w}: no specification in `specs/` (EXTENSION R9)")
    for p in own:
        for o, c, t in check_spec.check(p, offline=True).items:
            if o == "fail" and c not in MAKER and not (c == "references" and t.startswith(f"`{TESTS}")):
                r.fail("release", f"{w}/{rel(p, d)} does not follow SPECIFICATION: {c}: {t}")


def check_copy(r, d, base, w, names=None, terms=None, expect=None, lid=None, held=False, installed=False):
    """one release copy, wherever it lies: in its library, alone, or installed (R3, R8, R9, R10, R11). Returns its
    record, or None where it has none. An `installed` copy, checked whole by install.py before it moved into place and
    read-only since, is checked against its digests: its record against the lock's, its files against the record's
    part digest, its licence; its content is not read again (R9)"""
    rp = os.path.join(d, "release.yml")
    rec = yml(rp)
    if rec is None:
        r.fail("release", f"{w}: no `release.yml` (R3)")
        return None
    if expect and f"sha256:{sha(open(rp, 'rb').read())}" != expect:
        r.fail("release", f"{w}: its record is not the one its pin names, `{expect}` (R9)")
    kind = rec.get("kind")
    if kind not in INSTALLED:
        r.fail("release", f"{w}: its record names the kind `{kind}`, neither `model` nor `extract` (R3)")
        return rec
    validate(r, "release", defs("release" if kind in ("model", "extension") else "extract"), rec, f"{w}, `release.yml`")
    for top, dirs, fs in os.walk(d):                 # containment (R2, R9): nothing of a copy leads outside it
        for n in list(dirs) + fs:
            p = os.path.join(top, n)
            if not contained(p, d):
                r.fail("release", f"`{rel(p, base)}` leads outside the copy, through a link or a junction; a release is a copy of its own (R2, R9)")
                if n in dirs:
                    dirs.remove(n)
    if lid and rec.get("library") != lid:
        r.fail("release", f"{w}: its record names the library `{rec.get('library')}`, not `{lid}` (R3)")
    if (rec.get("gate") or {}).get("result") != "pass":
        r.fail("release", f"{w}: its gate did not pass (R3, R8)")
    for x in rec.get("retires") or []:
        if isinstance(x, dict) and day(x.get("from")) is None:
            r.fail("release", f"{w}: retires `{x.get('id')}` from `{x.get('from')}`, which is no date YYYY-MM-DD (R4)")
    # parts (R3, R2): the copy holds its one public part, and its digest is that part's; `essentials` is the earlier
    # name of `model`, and an earlier `enhanced` part is history
    parts = rec.get("parts") if isinstance(rec.get("parts"), dict) else {}
    main = INSTALLED[kind]
    if main not in parts and EARLIER_PART.get(main) in parts:
        main = EARLIER_PART[main]
    part = parts.get(main) if isinstance(parts.get(main), dict) else {}
    if part.get("class") != "public":
        r.fail("release", f"{w}: its part `{main}` has the class `{part.get('class')}`; the installed part is `public` (R3; EXTENSION R12)")
    if part.get("digest") != part_digest(d):
        r.fail("release", f"{w}: its files are not those its record's `parts.{main}.digest` names (R3, R9)")
    for name, p in parts.items():
        if name == main:
            continue
        if isinstance(p, dict) and p.get("class") == "public":
            r.fail("release", f"{w}: its part `{name}` is `public` beside `{main}`; a release has one installed part (R3)")
        if os.path.exists(os.path.join(d, name)):
            r.fail("private", f"{w}: its served part `{name}/` lies in the copy; it is held only where it is served (R2)")
    for x in NEVER:
        if os.path.exists(os.path.join(d, x)):
            r.fail("private", f"{w}: holds `{x}/`, which no release carries (R12)")
    # licence (R11): the text of a licence by reference travels with the copy
    lic = str(rec.get("licence") or "")
    if not lic:
        r.fail("licence", f"{w}: names no licence (R11)")
    elif lic.startswith("LicenseRef-") and not (inside(d, f"LICENSES/{lic}.txt") and os.path.isfile(os.path.join(d, "LICENSES", f"{lic}.txt"))):
        r.fail("licence", f"{w}: names `{lic}`, whose text is not in its `LICENSES/` (R11)")
    if installed:                                     # the index still answers for its files (R3), read without the files' texts
        if kind == "extract":
            check_extract(r, rec.get("library"), d, rec, w)
        return rec
    # private (R10)
    for p in files(d):
        t = open(p, encoding="utf-8", errors="replace").read()
        if EMAIL.search(t) or PHONE.search(t) or CREDENTIAL.search(t):
            r.fail("private", f"`{rel(p, base)}` holds a contact datum or a credential (R10)")
    # the profile's mandatory content
    if kind in ("model", "extension"):
        profile = rec.get("profile") or ("specifications" if layout.release_id(rec) in layout.ESSENTIALS else "offer")   # retired with 0.4.0
        if profile == "specifications":
            if layout.release_id(rec) not in layout.ESSENTIALS:
                r.fail("release", f"{w}: the profile `specifications` is Commons Essentials' alone, not `{rec.get('extension')}`'s (EXTENSION R9)")
            specified(r, d, w)
        else:
            offered(r, d, w, names, held)
    else:
        check_patterns(r, d, base, names, terms, released=True)
        check_extract(r, rec.get("library"), d, rec, w)
    return rec


def check_release(folder, names=None, terms=None, expect=None):
    """one release copy where it lies, as a commons checks it at install (R9)"""
    r = Report()
    rec = check_copy(r, folder, folder, f"`{folder}`", names, terms, expect)
    if rec is not None and not expect:
        r.gap("release", "no record digest from a pin given (--expect): the copy agrees with itself, and whether it is the release its library holds is unverified (R9)")
    if names is None:
        r.gap("private", "no list of names given (--names); the release is unchecked for names (R10)")
    r.gap("release", UNBUILT)
    return r


def state_of(rid, version, records, today):
    """the state a version is in on a day, from the records; None where a retirement's date is no date"""
    if "-rc." in version:
        return "candidate"
    for rec in records:
        for x in rec.get("retires") or []:
            if isinstance(x, dict) and x.get("id") == f"{rid}@{version}":
                f = day(x.get("from"))
                return None if f is None else ("retired" if f <= today else "released")
    return "released"


def check(lib, names=None, terms=None, today=None):
    r = Report()
    today = today or datetime.date.today()
    cfg = yml(os.path.join(lib, "library.yml"))
    if cfg is None:
        r.fail("layout", "no `library.yml` (R1)")
        return r
    validate(r, "layout", SCHEMA, cfg, "`library.yml`")
    lid = cfg.get("id")
    withheld = {str(x.get("release")): x for x in cfg.get("withheld") or [] if isinstance(x, dict)}
    for x in withheld.values():
        if day(x.get("from")) is None:
            r.fail("layout", f"`library.yml` withholds `{x.get('release')}` from `{x.get('from')}`, which is no date YYYY-MM-DD (R4)")
    folders = []                                     # (id, kind, version, folder, variant)
    ident = re.compile(SCHEMA["$defs"]["id"]["pattern"])
    for x in sorted(os.listdir(lib)):
        p = os.path.join(lib, x)
        if x in ROOT:
            continue
        if not os.path.isdir(p) or not ident.match(x):
            r.fail("layout", f"`{x}` is no entry of a library's root (R1, R2)")
            continue
        for v in sorted(os.listdir(p)):
            q = os.path.join(p, v)
            if SEMVER.match(v) and os.path.isdir(q):
                folders.append((x, "extension", v, q, None))
            elif os.path.isdir(q) and ident.match(v) and any(SEMVER.match(u) for u in os.listdir(q)):
                for u in sorted(os.listdir(q)):          # a variant's releases (MODEL R30)
                    if not SEMVER.match(u) or not os.path.isdir(os.path.join(q, u)):
                        r.fail("layout", f"`{x}/{v}/{u}` is no release folder `<id>/<variant>/<version>/` (R2)")
                    else:
                        folders.append((x, "extension", u, os.path.join(q, u), v))
            else:
                r.fail("layout", f"`{x}/{v}` is no release folder `<id>/<version>/` or `<id>/<variant>/<version>/` (R2)")
    for v in sorted(os.listdir(os.path.join(lib, "patterns"))) if os.path.isdir(os.path.join(lib, "patterns")) else []:
        if not CALVER.match(v):
            r.fail("layout", f"`patterns/{v}` is no extract folder `patterns/<version>/` (R2)")
        else:
            folders.append(("patterns", "extract", v, os.path.join(lib, "patterns", v), None))
    releases = []                                    # (id, kind, version, folder, record), a variant's id `<model>/<variant>`
    for bare, kind, v, d, variant in folders:
        rid = f"{bare}/{variant}" if variant else bare
        w = f"`{rel(d, lib)}`"
        key = f"{rid}@{v}"
        if key in withheld:
            # withheld (R4): its record stays for the lineage, its files leave the library
            rec = yml(os.path.join(d, "release.yml"))
            if rec is None:
                r.fail("release", f"{w}: withheld, and its record `release.yml` is gone; the record stays (R4)")
                continue
            validate(r, "release", defs("release" if kind in ("model", "extension") else "extract"), rec, f"{w}, `release.yml`")
            if [p for p in files(d) if rel(p, d) != "release.yml"]:
                r.fail("release", f"{w}: withheld ({withheld[key].get('reason')}), and its files are still distributed (R4)")
        else:
            # a release the library holds is read against today's words as a `should`: it is never changed (R4) and
            # never deleted (R4), and a commons that installs it meets the same words as a fail (EXTENSION R12, R14)
            rec = check_copy(r, d, lib, w, names, terms, lid=lid, held=True)
            if rec is None:
                continue
        if rec.get("kind") != kind and not (kind == "extension" and layout.is_model(rec)):   # `model`, or its earlier `extension`
            r.fail("release", f"{w}: its record names the kind `{rec.get('kind')}` (R2, R3)")
        if kind in ("model", "extension") and layout.release_id(rec) != bare:
            r.fail("release", f"{w}: its record names the model `{layout.release_id(rec)}` (R3)")
        if kind in ("model", "extension") and rec.get("variant") != variant:
            r.fail("release", f"{w}: its record names the variant `{rec.get('variant')}`, its folder `{variant}` (R3; `model` R30)")
        if rec.get("version") != v:
            r.fail("release", f"{w}: its record names the version `{rec.get('version')}` (R3)")
        releases.append((rid, kind, v, d, rec))
    held = {(rid, v): d for rid, _, v, d, _ in releases}
    for key in sorted(withheld):
        rid, _, v = key.rpartition("@")
        if (rid, v) not in held:
            r.fail("release", f"`library.yml` withholds `{key}`, which this library does not hold (R4)")
    order = lambda v: tuple(int(x) for x in re.findall(r"\d+", v.split("-rc.")[0])) + ((0,) if "-rc." in v else (1,))
    for rid, kind, v, d, rec in releases:
        for x in rec.get("retires") or []:
            what = str(x.get("id") or "") if isinstance(x, dict) else ""
            if "@" in what:
                tid, _, tv = what.partition("@")
                if (tid, tv) not in held:
                    r.fail("release", f"`{rel(d, lib)}` retires `{what}`, which this library does not hold (R4)")
                elif tid == rid and order(tv) >= order(v):
                    r.fail("release", f"`{rel(d, lib)}` retires `{what}`, which is not an earlier version (R4)")
            else:
                earlier = [dd for (i, vv), dd in held.items() if i == rid and order(vv) < order(v)]
                if not any(what in recs_of(dd) for dd in earlier):
                    r.fail("release", f"`{rel(d, lib)}` retires `{what}`, which no earlier version of `{rid}` offered (R4)")
    if names is None:
        r.gap("private", "no list of names given (--names); the releases are unchecked for names (R10)")
    r.gap("release", UNBUILT)
    # index (R6): generated from the records and from what `library.yml` withholds
    records = [rec for *_, rec in releases]
    want = []
    for rid, kind, v, d, rec in releases:
        rp = os.path.join(d, "release.yml")
        bare, _, variant = rid.partition("/")
        e = {"id": bare, **({"variant": variant} if variant else {}), "kind": rec.get("kind") if layout.is_model(rec) else kind,
             "version": v, "record": rel(rp, lib), "digest": f"sha256:{sha(open(rp, 'rb').read())}", "state": state_of(rid, v, records, today)}
        if f"{rid}@{v}" in withheld:
            e["withheld"] = {"from": str(withheld[f"{rid}@{v}"].get("from")), "reason": withheld[f"{rid}@{v}"].get("reason")}
        want.append(e)
    ix = yml(os.path.join(lib, "index.yml"))
    if ix is None:
        r.fail("index", "no `index.yml` (R6)")
    else:
        validate(r, "index", defs("index"), ix, "`index.yml`")
        have = ix.get("releases") or []
        key = lambda e: (layout.ref_of(e), e.get("kind"), e.get("version"))
        hk, wk = {key(e): e for e in have}, {key(e): e for e in want}
        for k in sorted(set(wk) - set(hk), key=str):
            r.fail("index", f"the release `{k[0]}@{k[2]}` is not in `index.yml` (R6)")
        for k in sorted(set(hk) - set(wk), key=str):
            r.fail("index", f"`index.yml` lists `{k[0]}@{k[2]}`, which the library does not hold (R6)")
        for k in set(hk) & set(wk):
            for f in ("record", "digest", "state", "withheld"):
                if wk[k].get(f) is None and f == "state":
                    continue                     # no state where a retirement has no date; `release` fails it
                if hk[k].get(f) != wk[k].get(f):
                    r.fail("index", f"`index.yml` gives `{k[0]}@{k[2]}` the {f} `{hk[k].get(f)}`, its record `{wk[k].get(f)}` (R6)")
    # immutable (R4): in git, every released file is the one first released, and none has left but a withheld
    # release's files
    if git(lib, "rev-parse") is None:
        r.gap("immutable", "the library is not in git; that its releases never changed is unverified (R4)")
    else:
        pre = (git(lib, "rev-parse", "--show-prefix") or b"").decode().strip()
        for rid, kind, v, d, _ in releases:
            rp = rel(d, lib)
            first = (git(lib, "log", "--reverse", "--format=%H", "--", f"{rp}/release.yml") or b"").decode().split()
            if not first:
                continue
            listing = (git(lib, "ls-tree", "-r", "--full-name", "--name-only", first[0], "--", rp) or b"").decode().split()
            now = {rel(p, lib) for p in files(d)}
            was = {x[len(pre):] for x in listing}
            for x in sorted(was | now):
                if x not in now and f"{rid}@{v}" in withheld:
                    continue
                blob = git(lib, "show", f"{first[0]}:{pre}{x}") if x in was else None
                cur = os.path.join(lib, x)
                if x not in now or blob is None or sha(blob) != sha(open(cur, "rb").read()):
                    r.fail("immutable", f"`{x}` is not as `{rid}@{v}` was first released (R4)")
        gone = (git(lib, "log", "--diff-filter=D", "--name-only", "--format=", "--", ".") or b"").decode().split()
        for x in sorted({g for g in gone if g.endswith("/release.yml")}):
            if not os.path.isfile(os.path.join(lib, x[len(pre):])):
                r.fail("immutable", f"`{x[len(pre):]}` was released and has left the library (R4)")
    return r


def withheld_in(lib, bill):
    """the lines of a commons' bill whose release this library withholds, each with the release and its withholding
    (R18): computed by the commons from the library's `library.yml` and index, as it reads them; the library computes none"""
    lid = (yml(os.path.join(lib, "library.yml")) or {}).get("id")
    ix = yml(os.path.join(lib, "index.yml")) or {}
    held = {f"{lid}/{layout.ref_of(x)}@{x.get('version')}": x["withheld"] for x in ix.get("releases") or []   # a variant as `<model>/<variant>`
            if isinstance(x, dict) and isinstance(x.get("withheld"), dict)}
    return [(x, x["part"].split("#", 1)[0], held[x["part"].split("#", 1)[0]]) for x in (bill or {}).get("lines") or []
            if x["part"].split("#", 1)[0] in held]


def where_used(r, lib, core):
    """where-used on withholding (R18): each line of the CORE's bill that a release this library withholds touches"""
    import check_core   # here, not above: the bill is CORE's
    rep = check_core.check(core, offline=True)
    failed = [t for o, _, t in rep.items if o == "fail"]
    if not getattr(rep, "bill", None):
        r.gap("where-used", f"`{core}` has no bill: a finding on what it lists withholds it (core R37); "
                            f"{len(failed)} fail" + (f", first: {failed[0]}" if failed else ""))
        # repair diagnostics: the pins its lock declares, unverified, never a bill and never certified (the EA, commons.o#107)
        lp = os.path.join(core, ".commons", "lock.yml")
        lock = (yml(lp) or {}) if os.path.isfile(lp) else {}
        pins = [layout.ref_of(x) + "@" + str(x.get("version")) for x in layout.pins(lock)]
        for x in lock.get("patterns") or []:
            rec = yml(os.path.join(core, "patterns", str((x or {}).get("path")), "release.yml")) if isinstance(x, dict) else None
            if rec:
                pins.append(f"{rec.get('library')}/patterns@{rec.get('version')}")
        for x, rel, w in withheld_in(lib, {"lines": [{"part": p, "usage": "declared"} for p in pins]}):
            r.should("where-used", f"`{rel}` is a pin the lock declares, unverified since the CORE has no bill, and is "
                                   f"withheld from {w.get('from')} for {w.get('reason')}; repair the CORE before relying on it (R18, R4)")
        return r
    for x, rel, w in withheld_in(lib, rep.bill):
        r.should("where-used", f"`{x['part']}` ({x['usage']}) belongs to `{rel}`, withheld from {w.get('from')} for "
                               f"{w.get('reason')}; the commons keeps its copy and decides what follows (R18, R4)")
    origins = [{"part": str(check_model.origin(rec)).split("#", 1)[0], "usage": f"origin of {k}"}   # a record built from
               for k, (rec, _) in sorted(catalogue.records(layout.runtime(core)).items())   # it is reached by its
               if isinstance(rec, dict) and check_model.origin(rec)]                              # origin (core R37)
    for x, rel, w in withheld_in(lib, {"lines": origins}):
        r.should("where-used", f"`{x['usage'][10:]}` is built from `{rel}`, withheld from {w.get('from')} for "
                               f"{w.get('reason')}; the commons keeps its record and decides what follows (R18, R4)")
    return r


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("library", nargs="?")
    ap.add_argument("--patterns", help="check a folder of pattern files, as a pattern source does before it releases")
    ap.add_argument("--release", help="check one release copy, as a commons does at install")
    ap.add_argument("--expect", help="with --release: the record digest the pin gives, from the library's index")
    ap.add_argument("--names", help="a file of names of persons and organisations, one per line, kept outside git")
    ap.add_argument("--terms", help="a file of third-party codes and trademarks, one per line")
    ap.add_argument("--today", help="the date states are derived for, YYYY-MM-DD; today when omitted")
    ap.add_argument("--core", help="with a library: the lines of this CORE's bill that a withholding touches (R18)")
    ap.add_argument("--spec", choices=sorted(SPECS))
    a = ap.parse_args()
    names, terms = wordlist(a.names), wordlist(a.terms)
    if a.today and day(a.today) is None:
        ap.error(f"--today {a.today} is no date YYYY-MM-DD")
    if a.release:
        r = check_release(a.release, names, terms, a.expect)
        target = a.release
    elif a.patterns:
        r = Report()
        check_patterns(r, a.patterns, a.patterns, names, terms)
        target = a.patterns
    elif a.core:
        r = where_used(Report(), a.library, a.core)
        target = f"{a.core} against {a.library}"
    else:
        r = check(a.library, names, terms, day(a.today) if a.today else None)
        target = a.library
    items = [i for i in r.items if not a.spec or i[1] in SPECS[a.spec]]
    n = {o: sum(1 for i in items if i[0] == o) for o in ("fail", "should", "gap")}
    print(f"# {target}{' · ' + a.spec if a.spec else ''}: {n['fail']} fail · {n['should']} should · {n['gap']} gap")
    for o, c, t in items:
        print(f"{o}: {c}: {t}")
    return 1 if n["fail"] else 0


if __name__ == "__main__":
    sys.exit(main())
