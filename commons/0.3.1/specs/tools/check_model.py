#!/usr/bin/env python3
"""check_model.py — a model is well-formed in the grammar of Commons MODEL (model.md). Read-only.

Reads a model: one YAML file with `records` (and optionally `addresses`), or a folder whose YAML files each hold
one record or a `records` list. Reports each finding as fail (a MUST), should (a SHOULD) or gap (missing, not wrong),
and exits with 1 only on a fail. The check ids are those of model.md, part 6:

  schema  slugs  family  bindings  binding-ids  capability-map  bodies  no-persons  kinds-apart  accountable
  safeguards  addresses  coherence  shells  canon

A green check describes the model. It grants no authority to act.

Usage:  check_model.py MODEL [--canon value-creation-canon.yml] [--bindings] [--catalogue]
        --bindings prints the derived identity of every binding, one per line, so that two revisions can be compared
        --catalogue reads MODEL, a model folder, as a catalogue made for every commons of its kind, the check
        `catalogue` (R28, R29): every record holds every field the grammar requires but a Body's `mandate` and a Post's
        `held_by`, the commons' own, which a missing one leaves a gap; every kind whole; the thirteen families, a
        family no stream reaches a gap of the maker; the depth in `enhanced/`; the starting set and each family's
        `order`; and, for a model with `variant`, the check `variants` (R30, R31) against the other variants of its
        domain at hand, else a gap. `--extension` is its earlier name
"""
import argparse
import glob
import json
import os
import re
import sys

import jsonschema
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA = os.path.join(HERE, "..", "schemas", "model.schema.json")
CANON = next((p for p in (os.path.join(HERE, "..", "value-creation-canon.yml"),     # released with the Commons model (specs/)
                          os.path.join(HERE, "..", "..", "..", "workshop", "_specifications", "value-creation-canon.yml"))
              if os.path.exists(p)), os.path.join(HERE, "..", "value-creation-canon.yml"))
LEVELS = ["L0", "L1", "L2", "L3", "L4", "L5"]
DIMENSIONS = {"d0", "d1", "d2", "d3", "d4"}
EMAIL = re.compile(r"(?<![\w.+/-])[\w.+-]+@[\w-]+\.[\w.-]+")   # never the <library>/<extension>@<version> of an origin
PHONE = re.compile(r"\+\d[\d ()-]{7,}\d")
IDENT = re.compile(r"\b(github:[A-Za-z0-9-]+|person:P_\d+)")
HUMAN = re.compile(r"^(github:[A-Za-z0-9-]+|person:P_\d+)$")
SHELLED = {"stakeholder", "journey", "touchpoint", "value-exchange"}
FIELDS = {                                       # the bindings of each kind, as (field, target kind)
    "journey": [("stakeholder", "stakeholder")],   # the stakeholder side names nothing inside (Holger, commons.o#109 6571926000)
    "touchpoint": [("stakeholder", "stakeholder"), ("journey", "journey")],
    "value-exchange": [("touchpoint", "touchpoint")],
    "capability": [("parent", "capability")],
    "solution": [("carries", "capability")],
    "body": [("part_of", "body"), ("holds", "capability")],
    "post": [("of", "body"), ("accountable", "accountable")],
    "loop": [("carried_by", "body"), ("escalates_to", "body")],   # and `keeps`, a node of any kind (R10)
}
NOT_RECORDS = ("model.yml", "offer.yml", "release.yml", "sources.yml")   # a model folder's files beside its records
NOT_RECORD_DIRS = ("state", "enhanced", "specs", "views", "LICENSES")      # and its folders that hold no record (CORE R6)


def origin(x):
    """the origin a record names: `origin`, or its earlier key `adopted_from` (CORE R4)"""
    return x.get("origin") or x.get("adopted_from") if isinstance(x, dict) else None


class Report:
    def __init__(self):
        self.items = []

    def fail(self, check, text):
        self.items.append(("fail", check, text))

    def should(self, check, text):
        self.items.append(("should", check, text))

    def gap(self, check, text):
        self.items.append(("gap", check, text))


def load(path):
    if os.path.isdir(path):
        records, addresses = [], []
        for f in sorted(glob.glob(os.path.join(path, "**", "*.y*ml"), recursive=True)):
            top = os.path.relpath(f, path).replace(os.sep, "/").split("/")
            if (len(top) == 1 and top[0] in NOT_RECORDS) or (len(top) > 1 and top[0] in NOT_RECORD_DIRS):
                continue
            doc = yaml.safe_load(open(f, encoding="utf-8")) or {}
            if isinstance(doc, dict) and "records" in doc:
                records += doc["records"] or []
                addresses += doc.get("addresses") or []
            elif isinstance(doc, dict) and "kind" in doc:
                records.append(doc)
        return {"records": records, "addresses": addresses}
    return yaml.safe_load(open(path, encoding="utf-8")) or {}


def strings(value):
    """every string inside a value, for the person scan"""
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from strings(v)
    elif isinstance(value, list):
        for v in value:
            yield from strings(v)


def as_list(v):
    return v if isinstance(v, list) else ([] if v is None else [v])


def binding_ids(recs):
    """the derived identity of every binding: <kind>:<slug>#<field>:<target> (R22)"""
    out = []
    for x in recs:
        k, s = x.get("kind"), x.get("slug")
        for field, _ in FIELDS.get(k, []):
            for t in as_list(x.get(field)):
                out.append(f"{k}:{s}#{field}:{t}")
        if k == "value-stream":
            for st in x.get("steps") or []:
                for field in ("capabilities", "entities", "serves"):
                    for t in st.get(field) or []:
                        out.append(f"value-stream:{s}/{st.get('slug')}#{field}:{t}")
        if k == "post":
            for h in x.get("held_by") or []:
                out.append(f"post:{s}#held_by:{h.get('id')}")
        if k == "touchpoint" and x.get("at"):     # the step of its journey it stands at
            out.append(f"touchpoint:{s}#at:{x.get('journey')}/{x['at']}")
        if k == "loop" and x.get("keeps"):       # the node it keeps true (R1, R22)
            out.append(f"loop:{s}#keeps:{x['keeps']}")
    return out


COMMONS_OWN = {"body": {"mandate"}, "post": {"held_by"}}   # what a commons states for itself; activation writes the gap form
REFERENCE = re.compile(r"^reference\(([a-z0-9-]+)\)$")   # an entity's field that names another entity (R10)
EARLIER = {"journey": ("mirrors", "a step's `serves` ties the sides (R22)"),   # the earlier layout, read as a gap
           "touchpoint": ("steps", "a step's `serves` ties the sides (R22)"),
           "value-exchange": ("at", "a touchpoint stands `at` a step of its journey (R9)")}


def check(model, canon_path=None, extension=False):
    r = Report()
    schema = json.load(open(SCHEMA, encoding="utf-8"))
    dim_of = schema["x-dimension-of"]

    # schema (R1, R3, R5, R8, R9, R16); in an extension, an archetype leaves only the commons' own fields open (R28)
    for e in jsonschema.Draft202012Validator(schema).iter_errors(model):
        p = list(e.absolute_path)
        rec = model["records"][p[1]] if extension and len(p) == 2 and p[0] == "records" else None
        if (isinstance(rec, dict) and e.validator == "required"
                and e.message.split("'")[1] in COMMONS_OWN.get(rec.get("kind"), ())):
            r.gap("bindings", f"archetype {rec.get('kind')} `{rec.get('slug')}`: {e.message[:120]}, for a commons to state")
            continue
        r.fail("schema", f"{'/'.join(map(str, e.absolute_path)) or 'model'}: {e.message[:120]}")
    recs = [x for x in model.get("records") or [] if isinstance(x, dict)]

    # bodies (R14; D1, commons.o#109 6569751081): a capability is held by a Body; a Post holds none, offered or the
    # commons' own, it answers inside its Body by its responsibility and its accountable
    for x in recs:
        if x.get("kind") == "post" and "holds" in x:
            r.fail("bodies", f"{'archetype ' if extension else ''}post `{x.get('slug')}` holds capabilities; a capability is held by a Body (R14)")

    # slugs (R2)
    by = {}
    for x in recs:
        k, s = x.get("kind"), x.get("slug")
        if s in by.get(k, {}):
            r.fail("slugs", f"{k} `{s}` appears twice")
        by.setdefault(k, {})[s] = x
    caps = by.get("capability", {})
    bodies = by.get("body", {})
    posts = by.get("post", {})
    steps = {f"{s}/{st.get('slug')}": st for s, v in by.get("value-stream", {}).items() for st in v.get("steps") or []}

    # binding-ids (R22)
    seen = set()
    for b in binding_ids(recs):
        if b in seen:
            r.fail("binding-ids", f"the binding `{b}` is stated twice")
        seen.add(b)

    def resolve(kind, ref, where):
        if ref in (None, "", []):
            r.gap("bindings", f"{where}: not yet known")
            return None
        if ref not in by.get(kind, {}):
            r.gap("bindings", f"{where}: `{ref}` names no {kind} of the model yet")
            return None
        return by[kind][ref]

    def resolve_all(kind, refs, where):
        if not refs:
            r.gap("bindings", f"{where}: none yet")
            return []
        return [y for y in (resolve(kind, ref, where) for ref in refs) if y]

    # family (R4)
    for s, v in by.get("value-stream", {}).items():
        f, d = v.get("family"), v.get("dimension")
        if d and f in dim_of and dim_of[f] != d:
            r.fail("family", f"value stream `{s}`: dimension {d} disagrees with family {f} ({dim_of[f]})")

    # bindings, capability-map, coherence (R6, R7, R10, R14, R9)
    for s, v in by.get("value-stream", {}).items():
        for st in v.get("steps") or []:
            w = f"value stream `{s}`, step `{st.get('slug')}`"
            for c in resolve_all("capability", st.get("capabilities"), f"{w}, capabilities"):
                if c.get("level") != "L3":
                    r.fail("capability-map", f"{w} binds `{c['slug']}` at {c.get('level')}, not at L3")
            resolve_all("entity", st.get("entities"), f"{w}, entities")
            for ref in st.get("serves") or []:      # the one tie between the sides; a step that serves none is internal work
                resolve("touchpoint", ref, f"{w}, serves")
    # the stakeholder side stands on its own (R9; Holger, commons.o#109 6571926000): a journey's `mirrors` and a
    # touchpoint's `steps` are the earlier layout, read as a gap and never a fail; a step's `serves` ties the sides
    for k, (field, now) in EARLIER.items():
        for s, v in by.get(k, {}).items():
            if v.get(field):
                r.gap("bindings", f"{k} `{s}`, {field}: the earlier layout; {now}")
    served = {t for st in steps.values() for t in st.get("serves") or []}
    for s, v in by.get("journey", {}).items():
        resolve("stakeholder", v.get("stakeholder"), f"journey `{s}`, stakeholder")
    for s, v in by.get("touchpoint", {}).items():
        j = resolve("journey", v.get("journey"), f"touchpoint `{s}`, journey")
        if "stakeholder" in v:
            resolve("stakeholder", v.get("stakeholder"), f"touchpoint `{s}`, stakeholder")
            if j and j.get("stakeholder") and v.get("stakeholder") and j["stakeholder"] != v["stakeholder"]:
                r.fail("coherence", f"touchpoint `{s}` names stakeholder `{v['stakeholder']}`, its journey "
                                    f"`{j['slug']}` names `{j['stakeholder']}`")
        if v.get("at") and j and v["at"] not in {x.get("slug") for x in j.get("steps") or [] if isinstance(x, dict)}:
            r.gap("bindings", f"touchpoint `{s}`, at: `{v['at']}` names no step of its journey `{j['slug']}` yet")
        if s not in served and not v.get("steps") and not extension:   # in an offer it stands on the shelf (R28)
            r.gap("bindings", f"touchpoint `{s}`: no step serves it yet, a promise with no way of keeping it")
    for s, v in by.get("value-exchange", {}).items():
        resolve("touchpoint", v.get("touchpoint"), f"value exchange `{s}`, touchpoint")
        for half in ("offered", "returned"):
            if not v.get(half):
                r.gap("bindings", f"value exchange `{s}`: what is {half} is not yet known")
    for s, v in by.get("solution", {}).items():
        for c in resolve_all("capability", v.get("carries"), f"solution `{s}`, carries"):
            if c.get("level") != "L3":
                r.fail("capability-map", f"solution `{s}` carries `{c['slug']}` at {c.get('level')}, not at L3")
    for s, v in bodies.items():
        if v.get("part_of") is not None:
            resolve("body", v.get("part_of"), f"body `{s}`, part_of")
        if v.get("mandate") in (None, ""):
            r.gap("bindings", f"body `{s}`: its mandate is not yet referenced")
        for c in resolve_all("capability", v.get("holds"), f"body `{s}`, holds"):
            if c.get("level") not in LEVELS[:4]:
                r.fail("capability-map", f"body `{s}` holds `{c['slug']}` at {c.get('level')}; a Body holds L0 to L3 only")
    for s, v in by.get("loop", {}).items():       # a loop keeps one node true, carried by a Body (R1, R10)
        kp = v.get("keeps")
        kind, _, slug = str(kp or "").partition(":")
        if kp in (None, ""):
            r.gap("bindings", f"loop `{s}`, keeps: not yet known")
        elif kind == "family":
            if slug not in dim_of:
                r.fail("bindings", f"loop `{s}` keeps `{kp}`, which is no family of MODEL")
        elif kind == "dimension":
            if slug not in set(dim_of.values()):
                r.fail("bindings", f"loop `{s}` keeps `{kp}`, which is no dimension")
        elif kind == "value-stream" and "/" in slug:
            if slug not in steps:
                r.gap("bindings", f"loop `{s}`, keeps: `{kp}` names no step of the model yet")
        else:
            resolve(kind, slug, f"loop `{s}`, keeps")
        resolve("body", v.get("carried_by"), f"loop `{s}`, carried_by")
        if v.get("escalates_to") is not None:
            resolve("body", v.get("escalates_to"), f"loop `{s}`, escalates_to")
    for x in recs:                               # the earlier key of `origin`, read as it (CORE R4)
        if x.get("adopted_from") and not x.get("origin"):
            r.gap("bindings", f"{x.get('kind')} `{x.get('slug')}`, adopted_from: the earlier key of `origin`, unmigrated")
    for s, v in by.get("entity", {}).items():       # an entity's references and relations are bindings (R10)
        for a in v.get("attributes") or []:
            m = REFERENCE.match(str(a.get("type"))) if isinstance(a, dict) else None
            if m:
                resolve("entity", m[1], f"entity `{s}`, field `{a.get('name')}`")
        for x in v.get("relations") or []:
            if isinstance(x, dict):
                resolve("entity", x.get("target"), f"entity `{s}`, relation `{x.get('type')}`")
    for s, v in caps.items():
        lv, p = v.get("level"), v.get("parent")
        if lv not in LEVELS:
            continue
        if lv == "L0":
            if p is not None:
                r.fail("capability-map", f"capability `{s}` is at L0 and names a parent")
            continue
        pc = resolve("capability", p, f"capability `{s}`, parent")
        if pc and pc.get("level") != LEVELS[LEVELS.index(lv) - 1]:
            r.fail("capability-map", f"capability `{s}` at {lv} has parent `{p}` at {pc.get('level')}, not one level up")
    # an offer is a library (Holger, commons.o#109 6570298244): an offered L3 no step binds stands on the shelf, no gap
    bound = {c for st in steps.values() for c in st.get("capabilities") or []}
    for s, v in caps.items():
        if v.get("level") == "L3" and s not in bound and not extension:
            r.gap("capability-map", f"capability `{s}` at L3 is bound by no step: it stands nowhere yet")
    # in a commons' own model, an entity or a solution no step uses is a gap too (R9, R28; D1, commons.o#109 6571965126)
    used = {e for st in steps.values() for e in st.get("entities") or []}
    for s in by.get("entity", {}) if not extension else ():
        if s not in used:
            r.gap("bindings", f"entity `{s}`: no step uses it yet")
    for s, v in by.get("solution", {}).items() if not extension else ():
        if not bound & set(v.get("carries") or []):
            r.gap("bindings", f"solution `{s}`: no step uses what it carries yet")

    # bodies (R13): the part_of chain has no cycle,
    for s in bodies:
        chain, cur = [], s
        while cur in bodies and cur not in chain:
            chain.append(cur)
            cur = bodies[cur].get("part_of")
        if cur in chain:
            r.fail("bodies", f"body `{s}` is part of itself through {' → '.join(chain + [cur])}")
    # and at least one of its Posts is held by a human: agents only fail, none held by a human yet is a gap
    for s in bodies:
        held = [[h for h in p.get("held_by") or [] if not h.get("until")] for p in posts.values() if p.get("of") == s]
        if any(h.get("kind") == "human" for c in held for h in c):
            continue
        if held and all(c and all(h.get("kind") == "agent" for h in c) for c in held):
            r.fail("bodies", f"body `{s}` is held by agents only: a Body has at least one Post held by a human")
        else:
            r.gap("bodies", f"body `{s}`: no Post of it is held by a human yet")

    # no-persons (R11)
    for x in recs:
        allowed = set()
        if x.get("kind") == "post":
            allowed.add(x.get("accountable"))
            for h in x.get("held_by") or []:
                allowed |= {h.get("id"), h.get("on_behalf_of")}
            allowed.add(((x.get("safeguards") or {}).get("review") or {}).get("by"))
        for t in strings(x):
            if EMAIL.search(t) or PHONE.search(t):
                r.fail("no-persons", f"{x.get('kind')} `{x.get('slug')}` holds an e-mail address or a telephone number")
            for m in IDENT.findall(t):
                if m not in allowed:
                    r.fail("no-persons", f"{x.get('kind')} `{x.get('slug')}` names `{m}` outside a Post's identifiers")

    # kinds-apart (R1)
    for s in set(by.get("stakeholder", {})) & set(by.get("entity", {})):
        r.fail("kinds-apart", f"`{s}` is both a stakeholder and an entity")

    # accountable (R15) and safeguards (R17)
    def human_for(body, where, seen=()):
        """a Body's accountability: its steward Post `<body>.steward`, else the Body it is part of"""
        if body in seen:
            r.gap("accountable", f"{where}: the chain of accountability returns to `{body}`")
            return None
        if body not in bodies:
            r.gap("accountable", f"{where}: `{body}` names no Body of the model; accountability is held outside it")
            return None
        steward = posts.get(f"{body}.steward")
        if steward:
            a = steward.get("accountable") or ""
            if HUMAN.match(a):
                return a
            if a.startswith("body:"):
                return human_for(a[5:], where, seen + (body,))
        nxt = bodies[body].get("part_of")
        if nxt is None:
            r.gap("accountable", f"{where}: the chain ends at `{body}` without a human; accountability is held "
                                 "outside the model")
            return None
        return human_for(nxt, where, seen + (body,))

    for s, v in posts.items():
        resolve("body", v.get("of"), f"post `{s}`, of")
        a = v.get("accountable") or ""
        if a.startswith("body:"):
            human_for(a[5:], f"post `{s}`, accountable")
        cur = [h for h in v.get("held_by") or [] if not h.get("until")]
        if not cur:
            r.gap("accountable", f"post `{s}` is vacant: nobody serves it now")
        elif all(h.get("kind") == "agent" for h in cur) and not v.get("safeguards"):
            r.fail("safeguards", f"post `{s}` is served by agents only and carries no safeguards")

    # addresses (R18)
    for i, a in enumerate(model.get("addresses") or []):
        to = a.get("to") or {}
        k, s, w = to.get("kind"), to.get("slug"), f"address {i + 1} from `{a.get('from')}`"
        held = None
        if k == "dimension":
            held = s in DIMENSIONS or r.fail("addresses", f"{w}: `{s}` is no dimension of the grammar")
        elif k == "family":
            held = s in dim_of or r.fail("addresses", f"{w}: `{s}` is no family of the grammar")
        elif k == "step":
            held = s in steps
        elif k:
            held = s in by.get(k, {})
        if held is False:
            r.gap("addresses", f"{w}: the {k} `{s}` is not in this model, so the address recognises nothing yet")

    # shells (R19)
    for x in recs:
        if x.get("kind") not in SHELLED and ("shell" in x or "shells" in x):
            r.should("shells", f"{x.get('kind')} `{x.get('slug')}` names a shell; only stakeholders, journeys, "
                               "touchpoints and value exchanges do")
    for s, v in by.get("stakeholder", {}).items():
        if not v.get("shell"):
            r.should("shells", f"stakeholder `{s}` names no shell")

    # canon (R21)
    path = canon_path or CANON
    if not os.path.exists(path):
        r.gap("canon", "the canon data is not at hand; the families are not compared")
    else:
        c = yaml.safe_load(open(path, encoding="utf-8")) or {}
        theirs = {f["slug"]: f["vsd"] for f in c.get("vsf") or []}
        if theirs != dim_of:
            r.fail("canon", f"the families differ from the canon data: {sorted(set(theirs) ^ set(dim_of))}")
    return r


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("--canon")
    ap.add_argument("--bindings", action="store_true")
    ap.add_argument("--catalogue", "--extension", dest="catalogue", action="store_true")
    a = ap.parse_args()
    if os.path.isfile(os.path.join(a.model, ".commons", "commons.yml")):   # a CORE's root: its own model is its runtime
        runtime = os.path.join(a.model, "models", "runtime")
        print(f"# {a.model} is a CORE: its own model is its runtime, so `{runtime.replace(os.sep, '/')}` is checked; "
              f"its installed copies are checked by check_core.py")
        a.model = runtime
    if a.catalogue and os.path.isdir(a.model):   # a model folder: the grammar and the catalogue's own checks (R28, R29)
        import catalogue                   # here, not above: it reads this module
        r = catalogue.Report()             # the catalogue's report, which also holds what the depth counts
        catalogue.catalogue(r, a.model)
        n = {o: sum(1 for i in r.items if i[0] == o) for o in ("fail", "should", "gap")}
        print(f"# {a.model}: {n['fail']} fail · {n['should']} should · {n['gap']} gap")
        for o, c, t in r.items:
            print(f"{o}: {c}: {t}")
        for t in r.notes:
            print(f"note: {t}")
        return 1 if n["fail"] else 0
    model = load(a.model)
    if a.bindings:
        print("\n".join(binding_ids([x for x in model.get("records") or [] if isinstance(x, dict)])))
        return 0
    r = check(model, a.canon, a.catalogue)
    n = {o: sum(1 for i in r.items if i[0] == o) for o in ("fail", "should", "gap")}
    print(f"# {a.model}: {n['fail']} fail · {n['should']} should · {n['gap']} gap")
    for o, c, t in r.items:
        print(f"{o}: {c}: {t}")
    return 1 if n["fail"] else 0


if __name__ == "__main__":
    sys.exit(main())
