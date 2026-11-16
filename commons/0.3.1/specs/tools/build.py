#!/usr/bin/env python3
"""build.py — a help for building: the records a scope of an installed model brings into the runtime, prepared on a
working branch for a pull request (CORE R6; the models note of commons.o#109, part 7; Holger, commons.o#110
6610425987: "30 ok", "32 ok", "33 ok").

A commons builds its runtime from the models it installs and its own records. Putting a record into the runtime is a
change of `main`, made by decision as every change is: a pull request, its Story, and the merge (CORE R10; FLOW). So
this help writes no event and never writes into `main`; a person accountable chooses one origin for each record and
takes the change.

The model is the commons' primary, or with `--model <library>/<model>` any other it pins. Where another installed
model holds a record of the package too, the package shows it under `elsewhere`.

The scope is `whole`, `family:<f>`, `value-stream:<s>` (a bare stream slug reads as one) or `<kind>:<slug>`. One record,
`<kind>:<slug>`, is what MODEL has it bind, transitively, and nothing carried; a stakeholder, journey, touchpoint or
value exchange takes only what it binds outward, and the package shows the **proposals**: the streams whose steps
serve the touchpoints it leads to. Any other scope's package is:
- **bound:** each stream in the scope, the capabilities its steps bind with their parent chain up to L0, the entities
  its steps reference, and the stakeholders it names;
- **carried:** what binds to what is taken: the touchpoints its steps serve, each with its journey and stakeholder, the
  value exchanges at those touchpoints, the solutions that carry a taken capability, the Bodies that hold one with
  their Posts, and the records a kind's specification declares a stream's fields to refer to (`x-refers`); Bodies and
  Posts come with their places and never with their mandate or who holds a Post (`mandate: null`, `held_by: []`);
- **reused:** what the runtime already holds by its origin, so that nothing is built twice;
- **without:** what `--without` names, an id or a kind as `<kind>:*`, and what the history of the commons records as
  not selected; a stream goes with its package, a Body with its Posts;
- **unresolved** and **beyond:** what the package binds and the model does not hold, and what it binds outside the
  package; derived again whenever the runtime is read (*not yet, offered*, or *not yet*), never written.

`--write` writes every record of the package that is neither reused nor without nor left open (`--open`) into the
runtime, each naming its `origin` (`adopted_from` in a CORE still on the earlier layout). It writes nothing where a
record would take the place of one the commons holds, and nothing on `main`.

`--into NAME` builds an emulation, `models/emulation/<NAME>/`, in place of the runtime, from the same models (CORE R6):
a new one is seeded with the runtime's own records, those naming no origin, and its `model.yml` names the model it is
built from as its `origin`. A variant is named `<library>/<model>/<variant>` (MODEL R30).

`--take-up NAME --keep-as EARLIER` makes the emulation NAME the runtime, on the branch whose merge is the decision
(CORE R6, part 5): the runtime moves whole, its records, their origins, `loops/` and `state/` unchanged, to
`models/emulation/<EARLIER>/`, whose `model.yml` names the runtime's revision as its origin, so that its records are
retired where they stand (MODEL part 5); the emulation moves into its place; and the pin it was built from becomes the
primary. A commons grows into the next variant of its domain so, never by an update (CORE R39). Nothing is deleted.

`--carry value-stream:<s>` writes the decisive selection of its family (blueprint R10, C6; commons.core#113): the
stream the commons builds the family from, `essential: true` on it in the runtime, and on no other stream of the
family. An agent proposes it; a person, or the Body answering for the dimension, takes it, so it is written on a
working branch only, with `--write`, and is the commons' own act.

Usage:  build.py CORE SCOPE [--model library/model[/variant]] [--into NAME] [--without kind:slug|kind:* ...] [--open kind:slug ...] [--write]
        build.py CORE --take-up NAME --keep-as EARLIER
        build.py CORE --carry value-stream:<s> [--write]
"""
import argparse
import copy
import glob
import itertools
import os
import re
import shutil
import subprocess
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True   # the tools never write into the install they lie in (SPECIFICATION R29; CORE R39)
sys.path.insert(0, HERE)
from catalogue import activation, not_selected, one_record, package  # noqa: E402
import check_model  # noqa: E402
import layout  # noqa: E402
from take_update import declared, spec_roots  # noqa: E402

FOLDER = {"value-stream": "value-streams", "capability": "capabilities", "entity": "entities", "stakeholder": "stakeholders",
          "journey": "journeys", "touchpoint": "touchpoints", "value-exchange": "value-exchanges", "solution": "solutions",
          "body": "bodies", "post": layout.post_folder()}   # a Post in its Body's folder, `posts/` its earlier place (PO-a)
COMMONS_OWN = {"body": {"mandate": None}, "post": {"held_by": []}}   # the commons' own acts, written as gaps (MODEL R28)


def yml(p):
    return yaml.safe_load(open(p, encoding="utf-8")) if os.path.exists(p) else None


def dump(p, d):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        yaml.safe_dump(d, f, sort_keys=False, allow_unicode=True, width=120)


def records(reg):
    out = {}
    for f in sorted(glob.glob(os.path.join(reg, "*", "*.y*ml"))):
        rec = yml(f) or {}
        if isinstance(rec, dict) and rec.get("kind") and rec.get("slug"):
            out[f"{rec['kind']}:{rec['slug']}"] = rec
    return out


def scope_of(arg):
    """the scope; a bare stream slug is one stream"""
    if arg == "whole" or arg.startswith(("family:", "value-stream:")) or one_record(arg):
        return arg
    return f"value-stream:{arg}"


def history(core, ref=""):
    """what the commons' history records as not selected from one model: earlier `not-selected` events and the
    `not_selected` of earlier activations, read for their words and never checked (Holger 6610425987, 33)"""
    out = []
    for f in sorted(glob.glob(os.path.join(core, "lifecycle", "events", "*.y*ml"))):
        ev = yml(f) or {}
        if ev.get("kind") == "not-selected" and "#" in str(ev.get("archetype")) and str(ev["archetype"]).startswith(ref):
            out.append(str(ev["archetype"]).split("#", 1)[1])
        if ev.get("kind") == "decision" and isinstance(ev.get("activates"), dict) and str(ev["activates"].get("extension")).startswith(ref):
            out += not_selected(ev["activates"])
    return out


def proposal(core, scope, without=(), model=None, into=None):
    cfg = yml(os.path.join(core, ".commons", "commons.yml")) or {}
    pins = [x for x in layout.pins(cfg) if "/" in str(x.get("id"))]
    prim = next((x for x in pins if layout.ref_of(x) == model), None) if model else next((x for x in pins if x.get("primary")), None)
    if prim is None:
        sys.exit(f"the CORE pins no `{model}`" if model else "the CORE pins no model of its kind as its primary")
    ref, version = layout.ref_of(prim), str(prim["version"])
    at = layout.copy(core, ref)
    offered = records(layout.records(at))
    if into and not os.path.isdir(into):         # a new emulation holds the runtime's own records first (`seed`)
        local = {k: v for k, v in records(layout.runtime(core)).items() if not check_model.origin(v)}
    else:
        local = records(into or layout.runtime(core))
    origins = {str(check_model.origin(r)).split("#", 1)[1] for r in local.values()    # held from this model
               if str(check_model.origin(r) or "").startswith(f"{ref}@") and "#" in str(check_model.origin(r))}
    others = {f"{layout.ref_of(x)}@{x['version']}": records(layout.records(layout.copy(core, layout.ref_of(x))))
              for x in pins if layout.ref_of(x) != ref and x["id"].split("/")[-1] not in layout.ESSENTIALS}
    if not package(offered, scope)[0]:
        sys.exit(f"`{ref}@{version}` holds nothing in the scope `{scope}`")
    try:                                         # the one derivation of a package, the renderer's too
        a = activation(offered, scope, without, history(core, f"{ref}@"), origins, declared(*spec_roots(core, ref, at)))
    except ValueError as e:
        sys.exit(str(e))
    take, reused = a["take"], a["reused"]

    def place(k):
        kind, slug = k.split(":", 1)
        return os.path.join(into or layout.runtime(core), FOLDER[kind], f"{slug}.yml")
    collisions = [k for k in take if k not in reused and (k in local or os.path.exists(place(k)))]
    elsewhere = {k: [o for o, recs in others.items() if k in recs] for k in take if k not in reused}
    return {"model": f"{ref}@{version}", "scope": scope, "bound": a["bound"], "carried": a["carried"],
            "reused": reused, "without": a["not_selected"], "collisions": collisions,
            "unresolved": a["unresolved"], "beyond": a["beyond"], **({"proposals": a["proposals"]} if a["proposals"] else {}),
            **({"elsewhere": {k: v for k, v in elsewhere.items() if v}} if any(elsewhere.values()) else {})}, offered


def on_main(core):
    """the default branch the CORE's checkout is on, else "": `main`, `master`, or the branch its remote names as HEAD
    (TA-8; CORE R10), so that the guard holds whatever a repository calls its main line"""
    git = lambda *a: subprocess.run(["git", "-C", core, *a], capture_output=True, text=True)
    out = git("branch", "--show-current")
    branch = out.stdout.strip() if out.returncode == 0 else ""
    head = git("symbolic-ref", "--short", "refs/remotes/origin/HEAD").stdout.strip().split("/", 1)[-1]
    return branch if branch and (branch in ("main", "master") or branch == head) else ""


def revision(core):
    """`owner/repo@rev` of the CORE, for the origin of a runtime kept as an emulation (MODEL part 5)"""
    git = lambda *a: (subprocess.run(["git", "-C", core, *a], capture_output=True, text=True).stdout or "").strip()
    remote = git("remote", "get-url", "origin").removesuffix(".git").rstrip("/")
    repo = "/".join(remote.replace(":", "/").split("/")[-2:]) if remote else os.path.basename(os.path.abspath(core))
    return f"{repo}@{git('rev-parse', '--short=7', 'HEAD') or '0000000'}"


def seed(core, into, ref, version):
    """a new emulation: its `model.yml` naming the model it is built from, and the runtime's own records, those naming
    no origin (CORE R6); returns how many records were copied"""
    at = layout.copy(core, ref)
    made = yml(layout.model_file(at)) or {}
    m = {"id": made.get("id") or ref.split("/")[1], "title": made.get("title") or ref, "origin": f"{ref}@{version}"}
    if isinstance(made.get("variant"), dict):
        m["variant"] = made["variant"]
    dump(os.path.join(into, "model.yml"), m)
    n = 0
    for f in sorted(glob.glob(os.path.join(layout.runtime(core), "*", "*.y*ml"))):
        rec = yml(f) or {}
        if isinstance(rec, dict) and rec.get("kind") and not check_model.origin(rec):
            dump(os.path.join(into, os.path.relpath(f, layout.runtime(core))), rec)
            n += 1
    return n


def take_up(core, name, keep_as):
    """the emulation `name` becomes the runtime, the runtime kept whole as the emulation `keep_as` (CORE R6, part 5)"""
    if on_main(core):
        print(f"# nothing moved: the CORE is on `{on_main(core)}`, its main line; a take-up is made on a working branch and taken by its merge (CORE R6, R10)")
        return 2
    emus = os.path.join(core, "models", "emulation")
    src, keep, rt = os.path.join(emus, name), os.path.join(emus, keep_as), layout.runtime(core)
    if not os.path.isdir(src):
        sys.exit(f"no emulation `models/emulation/{name}/` to take up")
    if os.path.exists(keep):
        sys.exit(f"`models/emulation/{keep_as}/` exists: the runtime is kept under a name of its own")
    if os.path.normpath(os.path.relpath(rt, core)).replace(os.sep, "/") != "models/runtime":
        sys.exit("the runtime is at an earlier place: migrate the CORE first (CORE R4)")
    made = yml(layout.model_file(src)) or {}
    built = str(made.get("origin") or "").split("@")[0]
    cfg_p = os.path.join(core, ".commons", "commons.yml")
    cfg = yml(cfg_p) or {}
    pins = layout.pins(cfg)
    prim = next((x for x in pins if x.get("primary")), None)
    was = yml(layout.model_file(layout.copy(core, layout.ref_of(prim)))) if prim else {}
    shutil.move(rt, keep)                        # the runtime whole, its records and their origins unchanged
    dump(os.path.join(keep, "model.yml"), {"id": (was or {}).get("id") or keep_as, "title": f"The runtime before {name}",
                                           "origin": f"{revision(core)}:models/runtime"})
    shutil.move(src, rt)
    os.remove(os.path.join(rt, os.path.basename(layout.model_file(rt))))   # the runtime's settings are commons.yml's (MODEL part 5)
    if built and any(layout.ref_of(x) == built for x in pins):
        for x in pins:
            x.pop("primary", None)
            if layout.ref_of(x) == built:
                x["primary"] = True
        head = "".join(itertools.takewhile(lambda l: l.startswith("#"), open(cfg_p, encoding="utf-8").read().splitlines(True)))
        with open(cfg_p, "w", encoding="utf-8", newline="\n") as f:
            f.write(head)
            yaml.safe_dump(cfg, f, sort_keys=False, allow_unicode=True, width=120)
    print(f"# taken up: `models/emulation/{name}/` is the runtime; the runtime is kept whole as `models/emulation/{keep_as}/`, "
          f"its records retired where they stand" + (f"; `{built}` is the primary" if built else "") + ". Take the change by a pull request")
    return 0


def carry(core, stream, write):
    """the decisive selection of a family (blueprint R10): `essential: true` on the stream, removed from every other
    stream of its family in the runtime; each record changed in its line, the rest of the file as the commons wrote it"""
    slug = stream.split(":", 1)[1] if stream.startswith("value-stream:") else stream
    folder = os.path.join(layout.runtime(core), "value-streams")
    files = {(yml(f) or {}).get("slug"): f for f in sorted(glob.glob(os.path.join(folder, "*.y*ml")))}
    if slug not in files:
        print(f"# nothing written: the runtime holds no stream `{slug}`; a family is carried by a stream the commons runs (blueprint R10)")
        return 2
    fam = (yml(files[slug]) or {}).get("family")
    others = [s for s, f in files.items() if s != slug and (yml(f) or {}).get("family") == fam and (yml(f) or {}).get("essential") is True]
    print(f"carry: `value-stream:{slug}` carries the family `{fam}`" + (f"; `essential` leaves {', '.join(others)}" if others else ""))
    if not write:
        return 0
    if on_main(core):
        print(f"# nothing written: the CORE is on `{on_main(core)}`, its main line; the selection is made on a working branch and taken by decision (CORE R10)")
        return 2
    for s, value in [(slug, True)] + [(o, False) for o in others]:
        t = open(files[s], encoding="utf-8").read()
        lines = [l for l in t.splitlines() if not re.match(r"essential:\s", l)]
        if value:
            lines.append("essential: true")
        open(files[s], "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
    print(f"# written: the decisive selection of `{fam}`, on this branch; take it by decision")
    return 0


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("core")
    ap.add_argument("scope", nargs="?")
    ap.add_argument("--open", nargs="*", default=[])
    ap.add_argument("--without", nargs="*", default=[])
    ap.add_argument("--model")
    ap.add_argument("--into", metavar="NAME")
    ap.add_argument("--take-up", metavar="NAME")
    ap.add_argument("--keep-as", metavar="EARLIER")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--carry", metavar="value-stream:<s>")
    a = ap.parse_args()
    if a.carry:
        return carry(a.core, a.carry, a.write)
    if a.take_up:
        if not a.keep_as:
            sys.exit("--take-up needs --keep-as: the runtime is kept whole as an emulation of its own name (CORE R6)")
        return take_up(a.core, a.take_up, a.keep_as)
    if not a.scope:
        sys.exit("a scope is needed: whole, family:<f>, value-stream:<s> or <kind>:<slug>")
    scope = scope_of(a.scope)
    into = os.path.join(a.core, "models", "emulation", a.into) if a.into else None
    p, offered = proposal(a.core, scope, a.without, a.model, into)
    for k in a.open:
        if k not in p["bound"] + p["carried"]:
            sys.exit(f"`{k}` (--open) is not a record of this package")
    print(yaml.safe_dump(p, sort_keys=False, allow_unicode=True, width=120), end="")
    if not a.write:
        return 0
    if on_main(a.core):
        print(f"# nothing written: the CORE is on `{on_main(a.core)}`, its main line; a change of the runtime is made on a working branch and taken by decision (CORE R10)")
        return 2
    take = [k for k in p["bound"] + p["carried"] if k not in a.open]
    clash = [k for k in take if k in p["collisions"]]
    if clash:
        print(f"# nothing written: {', '.join(clash)} collide with what the commons holds; decide them first "
              f"(build under another slug, leave them out with --without, or open with --open)")
        return 2
    rt = into or layout.runtime(a.core)
    key = "adopted_from" if os.path.basename(os.path.normpath(rt)) == "registry" else "origin"   # one key per layout (R4)
    writes = []
    for k in take:
        rec = copy.deepcopy(offered[k])
        rec.pop("start", None)
        rec.update(copy.deepcopy(COMMONS_OWN.get(rec.get("kind"), {})))
        rec[key] = f"{p['model']}#{k}"
        kind, slug = k.split(":", 1)
        writes.append((os.path.join(rt, FOLDER[kind], f"{slug}.yml"), rec))
    taken = [t for t, _ in writes if os.path.exists(t)]
    if taken:
        print(f"# nothing written: {', '.join(os.path.relpath(t, a.core) for t in taken)} exist")
        return 2
    seeded = None
    if into and not os.path.isdir(into):
        seeded = seed(a.core, into, p["model"].rsplit("@", 1)[0], p["model"].rsplit("@", 1)[1])
    for target, rec in writes:
        dump(target, rec)
    if seeded is not None:
        print(f"# a new emulation `models/emulation/{a.into}/`, seeded with the runtime's {seeded} own records")
    print(f"# written: {len(take)} records ({len([k for k in take if k in p['bound']])} bound, "
          f"{len([k for k in take if k in p['carried']])} carried), {len(p['reused'])} reused, {len(p['without'])} without, "
          f"{len(a.open)} left open; {len(p['unresolved'])} not offered and {len(p['beyond'])} not yet stay derived. "
          f"Take the change by a pull request")
    return 0


if __name__ == "__main__":
    sys.exit(main())
