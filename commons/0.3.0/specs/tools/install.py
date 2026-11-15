#!/usr/bin/env python3
"""install.py — a commons installs a released extension in one step, whole and read-only (extension.md R12).

The release is given as its folder or as its zip, as a library publishes it. The copy is staged inside the CORE and
checked by the gate's code of a release copy, the one code that checks a copy wherever it lies (`library` R9), against
the record digest the library gives for the release (--expect). Only when that check passes does the copy move to
`models/commons/<library>/<model>/` (`extensions/<library>/<extension>/` in a CORE that still holds its copies there,
`layout.copy_target`), and the lock `.commons/lock.yml` record it with its origin, its record digest and
which of its parts are installed and which served. On any failure nothing is written.

Installing writes nothing into the registry: what a commons makes its own is activated afterwards
(`build.py`). It names the extension in `.commons/commons.yml` where the commons does not pin it yet, and an
extension of the commons' kind becomes its primary in place of Commons Essentials (R9, CORE R1); the agent file is
generated again from what changed (CORE R36). A pin at another
version, or an extension already installed, is an update and is taken with `take_update.py`.

A variant (its record names `variant`, MODEL R30) is installed in `models/commons/<library>/<model>/<variant>/`, beside
the other variants of its domain (CORE R39), and pinned and locked with its `variant`. A second variant of a domain
the commons already pins is no update and becomes no primary: the commons grows into it by a take-up (`build.py`).

The origin is the library's address in `libraries:` at the release's tag `<extension>-<version>`, unless --origin
names it.

An extract of patterns (LIBRARY-PATTERNS R17) is installed the same way, whole and read-only, checked against its
record digest (CORE R28): it moves to `patterns/commons/<library>/`, the lock records it under `patterns` as
`{path, origin, record}`, its origin the release its index names, and the graph's register `graph/sources.yml`, where
the CORE has one, gains it as a source pinned by the lock (`graph` R3). Nothing of the commons' settings changes. A
CORE holds one extract per library; a newer one is taken up by decision (R28), never installed over it.

`--take-up` takes a newer release of a model the commons installed, the Commons model's among them: by the commons'
decision, on a working branch, the new copy is checked as at install and takes the place of the installed one, which
git keeps in the history, and the lock and the pin name the newer version (CORE R39). It writes nothing into the
runtime: a record built from the older release is taken up record by record with `take_update.py`, whose `--from` is
the older release in the library. A release no newer than the one installed is refused.

Usage:  install.py CORE --from FOLDER|ZIP --expect sha256:... [--origin owner/repo@rev[:path]] [--take-up]
"""
import argparse
import itertools
import re
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True   # the tools never write into the install they lie in (SPECIFICATION R29; `extension` R12)
sys.path.insert(0, HERE)
import check_library  # noqa: E402
import layout  # noqa: E402
from check_core import LOCK, Report  # noqa: E402

COMMONS = os.path.join(".commons", "commons.yml")
HEAD = "# generated: what this CORE installed, with the record digest the library's index gives (LIBRARY R9)\n"


def yml(p):
    return yaml.safe_load(open(p, encoding="utf-8")) if os.path.exists(p) else None


def settle(p, cfg):
    """commons.yml with its pins and libraries as `cfg` holds them, changed in place: the block of the pins and the
    libraries' lines are written anew, every other line, comment and order kept; where the file cannot be read so, it
    is written whole, its opening comment kept"""
    text = open(p, encoding="utf-8").read() if os.path.exists(p) else ""
    lines = text.splitlines(True)
    key = layout.pin_key(cfg)

    def block(name):                             # (start, end) of a top-level key's block, or None
        for i, l in enumerate(lines):
            if re.match(rf"{re.escape(name)}:(\s|$)", l):
                j = i + 1
                while j < len(lines) and (not lines[j].strip() or lines[j][:1] in " \t-#"):
                    j += 1
                return i, j
        return None

    def comment(l):
        m = re.search(r"\s(#.*)$", l.rstrip("\n"))
        return f"   {m[1]}" if m else ""

    pins = yaml.safe_dump(cfg.get(key) or [], sort_keys=False, allow_unicode=True, width=120)
    at = block(key)
    if at:
        i, j = at
        body = "\n" if not cfg.get(key) else "\n" + pins
        new = [f"{key}:{' []' if not cfg.get(key) else ''}{comment(lines[i])}{body}"]
        lines[i:j] = new
    else:
        lines.append(f"{key}:\n{pins}")
    libs = cfg.get("libraries") or {}
    at = block("libraries")
    if at:
        i, j = at
        have = {m[1]: k for k in range(i + 1, j) for m in [re.match(r"\s+([^:#\s]+):", lines[k])] if m}
        for lib, address in libs.items():
            if lib not in have:
                lines.insert(j, f"  {lib}: {address}\n")
                j += 1
    elif libs:
        lines.append("libraries:\n" + "".join(f"  {k}: {v}\n" for k, v in libs.items()))
    out = "".join(lines)
    if not out.endswith("\n"):
        out += "\n"
    try:
        same = yaml.safe_load(out) == cfg
    except yaml.YAMLError:
        same = False
    if not same:                                 # an unusual layout: written whole, its opening comment kept
        head = "".join(itertools.takewhile(lambda x: x.startswith("#"), text.splitlines(True)))
        return dump(p, cfg, head)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(out)


def dump(p, d, head=""):
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(head)
        yaml.safe_dump(d, f, sort_keys=False, allow_unicode=True, width=120)


def unpack(src, into):
    """a zip unpacked as it is, every member inside the folder; a folder copied as it is"""
    if os.path.isdir(src):
        shutil.copytree(src, into)
        return
    with zipfile.ZipFile(src) as z:
        for n in z.namelist():
            if os.path.isabs(n) or ".." in n.replace("\\", "/").split("/"):
                sys.exit(f"nothing installed: `{n}` in the zip lies outside the release")
        z.extractall(into)


def agent(core, wrote):
    """the agent file follows what it is generated from, in the same step (CORE R36); where it cannot, it is said"""
    run = subprocess.run([sys.executable, os.path.join(HERE, "make_agent.py"), core], capture_output=True, text=True)
    if run.returncode == 0:
        wrote.append("AGENT.md")
    else:
        why = ((run.stderr or run.stdout).strip().splitlines() or ["make_agent.py failed"])[-1]
        print(f"note: AGENT.md was not generated again ({why}); run make_agent.py", file=sys.stderr)


def install_extract(core, copy, rec, expect, origin=None):
    """an extract of patterns installed under `patterns/commons/<library>/` (CORE R28); returns (report, what was written)"""
    lib, version = rec.get("library"), str(rec.get("version"))
    if not lib:
        sys.exit("nothing installed: the release record names no library (LIBRARY R3)")
    cfg = yml(os.path.join(core, COMMONS))
    if cfg is None:
        sys.exit(f"nothing installed: `{core}` has no `{COMMONS}` (CORE R1)")
    pd = (cfg.get("locations") or {}).get("patterns") or "patterns"
    path = f"commons/{lib}"
    at = os.path.join(core, pd, "commons", lib)
    lock = yml(os.path.join(core, LOCK)) or {}
    if os.path.exists(at) or any(isinstance(e, dict) and e.get("path") == path for e in lock.get("patterns") or []):
        sys.exit(f"nothing installed: an extract of `{lib}` is installed already; a newer one is taken up by decision (CORE R28)")
    reg_p = os.path.join(core, "graph", "sources.yml")
    reg = yml(reg_p) if os.path.isfile(reg_p) else None
    ref = f"{pd}/{path}/"
    sources = (reg or {}).get("sources") or []
    if any(isinstance(e, dict) and e.get("id") == lib and e.get("ref") != ref for e in sources):
        sys.exit(f"nothing installed: the register names a source `{lib}` at another place (graph R2)")
    head = {}
    if os.path.isfile(os.path.join(copy, "index.jsonl")):
        head = json.loads(next((x for x in open(os.path.join(copy, "index.jsonl"), encoding="utf-8") if x.strip()), "{}"))
    origin = origin or head.get("release")
    if not origin:
        sys.exit("nothing installed: the extract's index names no release, and --origin gives none (CORE R28)")
    r = Report()
    check_library.check_copy(r, copy, copy, f"`{lib}` {version}", expect=expect)
    if any(o == "fail" for o, _, _ in r.items):
        return r, []
    # the check passed: the copy moves into place, then the lock and the register follow it
    os.makedirs(os.path.dirname(at), exist_ok=True)
    shutil.move(copy, at)
    wrote = [os.path.relpath(at, core)]
    lock.setdefault("patterns", []).append({"path": path, "origin": origin, "record": expect})
    dump(os.path.join(core, LOCK), lock, HEAD)
    wrote.append(LOCK)
    if reg is not None and not any(isinstance(e, dict) and e.get("ref") == ref for e in sources):
        part = (rec.get("parts") or {}).get("patterns") or {}
        sources.append({"id": lib, "kind": "patterns", "ref": ref, "class": part.get("class") or "public", "pin": "lock"})
        reg["sources"] = sources
        top = "".join(itertools.takewhile(lambda x: x.startswith("#"), open(reg_p, encoding="utf-8").read().splitlines(True)))
        dump(reg_p, reg, top)
        wrote.append(os.path.join("graph", "sources.yml"))
    agent(core, wrote)
    return r, wrote


def newer(a, b):
    """whether version `a` comes after `b`, a candidate before its release"""
    key = lambda v: tuple(int(x) for x in str(v).split("-rc.")[0].split(".")) + ((0, int(str(v).split("-rc.")[1])) if "-rc." in str(v) else (1, 0))
    return key(a) > key(b)


def take_up(core, copy, rec, expect, origin=None):
    """a newer release in place of the installed copy, its lock entry and pin (CORE R39); returns (report, written)"""
    lib, ext, version, variant = rec.get("library"), layout.release_id(rec), str(rec.get("version")), rec.get("variant")
    ref = layout.ref_of({"id": f"{lib}/{ext}", "variant": variant})
    lock_p, cfg_p = os.path.join(core, LOCK), os.path.join(core, COMMONS)
    lock, cfg = yml(lock_p) or {}, yml(cfg_p) or {}
    entry = next((e for e in layout.pins(lock) if layout.canonical(layout.ref_of(e)) == layout.canonical(ref)), None)
    at = layout.copy(core, ref)
    if entry is None or not os.path.isdir(at):
        sys.exit(f"nothing taken up: `{ref}` is not installed; a first release is installed without --take-up")
    if not newer(version, entry.get("version")):
        sys.exit(f"nothing taken up: `{ref}` is installed at {entry.get('version')}, and {version} is not newer (CORE R39)")
    r = Report()
    check_library.check_copy(r, copy, copy, f"`{ref}` {version}", expect=expect)
    if any(o == "fail" for o, _, _ in r.items):
        return r, []
    def writable(fn, p, _):
        os.chmod(p, 0o666)
        fn(p)
    shutil.rmtree(at, onerror=writable)              # git keeps the older copy in the history
    shutil.move(copy, at)
    address = (cfg.get("libraries") or {}).get(lib)
    tag = f"{ext}-{variant}-{version}" if variant else f"{ext}-{version}"
    parts = rec.get("parts") or {}
    entry.update({"id": f"{lib}/{ext}", "version": version, "origin": origin or (f"{address}@{tag}" if address else entry.get("origin")), "record": expect,
                  "installed": [n for n, p in parts.items() if isinstance(p, dict) and p.get("class") == "public"],
                  "served": [n for n, p in parts.items() if isinstance(p, dict) and p.get("class") != "public"]})
    dump(lock_p, lock, HEAD)
    for x in layout.pins(cfg):
        if layout.canonical(layout.ref_of(x)) == layout.canonical(ref) or (x.get("id") in layout.ESSENTIALS and ext in layout.ESSENTIALS):
            x["version"] = version
            x["id"] = f"{lib}/{ext}" if "/" in str(x.get("id")) else ext   # the pin follows the newer id (F-a)
    settle(cfg_p, cfg)                           # in place: the commons' comments and order kept
    wrote = [os.path.relpath(at, core), LOCK, COMMONS]
    agent(core, wrote)
    return r, wrote


def pinned(x, domain, ext, variant=None):
    """whether a pin or a lock entry `x` names the model `domain` (`<library>/<model>`) and its variant, under its id or
    the id alone, the Commons model under its earlier id `commons-essentials` too (CORE part 5)"""
    return isinstance(x, dict) and x.get("variant") == variant and (x.get("id") in (domain, ext) or (
        ext in layout.ESSENTIALS and str(x.get("id") or "").split("/")[-1] in layout.ESSENTIALS))


def install(core, src, expect, origin=None, take=False):
    """returns the report of the check of the copy and what was written; nothing is written where it fails"""
    stage = tempfile.mkdtemp(prefix=".install-", dir=core)
    copy = os.path.join(stage, "copy")
    try:
        unpack(src, copy)
        rec = yml(os.path.join(copy, "release.yml")) or {}
        if rec.get("kind") == "extract":
            return install_extract(core, copy, rec, expect, origin)
        if take:
            return take_up(core, copy, rec, expect, origin)
        lib, ext, version = rec.get("library"), layout.release_id(rec), str(rec.get("version"))
        if not layout.is_model(rec) or not lib or not ext:
            sys.exit("nothing installed: the release record names no extension of a library (LIBRARY R3)")
        variant = rec.get("variant")
        domain = f"{lib}/{ext}"
        ref = layout.ref_of({"id": domain, "variant": variant})
        at = layout.copy_target(core, ref)
        cfg = yml(os.path.join(core, COMMONS))
        if cfg is None:
            sys.exit(f"nothing installed: `{core}` has no `{COMMONS}` (CORE R1)")
        lock = yml(os.path.join(core, LOCK)) or {}
        same = lambda x: pinned(x, domain, ext, variant)
        if os.path.exists(at) or os.path.exists(layout.copy(core, ref)) or any(same(e) for e in layout.pins(lock)):
            sys.exit(f"nothing installed: `{ref}` is installed already; a newer release is taken up with --take-up, its records with take_update.py")
        if variant and os.path.isfile(os.path.join(os.path.dirname(at), "release.yml")):
            sys.exit(f"nothing installed: `{domain}` is installed as a model without variants; its variant `{variant}` cannot stand beside it (CORE R39)")
        pins = [x for x in layout.pins(cfg) if same(x)]
        repin = None
        if pins and (str(pins[0].get("version")) != version or pins[0].get("id") != domain):
            # nothing of it is installed (above): the pin names a release this CORE never installed, so this is the
            # first installation, and the pin follows the release
            repin = f"{pins[0].get('id')} {pins[0].get('version')} was pinned and never installed; the pin now names {domain} {version}"
        address = (cfg.get("libraries") or {}).get(lib)
        if str(address or "").lower() == "commons-engineering/commons-core" and lib == "commons-engineering":
            print(f"hint: the library `{lib}` is cloudsters/federation.library; `libraries:` in {COMMONS} still names "
                  f"Commons-Engineering/commons-core, the commons' own setting to change")
        if not origin and not address:
            sys.exit(f"nothing installed: the CORE names no library `{lib}` in `libraries:`, and --origin gives none (R12)")
        r = Report()
        check_library.check_copy(r, copy, copy, f"`{ref}` {version}", expect=expect)
        if any(o == "fail" for o, _, _ in r.items):
            return r, []
        # the check passed: the copy moves into place, then the settings and the lock follow it
        os.makedirs(os.path.dirname(at), exist_ok=True)
        shutil.move(copy, at)
        wrote = [os.path.relpath(at, core)]
        parts = rec.get("parts") or {}
        tag = f"{ext}-{variant}-{version}" if variant else f"{ext}-{version}"
        entry = {"id": domain, **({"variant": variant} if variant else {}), "version": version,
                 "origin": origin or f"{address}@{tag}", "record": expect,
                 "installed": [n for n, p in parts.items() if isinstance(p, dict) and p.get("class") == "public"],
                 "served": [n for n, p in parts.items() if isinstance(p, dict) and p.get("class") != "public"]}
        lock.setdefault(layout.pin_key(cfg), []).append(entry)   # the lock speaks as commons.yml does
        dump(os.path.join(core, LOCK), lock, HEAD)
        wrote.append(LOCK)
        changed = False
        if repin:
            pins[0]["id"], pins[0]["version"] = domain, version
            if ext in layout.ESSENTIALS:
                pins[0].pop("primary", None)          # the Commons model is never a primary (CORE R1)
            for x in pins[1:]:                         # one pin of it, never a second beside the first
                cfg[layout.pin_key(cfg)].remove(x)
            print(f"pin: {repin}")
            changed = True
        elif not pins:
            pin = {"id": domain, **({"variant": variant} if variant else {}), "version": version}
            grows = any(x.get("id") in (domain, ext) for x in layout.pins(cfg))   # another variant of its domain is pinned
            if ext not in layout.ESSENTIALS and not grows:   # the extension of the commons' kind is its primary (R9)
                for x in layout.pins(cfg):
                    if isinstance(x, dict):
                        x.pop("primary", None)
                pin["primary"] = True
            cfg.setdefault(layout.pin_key(cfg), []).append(pin)
            changed = True
        if not address:
            cfg.setdefault("libraries", {})[lib] = origin.split("@", 1)[0]
            changed = True
        if changed:                                  # in place: the commons' comments and order kept
            settle(os.path.join(core, COMMONS), cfg)
            wrote.append(COMMONS)
        agent(core, wrote)
        return r, wrote
    finally:
        shutil.rmtree(stage, ignore_errors=True)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("core")
    ap.add_argument("--from", dest="src", required=True)
    ap.add_argument("--expect", required=True, help="the record digest the library gives for the release")
    ap.add_argument("--origin")
    ap.add_argument("--take-up", action="store_true", help="a newer release in place of the installed one (CORE R39)")
    a = ap.parse_args()
    r, wrote = install(a.core, a.src, a.expect, a.origin, a.take_up)
    for o, c, t in r.items:
        if o == "fail":
            print(f"{o}: {c}: {t}")
    if not wrote:
        print("# nothing installed: the copy does not pass the check of a release copy")
        return 1
    for w in wrote:
        print(f"# wrote {w.replace(os.sep, '/')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
