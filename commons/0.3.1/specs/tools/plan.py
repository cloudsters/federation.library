#!/usr/bin/env python3
"""plan.py — a commons' plan, its blueprint (`blueprint` R1–R25), read and judged; read-only, it never writes.

The plan is read from three layers, each only adding (R1): the frame, `specs/blueprint.yml` of the installed Commons
model; the primary domain model's layer, `blueprint.yml` at its copy's root; and the commons' own, `blueprint.yml` at
the CORE's root (structure key `blueprint`, structure 0.4.1). Their earlier places, `specs/views/blueprint.yml` and
`views/blueprint.yml`, are read and reported as unmigrated. A later layer's `faces` give an earlier section labels,
questions of the same meaning (R25), a domain's stricter evidence and a visibility (R22). The section `family` yields
one instance `<dimension>.<family>` per family, and a `per-selected` section one instance `element.<kind>.<slug>` per
record the commons selected (R9). Every section and instance gets one outcome, computed and never kept (R11):
`covered`, `on-shelf`, `missing`, `documented-absence` or `unsighted`, judged as part 5 says.

    python plan.py <core> [--json]     the plan with each section's outcome, in reading order

check_core.py runs `check(r, core)`, the checks of `blueprint` part 6: layers, frame, ids, binds, selection, outcomes,
evidence and reads; `trend` is reported as a gap until it is built (BP-5).
"""
import argparse
import glob
import json
import os
import sys

import jsonschema
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True   # the tools never write into the install they lie in (SPECIFICATION R29)
sys.path.insert(0, HERE)
import check_model  # noqa: E402
import layout  # noqa: E402

SCHEMA = os.path.join(HERE, "..", "schemas", "blueprint.schema.json")
KNOWLEDGE_SCHEMA = os.path.join(HERE, "..", "schemas", "core-knowledge.schema.json")
FRAME = os.path.join(HERE, "..", "blueprint.yml")          # the frame of the Commons model this tool comes with
SHELLS = ["SEED", "CORE", "PEER", "OPEN", "DOCK", "ROAM"]   # from the centre outward (mcp part 5; blueprint part 5)
CLASSES = {"public": "ROAM", "member": "OPEN", "personal": "CORE"}   # access.yml's default `classes` (mcp part 5)
ELEMENTS = ["stakeholder", "journey", "touchpoint", "value-exchange", "value-stream", "capability", "entity", "solution", "body"]
RECORD_KINDS = set(ELEMENTS) | {"loop"}
MODEL_KINDS = RECORD_KINDS | {"family", "element"}
OUTCOMES = ["covered", "on-shelf", "missing", "documented-absence", "unsighted"]
FRAME_IDS = (["identity", "identity.cores", "mandate", "purpose", "values", "qualities", "situation", "environment",
              "d0", "d1", "d2", "d3", "d4", "family"] + [f"element.{e}" for e in ELEMENTS] +
             ["knowledge", "lifecycle.path", "lifecycle.history", "lifecycle.near-future", "lifecycle.futures", "loops"])


def yml(p):
    try:
        return yaml.safe_load(open(p, encoding="utf-8")) if p and os.path.isfile(p) else None
    except yaml.YAMLError:
        return None


def shown(p, core):
    """a path as the CORE's reader sees it: relative to the CORE where it lies in it"""
    rel = os.path.relpath(os.path.abspath(p), os.path.abspath(core)) if core else p
    return (rel if not rel.startswith("..") else p).replace(os.sep, "/")


# --- the three layers (R1) ---------------------------------------------------------------------------------------

def frame_place(core):
    """(path, earlier): the frame of the installed Commons model, its earlier place `specs/views/blueprint.yml`, else
    this tool's own frame"""
    for base in sorted(glob.glob(os.path.join(core, "models", "commons", "*", "commons", "specs")) +
                       glob.glob(os.path.join(core, "extensions", "*", "commons-essentials", "specs"))) if core else []:
        if os.path.isfile(os.path.join(base, "blueprint.yml")):
            return os.path.join(base, "blueprint.yml"), False
        if os.path.isfile(os.path.join(base, "views", "blueprint.yml")):
            return os.path.join(base, "views", "blueprint.yml"), True
    return FRAME, False


def domain_place(at):
    """(path, earlier): the primary domain model's layer at its copy's root, its earlier place the layer derived at
    release, `views/blueprint.yml`; (None, False) where it holds none"""
    for p, earlier in ((os.path.join(at, "blueprint.yml"), False), (os.path.join(at, "views", "blueprint.yml"), True)) if at else []:
        if os.path.isfile(p):
            return p, earlier
    return None, False


def own_place(core):
    """(path, earlier): the commons' own layer, structure key `blueprint` (0.4.1), its earlier place `views/blueprint.yml`"""
    if not core:
        return None, False
    try:
        p, old = layout.locate(core, "blueprint")
    except Exception:                                # a structure definition without the key reads the default
        p, old = None, None
    if p and os.path.isfile(p) and p.endswith((".yml", ".yaml")):
        return p, bool(old)
    for q, earlier in ((os.path.join(core, "blueprint.yml"), False), (os.path.join(core, "views", "blueprint.yml"), True)):
        if os.path.isfile(q):
            return q, earlier
    return None, False


def layers(core, at):
    """[(layer, path or None, document, earlier)] for the frame, the domain and the commons, in that order"""
    return [(name, p, (yml(p) or {}) if p else {}, earlier)
            for name, (p, earlier) in (("frame", frame_place(core)), ("domain", domain_place(at)), ("commons", own_place(core)))]


def family_titles():
    """the thirteen families' titles, from the canon the Commons model releases (`specs/value-creation-canon.yml`)"""
    d = yml(os.path.join(HERE, "..", "value-creation-canon.yml")) or {}
    return {f.get("slug"): f.get("title") for f in d.get("vsf") or [] if isinstance(f, dict)}


def instances(order, rd):
    """the frame with its instances (R9): `family` as one `<dimension>.<family>` per family, within its dimension and
    following it; a `per-selected` section followed by one `element.<kind>.<slug>` per record of its kind the runtime
    holds"""
    pattern = next((s for s in order if s.get("cardinality") == "per-family"), None)
    titles = family_titles()
    out = []
    for s in order:
        if s.get("cardinality") == "per-family":
            continue
        out.append(s)
        b = s.get("binds") or {}
        if pattern and b.get("kind") == "dimension":
            for fam, dim in rd.dims.items():
                if dim == b.get("slug"):
                    out.append(dict(pattern, id=f"{dim}.{fam}", within=dim, binds={"kind": "family", "slug": fam},
                                    cardinality="one", _pattern=pattern["id"], labels={"en": titles.get(fam, fam)}))
        if s.get("cardinality") == "per-selected":
            kind = b.get("slug")
            for k in sorted(x for x in rd.own if x.startswith(f"{kind}:") and "/" not in x):
                slug = k.split(":", 1)[1]
                out.append(dict(s, id=f"element.{kind}.{slug}", within=s["id"], binds={"kind": kind, "slug": slug},
                                cardinality="one", _pattern=s["id"], labels={rd.lang: str((rd.own[k] or {}).get("title") or slug)}))
    return out


def merged(lays, rd=None):
    """the plan's sections in reading order, each with `_from` its layer: the frame's order, with its instances where a
    reading `rd` is given; a later layer's section after the last section of the one it lies within; a later layer's
    `faces` applied to earlier sections; an id an earlier layer holds is never taken (R5)"""
    order, ids = [], set()
    for name, _, doc, _ in lays:
        for s in doc.get("sections") or []:
            if not isinstance(s, dict) or not s.get("id") or s["id"] in ids:
                continue
            s = dict(s, _from=name)
            if name == "frame" or not s.get("within"):
                order.append(s)
            else:
                at = max((i for i, x in enumerate(order) if x["id"] == s["within"] or x.get("within") == s["within"]
                          and x["_from"] != "frame"), default=len(order) - 1)
                order.insert(at + 1, s)
            ids.add(s["id"])
        if name == "frame" and rd is not None:
            order = instances(order, rd)
            ids |= {s["id"] for s in order}
        for sid, face in (doc.get("faces") or {}).items() if name != "frame" else []:
            for s in order:
                if isinstance(face, dict) and (s["id"] == sid or s.get("_pattern") == sid):
                    apply_face(s, face, name)
    return order


def apply_face(s, face, layer):
    """a face given to an earlier section (R22, R25): labels; questions replaced one by one; a domain's evidence raised
    from `sourced` to `triangulated`, never lowered; a domain's visibility only further in, a commons' either way"""
    if face.get("labels"):
        s["labels"] = dict(s.get("labels") or {}, **face["labels"])
    if face.get("questions"):
        s["questions"] = list(face["questions"])
    if face.get("evidence") == "triangulated" and s.get("evidence") == "sourced" and layer == "domain":
        s["evidence"] = "triangulated"
    v = face.get("visibility")
    if v in SHELLS and (layer == "commons" or SHELLS.index(v) < SHELLS.index(s.get("visibility") or "ROAM")):
        s["visibility"] = v


# --- what answers a section (R8, R11, R13, R14) ------------------------------------------------------------------

class Knowledge:
    """the CORE's claims and sources, its access classes, its party register and its perspective"""

    def __init__(self, core):
        cl = yml(layout.path(core, "claims")) if core else None
        so = yml(layout.path(core, "sources")) if core else None
        self.claims = [c for c in ((cl or {}).get("claims") if isinstance(cl, dict) else cl) or [] if isinstance(c, dict)]
        self.sources = {s.get("id"): s for s in ((so or {}).get("sources") if isinstance(so, dict) else so) or [] if isinstance(s, dict)}
        acc = yml(os.path.join(core, ".commons", "access.yml")) if core else None
        self.classes = dict(CLASSES, **((acc or {}).get("classes") or {}))
        pe = yml(layout.path(core, "people")) if core else None
        rows = (pe or {}).get("people") if isinstance(pe, dict) else pe
        self.people = {str(v) for p in rows or [] if isinstance(p, dict) for v in (p.get("id"), p.get("handle"), p.get("github")) if v}
        cfg = yml(os.path.join(core, ".commons", "commons.yml")) if core else None
        self.observed = (cfg or {}).get("perspective") == "observed"
        self.superseded = {c.get("supersedes") for c in self.claims if c.get("supersedes")}
        try:
            ks = json.load(open(KNOWLEDGE_SCHEMA, encoding="utf-8"))
            self.claim_check = jsonschema.Draft202012Validator(dict(ks["$defs"]["claim"], **{"$defs": ks["$defs"]}))
        except (OSError, KeyError, ValueError):
            self.claim_check = None

    def contested(self, c):
        """contested and unresolved: its `contested_by` not empty and no claim superseding it (part 5)"""
        return bool(c.get("contested_by")) and c.get("id") not in self.superseded

    def about(self, names, kinds=None):
        """the claims about any of `names`, of one of `kinds` where they are named, a superseded claim never"""
        return [c for c in self.claims if set(map(str, c.get("about") or [])) & names and c.get("id") not in self.superseded
                and (not kinds or c.get("kind") in kinds)]

    def valid(self, c):
        return self.claim_check is None or not any(True for _ in self.claim_check.iter_errors(c))

    def reaches(self, sid, visibility):
        """a source's access class reaches as far out as the section's visibility (R14): a source without a class is
        public where its origin is, else personal; in an observed CORE only a public source reaches"""
        s = self.sources.get(sid)
        if not s:
            return False
        cls = s.get("class") or ("public" if s.get("origin") == "public" else "personal")
        if self.observed and cls != "public":
            return False
        shell = self.classes.get(cls)
        return shell in SHELLS and visibility in SHELLS and SHELLS.index(shell) >= SHELLS.index(visibility)

    def meets(self, c, rule, visibility):
        """a claim meets the evidence rule (R13), on the sources that reach the section's visibility (R14)"""
        srcs = [x for x in c.get("sources") or [] if self.reaches(x, visibility)]
        if rule == "own-word":
            return c.get("kind") == "self-description" and any(
                self.sources[x].get("origin") == "given" and str(self.sources[x].get("given_by") or "") in self.people
                and self.sources[x].get("confirmed") for x in srcs)
        if rule == "sourced":
            return len(srcs) >= 1
        if rule == "triangulated":
            distinct = {self.sources[x].get("copy_of") or x for x in srcs}
            itself = sum(1 for x in srcs if self.sources[x].get("about_itself"))
            return (len(distinct) >= 2 and itself <= 1) or (len(srcs) >= 1 and bool(c.get("limitation")))
        return True


class Judge:
    """one outcome per section and instance of a CORE's plan (R11), each judged once"""

    def __init__(self, rd, order):
        self.rd, self.cfg, self.order = rd, rd.cfg, order
        self.kn = Knowledge(rd.core)
        self.memo = {}
        self.broken = self.model_fails()

    def model_fails(self):
        """the runtime's records the model check fails (`computed`: each record passing check_model with its bindings)"""
        reg = layout.runtime(self.rd.core) if self.rd.core else None
        if not reg or not os.path.isdir(reg):
            return set()
        try:
            rep = check_model.check(check_model.load(reg))
        except Exception:
            return set()
        texts = [t for o, _, t in rep.items if o == "fail"]
        return {k for k in self.rd.own if "/" not in k and any(f"`{k.split(':', 1)[1]}`" in t for t in texts)}

    def records(self, sec):
        """(held, offered): the runtime's records under what the section binds, and whether an installed model holds any"""
        rd, b = self.rd, sec.get("binds") or {}
        kind, slug = b.get("kind"), b.get("slug")
        plain = lambda recs: [k for k in recs if "/" not in k]
        if kind in RECORD_KINDS:
            if slug:
                k = f"{kind}:{slug}"
                own = rd.origin_of(k)[0] if rd.origin_of(k)[1] is not None else None
                return ([own] if own else []), k in rd.offered
            return [k for k in plain(rd.own) if k.startswith(f"{kind}:")], any(k.startswith(f"{kind}:") for k in plain(rd.offered))
        if kind == "family":
            return rd.streams(slug, rd.own), bool(rd.streams(slug, rd.offered))
        if kind == "element":
            return [k for k in plain(rd.own) if k.startswith(f"{slug}:")], any(k.startswith(f"{slug}:") for k in plain(rd.offered))
        return [], False

    def outcome(self, sec):
        """(outcome, note) of one section or instance (R11, part 5)"""
        if sec["id"] not in self.memo:
            self.memo[sec["id"]] = self.judge(sec)
        return self.memo[sec["id"]]

    def judge(self, sec):
        rd, kn = self.rd, self.kn
        rule, vis = sec.get("evidence") or "computed", sec.get("visibility") or "CORE"
        b = sec.get("binds") or {}
        kind = b.get("kind")
        names = {sec["id"]} | ({str(b["about"])} if b.get("about") else set())
        claims = kn.about(names, set(sec.get("answers") or []) or None) if b.get("about") or kind != "knowledge" else []
        if b.get("claim"):
            claims = [c for c in claims if c.get("kind") == b["claim"]]
        if sec.get("empty") == "absence":             # a documented absence: a claim of absence meeting the rule
            gone = [c for c in kn.about(names) if c.get("absence") is True and not kn.contested(c)
                    and kn.meets(c, "sourced" if rule == "computed" else rule, vis)]
            if gone:
                return "documented-absence", None
        if kind == "worlds":
            mine = str(self.cfg.get("id") or "")
            worlds = [s for s in self.cfg.get("sources") or [] if isinstance(s, dict) and str(s.get("world_of") or "") == mine]
            return ("covered", None) if worlds else ("unsighted", "no world of this commons is at hand")
        if kind == "dimension":                       # each family instance within it covered or a documented absence
            fams = [s for s in self.order if s.get("within") == sec["id"] and (s.get("binds") or {}).get("kind") == "family"]
            outs = [self.outcome(s)[0] for s in fams]
            if fams and all(o in ("covered", "documented-absence") for o in outs):
                return "covered", None
            if outs and all(o == "on-shelf" for o in outs):
                return "on-shelf", None
            done = sum(o in ("covered", "documented-absence") for o in outs)
            reached = any(self.records(s)[0] or self.records(s)[1] for s in fams)
            if not done and not reached:
                return "missing", ("not offered" if rd.ref else None)
            return "missing", (f"{done} of {len(fams)} families covered" if fams else None)
        if kind == "knowledge" and not b.get("about"):   # the whole claim register: at least one claim, each valid
            if not kn.claims:
                return "missing", None
            bad = [c.get("id") for c in kn.claims if not kn.valid(c)]
            return ("missing", f"{len(bad)} claims not valid") if bad else ("covered", None)
        if kind in MODEL_KINDS:
            held, offered = self.records(sec)
            if not held:
                return ("on-shelf", None) if offered else ("missing", "not offered" if rd.ref else None)
            if rule == "computed":
                broken = [k for k in held if k in self.broken]
                return ("missing", f"{len(broken)} records fail the model check") if broken else ("covered", None)
        elif kind == "identity":
            if not self.cfg.get(b.get("field")):
                return "missing", None
        elif kind == "lifecycle":
            there = os.path.isfile(os.path.join(rd.core, "lifecycle", "stage.yml")) if b.get("of") == "stage" else \
                bool(glob.glob(os.path.join(rd.core, "lifecycle", "events", "*.y*ml")))
            if not there:
                return "missing", None
        elif kind == "knowledge" and not claims:
            return "missing", None
        if rule == "computed":
            return "covered", None
        good = [c for c in claims if c.get("absence") is not True and kn.meets(c, rule, vis)]   # the claim carrying its standing
        if not good:
            return "missing", "answered, awaiting evidence" if claims else "awaiting a claim of its standing"
        if all(kn.contested(c) for c in good):
            return "missing", "contested"
        return "covered", None


# --- the checks of part 6 ----------------------------------------------------------------------------------------

def reads_cycle(order):
    """a cycle in `reads` as the ids along it, else None (R16)"""
    graph = {s["id"]: list(s.get("reads") or []) for s in order}
    state = {}

    def visit(n, path):
        if state.get(n) == 1:
            return path[path.index(n):] + [n]
        if state.get(n) == 2 or n not in graph:
            return None
        state[n] = 1
        for m in graph[n]:
            found = visit(m, path + [n])
            if found:
                return found
        state[n] = 2
        return None

    for n in graph:
        found = visit(n, [])
        if found:
            return found
    return None


def check(r, core, rd=None):
    """the checks of `blueprint` part 6 over the CORE's plan, reported into `r` (check_core's Report)"""
    import render_blueprint   # here, not above: it reads this module
    try:
        rd = rd or render_blueprint.Reading(core)
    except Exception as e:                          # a CORE whose models cannot be read: its plan is not judged
        r.gap("layers", f"the plan is not read: the CORE's models cannot be read ({type(e).__name__}: {e})")
        return {}
    lays = layers(core, rd.at)
    v = jsonschema.Draft202012Validator(json.load(open(SCHEMA, encoding="utf-8")))
    where = {}
    for name, p, doc, earlier in lays:
        if not p:
            continue
        at = shown(p, core)
        if earlier:
            r.gap("layers", f"the {name}'s layer is read at its earlier place `{at}`: unmigrated (part 5)")
            continue                                  # an earlier layer is read as it was, never judged by today's schema
        for e in sorted(v.iter_errors(doc), key=lambda e: list(e.path)):
            r.fail("layers", f"`{at}`: {'/'.join(map(str, e.path)) or '(root)'}: {e.message[:200]} (R4)")
        for s in doc.get("sections") or []:
            if isinstance(s, dict) and s.get("id"):
                if s["id"] in where:
                    r.fail("ids", f"`{at}`: the section `{s['id']}` is the {where[s['id']]}'s too: an id is unique across the layers (R5)")
                else:
                    where[s["id"]] = name
    order, plain = merged(lays, rd), merged(lays)
    ids = {s["id"] for s in order} | {s["id"] for s in plain}
    old = {name for name, _, _, earlier in lays if earlier}
    judged = [s for s in plain if s["_from"] not in old]   # a layer at its earlier place is read, never judged by today's rules
    taken = {s["id"] for s in order if s.get("_pattern")}   # the frame's instances hold their ids too (R5, R9)
    for name, p, doc, earlier in lays[1:]:
        for s in doc.get("sections") or [] if not earlier else []:
            if isinstance(s, dict) and s.get("id") in taken:
                r.fail("ids", f"`{shown(p, core)}`: the section `{s['id']}` takes the id of a frame instance (R5, R9)")
    # layers (R1, R6, R7, R22)
    for s in judged:
        if s["_from"] != "frame" and not s.get("within"):
            r.fail("layers", f"the {s['_from']}'s section `{s['id']}` lies within no section; only a top section of the frame does (R1)")
        elif s.get("within") and s["within"] not in ids:
            r.fail("layers", f"the section `{s['id']}` lies within `{s['within']}`, which no layer holds (R1)")
    base = {s["id"]: s for s in merged(lays[:1])}
    for name, p, doc, earlier in lays[1:]:
        for sid, face in (doc.get("faces") or {}).items() if not earlier else []:
            if sid not in ids:
                r.fail("layers", f"the {name}'s layer gives a face to `{sid}`, which no earlier layer holds (R6, R7)")
                continue
            was = base.get(sid) or {}
            if isinstance(face, dict) and name == "domain" and face.get("visibility") in SHELLS and was.get("visibility") in SHELLS \
                    and SHELLS.index(face["visibility"]) > SHELLS.index(was["visibility"]):
                r.fail("layers", f"the domain's face of `{sid}` widens its visibility from {was['visibility']} to {face['visibility']}; a domain only narrows (R22)")
            if isinstance(face, dict) and face.get("evidence") and (name != "domain" or was.get("evidence") != "sourced"):
                r.fail("layers", f"the {name}'s face of `{sid}` raises its evidence to {face['evidence']}: only a domain does, and only from `sourced` (R22)")
    # frame (R2, R9)
    frame = [s for s in plain if s["_from"] == "frame"]
    got = [s["id"] for s in frame]
    if set(FRAME_IDS) - set(got) or [i for i in got if i in FRAME_IDS] != [i for i in FRAME_IDS if i in got]:
        r.fail("frame", f"the frame holds {len(set(FRAME_IDS) & set(got))} of the {len(FRAME_IDS)} sections of part 5, or not in "
                        f"their order; missing: {sorted(set(FRAME_IDS) - set(got))[:5]} (R2)")
    for s in frame:
        if not s.get("questions"):
            r.fail("frame", f"the frame's section `{s['id']}` asks no question (R2)")
        if s.get("evidence") != "computed" and not s.get("answers"):
            r.fail("frame", f"the frame's section `{s['id']}` names no claim kinds its answers take, and its evidence is not computed (R2)")
    want = {f"{d}.{f}" for f, d in rd.dims.items()}
    if any(s.get("cardinality") == "per-family" for s in frame) and not want <= {s["id"] for s in order}:
        r.fail("frame", f"the section `family` yields {len(want & {s['id'] for s in order})} of the {len(want)} family instances (R9)")
    # binds (R8)
    for s in judged:
        b = s.get("binds") or {}
        if any("/" in str(b.get(k) or "") or "\\" in str(b.get(k) or "") for k in ("slug", "field", "about")):
            r.fail("binds", f"the section `{s['id']}` binds by a path, `{b}`, never by key (R8)")
    # reads (R16)
    for s in judged:
        for x in s.get("reads") or []:
            if x not in ids:
                r.fail("reads", f"the section `{s['id']}` reads `{x}`, which the plan does not hold (R16)")
    cyc = reads_cycle(judged)
    if cyc:
        r.fail("reads", f"`reads` forms a cycle: {' → '.join(cyc)} (R16)")
    # selection (R10)
    for fam in rd.dims:
        runs = rd.streams(fam, rd.own)
        carry = [k for k in runs if (rd.own[k] or {}).get("essential") is True]
        if len(carry) > 1:
            r.fail("selection", f"the family `{fam}` has {len(carry)} carrying streams, {', '.join(carry)}: at most one carries `essential: true` (R10)")
        elif runs and not carry:
            r.gap("selection", f"the family `{fam}` runs {len(runs)} streams and none carries it: an open decisive selection (R10)")
    # outcomes and evidence (R11, R13, R14)
    judge, counts, waiting = Judge(rd, order), {}, []
    for s in order:
        if s.get("cardinality") == "per-selected":
            continue                                 # its instances carry the outcomes
        o, note = judge.outcome(s)
        if o not in OUTCOMES:
            r.fail("outcomes", f"the section `{s['id']}` has no outcome of part 5 (R11)")
        counts[o] = counts.get(o, 0) + 1
        if note == "answered, awaiting evidence":
            waiting.append(s["id"])
    r.gap("outcomes", "the plan: " + ", ".join(f"{counts.get(o, 0)} {o}" for o in OUTCOMES) + " (R11)")
    if waiting:
        r.gap("evidence", f"{len(waiting)} sections are answered below their evidence rule, e.g. `{waiting[0]}` (R13, R14)")
    r.gap("trend", "coverage over the history is not yet computed (R18, BP-5)")
    return counts


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("core")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    import render_blueprint
    rd = render_blueprint.Reading(a.core)
    order = merged(layers(a.core, rd.at), rd)
    judge = Judge(rd, order)
    rows = []
    for s in order:
        o, note = judge.outcome(s)
        rows.append({"id": s["id"], "layer": s["_from"], "outcome": o, **({"note": note} if note else {})})
    if a.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
    else:
        for x in rows:
            print(f"{x['id']:40} {x['outcome']}" + (f" · {x['note']}" if x.get("note") else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
