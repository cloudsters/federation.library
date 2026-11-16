#!/usr/bin/env python3
"""render_blueprint.py — renders a CORE's blueprint, the whole commons section by section, and its three model cuts,
from its records (core-views R1, R3, R8; the run's forms, commons.o#109, part E). Nothing is kept: every file is
generated, and its provenance record names what it rests on.

The plan is read from its three layers by plan.py (blueprint R1, part 5), in order, each only adding:
  1. the frame: `specs/blueprint.yml` of the installed Commons model (else the copy beside this tool), with one
     instance `<dimension>.<family>` of the section `family` per family and one `element.<kind>.<slug>` per selected
     record (R9);
  2. the primary domain model's layer: `blueprint.yml` at its installed copy's root;
  3. the commons' own: `blueprint.yml` at the CORE's root;
each read at its earlier place `views/blueprint.yml` too, as unmigrated. Outcomes are plan.py's (blueprint R11), and
the `gaps` view lists every section not covered with what it asks (R20).

One definition, three cuts (D1, commons.o#109 6569487111, rules A–D). Every cut renders the frame, all 13 families
among it, and each extension section under its `within`; what the offer does not reach reads *not offered*.
- **blueprint:** one outcome per section (R3): `covered` where the commons holds the record, activated or its own;
  `on-shelf` where an installed model holds it and the runtime has not built it, neither a gap nor a decision, with its
  record as the expected picture (`not-selected` its earlier name, and the history's not selected read as it); and
  `missing` otherwise, `missing · not offered` where the installed models hold none;
- **value cut:** families → streams with their outcome → steps → capabilities, by title with the slug beside;
  a family's streams in the order delivered: the commons' own `order` for the family where `commons.yml` states one,
  else the lists of its extensions' offers (`offer.yml` `order`), the primary first, then the others as pinned; an
  activated stream stands at its origin's place; what no list names follows, by title (CORE-VIEWS R21);
- **entity cut:** each entity with its type, fields, states and relations; a field or relation naming no record of
  the commons or the offer reads *not offered*;
- **element cut:** the records of each of the nine elements, Posts under their Body and value exchanges by
  touchpoint, *between*, *offered → returned*.
Each cut reads *used in* (D1, commons.o#109 6571965126): the commons' own streams and steps that use a record it
holds. A step uses what it binds and the touchpoints it serves, a capability is used where its children are, a solution
and a Body where what they carry or hold is used. The value cut reads it for capabilities, the entity cut for entities,
the element cut for every record. A held capability, entity, solution or touchpoint no stream of
the commons' own uses is a gap, a question for its own library: would it activate it?
With --offer, the offer page renders the frame over a release's own records instead: what a commons would hold, where
to begin, what each stream takes as one package (the same derivation as `build.py`), between whom and what
it asks, the proposals at each touchpoint (the offered streams whose steps serve it), and nothing the essentials do
not hold; depth is served through the MCP, never installed.

Writes into OUT (default: the CORE): `views/briefing/{briefing,gaps,value-model,entity-model,element-model}.md` and
`.provenance/briefing/manifest.json` (core-views part 5; `views/blueprint/` their earlier place); with --offer, `offer.md` and `.provenance/offer/manifest.json`.

Usage:  render_blueprint.py CORE [--out DIR]
        render_blueprint.py --offer RELEASE [--out DIR]
"""
import argparse
import glob
import hashlib
import json
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True   # the tools never write into the install they lie in (SPECIFICATION R29; `extension` R12)
sys.path.insert(0, HERE)
import catalogue  # noqa: E402
import layout  # noqa: E402
import take_update  # noqa: E402
import plan  # noqa: E402


def source(rec):
    """the origin a record names: `origin`, or its earlier key `adopted_from` (CORE R4), as check_model reads it"""
    return (rec.get("origin") or rec.get("adopted_from")) if isinstance(rec, dict) else None

OUT = "views/briefing"                     # the renderings (core-views part 5), `views/blueprint/` their earlier place
FRAME = plan.FRAME                         # the frame of the plan (blueprint part 5), its place moved from specs/views/
ELEMENTS = ["stakeholder", "journey", "touchpoint", "value-exchange", "value-stream", "capability", "entity", "solution", "body"]
PLURAL = {"stakeholder": "stakeholders", "journey": "journeys", "touchpoint": "touchpoints", "value-exchange": "value exchanges",
          "value-stream": "value streams", "capability": "capabilities", "entity": "entities", "solution": "solutions",
          "body": "Bodies", "post": "Posts"}
GENERATOR = "Commons-Engineering/commons.core:specs/tools/render_blueprint.py"
USED = ("capability", "entity", "solution", "touchpoint")   # held and used in no own stream: a gap (CORE-VIEWS R21)
DEPTH = "Deeper capabilities, measures, patterns and systems of record are served through the MCP under a grant."


def yml(p):
    return yaml.safe_load(open(p, encoding="utf-8")) if p and os.path.exists(p) else None


def digest(p):
    return "sha256:" + hashlib.sha256(open(p, "rb").read().replace(b"\r\n", b"\n")).hexdigest() if p and os.path.exists(p) else None


def label(sec, lang):
    ls = sec.get("labels") or {}
    return ls.get(lang) or ls.get("en") or next(iter(ls.values()), sec["id"])


def counted(n, kind):
    return f"{n} {({'body': 'Body', 'post': 'Post'}.get(kind, kind.replace('-', ' ')) if n == 1 else PLURAL[kind])}"


def definitions(core, ext_at, rd=None):
    """the three layers of the plan (blueprint R1), each as (path or None, its sections), and one ordered list of
    sections, a later layer's placed after the section it lies within; with a reading `rd`, the frame's instances in it
    (blueprint R9)"""
    lays = plan.layers(core, ext_at)
    defs = [(p, doc.get("sections") or []) for _, p, doc, _ in lays]
    return defs, plan.merged(lays, rd)

def answers(core):
    """what the commons did not select: the ids an activation names so, `not-selected` archetypes, and the offers it
    activated nothing of (`scope: none`)"""
    unselected, none = set(), set()
    for f in sorted(glob.glob(os.path.join(core, "lifecycle", "events", "*.y*ml"))):
        ev = yml(f) or {}
        act = ev.get("activates") if isinstance(ev.get("activates"), dict) else None
        if ev.get("kind") == "decision" and act:
            unselected |= set(catalogue.not_selected(act))
            if act.get("scope") == "none":
                none.add(str(act.get("extension") or "").split("@")[0])
        if ev.get("kind") == "not-selected" and "#" in str(ev.get("archetype")):
            unselected.add(str(ev["archetype"]).split("#", 1)[1])
    return unselected, none


class Reading:
    """a CORE read once: its settings, its primary extension's installed copy, its own records and its answers; or,
    with `release`, a release alone, as the offer page reads it: the offered records and nothing held"""

    def __init__(self, core=None, release=None):
        self.core = core
        if release:
            rel = yml(os.path.join(release, "release.yml")) or {}
            self.cfg, self.rel, self.at = {}, rel, release
            self.ref = layout.ref_of({"id": f"{rel.get('library')}/{layout.release_id(rel)}", "variant": rel.get("variant")})   # `model`, a variant's own
            self.version = str(rel.get("version"))
            roots = [os.path.join(release, "specs")]   # the bindings its kind declares (`x-refers`)
        else:
            self.cfg = yml(os.path.join(core, ".commons", "commons.yml")) or {}
            prim = next((x for x in layout.pins(self.cfg) if x.get("primary")
                         and str(x.get("id")).split("/")[-1] not in layout.ESSENTIALS), None)
            self.ref = layout.ref_of(prim) if prim else None   # a variant's own folder (MODEL R30)
            self.version = str(prim["version"]) if prim else None
            self.at = layout.copy(core, self.ref) if self.ref else None
            self.rel = yml(os.path.join(self.at, "release.yml")) or {} if self.at else {}
            roots = take_update.spec_roots(core, self.ref, self.at) if self.ref else []
        self.offered = {k: rec for k, (rec, _) in catalogue.records(layout.records(self.at)).items()} if self.at else {}
        self.own = {k: rec for k, (rec, _) in catalogue.records(layout.runtime(core)).items()} if core else {}
        self.refers = take_update.declared(*roots)
        self.lang = self.cfg.get("language") or "en"
        self.unselected, none = answers(core) if core else (set(), set())
        self.none = self.ref in none
        self.dims = json.load(open(os.path.join(HERE, "..", "schemas", "model.schema.json"), encoding="utf-8"))["x-dimension-of"]
        self.uses = self.used_by() if core else {}
        self.orders = self.delivered()
        self.loops = {}
        for f in sorted(glob.glob(os.path.join(self.at, "loops", "_family.*.loop.y*ml"))) if self.at else []:
            lp = yml(f) or {}
            if (lp.get("region") or {}).get("vsf"):
                self.loops[lp["region"]["vsf"]] = lp

    def delivered(self):
        """per family, the streams in the order delivered: the commons' own `order` where it states one for the family,
        else its extensions' lists, the primary first, then the others in the order `commons.yml` pins them"""
        offers = [self.at] if self.at else []
        for x in layout.pins(self.cfg) if self.core else []:
            i = layout.ref_of(x) if isinstance(x, dict) else ""
            if "/" in i and i != self.ref and i.split("/")[-1] not in layout.ESSENTIALS:
                offers.append(layout.copy(self.core, i))
        out = {}
        for at in offers:
            for fam, slugs in ((yml(layout.model_file(at)) or {}).get("order") or {}).items():
                out.setdefault(fam, []).extend(s for s in slugs or [] if s not in out.get(fam, []))
        out.update((self.cfg.get("order") or {}) if self.core else {})
        return out

    def rank(self, k):
        """a stream's place in its family: its index in the delivered list, by its own slug or its origin's, else
        after the named ones, by title"""
        rec = self.record(k) or {}
        names = [k.split(":", 1)[1], str(source(rec) or "").rsplit("#value-stream:", 1)[-1]]
        lst = self.orders.get(rec.get("family")) or []
        at = [lst.index(s) for s in names if s in lst]
        return (0, min(at), "") if at else (1, 0, str(rec.get("title") or k).lower())

    def used_by(self):
        """the commons' own steps that use each of its records, `<stream>/<step>` by id: what a step binds and serves,
        a capability where its children are used, a solution and a Body where what they carry or hold is used"""
        use = {}
        for k, rec in self.own.items():
            if k.startswith("value-stream:") and "/" not in k:
                for st in rec.get("steps") or []:
                    for field, kind in (("capabilities", "capability"), ("entities", "entity")):
                        for v in (st.get(field) or []) if isinstance(st, dict) else []:
                            use.setdefault(f"{kind}:{v}", set()).add(f"{rec.get('slug')}/{st.get('slug')}")
        streams = {k.split(":", 1)[1] for k in self.own if k.startswith("value-stream:") and "/" not in k}
        for tp, at in catalogue.serving(self.own).items():
            use.setdefault(f"touchpoint:{tp}", set()).update(s for s in at if s.split("/", 1)[0] in streams)
        for k in [k for k in use if k.startswith("capability:")]:
            seen, p = {k}, (self.own.get(k) or {}).get("parent")
            while p and f"capability:{p}" in self.own and f"capability:{p}" not in seen:
                seen.add(f"capability:{p}")
                use.setdefault(f"capability:{p}", set()).update(use[k])
                p = self.own[f"capability:{p}"].get("parent")
        for k, rec in self.own.items():
            field = {"solution": "carries", "body": "holds"}.get(k.split(":", 1)[0])
            for c in (rec.get(field) or []) if field else []:
                use.setdefault(k, set()).update(use.get(f"capability:{c}", ()))
        # the stakeholder side through its touchpoints: a value exchange at one, a journey and a stakeholder by theirs
        for k in self.own:
            if k.split(":", 1)[0] in ("value-exchange", "journey", "stakeholder"):
                for tp in catalogue.touchpoints_of(self.own, k):
                    use.setdefault(k, set()).update(use.get(tp, ()))
        for k, rec in self.own.items():              # a Post where its Body is used
            if k.startswith("post:"):
                use.setdefault(k, set()).update(use.get(f"body:{rec.get('of')}", ()))
        return {k: v for k, v in use.items() if v}

    def used(self, k):
        """where a held record is used, by stream with its steps; nothing for a record the commons does not hold"""
        ok = self.origin_of(k)[0]
        if ok is None or not self.core:
            return ""
        by = {}
        for x in sorted(self.uses.get(ok, ())):
            s, st = x.split("/", 1)
            by.setdefault(s, []).append(st)
        if not by:
            return " · used in no stream of its own" if ok.split(":", 1)[0] in USED else ""
        return " · used in " + ", ".join(f"`value-stream:{s}` ({', '.join(sts)})" for s, sts in by.items())

    def unused(self, kind):
        """the held records of a kind no stream of the commons' own uses"""
        return [k for k in self.own if k.startswith(f"{kind}:") and "/" not in k and not self.uses.get(k)]

    def origin_of(self, k):
        """the own record activated from an offered id, or the own record of that id"""
        for ok, rec in self.own.items():
            if str(source(rec) or "").split("#", 1)[-1] == k and "#" in str(source(rec)):
                return ok, rec
        return (k, self.own[k]) if k in self.own else (None, None)

    def record(self, k):
        """the record of an id as the commons holds it, else as offered"""
        return self.origin_of(k)[1] or self.offered.get(k)

    def against(self, k):
        return k in self.unselected or (self.none and k in self.offered)

    def state(self, k):
        """how a named id stands: held (''), not selected, offered and not yet, or not offered"""
        if self.core and self.origin_of(k)[1] is not None or not self.core and k in self.offered:
            return ""
        if self.against(k):
            return "not selected"
        return "not yet" if k in self.offered else "not offered"

    def mark(self, k):
        ok, rec = self.origin_of(k)
        if rec is None:
            return "not selected" if self.against(k) else "offered, not yet" if k in self.offered else ""
        src = source(rec)
        if not src:
            return "own"
        diff = catalogue.changed(self.offered.get(k) or {}, rec) if k in self.offered else []
        return f"from `{src}`" + (f", adapted: {', '.join(diff)}" if diff else "")

    def name(self, k, bold=False):
        """a record's title with its id beside it, kind and slug, so that two records of one title are never taken for
        one (rule C; D1, commons.o#109 6570167948, reading 2); an id no record holds, by its id"""
        rec = self.record(k)
        title = rec.get("title") if rec else None
        return (f"**{title}** `{k}`" if bold else f"{title} `{k}`") if title else f"`{k}`"

    def streams(self, fam, recs):
        return sorted((k for k, r in recs.items() if k.startswith("value-stream:") and "/" not in k and r.get("family") == fam),
                      key=self.rank)

    def ids(self, kind):
        """every id of a kind, held or offered, in one order"""
        return sorted({k for k in list(self.own) + list(self.offered) if k.startswith(f"{kind}:") and "/" not in k},
                      key=lambda k: (str((self.record(k) or {}).get("title") or k).lower(), k))

    def outcome(self, sec):
        """one outcome per section (R3), and the expected picture beside `missing`; `not offered` where an offer is
        installed and reaches nothing of the section (rule A)"""
        b = sec.get("binds") or {}
        kind, slug = b.get("kind"), b.get("slug")
        if kind in ELEMENTS:
            k = f"{kind}:{slug}"
            if self.origin_of(k)[1] is not None:
                return "covered", None
            if k in self.offered:                 # on the shelf: neither a gap nor a decision (R3)
                return "on-shelf", self.offered.get(k)
            return "missing", None
        if kind == "family":
            if self.streams(slug, self.own):
                return "covered", None
            offered = self.streams(slug, self.offered)
            if offered:
                return "on-shelf", {"streams": [self.offered[k].get("title") or k for k in offered]}
            return "missing", self.unoffered()
        if kind == "dimension":
            fams = [f for f, d in self.dims.items() if d == slug]
            if any(r.get("family") in fams for k, r in self.own.items() if k.startswith("value-stream:") and "/" not in k):
                return "covered", None
            reached = any(self.streams(f, self.offered) for f in fams)
            return ("on-shelf", None) if reached else ("missing", self.unoffered())
        if kind == "element":
            if any(k.startswith(f"{slug}:") and "/" not in k for k in self.own):
                return "covered", None
            n = sum(1 for k in self.offered if k.startswith(f"{slug}:") and "/" not in k)
            return ("on-shelf", {"offered": n}) if n else ("missing", self.unoffered())
        place = {"knowledge": "knowledge", "lifecycle": os.path.join("lifecycle", "stage.yml")}.get(kind)
        p = (layout.loops(self.core) if kind in ("loops", "operations") else   # `operations`, the frame's earlier section
             os.path.join(self.core, place) if place else None)
        held = p and (os.path.isfile(p) or (os.path.isdir(p) and [x for x in os.listdir(p) if x != ".keep"]))
        return ("covered", None) if held else ("missing", None)

    def unoffered(self):
        return {"not_offered": True} if self.ref else None


def picture(exp):
    if not exp:
        return ""
    if exp.get("not_offered"):
        return "not offered"
    if exp.get("streams"):
        return "expected: " + ", ".join(exp["streams"])
    if exp.get("offered"):
        return f"expected: {exp['offered']} offered"
    return "expected: " + (exp.get("title") or "") + (f" — {exp['summary']}" if exp.get("summary") else "")


def blueprint_md(rd, order):
    lines = [f"# {rd.cfg.get('name') or rd.cfg.get('id')}: briefing", "",
             f"*Generated from the records; never edited. Extension: `{rd.ref}@{rd.version}`.*" if rd.ref else "*Generated from the records; never edited. No extension of its kind installed yet.*", ""]
    counts, outcomes = {}, {}
    judge = plan.Judge(rd, order)
    for s in order:
        o, note = judge.outcome(s)                   # one outcome per section and instance (blueprint R11)
        outcomes[s["id"]] = o
        exp = rd.outcome(s)[1] if o in ("missing", "on-shelf") else None   # the expected picture beside it
        if s.get("cardinality") != "per-selected":   # a per-selected section counts through its instances, as check_core does
            counts[o] = counts.get(o, 0) + 1
        b = s.get("binds") or {}
        if s["id"] == "element.stakeholder":
            lines += ["## The nine elements", ""]
        depth = "####" if s["_from"] != "frame" or (s.get("_pattern") and b.get("kind") != "family") \
            else "###" if b.get("kind") in ("family", "element") else "##"
        lines.append(f"{depth} {label(s, rd.lang)}")
        line = f"`{s['id']}` · **{o}**"
        if note:
            line += f" · {note}"
        if o in ("missing", "on-shelf") and exp and picture(exp) != note:   # the expected picture, never the note twice
            line += f" · {picture(exp)}"
        if (s["_from"] != "frame" or s.get("_pattern")) and o == "covered" and b.get("slug"):
            line += f" · {rd.mark(b.get('kind') + ':' + str(b.get('slug')))}"
        lines.append(line)
        lines.append("")
    return "\n".join(lines), counts, outcomes


def gaps_md(rd, order):
    """the `gaps` view (blueprint R20; core-views): every section and instance not covered, with what it asks, what it
    reads and needs, and the evidence its answer must meet; the only view that shows a section's authoring fields"""
    judge = plan.Judge(rd, order)
    lines = [f"# {rd.cfg.get('name') or rd.cfg.get('id')}: gaps", "",
             "*Generated from the plan and the records; never edited. Every section not covered, as a question to work on.*", ""]
    n = 0
    for s in order:
        if s.get("cardinality") == "per-selected":
            continue                                 # its instances stand for it
        o, note = judge.outcome(s)
        if o == "covered":
            continue
        n += 1
        lines += [f"## {label(s, rd.lang)} `{s['id']}`", "", f"**{o}**" + (f" · {note}" if note else "")
                  + f" · evidence: {s.get('evidence') or 'computed'} · visibility: {s.get('visibility') or 'CORE'}", ""]
        lines += [f"- {q}" for q in s.get("questions") or []]
        if s.get("reads"):
            lines.append(f"- reads: {', '.join(f'`{x}`' for x in s['reads'])}")
        if s.get("needs"):
            lines.append(f"- needs: {', '.join(f'`{x}`' for x in s['needs'])}")
        lines.append("")
    if not n:
        lines += ["Every section is covered.", ""]
    return "\n".join(lines)


def frame_families(order, lang):
    """the frame's dimensions and families in order, as (dimension label, [(family slug, family label)])"""
    out = []
    for s in order:
        b = s.get("binds") or {}
        if s["_from"] == "frame" and b.get("kind") == "dimension":
            out.append((label(s, lang), []))
        elif s["_from"] == "frame" and b.get("kind") == "family" and out:
            out[-1][1].append((b.get("slug"), label(s, lang)))
    return out


def value_model(rd, order):
    lines = ["# Value model", "",
             "*The 13 families of the frame → value streams with their outcome → steps → capabilities; generated, never kept.*", ""]
    for dim, fams in frame_families(order, rd.lang):
        lines += [f"## {dim}", ""]
        for fam, fl in fams:
            lines += [f"### {fl} `family:{fam}`", ""]
            streams = sorted(set(rd.streams(fam, rd.own)) | set(rd.streams(fam, rd.offered)), key=rd.rank)
            if not rd.streams(fam, rd.own):
                lines += ["*nothing held*" + ("" if rd.streams(fam, rd.offered) or not rd.ref else " · not offered"), ""]
            for k in streams:
                rec = rd.record(k)
                lines.append(f"- {rd.name(k, True)} — {rd.mark(k) or 'own'}")
                if rec.get("outcome"):
                    lines.append(f"  - *Outcome:* {rec['outcome']}")
                for st in rec.get("steps") or []:
                    caps = []
                    for c in st.get("capabilities") or []:
                        m = rd.state(f"capability:{c}")
                        caps.append(rd.name(f"capability:{c}") + (f" ({m})" if m else ""))
                    lines.append(f"  - {st.get('title') or st.get('slug')} `{st.get('slug')}`: {', '.join(caps)}")
            if streams:
                lines.append("")
    caps = [k for k in rd.ids("capability") if rd.origin_of(k)[1] is not None]
    if caps:
        lines += ["## Where the capabilities are used", "",
                  f"*{len(rd.unused('capability'))} of {len(caps)} held capabilities are used in no stream of the commons' own.*", ""]
        lines += [f"- {rd.name(k)}{rd.used(k)}" for k in caps] + [""]
    return "\n".join(lines)


def entity_model(rd):
    ents = rd.ids("entity")
    lines = ["# Entity model", "", "*Entities with their fields, states and relations; generated, never kept.*", ""]
    fields = [m[1] for k in ents for a in rd.record(k).get("attributes") or [] if isinstance(a, dict)
              and (m := catalogue.REFERENCE.match(str(a.get("type"))))]
    rels = [x.get("target") for k in ents for x in rd.record(k).get("relations") or [] if isinstance(x, dict)]
    nf, nr = (sum(1 for x in xs if rd.state(f"entity:{x}") == "not offered") for xs in (fields, rels))
    if nf or nr:
        lines += [f"{nf} of {len(fields)} `reference(…)` fields and {nr} of {len(rels)} relations name an entity neither the commons "
                  f"nor the offer holds: *not offered*.", ""]
    for k in ents:
        rec = rd.record(k)
        lines += [f"## {rec.get('title') or k}", "", f"`{k}` · {rec.get('type') or 'untyped'} · {rd.mark(k) or 'own'}{rd.used(k)}", ""]
        if rec.get("attributes"):
            lines += ["| Field | Type | Cardinality |", "|---|---|---|"]
            for a in rec["attributes"]:
                if isinstance(a, dict):
                    m = catalogue.REFERENCE.match(str(a.get("type")))
                    s = rd.state(f"entity:{m[1]}") if m else ""
                    lines.append(f"| {a.get('name')} | {a.get('type')}{' · ' + s if s else ''} | {a.get('card', '')} |")
            lines.append("")
        if rec.get("states"):
            lines += ["States: " + " → ".join(str(x) for x in rec["states"]), ""]
        for r in rec.get("relations") or []:
            if isinstance(r, dict):
                s = rd.state(f"entity:{r.get('target')}")
                lines.append(f"- {r.get('type')} → {rd.name('entity:' + str(r.get('target')))}" + (f" · {s}" if s else ""))
        lines.append("")
    return "\n".join(lines)


def element_model(rd):
    """the records of each of the nine elements (part E; D1, commons.o#109 6569487111, V1): the counts, then every
    record with its mark and where it is used, value exchanges by touchpoint and Posts under their Body"""
    lines = ["# Element model", "", "*The records of each of the nine elements, Posts with their Body; generated, never kept.*", "",
             "| # | Element | Held | Activated | Offered, not yet | Not selected | The commons' own, open | Held, used in no own stream |",
             "|---|---|---|---|---|---|---|---|"]
    for n, e in [(n, e) for n, e in enumerate(ELEMENTS, 1)] + [(9, "post")]:
        own = [k for k in rd.own if k.startswith(f"{e}:") and "/" not in k]
        act = [k for k in own if source(rd.own[k])]
        taken = {str(source(rd.own[k])).split("#", 1)[-1] for k in act}
        rest = [k for k in rd.offered if k.startswith(f"{e}:") and "/" not in k and k not in taken and k not in rd.own]
        no = [k for k in rest if rd.against(k)]
        gap = {"body": ("mandate", lambda r: r.get("mandate") is None), "post": ("held_by", lambda r: not r.get("held_by"))}.get(e)
        opened = f"{sum(1 for k in own if gap[1](rd.own[k]))} `{gap[0]}`" if gap else "—"
        idle = len(rd.unused(e)) if e in USED else "—"
        lines.append(f"| {n} | {e} | {len(own)} | {len(act)} | {len(rest) - len(no)} | {len(no)} | {opened} | {idle} |")
    lines.append("")
    posts = {}
    for k in rd.ids("post"):
        posts.setdefault(f"body:{(rd.record(k) or {}).get('of')}", []).append(k)
    fams = list(rd.dims)
    for n, e in enumerate(ELEMENTS, 1):
        ids = rd.ids(e)
        if e == "value-stream":                  # by family in the frame's order, then as delivered (R21)
            ids.sort(key=lambda k: (fams.index(f) if (f := (rd.record(k) or {}).get("family")) in fams else len(fams), rd.rank(k)))
        lines += [f"## {n} {e.replace('-', ' ').capitalize()}", ""]
        if not ids:
            lines += ["*none*", ""]
            continue
        if e == "value-exchange":
            by = {}
            for k in ids:
                by.setdefault(f"touchpoint:{(rd.record(k) or {}).get('touchpoint')}", []).append(k)
            for tp in sorted(by, key=lambda t: rd.name(t).lower()):
                lines += [f"### At {rd.name(tp)}", ""]
                for k in by[tp]:
                    rec = rd.record(k)
                    between = ", ".join(rd.name(f"stakeholder:{s}") for s in rec.get("between") or [])
                    lines.append(f"- {rd.name(k, True)} · between {between or '—'} · {rd.mark(k) or 'own'}{rd.used(k)}")
                    lines.append(f"  - {'; '.join(rec.get('offered') or []) or '—'} → {'; '.join(rec.get('returned') or []) or '—'}")
                lines.append("")
            continue
        for k in ids:
            rec = rd.record(k)
            line = f"- {rd.name(k, True)} · {rd.mark(k) or 'own'}"
            if e == "body":
                place = f"part of {rd.name('body:' + rec['part_of'])}" if rec.get("part_of") else "stands on its own"
                line += f" · {rec.get('form') or 'no form'} · {place} · mandate: {'open' if rec.get('mandate') is None else 'stated'}"
            line += rd.used(k)
            lines.append(line)
            for p in posts.pop(k, []) if e == "body" else []:
                held = ", ".join(str(h.get("id")) for h in (rd.record(p) or {}).get("held_by") or [] if isinstance(h, dict))
                lines.append(f"  - Post {rd.name(p, True)} · {rd.mark(p) or 'own'} · held by: {held or 'open'}{rd.used(p)}")
        lines.append("")
    if posts:
        lines += ["## Posts of no Body held or offered", ""] + [f"- {rd.name(p, True)} · {rd.mark(p) or 'own'}" for ps in posts.values() for p in ps] + [""]
    return "\n".join(lines)


def named(p, core):
    """a definition's path inside the CORE, or the copy beside this tool"""
    if not p:
        return None
    a, c = os.path.abspath(p), os.path.abspath(core)
    return os.path.relpath(a, c).replace(os.sep, "/") if a.startswith(c + os.sep) else "specs/blueprint.yml (beside the tool)"


def write(out, rel, text):
    p = os.path.join(out, *rel.split("/"))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return p


def render(core, out=None):
    out = out or core
    rd = Reading(core)
    defs, order = definitions(core, rd.at, rd)
    bp, counts, outcomes = blueprint_md(rd, order)
    files = {f"{OUT}/briefing.md": bp, f"{OUT}/gaps.md": gaps_md(rd, order),   # core-views part 5: views/briefing/
             f"{OUT}/value-model.md": value_model(rd, order),
             f"{OUT}/entity-model.md": entity_model(rd), f"{OUT}/element-model.md": element_model(rd)}
    for rel, text in files.items():
        write(out, rel, text)
    inputs = sorted(glob.glob(os.path.join(layout.runtime(core), "*", "*.y*ml")) + glob.glob(os.path.join(core, "lifecycle", "events", "*.y*ml"))
                    + [os.path.join(core, ".commons", "commons.yml"), os.path.join(core, ".commons", "lock.yml")]
                    + [p for p in (layout.path(core, "claims"), layout.path(core, "sources")) if p])
    grammar = next((str(x.get("version")) for x in layout.pins(rd.cfg) if str(x.get("id")).split("/")[-1] in layout.ESSENTIALS), None)
    man = {"generator": GENERATOR,   # the provenance record of the view `briefing` (core-views R8)
           "definitions": {"blueprint": grammar or (digest(defs[0][0]) or "")[7:19], "view": "briefing",
                           "structure": str(rd.cfg.get("structure") or ""),
                           "layers": [{"from": n, "path": named(p, core), "digest": digest(p)} for n, (p, _) in zip(("frame", "domain", "commons"), defs)]},
           "inputs": {os.path.relpath(p, core).replace(os.sep, "/"): digest(p)[7:] for p in inputs if os.path.exists(p)},
           "outcomes": outcomes, "counts": counts, "unused": {e: n for e in USED if (n := len(rd.unused(e)))}, "outputs": {rel: "sha256:" + hashlib.sha256(t.encode("utf-8")).hexdigest() for rel, t in files.items()}}
    write(out, f"{layout.provenance_dir(out)}/briefing/manifest.json", json.dumps(man, indent=2, ensure_ascii=False) + "\n")
    return man


def stream_offer(rd, k):
    """one offered stream as a commons would take it: its own words (rule C) and its package (rule B)"""
    rec = rd.offered[k]
    a = catalogue.activation(rd.offered, k, refers=rd.refers)
    take = a["take"]
    lines = [f"#### {rd.name(k)}" + (" · a place to begin" if rec.get("start") else ""), ""]
    if rec.get("summary"):
        lines += [rec["summary"], ""]
    if rec.get("trigger"):
        lines.append(f"- **When it starts:** {rec['trigger']}")
    if rec.get("outcome"):
        lines.append(f"- **What the commons holds:** {rec['outcome']}")
    kinds = [counted(n, e) for e in ELEMENTS + ["post"] if (n := sum(1 for x in take if x.startswith(f"{e}:")))]
    lines.append(f"- **What comes with it:** activating it takes {len(take)} records as one package, {len(a['bound'])} bound and "
                 f"{len(a['carried'])} carried: {', '.join(kinds)}.")
    people = [rd.name(x) for x in take if x.startswith("stakeholder:")]
    nx = sum(1 for x in take if x.startswith("value-exchange:"))
    if people:
        lines.append(f"- **Between whom:** {', '.join(people)}; {counted(nx, 'value-exchange')} pass between them.")
    bodies = [x for x in take if x.startswith("body:")]
    if bodies:
        held = []
        for b in bodies:
            ps = [rd.name(p) for p in take if p.startswith("post:") and rd.offered[p].get("of") == b.split(":", 1)[1]]
            held.append(rd.name(b) + (f" (Posts: {', '.join(ps)})" if ps else ""))
        lines.append(f"- **What it asks:** Bodies to hold what it brings, as offered: {', '.join(held)}.")
    gaps = [counted(n, e) for e in ELEMENTS + ["post"] if (n := sum(1 for x in a["unresolved"] if x.startswith(f"{e}:")))]
    if gaps:                                     # named by its cause, the records that name them (D3, commons.o#109 N1)
        by = {x.split(":", 1)[0] for x in take for ref in catalogue.bound(rd.offered[x]) if ref in a["unresolved"]}
        by = [PLURAL[e] for e in ELEMENTS + ["post"] if e in by]
        lines.append(f"- **Not offered:** {', '.join(gaps)} the offer does not hold, named by the "
                     f"{' and '.join([', '.join(by[:-1]), by[-1]] if len(by) > 1 else by)} that come with it.")
    return lines + [""]


def render_offer(release, out=None):
    """the offer page: the frame over the release's own records, holding only what the essentials hold (rule A)"""
    out = out or release
    rd = Reading(release=release)
    rec, off = rd.rel, yml(layout.model_file(release)) or {}
    defs, order = definitions(None, release, rd)
    kind = str(off.get("kind") or "").replace("-", " ")
    lines = [f"# For a {kind}" if kind else f"# {rd.ref}", "", f"`{rd.ref}@{rd.version}` · *generated from the release; never edited*", ""]
    if off.get("gives"):
        lines += [f"**What it gives:** {off['gives']}", ""]
    start = [rd.name(k) for k in sorted(rd.offered) if k.startswith("value-stream:") and "/" not in k and rd.offered[k].get("start")]
    if start:
        lines += [f"**Where to begin:** {', '.join(start)}.", ""]
    if off.get("asks"):
        lines += [f"**What it asks:** {off['asks']}", ""]
    if (rec.get("parts") or {}).get("enhanced"):
        lines += [f"**Depth:** {DEPTH}", ""]
    for dim, fams in frame_families(order, "en"):
        reached = [f for f, _ in fams if rd.streams(f, rd.offered)]
        lines += [f"## {dim}", ""] + ([] if reached else ["*not offered*", ""])
        for fam, fl in fams:
            lines += [f"### {fl} `family:{fam}`", ""]
            if fam not in reached:
                lines += ["*not offered*", ""]
                continue
            lp = rd.loops.get(fam)
            if lp:
                lines += [f"Steered by the family's loop *{lp.get('title')}* `{lp.get('loop')}`.", ""]
            ext = [s for s in order if s["_from"] == "domain" and (s.get("binds") or {}).get("kind") == "value-stream"
                   and f"value-stream:{s['binds'].get('slug')}" in rd.offered and rd.offered[f"value-stream:{s['binds']['slug']}"].get("family") == fam]
            for s in sorted(ext, key=lambda s: rd.rank(f"value-stream:{s['binds']['slug']}")):
                lines += stream_offer(rd, f"value-stream:{s['binds']['slug']}")
    lines += ["## The nine elements", ""]
    for n, e in enumerate(ELEMENTS, 1):
        ids = rd.ids(e)
        posts = len(rd.ids("post")) if e == "body" else 0
        lines += [f"### {n} {e.replace('-', ' ').capitalize()}", "",
                  (f"{counted(len(ids), e)} offered" + (f", with {counted(posts, 'post')}" if posts else "")) if ids else "*not offered*", ""]
        if e == "entity":
            lines += [f"- {rd.name(k)} · {rd.offered[k].get('type') or 'untyped'}" for k in ids] + ([""] if ids else [])
        if e == "touchpoint" and ids:            # the solution proposals at each agreed place (CORE-VIEWS R22)
            pro = catalogue.proposals(rd.offered, ids)
            lines += [f"- {rd.name(k)} · " + (f"proposals: {', '.join(rd.name(s) for s in pro[k])}" if pro[k] else "no proposal yet")
                      for k in ids] + [""]
    lines += ["## The commons' own", "", "What it knows, where it is heading and how it steers are the commons' own; no offer holds them.", ""]
    lines += ["---", "", f"Questions and answers about this offer go to `{rec.get('answers')}`.", ""]
    text = "\n".join(lines)
    write(out, "offer.md", text)
    man = {"generator": GENERATOR, "release": f"{rd.ref}@{rd.version}",
           "definitions": [{"from": "frame", "digest": digest(defs[0][0])}, {"from": "domain", "digest": digest(defs[1][0])}],
           "output": "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()}
    write(out, f"{layout.provenance_dir(out)}/offer/manifest.json", json.dumps(man, indent=2, ensure_ascii=False) + "\n")
    return man


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("core", nargs="?")
    ap.add_argument("--offer")
    ap.add_argument("--out")
    a = ap.parse_args()
    if a.offer:
        man = render_offer(a.offer, a.out)
        print(f"# rendered the offer page of {man['release']}")
        return 0
    if not a.core:
        ap.error("a CORE, or --offer RELEASE")
    man = render(a.core, a.out)
    print("# rendered the briefing: " + ", ".join(f"{n} {o}" for o, n in sorted(man["counts"].items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
