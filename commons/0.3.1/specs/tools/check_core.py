#!/usr/bin/env python3
"""check_core.py — a repository is a well-formed Commons CORE (core.md, core-knowledge.md, core-views.md). Read-only.

Reports each finding as fail (a MUST), should (a SHOULD) or gap (missing, not wrong), and exits with 1 only on a
fail. The check ids are those of the three specifications, part 6:

  core            commons  names  layout  registry  lifecycle  people  world  build  patterns  agent  bill
  core-knowledge  knowledge  sources  claims  ladder  expectations  corrections  register  private
  core-views      sections  views  provenance-record  cuts

The ids are unique across the three, so that each resolves to one specification; --spec reports the findings of one
specification only.

Installed specifications (R26) are read from the generated lock `.commons/lock.yml` (`specs: [{path, origin,
version}]`) and compared with their origin, read from a local checkout at that revision. An installed extract of
patterns (R28) is read from the same lock (`patterns: [{path, origin, record}]`) and checked as a release copy
by check_library.py's `check_copy` against that record digest, the one code of every copy (LIBRARY R8, R9); its origin
is not resolved here.

The bill of materials (R37) is generated, never kept: the lock's installed and served parts, the systems of the
Fabric and the COREs the graph reads, one line each; --bill prints it.

The structure definition is Commons Essentials' `specs/structure.yml` (part 5): the CORE's installed copy under
`extensions/<library>/commons-essentials/`, else one in its `specs/` (the earlier layout), else the one beside this tool, where its version is the one the CORE declares; else the reference this tool pins as its
default, from a local checkout of that repository at that revision; or the file given with --structure. Where the one of the CORE's declared version is not at hand, the
layout is reported as a gap, not guessed. A part moved by
`locations` is checked where it was moved to: a folder of the CORE, or owner/repo@rev:path read from a local checkout
at that revision. What cannot be read there is reported as unverified, never passed.

Usage:  check_core.py CORE [--structure structure.yml] [--spec core|core-knowledge|core-views] [--offline] [--bill]
"""
import argparse
import datetime
import glob
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time

import jsonschema
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMAS = os.path.join(HERE, "..", "schemas")
STRUCTURE = "Commons-Engineering/workshop@f2baad1eb4:_extensions/cloudsters-commons-essentials/structure/structure.yml"   # the default where no `specs/structure.yml` of the declared version is at hand
AREAS = ["runtime", "commons", "emulation", "knowledge", "lifecycle", "workshop", "views", "specs", "patterns", "graph", "fabric"]
EARLIER_KEYS = {"registry": "runtime", "extensions": "commons", "offer": "emulation"}   # the structure keys before 0.4.0
LOCK = os.path.join(".commons", "lock.yml")   # the generated lock (part 5)
REQUIRED_AREAS = ["runtime", "lifecycle"]
EMAIL = re.compile(r"(?<![\w.+/-])[\w.+-]+@[\w-]+(\.[\w-]+)*\.[A-Za-z]{2,}\b")   # never owner/repo@rev, nor an extension@version
PHONE = re.compile(r"\+\d[\d ()-]{7,}\d")
NAME = re.compile(r"^([a-z0-9-]+\.){0,2}[a-z0-9-]+(\.[0-9]+)?\.core$")
RUNG = {"belegt": "evidenced", "established": "evidenced", "Beleg": "evidenced",
        "unbestätigt": "claimed", "unbestaetigt": "claimed", "website": "claimed", "marktreport": "claimed",
        "intern": "claimed", "inferred": "claimed", "abgeleitet": "claimed", "gerechnet": "claimed",
        "Nachweis": "claimed", "Annahme": "assumed", "hypothesis": "assumed",
        "divergent": "contested", "contested": "contested", "contested-strong": "contested"}
KINDS = {"briefing", "lighthouse", "spoken", "portal", "card", "gaps", "curriculum"}
OUTCOMES = {"covered", "on-shelf", "missing", "documented-absence", "unsighted", "not-selected"}   # the last, the earlier name of on-shelf
DEFINITIONS = ["blueprint", "view", "structure"]
HASH = re.compile(r"^[0-9a-f]{64}$")
AGENT_PARTS = ["1 · Who", "2 · Where", "3 · How it answers", "4 · What it never does", "5 · How a role starts"]
OWN = "## Own guidance"
QID = re.compile(r"^[a-z0-9][a-z0-9.-]*/[A-Za-z0-9_.-]+$")   # a source-qualified pattern id (R34)
RELEASE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9-]*/[A-Za-z0-9._-]+@[^\s:@]+$")
EXTRACT = ["path", "origin", "record"]
EXPECTATION = re.compile(r"(^|[/:])(\.provenance|\.build|graph/runs)/")   # where expectations and computed edges are kept
SPECS = {"core": ["commons", "names", "layout", "models", "lifecycle", "people", "world", "provenance", "patterns", "agent", "bill", "federation", "releases"],
         "core-knowledge": ["knowledge", "sources", "claims", "ladder", "expectations", "corrections", "register", "private"],
         "core-views": ["views", "provenance-record", "cuts"],
         "blueprint": ["layers", "frame", "ids", "binds", "selection", "outcomes", "evidence", "reads", "trend"]}

sys.dont_write_bytecode = True   # the tools never write into the install they lie in (SPECIFICATION R29; `extension` R12)
sys.path.insert(0, HERE)
import check_model  # noqa: E402
import layout  # noqa: E402
from check_spec import REMOTE, git, local_checkout, remote_like, resolve  # noqa: E402


class Report:
    def __init__(self):
        self.items = []

    def fail(self, check, text):
        self.items.append(("fail", check, text))

    def should(self, check, text):
        self.items.append(("should", check, text))

    def gap(self, check, text):
        self.items.append(("gap", check, text))


def schema(name):
    return json.load(open(os.path.join(SCHEMAS, name), encoding="utf-8"))


def validate(r, check, sch, doc, where, ref=None):
    if ref:
        sch = dict(sch["$defs"][ref], **{"$defs": sch["$defs"], "$schema": sch["$schema"]})
    for e in jsonschema.Draft202012Validator(sch).iter_errors(doc):
        r.fail(check, f"{where}: {'/'.join(map(str, e.absolute_path)) or 'root'}: {e.message[:110]}")


def yml(path):
    return yaml.safe_load(open(path, encoding="utf-8")) if os.path.exists(path) else None


def files(d):
    return [f for f in glob.glob(os.path.join(d, "**", "*"), recursive=True) if os.path.isfile(f)] if os.path.isdir(d) else []


def scan_persons(r, check, paths, skip):
    for f in paths:
        if os.path.abspath(f) in skip or not f.endswith((".yml", ".yaml", ".md", ".json")):
            continue
        t = open(f, encoding="utf-8", errors="replace").read()
        if EMAIL.search(t) or PHONE.search(t):
            r.fail(check, f"`{f}` holds an e-mail address or a telephone number")


def export(checkout, rev, path, into):
    """the tree of path at rev, written under into, or None"""
    out = subprocess.run(["git", "-C", checkout, "archive", "--format=tar", rev, "--", path], capture_output=True)
    if out.returncode:
        return None
    tarfile.open(fileobj=io.BytesIO(out.stdout)).extractall(into)
    return os.path.normpath(os.path.join(into, path))


def place(r, core, key, ref, offline, tmp):
    """where a part moved by `locations` is read, or None where it cannot be (R4)"""
    if remote_like(ref):
        state, c = resolve(ref, core, offline)
        m = REMOTE.match(ref)
        p = export(c, m["rev"], m["path"], tempfile.mkdtemp(dir=tmp)) if state == "found" and c else None
        if p:
            return p
        if state == "found":
            r.gap("layout", f"`{key}` at `{ref}` exists, but no local checkout holds that revision: its content is unverified")
        elif state == "unreachable":
            r.gap("layout", f"`{key}` at `{ref}` cannot be reached: its content is unverified")
        elif state == "missing":
            r.fail("layout", f"`{key}` is moved to `{ref}`, which does not exist at that revision")
        else:
            r.fail("layout", f"`{key}` is moved to `{ref}`, which is neither a folder nor owner/repo@rev:path")
        return None
    p = os.path.normpath(os.path.join(core, ref))
    if not os.path.exists(p):
        r.fail("layout", f"`{key}` is moved to `{ref}`, which does not exist")
        return None
    return p


def digest(path):
    """the hash of a file as git holds it, whatever the line endings of this checkout"""
    return hashlib.sha256(open(path, "rb").read().replace(b"\r\n", b"\n")).hexdigest()


def front(path):
    """the front matter of a pattern file, or None"""
    t = open(path, encoding="utf-8", errors="replace").read()
    if not t.startswith("---"):
        return None
    try:
        fm = yaml.safe_load(t.split("---", 2)[1])
    except yaml.YAMLError:
        return None
    return fm if isinstance(fm, dict) else None


def computed(fm):
    """whether a pattern's garden block holds anything (R28, R34)"""
    g = fm.get("graph_garden")
    return any(v for v in g.values()) if isinstance(g, dict) else bool(g)


def extract(r, pd, n, e, installed):
    """one installed extract: its lock entry, and its copy checked by the gate's code of a release copy against the
    record digest its lock took from the library's index (R28; LIBRARY R9)"""
    import check_library   # here, not above: it reads PHONE and Report from this module
    at = f"`{LOCK}` patterns[{n}]"
    missing = [k for k in EXTRACT if not e.get(k)]
    if missing:
        r.fail("patterns", f"{at} records no {', '.join(missing)} (R28)")
    if e.get("origin") and not RELEASE.match(str(e["origin"])):
        r.fail("patterns", f"{at}: the origin `{e['origin']}` is not owner/repo@rev (R28)")
    src = e.get("path")
    d = os.path.join(pd, str(src or ""))
    if not src or not os.path.isdir(d):
        r.fail("patterns", f"{at}: `patterns/{src}/` does not exist (R28)")
        return
    copy = check_library.Report()
    rec = check_library.check_copy(copy, d, pd, f"`patterns/{src}`", expect=e.get("record"), installed=True)
    for o, c, t in copy.items:
        getattr(r, o)("patterns", f"{c}: {t} (LIBRARY R9)")
    if rec is None:
        return
    if rec.get("library") != os.path.basename(str(src)):
        r.fail("patterns", f"`patterns/{src}/` holds a release of `{rec.get('library')}`; it lies under its library (R28)")
    for x in [json.loads(y) for y in open(os.path.join(d, "index.jsonl"), encoding="utf-8") if y.strip()][1:]             if os.path.isfile(os.path.join(d, "index.jsonl")) else []:
        f = os.path.join(d, str(x.get("file") or ""))
        installed[x.get("id")] = {"slug": x.get("slug"), "license": (front(f) or {}).get("license") if os.path.isfile(f) else None}


def patterns(r, pd, lock):
    """the installed extracts and the commons' own patterns (R28, R34)"""
    entries = (lock or {}).get("patterns") or [] if isinstance(lock, dict) else []
    if not entries:
        r.gap("patterns", "the CORE has not installed an extract yet (R28)")
    installed, recorded = {}, set()
    for n, e in enumerate(entries):
        e = e if isinstance(e, dict) else {}
        recorded.add(str(e.get("path")))
        extract(r, pd, n, e, installed)
    if not os.path.isdir(pd):
        return
    held = [f"commons/{x}" for x in sorted(os.listdir(os.path.join(pd, "commons")))] if os.path.isdir(os.path.join(pd, "commons")) else []
    held += [x for x in sorted(os.listdir(pd)) if x != "commons" and os.path.isfile(os.path.join(pd, x, "release.yml"))]   # the earlier place
    for x in held:                               # an extract lies in patterns/commons/<library>/ (R28)
        if x not in recorded:
            r.fail("patterns", f"`patterns/{x}/` is installed without a record in the lock (R28)")
    bare = {k.split("/", 1)[1] for k in installed}
    slugs = {v["slug"] for v in installed.values()}
    own = [f for f in sorted(glob.glob(os.path.join(pd, "**", "*.md"), recursive=True))   # own patterns lie anywhere
           if not any(os.path.relpath(f, pd).replace(os.sep, "/").startswith(x + "/") for x in held + ["commons"])]
    for f in own:                                # outside the extracts, read by their `id` (R34)
        name = f"`patterns/{os.path.relpath(f, pd).replace(os.sep, '/')}`"
        fm = front(f)
        if fm is None or not fm.get("id"):
            r.fail("patterns", f"{name}: an own pattern without front matter or `id` (R34)")
            continue
        if fm["id"] in bare or fm.get("slug") in slugs:
            r.fail("patterns", f"{name}: takes the id or slug of an installed pattern; an adaptation names `origin` (R34)")
        if computed(fm):
            r.fail("patterns", f"{name}: holds a computed relation (R34)")
        a = fm.get("origin") or fm.get("adopted_from")   # `adopted_from`, its earlier key (R4)
        if a is None:
            continue
        ref = a.get("id") if isinstance(a, dict) else a
        if not isinstance(a, dict) or not a.get("release") or not QID.match(str(ref)):
            r.fail("patterns", f"{name}: `origin` names no source-qualified id and release (R34)")
        elif ref not in installed:
            r.gap("patterns", f"{name}: adapted from `{ref}`, which is not installed here; its origin is unverified")
        elif fm.get("license") != installed[ref]["license"]:
            r.fail("patterns", f"{name}: does not keep the licence `{installed[ref]['license']}` of its origin (R34)")


def bill(r, core, where, lock, mark=0):
    """the CORE's single-level bill of materials (R37): one line per part it holds or uses directly, generated from
    what already holds it: the lock's installed and served parts, the systems and COREs it reads; withheld only by a
    finding on what it lists, those from `mark` on: the lock, the installed copies and the sources read, while every
    other finding stands beside it"""
    import catalogue   # here, not above: it reads this module
    lock = lock if isinstance(lock, dict) else {}
    licences, digests = {}, {}
    for f in repository_files(core):
        if f.endswith((".yml", ".yaml", ".json")) and os.path.isfile(f) and governed(core, f) and kept_bill(f):
            r.fail("bill", f"`{os.path.relpath(f, core)}` holds a bill of materials; the bill is generated, never kept (R37)")
    lines = []
    sd = where.get("specs") or os.path.join(core, "specs")
    for e in lock.get("specs") or []:
        e = e if isinstance(e, dict) else {}
        f = os.path.join(sd, str(e.get("path") or ""))
        sid = (front(f) or {}).get("id") if os.path.isfile(f) else None
        lines.append({"part": f"{sid or e.get('path')}@{e.get('version')}", "usage": "installed", "origin": e.get("origin")})
    locked = set()
    for e in layout.pins(lock):
        e = e if isinstance(e, dict) else {}
        ref = layout.ref_of(e)
        locked.add(layout.canonical(ref))
        rel = yml(os.path.join(layout.copy(core, ref), "release.yml")) or {}
        licences[ref], digests[ref] = rel.get("licence"), e.get("record")
        parts = rel.get("parts") if isinstance(rel.get("parts"), dict) else {}
        for usage in ("installed", "served"):
            for p in e.get(usage) or []:
                if not isinstance(parts.get(p), dict):
                    r.fail("bill", f"`{LOCK}`: `{ref}` is {usage} with the part `{p}`, which its release record does not name (LIBRARY R3)")
                lines.append({"part": f"{ref}@{e.get('version')}#{p}", "usage": usage, "origin": e.get("origin"),
                              "record": e.get("record"), "class": (parts.get(p) or {}).get("class"), "licence": rel.get("licence")})
    for ref, d in layout.installed(core).items():
        if layout.canonical(ref) not in locked:
            r.fail("bill", f"`{os.path.relpath(d, core)}/` is installed without its entry in the lock (R39)")
    pins = [x for x in layout.pins(yml(os.path.join(core, ".commons", "commons.yml")))
            if isinstance(x, dict) and x.get("id")]
    held = [e for e in layout.pins(lock) if e.get("id")]
    for x in pins:                                   # the pins against the lock, an unqualified pin read by its extension
        at = [e for e in held if same_extension(e, x)]
        if not at:
            r.gap("bill", f"`{layout.ref_of(x)}` {x.get('version')} is pinned and not installed yet; the lock has no entry for it (`extension` R12)")
        for e in at:
            if str(e.get("version")) != str(x.get("version")):
                r.fail("bill", f"`{LOCK}` holds `{layout.ref_of(e)}` at {e.get('version')}, but `commons.yml` pins {x.get('version')} (`extension` R12)")
    for e in held:
        if not any(same_extension(e, x) for x in pins):
            r.fail("bill", f"`{LOCK}` holds `{layout.ref_of(e)}`, which `commons.yml` does not pin (`extension` R12)")
    pd = where.get("patterns") or os.path.join(core, "patterns")
    for e in lock.get("patterns") or []:
        e = e if isinstance(e, dict) else {}
        rel = yml(os.path.join(pd, str(e.get("path") or ""), "release.yml")) or {}
        lines.append({"part": f"{rel.get('library') or e.get('path')}/patterns@{rel.get('version')}#patterns", "usage": "installed",
                      "origin": e.get("origin"), "record": e.get("record"), "class": "public", "licence": rel.get("licence")})
    fd = where.get("fabric") or os.path.join(core, "fabric")
    for x in (yml(os.path.join(fd, "systems.yml")) or {}).get("systems") or []:
        if isinstance(x, dict) and not x.get("id"):
            r.fail("bill", "`fabric/systems.yml`: a system read names no `id`, so no line can name it")
        elif isinstance(x, dict):
            lines.append({"part": f"fabric/systems.yml#{x.get('id')}", "usage": "read", "access": x.get("access"),
                          "class": x.get("class"), "holder": x.get("holder")})
    gd = where.get("graph") or os.path.join(core, "graph")
    for x in (yml(os.path.join(gd, "sources.yml")) or {}).get("sources") or []:
        if isinstance(x, dict) and x.get("kind") == "core" and not x.get("ref"):
            r.fail("bill", f"`graph/sources.yml`: the CORE read as `{x.get('id')}` names no `ref`, so no line can name it")
        elif isinstance(x, dict) and x.get("kind") == "core":
            lines.append({"part": str(x.get("ref")), "usage": "read", "access": x.get("grant"), "class": x.get("class")})
    # a record of the runtime is the commons' own and no line: where-used resolves its `origin` (R37; Holger 6610425987,
    # 32). The bill says what the CORE is made of only where the checks of what it lists pass: a model it installs or
    # serves is checked as at install (R39; LIBRARY R9); a pin alone is no line, so a model a CORE pins without
    # installing it is not checked here
    if layout.pins(lock):
        ext = catalogue.Report()
        catalogue.fit(core, ext)
        failed = [t for o, _, t in ext.items if o == "fail"]
        if failed:
            r.fail("bill", f"no bill is generated: the checks of what it installs fail on what it would list (R39) ({len(failed)}): " + "; ".join(failed))
            return None
    if any(o == "fail" for o, _, _ in r.items[mark:]):
        return None
    return dict(revision(core), lines=[{k: v for k, v in x.items() if v is not None} for x in lines])


def same_extension(a, b):
    """whether two names are one extension: equal, or, where one is unqualified, equal in the extension (`extension` R1);
    a pin or a lock entry is read with its variant, `<library>/<model>/<variant>` (MODEL R30)"""
    va, vb = (a.get("variant") if isinstance(a, dict) else None), (b.get("variant") if isinstance(b, dict) else None)
    if va != vb:
        return False
    a, b = (layout.canonical(x.get("id") if isinstance(x, dict) else x) for x in (a, b))   # `commons-essentials` the earlier id
    return a == b or (("/" not in a or "/" not in b) and a.split("/")[-1] == b.split("/")[-1])


def governed(core, f):
    """whether a file is of the CORE's governed state, where a kept bill would stand beside the generated one: every
    file but the copies installed from elsewhere, checked against their records, and a dated event of `lifecycle/events/`
    that passes as one, a record of what happened (the found state that healing keeps among them) (R37)"""
    at = os.path.relpath(f, core).replace(os.sep, "/").split("/")
    if at[0] in ("specs", "patterns", "extensions"):
        return False
    if at[:2] == ["lifecycle", "events"] and len(at) == 3:
        ev, t = yml(f), Report()
        validate(t, "lifecycle", schema("core.schema.json"), ev, "", "event")
        return not (isinstance(ev, dict) and not t.items)
    return True



RELEASES_RULE = "R40"   # the comparison of a CORE's pins with its libraries' indexes (Holger 6892413220, AL-1, AL-2)


def version_key(v):
    """orders versions such as 0.3.0, 1.0.0-rc.2 or v2026.11.3; a release candidate before its release"""
    v = str(v).lstrip("v")
    base, _, rc = v.partition("-rc.")
    return tuple(int(x) if x.isdigit() else 0 for x in base.split(".")) + ((0, int(rc)) if rc.isdigit() else (1, 0))


def library_clone(core, cfg, lib):
    """the last clone of a library: the path the settings give in `library_clones`, else `../library`"""
    rel = ((cfg or {}).get("library_clones") or {}).get(lib) or os.path.join("..", "library")
    return os.path.normpath(os.path.join(core, rel))


def quiet_git(*args, timeout=30):
    """a git command's output, or None where it fails or git is not at hand"""
    try:
        p = subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
        return p.stdout if p.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def read_library(core, cfg, lib, offline):
    """(index, library.yml, the reading's source and date) of a library, or (None, None, what was tried). Online,
    the public repository itself: the clone's origin fetched, without touching its files, else the raw `index.yml`
    of the repository `libraries` names; offline, or where neither answers, the last clone and its date. No
    federation.mcp: the public library is read directly (Holger 6892504427, FM-1, FM-2)"""
    clone, repo = library_clone(core, cfg, lib), ((cfg or {}).get("libraries") or {}).get(lib)
    today = datetime.date.today().isoformat()
    has_clone = os.path.isfile(os.path.join(clone, "index.yml"))
    if not offline and has_clone and quiet_git("-C", clone, "fetch", "--quiet", "origin", "HEAD") is not None:
        ix, lm = quiet_git("-C", clone, "show", "FETCH_HEAD:index.yml"), quiet_git("-C", clone, "show", "FETCH_HEAD:library.yml")
        if ix:
            url = (quiet_git("-C", clone, "remote", "get-url", "origin") or "origin").strip()
            return yaml.safe_load(ix), yaml.safe_load(lm or "") or {}, f"`{url}` online, fetched {today}"
    if not offline and not has_clone and re.fullmatch(r"[A-Za-z0-9-]+/[A-Za-z0-9._-]+", str(repo or "")):
        import urllib.request
        try:
            raw = lambda f: urllib.request.urlopen(f"https://raw.githubusercontent.com/{repo}/HEAD/{f}", timeout=15).read().decode("utf-8")
            return yaml.safe_load(raw("index.yml")), yaml.safe_load(raw("library.yml")) or {}, f"`{repo}` online, read {today}"
        except (OSError, ValueError, yaml.YAMLError):
            pass
    if has_clone:
        when = (quiet_git("-C", clone, "log", "-1", "--format=%cs %h", timeout=20) or "").strip() or \
            datetime.date.fromtimestamp(os.path.getmtime(os.path.join(clone, "index.yml"))).isoformat()
        return yml(os.path.join(clone, "index.yml")), yml(os.path.join(clone, "library.yml")) or {}, f"the last clone at `{clone}`, of {when}"
    return None, None, f"neither `{repo or lib}` online nor a clone at `{clone}`"


def releases(r, core, cfg, offline=False):
    """releases (R40): each pin and lock entry against the index of the library it comes from, read from the public
    library itself, or offline from its last clone. A newer released version is a gap, a question whose answer is
    the commons' decision (R28); a pinned version retired is a should; one withheld is a fail; no index at hand is a
    gap, not compared"""
    lock = yml(os.path.join(core, ".commons", "lock.yml")) or {}
    want = {}                                                    # `<library>/<model>[/<variant>]` → the version held
    for p in layout.pins(cfg) + layout.pins(lock):
        if p.get("id") and p.get("version") is not None:
            want.setdefault(layout.canonical(layout.ref_of(p)), str(p["version"]))
    for x in lock.get("patterns") or []:
        if isinstance(x, dict) and "@" in str(x.get("origin", "")):
            lib = str(x.get("path", "")).split("/")[-1] or "commons-engineering"
            want.setdefault(f"{lib}/patterns", str(x["origin"]).rsplit("@", 1)[1])
    for lib in sorted({k.split("/")[0] for k in want}):
        idx, meta, seen = read_library(core, cfg, lib, offline)
        if not isinstance(idx, dict) or (meta or {}).get("id") != lib:
            r.gap("releases", f"`{lib}`: not compared: {seen} could be read; clone the library there, or name its "
                              f"path under `library_clones` in commons.yml ({RELEASES_RULE})")
            continue
        withheld = {str(w.get("release")) for w in meta.get("withheld") or [] if isinstance(w, dict)}
        for ref, have in sorted(want.items()):
            if ref.split("/")[0] != lib:
                continue
            _, m, *v = ref.split("/")
            ids = {m, *layout.ESSENTIALS} if m in layout.ESSENTIALS else {m}
            hits = [e for e in idx.get("releases") or [] if isinstance(e, dict) and e.get("id") in ids
                    and (e.get("variant") or None) == (v[0] if v else None)]
            name = f"{m}/{v[0]}" if v else m
            pinned = next((e for e in hits if str(e.get("version")) == have), None)
            if pinned is None:
                r.gap("releases", f"`{ref}` {have}: the index of `{lib}` lists no such release; read from {seen} ({RELEASES_RULE})")
                continue
            if pinned.get("withheld") or f"{pinned.get('id')}@{have}" in withheld or f"{name}@{have}" in withheld:
                r.fail("releases", f"`{ref}` {have} is withheld by `{lib}`; where-used names the lines it touches, and "
                                   f"what follows is the commons' decision (library R18); read from {seen} ({RELEASES_RULE})")
            elif pinned.get("state") == "retired":
                r.should("releases", f"`{ref}` {have} is retired; a later release ends it ({RELEASES_RULE}; library R4); read from {seen}")
            newer = sorted((e for e in hits if e.get("state") == "released" and not e.get("withheld")
                            and version_key(e.get("version")) > version_key(have)), key=lambda e: version_key(e.get("version")))
            if newer:
                r.gap("releases", f"`{ref}` {have}: `{lib}` has released {newer[-1]['version']}; take it up with "
                                  f"`install.py --take-up`, by decision (R28); read from {seen} ({RELEASES_RULE})")


def federation(r, core):
    """federation (R38): the dated reading of what `federation.mcp` offers each shell, generated, naming no one's access"""
    f = os.path.join(core, ".commons", "federation.yml")
    if not os.path.exists(f):
        r.gap("federation", "there is no reading of what `federation.mcp` offers each shell yet; federation.mcp is not yet in operation, and the CORE works fully without it: the public library is read directly, and a reading is taken at the first contact (R38)")
        return
    try:
        d = yml(f)
    except yaml.YAMLError as e:
        r.fail("federation", f"`.commons/federation.yml` does not parse: {str(e)[:110]}")
        return
    if not isinstance(d, dict):
        r.fail("federation", "`.commons/federation.yml` is no reading: it names whom it was read from, when, by what and each shell's offer (R38)")
        return
    at = d.get("read_at")
    d = {**d, "read_at": at.isoformat() if hasattr(at, "isoformat") else at}   # YAML reads an unquoted date or time as one
    validate(r, "federation", schema("core.schema.json"), d, "`.commons/federation.yml`", "reading")
    if isinstance(d["read_at"], str) and d["read_at"]:
        try:
            datetime.datetime.fromisoformat(d["read_at"].replace("Z", "+00:00"))
        except ValueError:
            r.fail("federation", f"`.commons/federation.yml`: read_at `{d['read_at']}` is no date or time, so the reading's age cannot be named (R38)")
    for sh, o in (d["shells"] if isinstance(d.get("shells"), dict) else {}).items():
        validate(r, "federation", schema("mcp.schema.json"), o, f"`.commons/federation.yml`: shells/{sh}", "offered")
    try:
        acc = yml(os.path.join(core, ".commons", "access.yml")) or yml(os.path.join(core, "access.yml"))
    except yaml.YAMLError:
        acc = None   # `mcp` reads it
    named = acc.get("federation") if isinstance(acc, dict) else None
    if named and d.get("from") and d["from"] != named:
        r.should("federation", f"`.commons/federation.yml` was read from `{d['from']}`, while `access.yml` names `{named}` (R38; `mcp` R24)")
    names = re.findall(r"\b(?:account|key):[^\s,'\"\]}]+", yaml.safe_dump(d, allow_unicode=True))
    held = [k for k in ("users", "accounts", "gets") if k in d]
    if names or held:
        r.fail("federation", f"`.commons/federation.yml` holds someone's access ({', '.join(names[:3] or held)}): the offer is per shell and names no one (R38; `mcp` R7, R28)")


def kept_bill(f):
    """whether a file holds a bill of materials: a `bill`, or lines each naming a part and its usage (R37)"""
    try:
        d = json.load(open(f, encoding="utf-8")) if f.endswith(".json") else yaml.safe_load(open(f, encoding="utf-8"))
    except (ValueError, yaml.YAMLError, UnicodeDecodeError):
        return False
    d = d.get("bill", d) if isinstance(d, dict) else d
    rows = d.get("lines") if isinstance(d, dict) else d
    return isinstance(rows, list) and bool(rows) and all(isinstance(x, dict) and "part" in x and "usage" in x for x in rows)


def revision(core):
    """what generated a bill and the revision of the CORE it was generated from, with `read_at` where the CORE's files
    differ from that commit, as a cut of GRAPH names a source (R37)"""
    def out(d, *a):
        p = subprocess.run(["git", "-C", d, *a], capture_output=True, text=True)
        return p.stdout.strip() if p.returncode == 0 else ""
    url = out(HERE, "remote", "get-url", "origin")
    repo = re.sub(r"\.git$", "", url.rstrip("/")).split("github.com")[-1].lstrip("/:") if url else ""
    tool = os.path.relpath(os.path.abspath(__file__), out(HERE, "rev-parse", "--show-toplevel") or HERE).replace(os.sep, "/")
    at = {"generator": f"{repo}@{out(HERE, 'rev-parse', '--short', 'HEAD')}:{tool}" if repo else tool}
    rev = out(core, "rev-parse", "HEAD")
    if rev:
        at["rev"] = rev
        if out(core, "status", "--porcelain", "--", "."):
            at["read_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    return at


def repository_files(core):
    """the files of the CORE as its repository holds them: tracked, or new and not ignored; a git-ignored local file
    is the person's, not the CORE's (commons.o#95, 6465844553)"""
    out = subprocess.run(["git", "-C", core, "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                         capture_output=True)
    if out.returncode == 0:
        return [os.path.join(core, f) for f in out.stdout.decode("utf-8").split("\0") if f]
    return glob.glob(os.path.join(core, "**", "*"), recursive=True, include_hidden=True)


def agent(r, core):
    """agent (R36): one agent-neutral AGENT.md, its five parts generated with a provenance record; a pointer and a folder note
    are read for whether they point to it, in any wording"""
    path = os.path.join(core, "AGENT.md")
    for p in repository_files(core):
        rel = os.path.relpath(p, core).replace(os.sep, "/")
        if not os.path.isfile(p) or rel == "AGENT.md" or rel.startswith((".git/", "specs/", ".provenance/", ".build/")):
            continue
        if os.path.basename(p) == "AGENT.md":                       # a folder note
            lines = [l.strip() for l in open(p, encoding="utf-8", errors="replace").read().splitlines()]
            if "AGENT.md" not in next((l for l in lines if l), ""):
                r.fail("agent", f"the folder note `{rel}` does not open by pointing to `AGENT.md`")
    if not os.path.exists(path):
        r.gap("agent", "the CORE holds no `AGENT.md` yet")
        return
    text = open(path, encoding="utf-8").read()
    man = os.path.join(core, layout.provenance_dir(core), "agent", "manifest.json")
    if not os.path.exists(man):
        r.gap("agent", "`AGENT.md` is kept by hand, without its provenance record `.provenance/agent/manifest.json`: unmigrated (R4)")
        return
    gen = text.split("\n" + OWN, 1)[0]
    heads = [l[3:].strip() for l in gen.splitlines() if l.startswith("## ")]
    if heads != AGENT_PARTS:
        r.fail("agent", f"the generated part of `AGENT.md` holds the parts {heads}, not the five {AGENT_PARTS}")
    import make_agent                            # here, not above: the founding dialogue is the generator's text
    rules = [l.split("**")[1] for l in make_agent.FOUNDING if l[:1].isdigit() and "**" in l]
    missing = [x for x in rules if f"**{x}**" not in gen]
    if "\n### Founding dialogue" not in gen or missing:
        r.fail("agent", "the generated part of `AGENT.md` does not hold the founding dialogue"
                        + (f", without {', '.join(missing)}" if missing and len(missing) < len(rules) else "")
                        + "; generate it again with make_agent.py (R41)")
    m = json.load(open(man, encoding="utf-8"))
    if m.get("output") != hashlib.sha256(gen.encode("utf-8")).hexdigest():
        r.fail("agent", "the generated part of `AGENT.md` differs from what its provenance record says was generated: edited by hand")
    if not m.get("inputs"):
        r.fail("agent", "the provenance record of `AGENT.md` names no `inputs`: it is no provenance")
    for i, h in (m.get("inputs") or {}).items():
        f = os.path.join(core, i)
        if not HASH.match(str(h)):
            r.fail("agent", f"the provenance record of `AGENT.md` carries no hash for `{i}`")
        elif not os.path.isfile(f) or digest(f) != h:
            r.fail("agent", f"`{i}` changed and `AGENT.md` was not regenerated in the same commit")


def vkey(v):
    return tuple(int(x) if x.isdigit() else 0 for x in re.split(r"[.-]", str(v)))


def structure(path, core, version=None):
    """the structure definition: a file given with --structure, else Commons Essentials' `specs/structure.yml` of the
    declared version, the CORE's installed copy, one in its `specs/` (the earlier layout) or the one beside this tool,
    else the pinned reference from a local checkout"""
    if path:
        return yml(path)
    held = sorted(glob.glob(os.path.join(core, "models", "commons", "*", "commons", "specs", "structure.yml")) +
                  glob.glob(os.path.join(core, "extensions", "*", "commons-essentials", "specs", "structure.yml")))
    found = [sd for f in held + [os.path.join(core, "specs", "structure.yml"), os.path.join(HERE, "..", "structure.yml")]
             for sd in [yml(f) if os.path.isfile(f) else None] if isinstance(sd, dict) and sd.get("version")]
    for sd in found:
        if version is not None and str(sd.get("version")) == str(version):
            return sd
    newer = [sd for sd in found if version is not None and vkey(sd["version"]) > vkey(version)]
    if newer:                                    # a newer definition reads an earlier layout by its earlier locations (R4)
        return max(newer, key=lambda sd: vkey(sd["version"]))
    m = REMOTE.match(STRUCTURE)
    for base in (core, HERE):
        c = local_checkout(base, m["owner"], m["repo"])
        out = git(c, "show", f"{m['rev']}:{m['path']}") if c else None
        if out and out.returncode == 0:
            return yaml.safe_load(out.stdout)
    return None


def check(core, structure_path=None, offline=False):
    tmp = tempfile.mkdtemp(prefix="check_core-")
    try:
        return run(core, structure_path, offline, tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def run(core, structure_path, offline, tmp):
    r = Report()
    rule = schema("core.schema.json")
    cfg = yml(os.path.join(core, ".commons", "commons.yml"))

    # commons (R1)
    if cfg is None:
        r.fail("commons", "there is no `.commons/commons.yml`")
        return r
    validate(r, "commons", rule, cfg, "commons.yml")
    # at most one primary, the extension of the commons' kind, never Commons Essentials; none yet is a gap (R1;
    # EXTENSION R9; D1, commons.o#109 6569929566)
    prim = [x for x in layout.pins(cfg) if x.get("primary")]
    if "extensions" in cfg and "models" not in cfg:
        r.gap("commons", "`commons.yml`: `extensions` is the earlier key of `models`: unmigrated (R4)")
    if any(str(x.get("id")).split("/")[-1] in layout.ESSENTIALS for x in prim):
        r.fail("commons", "the Commons model is marked primary: the discipline's grammar is never a commons' primary (R1)")
    if len(prim) > 1:
        r.fail("commons", f"{len(prim)} primary extensions: at most one, the extension of the commons' kind (R1)")
    if not prim:
        r.gap("commons", "no primary yet, a question for the commons: which value creation is modelled here? The founding "
                         "dialogue of AGENT.md finds it, and `python bootstrap.py --domain <domain>` installs the domain "
                         "model that fits (R1)")
    if cfg.get("target") and cfg.get("as_of") and cfg.get("slice") is not None:
        if int(str(cfg["as_of"])[:4]) + int(cfg["slice"]) != cfg["target"]:
            r.fail("commons", "`target` disagrees with the year of `as_of` plus `slice`")

    # names (R3)
    folder = os.path.basename(os.path.abspath(core))
    if not NAME.match(folder):
        r.gap("names", f"the folder `{folder}` is not named `[holder.][world.][commons][.slice].core`: unmigrated (R4)")
    segs = folder.removesuffix(".core").split(".")
    digits = [i for i, s in enumerate(segs) if s.isdigit()]
    sl = int(cfg.get("slice") or 0)
    if digits and (digits != [len(segs) - 1] or int(segs[-1]) != sl):
        r.fail("names", f"the folder `{folder}` names the slice {'.'.join(segs[i] for i in digits)}, the CORE states `slice` {sl}")
    elif digits and sl == 0:
        r.fail("names", f"the folder `{folder}` writes the slice 0, which is omitted")
    elif not digits and sl:
        r.fail("names", f"the folder `{folder}` does not name the slice {sl}")

    # layout (R4, R5)
    sd = structure(structure_path, core, cfg.get("structure"))
    if not sd or vkey(sd.get("version")) < vkey(cfg.get("structure")):
        r.gap("layout", f"the structure definition {cfg.get('structure')} is not at hand; the layout is not checked")
        sd = None
    elif str(sd.get("version")) != str(cfg.get("structure")):
        tool = os.path.relpath(os.path.join(HERE, "migrate_core.py"), core).replace(os.sep, "/")
        r.gap("layout", f"the CORE states structure {cfg.get('structure')} and is read with {sd.get('version')}: its parts at "
                        f"their earlier locations are unmigrated (R4); `python {tool} . --apply` moves it, on a working branch")
    loc = cfg.get("locations") or {}
    where = {}
    if sd:
        areas = dict(sd.get("areas") or {})
        areas.setdefault("knowledge", {"path": "knowledge", "earlier": ["workshop/evidence", "instance/workshop/evidence"]})
        keys = set(areas) | set(sd.get("paths") or {}) | {"people"}
        for k in loc:
            if k not in keys and EARLIER_KEYS.get(k) not in keys:
                r.fail("layout", f"`locations` moves `{k}`, which is no structure key")
        loc = {EARLIER_KEYS.get(k, k): v for k, v in loc.items()}   # an earlier key moves its new one (R4)
        for k in AREAS:
            a = areas.get(k) or areas.get({v: o for o, v in EARLIER_KEYS.items()}.get(k)) or {"path": k}   # a definition before 0.4.0 names it by its earlier key
            p = os.path.join(core, a["path"])
            if k in loc:
                where[k] = place(r, core, k, loc[k], offline, tmp)
                if files(p) and where[k] != os.path.normpath(p):
                    r.fail("layout", f"`{k}` is moved by `locations`, and its default place `{a['path']}` still holds files")
                continue
            if os.path.isdir(p):
                where[k] = p
                continue
            old = next((e for e in a.get("earlier") or [] if os.path.isdir(os.path.join(core, e))), None)
            if old:
                where[k] = os.path.join(core, old)
                r.gap("layout", f"`{k}` is at its earlier place `{old}`: unmigrated")
            elif k in REQUIRED_AREAS:
                r.fail("layout", f"the area `{k}` is missing")
        for ra in sd.get("retired_areas") or []:
            if files(os.path.join(core, ra)):
                r.fail("layout", f"the retired area `{ra}` holds files")
        if os.path.exists(os.path.join(core, ".commons", "account.yml")):
            r.fail("layout", "`.commons/account.yml` is an engagement record inside the CORE")
    else:
        for k in AREAS:
            if k in loc:
                where[k] = place(r, core, k, loc[k], offline, tmp)
            elif os.path.isdir(os.path.join(core, k)):
                where[k] = os.path.join(core, k)

    # models (R6): the runtime, every model in one generation of element folders
    reg = where.get("runtime")
    if reg and sd:
        gens = {}
        for e in sd.get("elements") or []:
            names = [e["folder"]] + [x["folder"] for x in e.get("earlier") or []]
            full = [n for n in names if files(os.path.join(reg, n))]
            if len(full) > 1:
                r.fail("models", f"element `{e['key']}` is held in {full}: two generations at once")
            gens[e["key"]] = full
        if any(full and full[0] != e["folder"] for e in sd.get("elements") or [] for full in [gens.get(e["key"])]):
            r.gap("models", "the runtime is on an earlier generation of element folders: unmigrated")
    if reg:
        rep = check_model.check(check_model.load(reg), extension=cfg.get("instance_type") == "extension")
        for o, c, t in rep.items:
            if o == "fail":
                r.fail("models", f"{c}: {t}")
            elif o == "should":                      # TA-5: the model check's shoulds are the CORE's, never dropped
                r.should("models", f"{c}: {t}")
        n = sum(1 for o, _, _ in rep.items if o == "gap")
        if n:
            tool = os.path.relpath(os.path.join(HERE, "check_model.py"), core).replace(os.sep, "/")
            r.gap("models", f"the runtime holds {n} gaps; `python {tool} models/runtime` lists them")
    for name, d in layout.emulations(core).items():   # audit D4: every model, each emulation too, passes check_model (part 6)
        at = os.path.relpath(d, core).replace(os.sep, "/")
        own = [yml(os.path.join(d, f)) for f in ("model.yml", "offer.yml") if os.path.isfile(os.path.join(d, f))]
        m = check_model.load(d)
        built = any(check_model.origin(x) for x in m.get("records") or [])   # R6: built from a model, its records name their origins
        if built and not any(isinstance(x, dict) and x.get("origin") for x in own):
            r.fail("models", f"`{at}`: the emulation is built from a model, its records name their origins, and its `model.yml` "
                             f"names no `origin`, the model or revision it was built from (R6); a model its maker authors names none")
        if not m.get("records"):
            continue
        rep = check_model.check(m, extension=name == "offer" or cfg.get("instance_type") == "extension")
        for o, c, t in rep.items:
            if o in ("fail", "should"):
                getattr(r, o)("models", f"`{at}`: {c}: {t}")
        n = sum(1 for o, _, _ in rep.items if o == "gap")
        if n:
            r.gap("models", f"the emulation `{at}` holds {n} gaps; check_model.py lists them")
    # the models it installs and what it builds from them (R1, R6, R39): every copy whole and read-only, passing the
    # gate's checks against the lock's digest; every `origin` resolving to a record the pinned version holds, one
    # origin per record; at most one primary, never the Commons model
    if layout.installed(core):                    # a pin alone is no copy; the bill reads it (R37)
        import catalogue                       # here, not above: it reads this module
        for o, c, t in catalogue.fit(core, catalogue.Report()).items:
            if o == "should" and "retired for" in t:     # a term hint in an installed copy is its maker's, not the commons' (R14)
                continue
            if c == "fit" and t.startswith("no primary yet"):  # said once, under R1 above
                continue
            getattr(r, o)("models", f"{c}: {t}")

    # lifecycle (R11, R12)
    lc = where.get("lifecycle")
    if lc:
        events = {}
        for f in sorted(glob.glob(os.path.join(lc, "events", "*.y*ml"))):
            ev = yml(f) or {}
            validate(r, "lifecycle", rule, ev, os.path.relpath(f, core), "event")
            if ev.get("id") in events:
                r.fail("lifecycle", f"the event id `{ev.get('id')}` appears twice")
            events[ev.get("id")] = ev
        st = yml(os.path.join(lc, "stage.yml"))
        if st is None:
            r.gap("lifecycle", "there is no `stage.yml` yet: record the founding, an event of kind `founding` in lifecycle/events/ and `stage.yml` naming it with its stage, e.g. Seed (R11)")
        else:
            validate(r, "lifecycle", rule, st, "stage.yml", "stage")
            ev = events.get(st.get("event"))
            if not ev or ev.get("kind") not in ("stage-change", "founding"):
                r.fail("lifecycle", f"`stage.yml` names `{st.get('event')}`, which is no stage-change or founding event")
        for i, ev in events.items():
            if ev.get("kind") == "correction" and ev.get("corrects") not in events:
                r.fail("lifecycle", f"the correction `{i}` names `{ev.get('corrects')}`, which is no event")

    # people (R14)
    pp = loc.get("people") or ((((sd or {}).get("paths") or {}).get("people")) or {}).get("path")
    skip = set()
    if not pp:
        r.gap("people", "the place of the party register is not stated")
    else:
        pf = place(r, core, "people", pp, offline, tmp) if "people" in loc else os.path.join(core, pp)
        if pf:
            skip.add(os.path.abspath(pf))
        doc = yml(pf) if pf else None
        if pf is None:
            pass                                                # reported by place
        elif doc is None:
            r.gap("people", f"the party register `{pp}` does not exist yet")
        else:
            validate(r, "people", rule, doc, pp, "people")
    party = {p.get("id") for p in (doc or {}).get("people") or [] if isinstance(p, dict)} if pp and isinstance(doc, dict) else None
    scan_persons(r, "people", [f for k in ("runtime", "lifecycle", "views") for f in files(where.get(k) or "")]
                 + (files(layout.loops(core)) if not (where.get("runtime") or "").startswith(os.path.join(core, "models")) else [])
                 + files(os.path.join(core, ".commons")), skip)

    # world (R17)
    if cfg.get("instance_type") == "world" and files(where.get("knowledge") or ""):
        r.fail("world", "a world CORE holds evidence of its own in `knowledge/`")

    # specs (R5, R26): an installed specification is recorded in the lock and is the same text as its origin; from here
    # to the bill, every finding is on what the bill lists
    mark = len(r.items)
    lock = yml(os.path.join(core, LOCK))
    for n, e in enumerate((lock or {}).get("specs") or [] if isinstance(lock, dict) else []):
        where_ = f"`{LOCK}` specs[{n}]"
        origin, path, version = (e or {}).get("origin"), (e or {}).get("path"), (e or {}).get("version")
        if not version:
            r.fail("layout", f"{where_} records no version (R26)")
        m = REMOTE.match(str(origin or ""))
        if not m:
            r.fail("layout", f"{where_}: the origin `{origin}` is not owner/repo@rev:path (R26)")
            continue
        installed = os.path.join(where.get("specs") or os.path.join(core, "specs"), path or os.path.basename(m["path"]))
        if not os.path.isfile(installed):
            r.fail("layout", f"{where_}: the installed specification `{os.path.relpath(installed, core)}` does not exist")
            continue
        state, c = resolve(origin, core, offline)
        if state == "found" and c:
            shown = subprocess.run(["git", "-C", c, "show", f"{m['rev']}:{m['path']}"], capture_output=True)
            same = shown.returncode == 0 and shown.stdout.replace(b"\r\n", b"\n") == \
                open(installed, "rb").read().replace(b"\r\n", b"\n")
            if not same:
                r.fail("layout", f"`{os.path.relpath(installed, core)}` differs from its origin `{origin}`: edited in place (R26)")
        elif state == "found":
            r.gap("layout", f"`{os.path.relpath(installed, core)}`: its origin `{origin}` exists, but no local checkout holds it; unverified")
        elif state == "unreachable":
            r.gap("layout", f"`{os.path.relpath(installed, core)}`: its origin `{origin}` cannot be reached; unverified")
        else:
            r.fail("layout", f"`{os.path.relpath(installed, core)}`: its origin `{origin}` does not exist at that revision")

    # patterns (R28, R34)
    patterns(r, where.get("patterns") or os.path.join(core, "patterns"), lock)

    # bill (R37)
    r.bill = bill(r, core, where, lock, mark)

    # federation (R38)
    federation(r, core)
    releases(r, core, cfg, offline)

    # agent (R36)
    agent(r, core)

    # build (R18)
    gi = os.path.join(core, ".gitignore")
    if os.path.exists(gi) and any(re.match(r"^/?\.(provenance|build)/?\s*$", l) for l in open(gi, encoding="utf-8")):
        r.fail("provenance", "`.gitignore` excludes the provenance record, so it is not committed")
    if os.path.isdir(os.path.join(core, ".build")):
        r.gap("provenance", "the provenance record is at its earlier place `.build/`: unmigrated (R4)")

    # knowledge, sources, claims, ladder, register, private (core-knowledge)
    kr = schema("core-knowledge.schema.json")
    kd = where.get("knowledge")
    if not kd:
        if "knowledge" not in loc and cfg.get("instance_type") != "world":   # a moved one is reported by place; a world holds none (R17)
            r.gap("knowledge", "the CORE holds no `knowledge/` yet")
    else:
        src = yml(os.path.join(kd, "sources.yml")) or {}
        src = src.get("sources") if isinstance(src, dict) else src
        ids = set()
        for s in src or []:
            validate(r, "sources", kr, s, f"source `{s.get('id')}`", "source")
            ids.add(s.get("id"))
        # a jurisdiction's law binds records in its own file, by sources of that jurisdiction (`core-knowledge` R20)
        bysrc = {s.get("id"): s for s in src or [] if isinstance(s, dict)}
        for f in sorted(glob.glob(os.path.join(kd, "jurisdictions", "*.y*ml"))):
            jd, where_j = yml(f) or {}, os.path.relpath(f, core)
            validate(r, "sources", kr, jd, where_j, "jurisdiction")
            for bd in (jd.get("bindings") or []) if isinstance(jd, dict) else []:
                for b in (bd.get("binds") or []) if isinstance(bd, dict) else []:
                    s = bysrc.get(b.get("source")) if isinstance(b, dict) else None
                    if s is None:
                        r.fail("sources", f"`{where_j}` binds `{b}`, which is no source of `sources.yml` (`core-knowledge` R20)")
                    elif s.get("jurisdiction") != jd.get("jurisdiction"):
                        r.fail("sources", f"`{where_j}` binds `{b.get('source')}` of `{s.get('jurisdiction')}`, not of `{jd.get('jurisdiction')}` (`core-knowledge` R20)")
        # expectations (`core-knowledge` R7): an expectation is cached with a provenance record, and a run's computed output lives in its
        # package; a source that points into either, of this CORE or another, would make a guess evidence
        for s in src or []:
            at = [str(s.get("url") or ""), str((s.get("raw") or {}).get("ref") or "") if isinstance(s.get("raw"), dict) else ""]
            if any(EXPECTATION.search(a) for a in at):
                r.fail("expectations", f"source `{s.get('id')}` points at an expectation or a run's output, never evidence: an expected statement does not return as a fact (`core-knowledge` R7)")
        cl = yml(os.path.join(kd, "claims.yml")) or {}
        cl = cl.get("claims") if isinstance(cl, dict) else cl
        cids = {c.get("id") for c in cl or []}
        for c in cl or []:
            validate(r, "claims", kr, c, f"claim `{c.get('id')}`", "claim")
            if not c.get("sources") and c.get("kind") != "derived":
                r.gap("claims", f"claim `{c.get('id')}` rests on no source yet")
            for s in c.get("sources") or []:
                if s not in ids:
                    r.fail("claims", f"claim `{c.get('id')}` names the source `{s}`, which is not in `sources.yml`")
            for i in c.get("inputs") or []:
                if i not in cids:
                    r.fail("claims", f"claim `{c.get('id')}` is derived from `{i}`, which is no claim")
            w = c.get("confidence")
            if w and w not in RUNG:
                r.fail("ladder", f"claim `{c.get('id')}`: the word `{w}` is not in the mapping of part 5")

        # corrections (R17, R18): a claim that carries a correction is the commons' own word, and names its giver from
        # the party register, the standing they held, the date, what it corrects and any further use with its word
        held = set()
        for f in files(where.get("runtime") or ""):
            rec = yml(f) if f.endswith((".yml", ".yaml")) else None
            if isinstance(rec, dict) and rec.get("kind") and rec.get("slug"):
                held |= {f"{rec['kind']}:{rec['slug']}", str(rec["slug"])}
        for c in cl or []:
            if not isinstance(c, dict) or "correction" not in c:
                continue
            cid = c.get("id")
            validate(r, "corrections", kr, c, f"claim `{cid}`", "claim_with_correction")
            k = c.get("correction") if isinstance(c.get("correction"), dict) else {}
            if party is not None and k.get("given_by") not in party:
                r.fail("corrections", f"claim `{cid}`: the correction's giver `{k.get('given_by')}` is not in the party register (R17)")
            if k.get("corrects") and k["corrects"] not in cids and k["corrects"] not in held:
                r.fail("corrections", f"claim `{cid}` corrects `{k['corrects']}`, which is no claim or record of this CORE (R17)")
            if k.get("prompted") and not c.get("sources"):
                r.gap("corrections", f"claim `{cid}` was prompted by `{k['prompted']}` and rests on no source: judged on its own evidence, it corroborates nothing (R17)")
        reg_file = yml(os.path.join(kd, "stakeholders.yml")) or {}
        if cfg.get("perspective") == "observed":                # holding a CORE is no observation mandate
            for p in reg_file.get("parties") or []:
                if p.get("visibility") == "private":
                    r.fail("register", f"a twin observed from outside holds the private entry `{p.get('id')}`")
        scan_persons(r, "private", files(kd), skip)

    # views, provenance-record (core-views); a view's sections resolve in the CORE's plan (blueprint R1, R9)
    vr = schema("core-views.schema.json")
    vd = where.get("views")
    secs = None
    if vd and glob.glob(os.path.join(vd, "*", "view.yml")):
        try:
            import plan  # noqa: E402
            import render_blueprint  # noqa: E402
            rdg = render_blueprint.Reading(core)
            secs = {s["id"] for s in plan.merged(plan.layers(core, rdg.at), rdg)} | {s["id"] for s in plan.merged(plan.layers(core, rdg.at))}
        except Exception:                            # a CORE whose models cannot be read: its views are not resolved
            secs = None
    for vf in sorted(glob.glob(os.path.join(vd, "*", "view.yml"))) if vd else []:
        name = os.path.basename(os.path.dirname(vf))
        v = yml(vf) or {}
        validate(r, "views", vr, v, f"view `{name}`", "view")
        if v.get("name") and v["name"] != name:
            r.fail("views", f"view `{name}` calls itself `{v['name']}`; a view is known by its folder (R5)")
        if v.get("kind") and v["kind"] not in KINDS:
            r.should("views", f"view `{name}` is of the own kind `{v['kind']}`")
        for k in ("promise", "way_back"):
            if not v.get(k):
                r.fail("views", f"view `{name}` does not state its `{k}`")
        if cfg.get("language") and cfg["language"] not in (v.get("languages") or []):
            r.fail("views", f"view `{name}` is not rendered in the commons' own language `{cfg['language']}`")
        if secs is None:
            r.gap("views", f"view `{name}`: the plan cannot be read to resolve its sections")
        else:
            for s in v.get("sections") or []:
                if s not in secs:
                    r.fail("views", f"view `{name}` names the section `{s}`, which the plan does not hold (blueprint R5)")
        for a in v.get("after") or []:
            if a == name or (yml(os.path.join(vd, a, "view.yml")) or {}).get("kind") != "curriculum":
                r.fail("views", f"view `{name}` comes after `{a}`, which is no other curriculum view of this CORE")
        rendered = [f for f in files(os.path.dirname(vf)) if os.path.basename(f) != "view.yml"]
        man = os.path.join(core, layout.provenance_dir(core), name, "manifest.json")
        if rendered and not os.path.exists(man):
            r.fail("provenance-record", f"view `{name}` is rendered, but has no provenance record `{layout.provenance_dir(core)}/{name}/manifest.json`")
        elif os.path.exists(man):
            m = json.load(open(man, encoding="utf-8"))
            for k in ("definitions", "inputs", "outcomes"):
                if not m.get(k):
                    r.fail("provenance-record", f"the provenance record of `{name}` names no `{k}`: it is no provenance")
            d = m.get("definitions") or {}
            for k in DEFINITIONS if d else []:
                if not d.get(k):
                    r.fail("provenance-record", f"the provenance record of `{name}` names no version of the {k} definition")
            if d.get("view") and d["view"] != name:
                r.fail("provenance-record", f"the provenance record of `{name}` was made for the view `{d['view']}`")
            if d.get("structure") and cfg.get("structure") and str(d["structure"]) != str(cfg["structure"]):
                r.gap("provenance-record", f"view `{name}` was built on structure {d['structure']}, the CORE is on {cfg['structure']}: stale")
            for i, h in (m.get("inputs") or {}).items():
                f = os.path.join(core, i)
                if not HASH.match(str(h)):
                    r.fail("provenance-record", f"view `{name}`: the input `{i}` carries no hash")
                elif not os.path.isfile(f) or digest(f) != h:
                    r.gap("provenance-record", f"view `{name}`: the input `{i}` changed since the rendering: stale")
            for s in (v.get("sections") or []) if m.get("outcomes") else []:
                if s not in m["outcomes"]:
                    r.fail("provenance-record", f"view `{name}`: the section `{s}` has no outcome")
            full = str(m.get("generator") or "").endswith("render_blueprint.py")   # the full briefing renders the whole plan
            for s, o in (m.get("outcomes") or {}).items():
                if o not in OUTCOMES:
                    r.fail("provenance-record", f"view `{name}`, section `{s}`: `{o}` is none of the five outcomes")
                if s not in (v.get("sections") or []) and not full:
                    r.fail("provenance-record", f"view `{name}`: the outcome of `{s}` belongs to no section of the view")
    cuts(r, core)
    import plan  # noqa: E402  (it reads render_blueprint, which reads this module's neighbours)
    plan.check(r, core)                          # the plan (blueprint part 6)
    return r


def cuts(r, core):
    """cuts (core-views R21, R22): the three cuts and every offer page the CORE holds are as render_blueprint.py
    generated them, each with its provenance record, never edited; each holds every frame section, the thirteen families
    among them; the element cut shows the gap of each held record no step uses; an offer page shows each touchpoint's
    proposals, counts each stream as the package activation derives for it, and names no installed depth"""
    import catalogue  # noqa: E402  (it reads check_core)
    import render_blueprint  # noqa: E402
    try:
        frame = [s for s in render_blueprint.definitions(core, None, render_blueprint.Reading(core))[1] if s["_from"] == "frame"]
    except Exception:                                # a CORE whose models cannot be read: the frame alone, without instances
        frame = [s for s in render_blueprint.definitions(core, None)[1] if s["_from"] == "frame"]
    ids = [s["id"] for s in frame if s.get("cardinality") != "per-family"]   # the frame's sections with their instances (blueprint R9)
    fams = [s["binds"]["slug"] for s in frame if (s.get("binds") or {}).get("kind") == "family" and s["binds"].get("slug")]   # the instances, never the pattern

    def made(text, want, what):
        if want != "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest():
            r.fail("cuts", f"`{what}` is not as its provenance record says it was generated: edited by hand, or rendered without one (CORE-VIEWS R21)")
    folder, name, full = "views/briefing", "briefing", "briefing"   # core-views part 5; `views/blueprint/` the earlier place
    made_here = (yml(os.path.join(core, layout.provenance_dir(core), "briefing", "manifest.json")) or {}).get("generator") == render_blueprint.GENERATOR
    if not made_here:                               # `views/briefing/` holds a view rendered otherwise, or nothing render_blueprint made
        folder, name, full = "views/blueprint", "blueprint", "blueprint"
        if os.path.isdir(os.path.join(core, folder)):
            r.gap("cuts", "the renderings lie at their earlier place `views/blueprint/`: unmigrated; render_blueprint.py writes them into `views/briefing/` (core-views part 5)")
    earlier = folder == "views/blueprint"
    rendered = [f for f in (full, "gaps", "value-model", "entity-model", "element-model")
                if os.path.exists(os.path.join(core, folder, f"{f}.md"))]
    if rendered:
        bm = os.path.join(core, layout.provenance_dir(core), name, "manifest.json")
        outputs = (json.load(open(bm, encoding="utf-8")) if os.path.exists(bm) else {}).get("outputs") or {}
        text = {f: open(os.path.join(core, folder, f"{f}.md"), encoding="utf-8").read() for f in rendered}
        for f in rendered:
            made(text[f], outputs.get(f"{folder}/{f}.md"), f"{folder}/{f}.md")
        for f, need in ((full, [f"`{i}` ·" for i in ids]), ("value-model", [f"`family:{x}`\n" for x in fams])) if not earlier else ():
            missing = [n for n in need if f in text and n not in text[f]]
            if missing:
                r.fail("cuts", f"`{folder}/{f}.md` lacks {len(missing)} frame sections, e.g. {missing[0].strip()}: every cut holds the frame (CORE-VIEWS R21)")
        if "element-model" in text:                  # a held record no step uses shows its gap (R21; MODEL R28)
            rd = render_blueprint.Reading(core)
            lines = text["element-model"].splitlines()
            idle = [k for e in render_blueprint.USED for k in rd.unused(e)
                    if not any(f"`{k}`" in x and "used in no stream of its own" in x for x in lines)]
            if idle:
                r.fail("cuts", f"`{folder}/element-model.md` does not show {len(idle)} held records no step uses, e.g. "
                               f"`{idle[0]}`: a held record no step uses shows its gap (CORE-VIEWS R21)")
    for m in sorted(glob.glob(os.path.join(core, "**", ".provenance", "offer", "manifest.json"), recursive=True) +
                    glob.glob(os.path.join(core, "**", ".build", "offer", "manifest.json"), recursive=True)):
        at = os.path.dirname(os.path.dirname(os.path.dirname(m)))
        page = os.path.join(at, "offer.md")
        rel = os.path.relpath(page, core).replace(os.sep, "/")
        if not os.path.exists(page):
            r.fail("cuts", f"`{os.path.relpath(m, core)}` records an offer page, and `{rel}` is not there")
            continue
        man, text = json.load(open(m, encoding="utf-8")), open(page, encoding="utf-8").read()
        made(text, man.get("output"), rel)
        missing = [f for f in fams if f"`family:{f}`\n" not in text]
        if missing:
            r.fail("cuts", f"`{rel}` lacks {len(missing)} families of the frame, e.g. `{missing[0]}`: the offer page renders the frame (CORE-VIEWS R22)")
        if re.search(r"(depth|deeper)[^.\n]*\binstall|\binstall[^.\n]*(depth|deeper)", text, re.I):
            r.fail("cuts", f"`{rel}` says depth is installed: it is served through the MCP under a grant, never installed (CORE-VIEWS R22)")
        ref, _, version = str(man.get("release") or "").partition("@")
        rd = layout.copy(core, ref) if "/" in ref else None
        if not (rd and str((yml(os.path.join(rd, "release.yml")) or {}).get("version")) == version):
            r.gap("cuts", f"`{rel}` is the page of `{man.get('release')}`, which this CORE does not install: its counts are not read here")
            continue
        offer = render_blueprint.Reading(release=rd)
        tps = sorted(k for k in offer.offered if k.startswith("touchpoint:"))
        shown = {m[1]: len(re.findall(r"`value-stream:", m[2] or "")) for m in
                 re.finditer(r"(?m)^- .*?`(touchpoint:[a-z0-9.-]+)` · (?:proposals: (.*)|no proposal yet)$", text)}
        pro = catalogue.proposals(offer.offered, tps)
        wrong = [k for k in tps if shown.get(k) != len(pro[k])]
        if wrong:
            r.fail("cuts", f"`{rel}` does not show the proposals of {len(wrong)} touchpoints as activation derives them, e.g. "
                           f"`{wrong[0]}`: the offer page shows each touchpoint's proposals (CORE-VIEWS R22)")
        stream = None
        for line in text.splitlines():
            h = re.match(r"^#### .*?`value-stream:([a-z0-9-]+)`", line)
            if h:
                stream = f"value-stream:{h[1]}"
            n = re.match(r"^- \*\*What comes with it:\*\* activating it takes (\d+) records", line)
            if n and stream:
                want = len(catalogue.activation(offer.offered, stream, refers=offer.refers)["take"]) if stream in offer.offered else None
                if want != int(n[1]):
                    r.fail("cuts", f"`{rel}` counts {n[1]} records for `{stream}`, and activation takes {want}: the page counts as activation derives (CORE-VIEWS R22)")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("core")
    ap.add_argument("--structure")
    ap.add_argument("--spec", choices=sorted(SPECS), help="report the findings of one specification only")
    ap.add_argument("--offline", action="store_true", help="read moved parts from local checkouts only")
    ap.add_argument("--bill", action="store_true", help="print the CORE's bill of materials (R37) after the findings")
    a = ap.parse_args()
    rep = check(a.core, a.structure, a.offline)
    items = [i for i in rep.items if not a.spec or i[1] in SPECS[a.spec]]
    n = {o: sum(1 for i in items if i[0] == o) for o in ("fail", "should", "gap")}
    print(f"# {a.core}{' · ' + a.spec if a.spec else ''}: {n['fail']} fail · {n['should']} should · {n['gap']} gap")
    for o, c, t in items:
        print(f"{o}: {c}: {t}")
    if a.bill and getattr(rep, "bill", None) is None:
        print("# no bill: a finding on what the bill lists withholds it (R37)")
    elif a.bill:
        print(yaml.safe_dump({"bill": rep.bill}, sort_keys=False, allow_unicode=True), end="")
    return 1 if n["fail"] else 0


if __name__ == "__main__":
    sys.exit(main())
