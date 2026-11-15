#!/usr/bin/env python3
"""migrate_core.py — move a CORE from structure 0.3.0 to 0.4.0 in one run (CORE R4, R6, R18, R39; `structure.yml`
0.4.0; commons.o#110). A help: it prints what it would do, and does it only with `--apply`.

What moves, each to the place the structure definition gives it, with `git mv` inside a work tree:
- `registry/<element>/` into `models/runtime/<element>/`;
- `operations/loops/` into `models/runtime/loops/`, its `_state/` into `models/runtime/state/`;
- `operations/loops/_contract.yml` and `operations/rhythms.md`, which dissolve, into `workshop/_migration/`, kept and
  reported, never deleted;
- `extensions/<library>/<extension>/` into `models/commons/<library>/<model>/`, Commons Essentials into
  `models/commons/<library>/commons/`; an installed copy is moved whole and never changed, since its digest is its
  release's (LIBRARY R9);
- `offer/` into `models/emulation/<id>/`, its `offer.yml` as `model.yml` and the element folders of its `registry/`
  directly in the emulation's folder;
- `.build/` into `.provenance/`;
- an installed pattern extract `patterns/<library>/` into `patterns/commons/<library>/`.

What is renamed: in `commons.yml` the key `extensions` as `models`, `structure` as 0.4.0 and the keys of `locations`;
in the lock `extensions` as `models` and an extract's `path`; in both the Commons model's earlier id
`commons-essentials` as `commons`, with its folder, also in a CORE already on 0.4.0; and in the runtime's and every emulation's records the
key `adopted_from` as `origin`. A loop contract stays as it is: a loop record states its `carried_by` and its
`rhythm`, which only the commons can say. Nothing is migrated twice, and nothing goes back (R4).

Only a release copy moves into `models/commons/`: a folder of `extensions/` that holds its `release.yml` or that the lock
names. A copy that is no release (a pack copied in by hand, a template, patterns kept beside the model) is never moved
as if it were installed: it goes whole to `workshop/_migration/extensions/<library>/<name>/`, and
`workshop/_migration/origin.yml` records where it lay, the commit that last changed it and why it was not installed.
A CORE on the earliest layout, its settings in `.commons/identity.yml` and `.commons/config.yml` and no `commons.yml`,
gains `commons.yml` from them in the same run: `id` from `slug`, `name`, `language` from `locale`, `instance_type`
`commons`, and the `code` the commons gives with --code where its identity names none; nothing is guessed, and without
a code the run stops before it writes anything. The packs `config.yml` names are no releases and are recorded in
`origin.yml`, never pinned; the commons installs its models afterwards (`install.py`). The earlier settings files are
kept in `workshop/_migration/.commons/`. --library ID=OWNER/REPO names where the commons' releases are held.
The Commons model is never a commons' primary (CORE R1): a pin of it marked `primary`, as the template of 0.3.0 wrote
it, loses the mark. `AGENT.md` is generated again by `make_agent.py` beside this tool, so that the changed settings and
the agent file stand in one commit (R36).

Usage:  migrate_core.py CORE [--apply] [--code CODE] [--library ID=OWNER/REPO]
"""
import argparse
import glob
import os
import re
import shutil
import subprocess
import sys

import yaml

sys.dont_write_bytecode = True   # the tools never write into the install they lie in (SPECIFICATION R29)
ESSENTIALS = "commons-essentials"
KEYS = {"registry": "runtime", "extensions": "commons", "offer": "emulation"}
EARLIER_ID = re.compile(r"(\bid:\s*['\"]?)((?:[a-z0-9-]+/)?)commons-essentials(?=['\"]?[\s,}])")   # the Commons model's earlier id


def yml(p):
    try:
        return yaml.safe_load(open(p, encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return None


def released(core, lib, ext):
    """whether `extensions/<lib>/<ext>/` is a release copy: it holds its record, or the lock names it (CORE R39)"""
    if os.path.isfile(os.path.join(core, "extensions", lib, ext, "release.yml")):
        return True
    lock = yml(os.path.join(core, ".commons", "lock.yml")) or {}
    ids = {str(x.get("id")) for x in (lock.get("models") or lock.get("extensions") or []) if isinstance(x, dict)}
    return f"{lib}/{ext}" in ids or (ext == ESSENTIALS and ESSENTIALS in ids)


def legacy(core):
    """whether the CORE is on the earliest layout: settings in `identity.yml`, no `commons.yml`"""
    return (not os.path.isfile(os.path.join(core, ".commons", "commons.yml"))
            and os.path.isfile(os.path.join(core, ".commons", "identity.yml")))


LEGACY_FILES = ("identity.yml", "config.yml", "a2a.yml", "deliverables.yml")   # the earliest layout's settings, kept


def settings(core, code=None, libraries=None):
    """`commons.yml` of a CORE on the earliest layout, from its identity and config; (doc, packs, missing)"""
    idn = yml(os.path.join(core, ".commons", "identity.yml")) or {}
    cfg = yml(os.path.join(core, ".commons", "config.yml")) or {}
    doc = {"id": idn.get("slug") or idn.get("id"), "name": idn.get("name"), "code": idn.get("code") or code,
           "instance_type": "commons", "language": idn.get("locale") or idn.get("language"), "structure": "0.4.0",
           "models": []}
    if libraries:
        doc["libraries"] = dict(libraries)
    missing = [k for k in ("id", "name", "code", "language") if not doc.get(k)]
    packs = [str(x if not isinstance(x, dict) else x.get("id")) for x in (cfg.get("extensions") or [])]
    return doc, packs, missing


def last_commit(core, path):
    out = subprocess.run(["git", "-C", core, "log", "-1", "--format=%H", "--", path], capture_output=True, text=True)
    return out.stdout.strip() or None


def plan(core):
    """[(source, target)] of every move, relative to the CORE"""
    moves = []
    j = lambda *p: os.path.join(core, *p)
    if os.path.isdir(j("registry")):
        moves += [(f"registry/{n}", f"models/runtime/{n}") for n in sorted(os.listdir(j("registry")))]
    if os.path.isdir(j("operations", "loops")):
        for n in sorted(os.listdir(j("operations", "loops"))):
            to = {"_state": "models/runtime/state", "_contract.yml": "workshop/_migration/_contract.yml"}.get(n, f"models/runtime/loops/{n}")
            moves.append((f"operations/loops/{n}", to))
    if os.path.isfile(j("operations", "rhythms.md")):
        moves.append(("operations/rhythms.md", "workshop/_migration/rhythms.md"))
    for d in sorted(glob.glob(j("extensions", "*", "*", ""))):
        lib, ext = os.path.normpath(d).split(os.sep)[-2:]
        if released(core, lib, ext):
            moves.append((f"extensions/{lib}/{ext}", f"models/commons/{lib}/{'commons' if ext == ESSENTIALS else ext}"))
        else:                                          # no release: kept with its origin, never moved as if installed
            moves.append((f"extensions/{lib}/{ext}", f"workshop/_migration/extensions/{lib}/{ext}"))
    if legacy(core):
        moves += [(f".commons/{f}", f"workshop/_migration/.commons/{f}") for f in LEGACY_FILES
                  if os.path.isfile(j(".commons", f))]
    if os.path.isdir(j("offer")):
        mid = str((yml(j("offer", "offer.yml")) or {}).get("id") or "offer")
        for n in sorted(os.listdir(j("offer"))):
            if n == "offer.yml":
                moves.append(("offer/offer.yml", f"models/emulation/{mid}/model.yml"))
            elif n == "registry" and os.path.isdir(j("offer", "registry")):
                moves += [(f"offer/registry/{e}", f"models/emulation/{mid}/{e}") for e in sorted(os.listdir(j("offer", "registry")))]
            else:
                moves.append((f"offer/{n}", f"models/emulation/{mid}/{n}"))
    if os.path.isdir(j(".build")) and not os.path.exists(j(".provenance")):
        moves.append((".build", ".provenance"))
    for d in sorted(glob.glob(j("patterns", "*", ""))):
        n = os.path.basename(os.path.normpath(d))
        if n != "commons" and os.path.isfile(os.path.join(d, "release.yml")):
            moves.append((f"patterns/{n}", f"patterns/commons/{n}"))
    return [(s, t) for s, t in moves if not os.path.exists(j(t))]


def git_tree(core):
    out = subprocess.run(["git", "-C", core, "rev-parse", "--is-inside-work-tree"], capture_output=True, text=True)
    return out.returncode == 0 and out.stdout.strip() == "true"


def move(core, s, t, git):
    os.makedirs(os.path.dirname(os.path.join(core, t)), exist_ok=True)
    tracked = git and subprocess.run(["git", "-C", core, "ls-files", "--error-unmatch", s], capture_output=True).returncode == 0
    if tracked:
        subprocess.run(["git", "-C", core, "mv", s, t], check=True)
    else:
        shutil.move(os.path.join(core, s), os.path.join(core, t))


def rename_keys(core, plan_done=()):
    """the keys of 0.4.0 in the settings, the lock and the records; returns the files changed"""
    changed = []
    p = os.path.join(core, ".commons", "commons.yml")
    t = open(p, encoding="utf-8").read() if os.path.isfile(p) else None
    if t is not None:
        u = re.sub(r"(?m)^extensions:", "models:", t)
        u = re.sub(r"(?m)^structure: .*$", "structure: 0.4.0", u)
        u = EARLIER_ID.sub(r"\g<1>\g<2>commons", u)          # the pin follows the copy's folder (CORE R39)
        u = re.sub(r"(?m)^(-\s+id:\s*['\"]?(?:[a-z0-9-]+/)?commons['\"]?\s*\n(?:[ \t]+(?!primary:).*\n)*?)[ \t]+primary:\s*true[ \t]*\n",
                   r"\1", u)                                  # the grammar is never a commons' primary (CORE R1)
        for o, n in KEYS.items():
            u = re.sub(rf"(?m)^(\s+){o}:", rf"\1{n}:", u) if re.search(r"(?m)^locations:", u) else u
        if u != t:
            open(p, "w", encoding="utf-8", newline="\n").write(u)
            changed.append(".commons/commons.yml")
    p = os.path.join(core, ".commons", "lock.yml")
    t = open(p, encoding="utf-8").read() if os.path.isfile(p) else None
    if t is not None:
        u = re.sub(r"(?m)^extensions:", "models:", t)
        u = EARLIER_ID.sub(r"\g<1>\g<2>commons", u)          # the lock follows it too
        lock = yaml.safe_load(u) or {}
        for x in lock.get("patterns") or []:
            if isinstance(x, dict) and x.get("path") and not str(x["path"]).startswith("commons/"):
                u = re.sub(rf"(?m)^(\s*-?\s*path:\s*){re.escape(str(x['path']))}\s*$", rf"\g<1>commons/{x['path']}", u)
        if u != t:
            open(p, "w", encoding="utf-8", newline="\n").write(u)
            changed.append(".commons/lock.yml")
    p = os.path.join(core, "graph", "sources.yml")    # the graph's register: the kinds and places of 0.4.0 (GRAPH part 5)
    t = open(p, encoding="utf-8").read() if os.path.isfile(p) else None
    if t is not None:
        u = re.sub(r"(\bkind:\s*)(registry|operations)\b", r"\1runtime", t)
        u = re.sub(r"(\bkind:\s*)extension\b", r"\1model", u)
        u = re.sub(r"(\bref:\s*)operations(/loops)?/?(?=[\s,}])", r"\1models/runtime/loops/", u)
        u = re.sub(r"(\bref:\s*)registry(?=[/\s,}])", r"\1models/runtime", u)
        u = re.sub(r"(\bref:\s*)extensions/", r"\1models/commons/", u)
        for s, d in [(s, d) for s, d in plan_done if s.startswith("patterns/")]:
            u = re.sub(rf"(\bref:\s*){re.escape(s)}(?=[/\s,}}])", rf"\g<1>{d}", u)
        if u != t:
            open(p, "w", encoding="utf-8", newline=chr(10)).write(u)
            changed.append("graph/sources.yml")
    for f in sorted(glob.glob(os.path.join(core, "models", "runtime", "**", "*.y*ml"), recursive=True) +
                    glob.glob(os.path.join(core, "models", "emulation", "*", "*", "*.y*ml"))):
        t = open(f, encoding="utf-8").read()
        u = re.sub(r"(?m)^(\s*)adopted_from:", r"\1origin:", t)
        if u != t:
            open(f, "w", encoding="utf-8", newline="\n").write(u)
            changed.append(os.path.relpath(f, core).replace(os.sep, "/"))
    return changed


def agent_again(core):
    """the agent file follows the settings, in the same commit (CORE R36): make_agent.py beside this tool"""
    agent = os.path.join(os.path.dirname(os.path.abspath(__file__)), "make_agent.py")
    if not os.path.isfile(agent):
        return
    r = subprocess.run([sys.executable, "-B", agent, core], capture_output=True, text=True, encoding="utf-8")
    why = ((r.stderr or r.stdout).strip().splitlines() or ["make_agent.py failed"])[-1]
    print("agent: AGENT.md generated again" if r.returncode == 0 else f"note: AGENT.md was not generated again ({why}); run make_agent.py")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("core")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--code", help="the commons' code, where its earlier identity names none")
    ap.add_argument("--library", action="append", default=[], metavar="ID=OWNER/REPO")
    a = ap.parse_args()
    early = legacy(a.core)
    if early:
        libs = [x.split("=", 1) for x in a.library if "=" in x]
        doc, packs, missing = settings(a.core, a.code, libs)
        print(f"settings: .commons/identity.yml and config.yml -> .commons/commons.yml (id {doc['id']}, language {doc['language']})")
        for p in packs:
            print(f"kept: pack `{p}` named in config.yml is no release; recorded in workshop/_migration/origin.yml, not pinned")
        if missing:
            print(f"# {a.core}: on the earliest layout; its identity names no {', '.join(missing)}: give "
                  f"{' '.join('--' + m for m in missing if m == 'code') or 'them in identity.yml'}; nothing is written")
            return 1
    cfg = yml(os.path.join(a.core, ".commons", "commons.yml")) or {}
    if not early and str(cfg.get("structure")) == "0.4.0" and not plan(a.core):
        ids = [f for f in (".commons/commons.yml", ".commons/lock.yml") if os.path.isfile(os.path.join(a.core, f))
               and EARLIER_ID.search(open(os.path.join(a.core, f), encoding="utf-8").read())]
        grammar = any(str(m.get("id", "")).split("/")[-1] in ("commons", ESSENTIALS) and m.get("primary")
                      for m in cfg.get("models") or [] if isinstance(m, dict))   # never a commons' primary (CORE R1)
        what = ([f"{', '.join(ids)} name the Commons model `commons-essentials`"] if ids else []) +                (["`commons.yml` marks the Commons model primary"] if grammar else [])
        if what and a.apply:                         # a CORE migrated before the id moved with the folder, or the mark
            for f in rename_keys(a.core):
                print(f"keys: {f}")
            agent_again(a.core)
            print(f"# {a.core}: on structure 0.4.0; repaired: {'; '.join(what)}")
        elif what:
            print(f"# {a.core}: on structure 0.4.0; {'; '.join(what)}; run with --apply to repair")
        else:
            print(f"# {a.core}: on structure 0.4.0 already; nothing to do")
        return 0
    moves = plan(a.core)
    for s, t in moves:
        print(f"move: {s} -> {t}")
    if not a.apply:
        print(f"# {len(moves)} moves and the keys of 0.4.0; run with --apply to do them")
        return 0
    git = git_tree(a.core)
    kept = [{"from": s, "to": t, "commit": last_commit(a.core, s) if git else None,
             "why": "no release copy: no release.yml and no entry in the lock" if s.startswith("extensions/")
             else "a settings file of the earliest layout, replaced by .commons/commons.yml"}
            for s, t in moves if t.startswith("workshop/_migration/") and (s.startswith("extensions/") or s.startswith(".commons/"))]
    for s, t in moves:
        move(a.core, s, t, git)
    if early:
        with open(os.path.join(a.core, ".commons", "commons.yml"), "w", encoding="utf-8", newline="\n") as f:
            f.write("# The settings of this CORE (core.md R1, part 5), written by migrate_core from the earlier identity.yml and config.yml\n")
            yaml.safe_dump(doc, f, sort_keys=False, allow_unicode=True, width=120)
        if git:
            subprocess.run(["git", "-C", a.core, "add", ".commons/commons.yml"], check=True)
        print("keys: .commons/commons.yml (written)")
    if kept or (early and packs):
        op = os.path.join(a.core, "workshop", "_migration", "origin.yml")
        old = yml(op) or {}
        rec = {"kept": (old.get("kept") or []) + kept}
        if early and packs:
            rec["packs"] = sorted(set((old.get("packs") or []) + packs))
        os.makedirs(os.path.dirname(op), exist_ok=True)
        with open(op, "w", encoding="utf-8", newline="\n") as f:
            f.write("# generated by migrate_core: what the migration kept and did not install, with its origin (CORE R4)\n")
            yaml.safe_dump(rec, f, sort_keys=False, allow_unicode=True, width=120)
        print(f"kept: {len(kept)} part(s) in workshop/_migration/, recorded in workshop/_migration/origin.yml")
    for d in ("registry", "operations", "extensions", "offer"):
        p = os.path.join(a.core, d)
        for at, _, _ in sorted(os.walk(p), key=lambda w: -len(w[0])) if os.path.isdir(p) else []:
            if not any(os.scandir(at)):
                os.rmdir(at)                     # only what the moves left empty
        if os.path.isdir(p):
            print(f"left: {d}/ still holds {sorted(os.listdir(p))}; nothing is moved silently")
    for f in rename_keys(a.core, moves):
        print(f"keys: {f}")
    agent_again(a.core)
    print(f"# {a.core}: on structure 0.4.0, {len(moves)} moves")
    return 0


if __name__ == "__main__":
    sys.exit(main())
