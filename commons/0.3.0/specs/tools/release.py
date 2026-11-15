#!/usr/bin/env python3
"""release.py — a maker releases a version of its model into a library, generated from its release event and never
written by hand (LIBRARY R3, R6, R19).

The source is the maker's repository at a clean commit that holds the release event,
`lifecycle/events/<date>-release-<extension>-<version>.yml`, a `decision` that names the version. The copy is:
- profile `specifications`, the source being `commons.core`: its `specs/` without the checks' own tests, and `LICENSES/`;
- a model, the source being a CORE that makes one: its emulation `models/emulation/<model>/` (`--model`, else the
  only one; `offer/` its earlier place), copied as `model.yml`, the element folders, `loops/` and `specs/`, with the
  attribution list `sources.yml` generated from the sources its records bind, the model's blueprint sections
  `views/blueprint.yml` derived from its records; its licence `CC-BY-SA-4.0` unless `--licence` names another (LIC), a
  `LicenseRef-` carrying its text in `LICENSES/`; the record names its `source`, the emulation at the commit, and the
  Commons model it is `written_in`. The depth is part of the model and goes with it (MODEL part 5).
  A release is always cut from an emulation, never from a runtime (R19).
- a variant (`model.yml` with `variant`, MODEL R30): a release of its own in `<model>/<variant>/<version>/`, its
  record and its index line naming the `variant`, its release event
  `lifecycle/events/<date>-release-<model>-<variant>-<version>.yml`.

A release has one part, `model` (`essentials` its earlier name), with its class and digest (LIBRARY part 5). The
`retires` its release event names go into the record as they stand, and what is retired from today on is `retired`
in the index (R4, R6).

The gate runs on the source (the catalogue and research checks of the model) and on the copy (check_library's check of a release copy);
the record says `gate.result: pass` only when both pass, and where either fails nothing is written. The library's index
gains the release's line, in the state `candidate` for a `-rc.N` version and `released` otherwise.

An extract (`--extract RUN --policy FILE`, LIBRARY-PATTERNS R17) is cut by `extract.py` from the source's stock and
its released graph run into `patterns/<version>/`: the patterns at their release paths and `index.jsonl`; its record
names the run, the extractor, the policy, the scope and the digest of the index, its one part `patterns`. Its
release event is `lifecycle/events/<date>-release-patterns-<version>.yml`; the `retires` it names, `[{id, from}]`,
go into the record as they stand, and so end earlier versions by a date (R4); one retired from today on is `retired`
in the index.

Usage:  release.py SOURCE --version V --into LIBRARY [--model NAME] [--licence LicenseRef-x --licence-file FILE] [--answers owner/repo]
        release.py SOURCE --version vYYYY.M.N --into LIBRARY --extract RUN --policy FILE [--names FILE] [--terms FILE] [--answers owner/repo]
"""
import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True   # the tools never write into the install they lie in (SPECIFICATION R29; `extension` R12)
sys.path.insert(0, HERE)
import check_library  # noqa: E402
import layout  # noqa: E402
from check_core import Report  # noqa: E402

COPIED = ("loops", "specs")                           # of a model's folder, beside its file and its records; `views/` is derived
PART = "model"                                        # a release's one part (LIBRARY part 5); `essentials` its earlier name


def yml(p):
    return yaml.safe_load(open(p, encoding="utf-8")) if os.path.exists(p) else None


def dump(p, d, head=""):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(head)
        yaml.safe_dump(d, f, sort_keys=False, allow_unicode=True, width=120)


def git(d, *args):
    out = subprocess.run(["git", "-C", d, *args], capture_output=True, text=True)
    return out.stdout.strip() if out.returncode == 0 else None


def origin(d):
    """`owner/repo@rev` of the repository a folder lies in"""
    remote = (git(d, "remote", "get-url", "origin") or "").removesuffix(".git").rstrip("/")
    repo = "/".join(remote.replace(":", "/").split("/")[-2:]) if remote else os.path.basename(os.path.abspath(d))
    return f"{repo}@{git(d, 'rev-parse', '--short=7', 'HEAD')}"


def tool():
    """the gate's path in the repository it lies in, wherever that copy of the tools lies (a library's copy included)"""
    prefix = git(HERE, "rev-parse", "--show-prefix")
    return f"{prefix}check_library.py" if prefix is not None else "specs/tools/check_library.py"


def sections(src, copy, ext):
    """the extension's blueprint sections, derived at release (the run's forms, part E, definition 2): one per value
    stream within its family's frame section, one per entity within `element.entity`; the maker's
    `offer/views/blueprint.yml` sets only their order and labels"""
    dims = json.load(open(os.path.join(HERE, "..", "schemas", "model.schema.json"), encoding="utf-8"))["x-dimension-of"]
    import catalogue  # noqa: E402
    made = {x.get("id"): x for x in (yml(os.path.join(catalogue.emulation_of(src), "views", "blueprint.yml")) or {}).get("sections") or [] if isinstance(x, dict)}
    out = []
    for f in sorted(glob.glob(os.path.join(layout.records(copy), "*", "*.y*ml"))):
        rec = yml(f) or {}
        kind, slug = rec.get("kind"), rec.get("slug")
        if kind == "value-stream" and rec.get("family") in dims:
            sid, within = f"{ext}.value-stream.{slug}", f"{dims[rec['family']]}.{rec['family']}"
        elif kind == "entity":
            sid, within = f"{ext}.entity.{slug}", "element.entity"
        else:
            continue
        out.append({"id": sid, "within": within, "binds": {"kind": kind, "slug": slug}, "cardinality": "one",
                    "labels": (made.get(sid) or {}).get("labels") or {"en": rec.get("title") or slug}})
    rank = {k: n for n, k in enumerate(made)}
    out.sort(key=lambda x: (x["within"], rank.get(x["id"], len(rank)), x["id"]))
    return {"sections": out}


def attribution(src, copy):
    """the attribution list (R31): each source the copy's records bind, with its designation, edition, jurisdiction and
    relation from the maker's research, never the research behind them"""
    research = {s.get("id"): s for s in (yml(os.path.join(src, "knowledge", "sources.yml")) or {}).get("sources") or [] if isinstance(s, dict)}
    bound = set()
    for f in glob.glob(os.path.join(layout.records(copy), "*", "*.y*ml")):
        for b in (yml(f) or {}).get("binds") or []:
            if isinstance(b, dict) and b.get("source"):
                bound.add(b["source"])
    return {"sources": [{k: research[s][k] for k in ("id", "designation", "edition", "jurisdiction", "relation") if k in research[s]}
                        for s in sorted(bound) if s in research]}


DOMAIN_LICENCE = "CC-BY-SA-4.0"   # a domain model's licence unless the release names another (Holger, commons.core#110 6885637782, LIC)


def release(src, version, into, licence=None, licence_file=None, answers=None, model=None):
    """returns (report, folder written or None)"""
    r = Report()
    lib = yml(os.path.join(into, "library.yml")) or {}
    if not lib.get("id"):
        sys.exit(f"`{into}` is no library: no `library.yml` with an `id` (LIBRARY R1)")
    import catalogue  # noqa: E402
    emu = catalogue.emulation_of(src, model)
    specifications = os.path.isfile(os.path.join(src, "specs", "structure.yml")) and not os.path.isdir(emu)
    if specifications:
        ext = check_library.ESSENTIALS
    else:
        cfg = yml(os.path.join(src, ".commons", "commons.yml")) or {}
        offer = yml(layout.model_file(emu)) or {}
        ext = offer.get("id") or str(cfg.get("id", "")).removesuffix(".core")
    variant = None if specifications else layout.variant_of(emu)    # a variant is a release of its own (MODEL R30)
    name = f"{ext}-{variant}" if variant else ext
    rev = git(src, "rev-parse", "HEAD")
    if rev is None:
        sys.exit(f"`{src}` is no git repository: a release names the commit it is made from (R3)")
    if git(src, "status", "--porcelain", "--untracked-files=no"):
        sys.exit(f"`{src}` has changes not committed: a release is made from a commit, never from a working copy (R3)")
    event = next((p for p in sorted(glob.glob(os.path.join(src, "lifecycle", "events", f"*-release-{name}-{version}.yml")))), None)
    ev = yml(event) if event else None
    if not (isinstance(ev, dict) and ev.get("kind") == "decision"):
        sys.exit(f"`{src}` holds no release event `lifecycle/events/<date>-release-{name}-{version}.yml` at {rev[:7]}: "
                 f"the maker decides the release first, and the record is generated from it (R3)")
    repo = origin(src).split("@")[0]
    base = os.path.join(into, ext, *([variant] if variant else []))
    out = os.path.join(base, version)
    if os.path.exists(out):
        sys.exit(f"`{os.path.relpath(out, into)}` exists: a released version is never changed (LIBRARY R4)")
    stage = tempfile.mkdtemp(prefix=".release-", dir=into)
    copy = os.path.join(stage, "copy")
    try:
        os.makedirs(copy)
        if specifications:
            shutil.copytree(os.path.join(src, "specs"), os.path.join(copy, "specs"),
                            ignore=lambda d, names: ["tests"] if os.path.normpath(d) == os.path.normpath(os.path.join(src, "specs", "tools")) else [])
        else:
            gate = catalogue.check(src, model=model)
            for o, c, t in gate.items:
                if o == "fail":
                    r.fail(c, f"the source: {t}")
            earlier = os.path.basename(os.path.normpath(emu)) == "offer"
            shutil.copy2(layout.model_file(emu), os.path.join(copy, "offer.yml" if earlier else "model.yml"))
            recs = layout.records(emu)
            for e in sorted(os.listdir(recs)):           # the record folders, directly in the copy (CORE R6)
                if os.path.isdir(os.path.join(recs, e)) and e in layout.record_folders():
                    shutil.copytree(os.path.join(recs, e), os.path.join(copy, "registry" if earlier else "", e))
            for x in COPIED:
                p = os.path.join(emu, x)
                if os.path.isdir(p):
                    shutil.copytree(p, os.path.join(copy, x))
            for p in layout.depth_files(emu):           # the depth, part of the model, where its files lie (MODEL part 5)
                os.makedirs(os.path.dirname(os.path.join(copy, os.path.relpath(p, emu))), exist_ok=True)
                shutil.copy2(p, os.path.join(copy, os.path.relpath(p, emu)))
            dump(os.path.join(copy, "sources.yml"), attribution(src, copy), "# the attribution list (extension R31), generated at release\n")
            dump(os.path.join(copy, "views", "blueprint.yml"), sections(src, copy, ext),
                 "# the extension's blueprint sections (the run's forms, part E), derived at release; never edited by hand\n")
        licence = licence or ("LicenseRef-commons-engineering" if specifications else DOMAIN_LICENCE)   # every domain model CC BY-SA 4.0 (LIC)
        if licence.startswith("LicenseRef-"):
            text = licence_file or os.path.join(src, "LICENSE")
            os.makedirs(os.path.join(copy, "LICENSES"))
            shutil.copy2(text, os.path.join(copy, "LICENSES", f"{licence}.txt"))
        parts = {PART: {"class": "public", "digest": check_library.part_digest(copy)}}
        earlier = sorted(glob.glob(os.path.join(base, "*", "release.yml")))
        last = ((yml(earlier[-1]) or {}).get("parts") or {}) if earlier else {}
        changed = [n for n, p in parts.items() if (last.get(n) or last.get("essentials") or {}).get("digest") != p["digest"]]
        mine = layout.pins(yml(os.path.join(src, ".commons", "lock.yml")) or {}) or layout.pins(cfg if not specifications else {})
        grammar = next((f"{x['id'].split('/')[0] if '/' in str(x['id']) else 'commons-engineering'}/commons@{x.get('version')}"
                        for x in mine if str(x.get("id")).split("/")[-1] in layout.ESSENTIALS), None)   # an unqualified pin: the first tier
        rel = {"kind": "model", "model": ext, **({"variant": variant} if variant else {}),
               **({} if specifications else {"source": f"{repo}@{rev}:{os.path.relpath(emu, src).replace(os.sep, '/')}"}),
               **({"written_in": grammar} if grammar and not specifications else {}),
               "library": lib["id"], "version": version, "made_in": f"{repo}@{rev}",
               "event": f"{repo}@{rev}:{os.path.relpath(event, src).replace(os.sep, '/')}",
               "gate": {"result": "pass", "check": f"{origin(HERE)}:{tool()}"},
               "changed": changed or list(parts), "parts": parts, "licence": licence,
               "answers": answers or repo, "renames": (ev.get("renames") or {})}
        if ev.get("retires"):                          # the event ends earlier versions or records by a date (R4)
            rel["retires"] = ev["retires"]
        dump(os.path.join(copy, "release.yml"), rel, "# generated from the release event of its source (library R3); never edited by hand\n")
        check_library.check_copy(r, copy, copy, f"`{layout.ref_of({'id': ext, 'variant': variant})}` {version}")
        if any(o == "fail" for o, _, _ in r.items):
            return r, None
        os.makedirs(os.path.dirname(out), exist_ok=True)
        shutil.move(copy, out)
    finally:
        shutil.rmtree(stage, ignore_errors=True)
    idx_p = os.path.join(into, "index.yml")
    idx = yml(idx_p) or {}
    idx.setdefault("releases", []).append({
        "id": ext, **({"variant": variant} if variant else {}), "kind": "model", "version": version,
        "record": os.path.relpath(os.path.join(out, "release.yml"), into).replace(os.sep, "/"),
        "digest": f"sha256:{check_library.sha(open(os.path.join(out, 'release.yml'), 'rb').read())}",
        "state": "candidate" if "-rc." in version else "released"})
    for e in idx["releases"]:   # what this record retires from today on is `retired` in the index (R4, R6)
        if check_library.state_of(layout.ref_of(e), str(e.get("version")), [rel], check_library.datetime.date.today()) == "retired":
            e["state"] = "retired"
    dump(idx_p, idx, "# generated from the release records (library.md R6); never edited by hand\n")
    return r, out


def release_extract(src, version, into, run, policy, answers=None, names=None, terms=None):
    """an extract released from the source's stock and one released run (LIBRARY-PATTERNS R17); returns (report, folder or None)"""
    import extract  # noqa: E402
    r = Report()
    lib = yml(os.path.join(into, "library.yml")) or {}
    if not lib.get("id"):
        sys.exit(f"`{into}` is no library: no `library.yml` with an `id` (LIBRARY R1)")
    rev = git(src, "rev-parse", "HEAD")
    if rev is None or git(src, "status", "--porcelain", "--untracked-files=no"):
        sys.exit(f"`{src}` is not at a clean commit: a release is made from a commit, never from a working copy (R3)")
    event = next(iter(sorted(glob.glob(os.path.join(src, "lifecycle", "events", f"*-release-patterns-{version}.yml")))), None)
    if not (event and (yml(event) or {}).get("kind") == "decision"):
        sys.exit(f"`{src}` holds no release event `lifecycle/events/<date>-release-patterns-{version}.yml` at {rev[:7]} (R3)")
    repo, out = origin(src).split("@")[0], os.path.join(into, "patterns", version)
    if os.path.exists(out):
        sys.exit(f"`{os.path.relpath(out, into)}` exists: a released version is never changed (LIBRARY R4)")
    stage = tempfile.mkdtemp(prefix=".release-", dir=into)
    copy = os.path.join(stage, "copy")
    try:
        pol = os.path.relpath(os.path.abspath(policy), os.path.abspath(src)).replace(os.sep, "/")
        lines, left, general, count = extract.cut(src, run, policy, copy, f"{origin(into).split('@')[0]}@{version}",
                                           policy_ref=f"{repo}@{rev[:7]}:{pol}", lid=lib["id"], names=names, terms=terms)
        for t in general:
            r.fail("extract", f"the source: {t}")
        head = lines[0]
        rel = {"kind": "extract", "library": lib["id"], "version": version, "made_in": f"{repo}@{rev}",
               "event": f"{repo}@{rev}:{os.path.relpath(event, src).replace(os.sep, '/')}",
               "gate": {"result": "pass", "check": f"{origin(HERE)}:{tool()}"},
               "graph_run": run, "extractor": head["extractor"], "policy": head["policy"], "scope": head["scope"],
               "count": count,
               "digest": f"sha256:{check_library.sha(open(os.path.join(copy, 'index.jsonl'), 'rb').read())}",
               "parts": {"patterns": {"class": "public", "digest": check_library.part_digest(copy)}},
               "licence": head["licence"], "answers": answers or repo}
        if (yml(event) or {}).get("retires"):   # the event ends earlier versions by a date (R4)
            rel["retires"] = yml(event)["retires"]
        dump(os.path.join(copy, "release.yml"), rel, "# generated from the release event of its source (library R3); never edited by hand\n")
        check_library.check_copy(r, copy, copy, f"`patterns` {version}", names, terms)
        check_library.check_extract(r, lib["id"], copy, rel, f"`patterns` {version}")
        if any(o == "fail" for o, _, _ in r.items):
            return r, None
        os.makedirs(os.path.dirname(out), exist_ok=True)
        shutil.move(copy, out)
    finally:
        shutil.rmtree(stage, ignore_errors=True)
    idx_p = os.path.join(into, "index.yml")
    idx = yml(idx_p) or {}
    idx.setdefault("releases", []).append({
        "id": "patterns", "kind": "extract", "version": version, "record": f"patterns/{version}/release.yml",
        "digest": f"sha256:{check_library.sha(open(os.path.join(out, 'release.yml'), 'rb').read())}",
        "state": "candidate" if "-rc." in version else "released"})
    for e in idx["releases"]:   # what this record retires from today on is `retired` in the index (R4, R6)
        if check_library.state_of(e.get("id"), str(e.get("version")), [rel], check_library.datetime.date.today()) == "retired":
            e["state"] = "retired"
    dump(idx_p, idx, "# generated from the release records (library.md R6); never edited by hand\n")
    return r, out


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("--version", required=True)
    ap.add_argument("--into", required=True)
    ap.add_argument("--licence")
    ap.add_argument("--licence-file")
    ap.add_argument("--answers")
    ap.add_argument("--model")
    ap.add_argument("--extract", metavar="RUN")
    ap.add_argument("--policy")
    ap.add_argument("--names")
    ap.add_argument("--terms")
    a = ap.parse_args()
    if a.extract:
        if not a.policy:
            sys.exit("--extract needs --policy: the extract is cut under a policy (LIBRARY-PATTERNS R17)")
        r, out = release_extract(a.source, a.version, a.into, a.extract, a.policy, a.answers,
                                 check_library.wordlist(a.names), check_library.wordlist(a.terms))
    else:
        r, out = release(a.source, a.version, a.into, a.licence, a.licence_file, a.answers, a.model)
    for o, c, t in r.items:
        if o == "fail":
            print(f"{o}: {c}: {t}")
    if out is None:
        print("# nothing released: the gate does not pass")
        return 1
    rec = os.path.join(out, "release.yml")
    print(f"# released {os.path.relpath(out, a.into).replace(os.sep, '/')}, record sha256:{check_library.sha(open(rec, 'rb').read())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
