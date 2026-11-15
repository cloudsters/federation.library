#!/usr/bin/env python3
"""take_update.py — a commons takes up a newer release of its model by a decision of its own (CORE R39).

Three-way, record by record, for every record that names the older release in its `origin` (`adopted_from` in a CORE
still on the earlier layout, MODEL part 5):
- the origin's rename map (R1) renames the origin id; the commons' record follows it where the commons kept the
  origin's slug, and surfaces a conflict where the commons gave the record a slug of its own;
- a reference to a record the commons renames follows it in every record of the registry, adopted or own. Which
  fields refer to which kind is MODEL's binding definition (`check_model.FIELDS`), the step bindings, and the
  `x-refers` a kind's specification declares in its schema: no second grammar;
- a field the origin changed is taken where the commons left it as it was; a field the commons changed is kept;
  a field both changed differently is a conflict, never overwritten;
- the origin names the newer release, under the key of the runtime's layout, and every archetype it names is offered
  there;
- a `not-selected` event stays as it is: it names what the commons did not select at that version;
- a record whose origin the newer release retires (its record's `retires`, LIBRARY R4) keeps that origin, is retired
  where it stands, a gap and no conflict, and the rest of the update is taken (CORE R39; MODEL part 5); whether the
  commons drops it later is its own decision. An origin the newer release neither holds nor retires stays a conflict.

An update is within one model or one variant of it (`<library>/<model>/<variant>`, MODEL R30). A commons grows into
the next variant of its domain by a take-up, never by an update (CORE R6, part 5; `build.py --take-up`).

Before anything is written, every resulting identity and path is checked against every record of the registry
and against each other: a rename that would take the place of another record, or two renames that would meet,
is a conflict, and nothing is written. `--keep-local` never licenses an overwrite.

Usage:  take_update.py CORE --from OLD_RELEASE --to NEW_RELEASE [--apply] [--keep-local]
        OLD_RELEASE and NEW_RELEASE are release copies (release.yml, the element folders, or `registry/` before).
        Without --apply it lists what it would do. With --apply it writes everything, or nothing while a conflict is open: an update is one act of the
        commons, never half taken. --keep-local is the commons' decision on its conflicts of slug and value: it keeps
        its own, and the record names the newer origin. A collision stays a conflict. Installing
        the new copy, the pin and the decision event are the commons' own steps (FLOW). Exit 2 while a conflict is open.
"""
import argparse
import copy
import glob
import json
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True   # the tools never write into the install they lie in (SPECIFICATION R29; `extension` R12)
sys.path.insert(0, HERE)
import check_model  # noqa: E402
import layout  # noqa: E402

STEP = {"capabilities": "capability", "entities": "entity", "serves": "touchpoint"}   # the bindings of a value stream's steps
EARLIER = {"journey": {"mirrors": "value-stream"}, "touchpoint": {"steps": "step"}}   # the earlier layout, still followed
SKIP = {"origin", "adopted_from", "binds", "start"}


def yml(p):
    return yaml.safe_load(open(p, encoding="utf-8")) if os.path.exists(p) else None


def records(reg):
    out = {}
    for f in sorted(glob.glob(os.path.join(reg, "*", "*.y*ml"))):
        rec = yml(f) or {}
        if isinstance(rec, dict) and rec.get("kind") and rec.get("slug"):
            out[f"{rec['kind']}:{rec['slug']}"] = (rec, f)
    return out


def declared(*roots):
    """the bindings a kind's specification adds: `x-refers: {field: kind}` per record kind in its schema's $defs"""
    out = {}
    for root in roots:
        for p in glob.glob(os.path.join(root, "**", "*.schema.json"), recursive=True):
            for kind, d in (json.load(open(p, encoding="utf-8")).get("$defs") or {}).items():
                if isinstance(d, dict) and isinstance(d.get("x-refers"), dict):
                    out.setdefault(kind, {}).update(d["x-refers"])
    return out


def spec_roots(core, ref, new):
    """where the bindings a kind declares are read: the commons' own `specs/`, the copy of every extension it installed
    but the one being replaced, Commons Essentials among them (R12, R9), and the newer release"""
    gone = os.path.normcase(os.path.abspath(layout.copy(core, ref)))
    held = [os.path.join(d, "specs") for d in layout.installed(core).values()
            if os.path.isdir(os.path.join(d, "specs")) and os.path.normcase(os.path.abspath(d)) != gone]
    return [os.path.join(core, "specs")] + held + [os.path.join(new, "specs")]


def bindings(kind, domain):
    b = {f: t for f, t in check_model.FIELDS.get(kind, [])}
    b.update(EARLIER.get(kind, {}))
    b.update(domain.get(kind, {}))
    return b


def follow(value, target, renames):
    """value with every reference of kind `target` renamed; a step is `stream/step` and follows its stream"""
    if isinstance(value, list):
        return [follow(v, target, renames) for v in value]
    if not isinstance(value, str):
        return value
    if target == "step" and "/" in value:
        stream, step = value.split("/", 1)
        return f"{renames.get('value-stream', {}).get(stream, stream)}/{step}"
    return renames.get(target, {}).get(value, value)


def rename_refs(rec, renames, domain):
    """a copy of the record with every reference in it to a renamed record renamed"""
    out = copy.deepcopy(rec)
    for field, target in bindings(rec.get("kind"), domain).items():
        if field in out:
            out[field] = follow(out[field], target, renames)
    if rec.get("kind") == "value-stream":
        for st in out.get("steps") or []:
            for field, target in STEP.items():
                if isinstance(st, dict) and field in st:
                    st[field] = follow(st[field], target, renames)
    return out


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("core")
    ap.add_argument("--from", dest="old", required=True)
    ap.add_argument("--to", dest="new", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--keep-local", action="store_true")
    a = ap.parse_args()
    ro, rn = yml(os.path.join(a.old, "release.yml")), yml(os.path.join(a.new, "release.yml"))
    ref = layout.ref_of({"id": f"{ro['library']}/{layout.release_id(ro)}", "variant": ro.get("variant")})
    if layout.ref_of({"id": f"{rn['library']}/{layout.release_id(rn)}", "variant": rn.get("variant")}) != ref:
        sys.exit(f"`{a.new}` is no release of `{ref}`: growing into another variant is a take-up, never an update (CORE R6; build.py --take-up)")
    old_v, new_v = ro["version"], rn["version"]
    retired = {str(x.get("id")) for x in rn.get("retires") or [] if isinstance(x, dict)}
    renames = {}
    for o, n in (rn.get("renames") or {}).items():
        k, s = o.split(":", 1)
        if n:
            renames.setdefault(k, {})[s] = n.split(":", 1)[1]
    domain = declared(*spec_roots(a.core, ref, a.new))
    base, newer = records(layout.records(a.old)), records(layout.records(a.new))
    local = records(layout.runtime(a.core))
    okey = "adopted_from" if os.path.basename(os.path.normpath(layout.runtime(a.core))) == "registry" else "origin"   # one key per layout (R4)
    plan, conflicts, writes, held = [], [], {}, set()

    moved_here = {}   # the renames this commons follows: only its own records that take the origin's new slug
    for key, (rec, f) in local.items():
        o = str(check_model.origin(rec) or "")
        if o.startswith(f"{ref}@{old_v}#"):
            okind, oslug = o.split("#", 1)[1].split(":", 1)
            nslug = renames.get(okind, {}).get(oslug, oslug)
            if nslug != oslug and rec.get("slug") == oslug:
                moved_here.setdefault(okind, {})[oslug] = nslug

    for key, (rec, f) in local.items():
        where = os.path.relpath(f, a.core)
        out = copy.deepcopy(rec)
        o = str(check_model.origin(rec) or "")
        if o.startswith(f"{ref}@{old_v}#"):
            okind, oslug = o.split("#", 1)[1].split(":", 1)
            nslug = renames.get(okind, {}).get(oslug, oslug)
            origin_old = (base.get(f"{okind}:{oslug}") or ({}, None))[0]
            origin_new = newer.get(f"{okind}:{nslug}")
            if origin_new is None and f"{okind}:{oslug}" in retired:
                plan.append(f"retired: {where}: `{okind}:{oslug}` is retired in {new_v}; it keeps its origin at {old_v}, "
                            f"retired where it stands, a gap and no conflict (CORE R39)")
                held.add(f)
                continue
            if origin_new is None:
                conflicts.append(f"{where}: `{okind}:{oslug}` is offered no more in {new_v}, which does not retire it: the commons decides")
                held.add(f)
                continue
            origin_new = origin_new[0]
            if nslug != oslug:
                if rec.get("slug") == oslug:
                    out["slug"] = nslug
                    plan.append(f"rename: {where}: `{oslug}` → `{nslug}`, as the origin renamed it")
                elif a.keep_local:
                    plan.append(f"kept: {where}: the commons' slug `{rec.get('slug')}`, by its decision; the origin is now `{nslug}`")
                else:
                    conflicts.append(f"{where}: the origin renamed `{oslug}` to `{nslug}`, and the commons calls it `{rec.get('slug')}`: kept, for decision")
                    held.add(f)
            was_rec, mine_rec = rename_refs(origin_old, renames, domain), rename_refs(rec, renames, domain)
            for fld in sorted((set(origin_old) | set(origin_new)) - SKIP - {"slug"}):
                was, now, mine = was_rec.get(fld), origin_new.get(fld), mine_rec.get(fld)
                if now == was or mine == now:
                    continue
                if mine == was:
                    out[fld] = now
                    plan.append(f"take: {where}: `{fld}` as {new_v} has it")
                elif a.keep_local:
                    plan.append(f"kept: {where}: the commons' `{fld}`, by its decision")
                else:
                    conflicts.append(f"{where}: `{fld}` changed in {new_v} and in the commons: kept, for decision")
                    held.add(f)
            out.pop("adopted_from" if okey == "origin" else "origin", None)
            out[okey] = f"{ref}@{new_v}#{okind}:{nslug}"
        moved = rename_refs(rec, moved_here, domain)
        for fld, val in rec.items():
            if fld in SKIP or fld == "slug" or moved.get(fld) == val:
                continue
            if out.get(fld) == val:
                out[fld] = moved[fld]
                plan.append(f"reference: {where}: `{fld}` follows the rename")
        if out != rec and f not in held:
            writes[f] = out

    # preflight: no write takes the place of another record, and no two writes meet
    files = {os.path.normcase(os.path.abspath(p)) for p in glob.glob(os.path.join(layout.runtime(a.core), "*", "*"))}
    targets = {}
    for f, out in writes.items():
        target = os.path.join(os.path.dirname(f), f"{out['slug']}{os.path.splitext(f)[1]}")
        t, src = os.path.normcase(os.path.abspath(target)), os.path.normcase(os.path.abspath(f))
        new_key = f"{out.get('kind')}:{out.get('slug')}"
        where = os.path.relpath(f, a.core)
        if t != src and t in files:
            conflicts.append(f"{where}: becoming `{new_key}` would take the place of `{os.path.relpath(target, a.core)}`, another record: nothing written, for decision")
        elif new_key in local and os.path.normcase(os.path.abspath(local[new_key][1])) != src:
            conflicts.append(f"{where}: becoming `{new_key}` would meet the record `{os.path.relpath(local[new_key][1], a.core)}`: nothing written, for decision")
        if t in targets:
            conflicts.append(f"{where} and {targets[t]}: both would become `{os.path.relpath(target, a.core)}`: nothing written, for decision")
        targets[t] = where

    for line in plan:
        print(line)
    for line in conflicts:
        print(f"conflict: {line}")
    print(f"# {a.core}: {ref} {old_v} → {new_v}: {len(writes)} records to write, {len(conflicts)} conflicts")
    if a.apply and conflicts:
        print("# nothing written: decide the conflicts first (--keep-local keeps the commons' own; it never overwrites)")
    elif a.apply:
        for f, out in writes.items():
            target = os.path.join(os.path.dirname(f), f"{out['slug']}{os.path.splitext(f)[1]}")
            with open(target, "w", encoding="utf-8", newline="\n") as h:
                yaml.safe_dump(out, h, sort_keys=False, allow_unicode=True, width=120)
            if os.path.normcase(target) != os.path.normcase(f):
                os.remove(f)                  # one record, one file, named by its slug
    return 2 if conflicts else 0


if __name__ == "__main__":
    sys.exit(main())
