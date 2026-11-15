#!/usr/bin/env python3
"""catalogue.py — a model offers well as a catalogue, and a commons installs and builds from it as it should.
Read-only. Earlier `check_extension.py` (D4-2, Holger 6625957149).

The module behind `check_model --catalogue` (MODEL R28, R29), `check_core`'s `models` (CORE), `build.py` and
`release.py` (LIBRARY R19). It reports each finding as fail (a MUST), should (a SHOULD) or gap (missing, not wrong),
under the check ids of the check that calls it, and exits with 1 only on a fail.

Usage:  catalogue.py DOMAIN_CORE [DOMAIN_CORE ...] [--core CORE]
        A [domain].core is read with check_core.py first, then its emulation `models/emulation/<model>/` (`offer/`
        its earlier place) and its research in `knowledge/`. The same code is the gate of a library: what passes
        here passes there. --core reads a commons that installs a released model: its pins and libraries, the
        installed copy under `models/commons/<library>/<model>/` (`extensions/` its earlier place) with its release
        record, and the records it built from it by their `origin`. Each built record is reported as unchanged or
        adapted, with the fields it changes: derived, never stated.
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
sys.dont_write_bytecode = True   # the tools never write into the install they lie in (SPECIFICATION R29; `extension` R12)
sys.path.insert(0, HERE)
import check_core  # noqa: E402
import layout  # noqa: E402
import rejected as rejected_words  # noqa: E402
import check_model  # noqa: E402

SCHEMA = json.load(open(os.path.join(HERE, "..", "schemas", "extension.schema.json"), encoding="utf-8"))
MODEL_SCHEMA = os.path.join(HERE, "..", "schemas", "model.schema.json")
EARLIER = "commons-library"    # once built in; a commons now names every library it installs from (R12, CORE R1)
EMAIL = re.compile(r"(?<![\w.+/-])[\w.+-]+@[\w-]+\.[\w.-]+")   # never the <library>/<extension>@<version> of an origin
PHONE = re.compile(r"\+\d[\d ()-]{7,}\d")
ORIGIN = re.compile(r"^(?P<library>[a-z0-9-]+)/(?P<ext>[a-z0-9-]+)(/(?P<variant>[a-z0-9-]+))?@(?P<version>\d+\.\d+\.\d+(-rc\.\d+)?)#(?P<kind>[a-z-]+):(?P<slug>[a-z0-9.-]+(/[a-z0-9.-]+)?)$")
SEM = re.compile(r"^\d+\.\d+\.\d+(-rc\.\d+)?$")
OLD_FORMAT = ["manifest.yml", "MANIFEST.md", "value-model.yml", "entity-model.yml", "element-model.yml",
              "blueprint.template.md", "capability-map.deep.yml"]
REFERENCE = check_model.REFERENCE   # an entity's field that names another entity
RELATIONS = {"derived-from", "adopt", "bind", "mirror", "own"}
RESEARCH = ["edition", "jurisdiction", "area", "relation", "verified", "licence", "class", "informs"]
TEXT = (".yml", ".yaml", ".md", ".json")


class Report(check_core.Report):
    def __init__(self):
        super().__init__()
        self.notes = []


def yml(p):
    return yaml.safe_load(open(p, encoding="utf-8")) if os.path.exists(p) else None


def valid(r, check, name, data, ref):
    v = jsonschema.Draft202012Validator({"$defs": SCHEMA["$defs"], "$ref": ref} if ref else SCHEMA)
    for e in v.iter_errors(data):
        r.fail(check, f"`{name}`: {'/'.join(map(str, e.absolute_path)) or 'the file'}: {e.message[:110]}")


def records(reg):
    """the records of a registry folder, by `<kind>:<slug>`, steps as `value-stream:<stream>/<step>`"""
    out = {}
    for f in sorted(glob.glob(os.path.join(reg, "*", "*.y*ml"))):
        rec = yml(f) or {}
        if isinstance(rec, dict) and rec.get("kind") and rec.get("slug"):
            out[f"{rec['kind']}:{rec['slug']}"] = (rec, f)
            for st in rec.get("steps") or []:
                if isinstance(st, dict) and st.get("slug"):
                    out[f"value-stream:{rec['slug']}/{st['slug']}"] = (st, f)
    return out


def loops(d):
    return {os.path.basename(f).rsplit(".loop.", 1)[0] for f in glob.glob(os.path.join(d, "*.loop.y*ml"))}


def texts(d, skip=()):
    for p in glob.glob(os.path.join(d, "**", "*"), recursive=True, include_hidden=True):
        if os.path.isfile(p) and p.endswith(TEXT) and os.path.relpath(p, d).split(os.sep)[0] not in skip:
            yield p, open(p, encoding="utf-8", errors="replace").read()


def commons_spec_ids():
    """the ids of the discipline's specifications: those beside this tool"""
    ids = set()
    for f in glob.glob(os.path.join(HERE, "..", "*.md")):
        t = open(f, encoding="utf-8").read()
        if t.startswith("---"):
            ids.add((yaml.safe_load(t.split("---")[1]) or {}).get("id"))
    return ids - {None}


def binds_of(recs):
    for k, (rec, f) in recs.items():
        if isinstance(rec, dict) and "/" not in k:
            for b in rec.get("binds") or []:
                yield k, f, b


def source_terms(s):
    """the words a source is known by: its designation and slug, the designation's leading part (`KHVVG` of `KHVVG,
    BGBl. 2024 I Nr. 400`), a short title in parentheses (`Artificial Intelligence Act`), and any `terms` it lists"""
    out = {s.get("designation"), s.get("slug"), *(s.get("terms") or [])}
    if s.get("designation"):
        out.add(str(s["designation"]).split(",")[0].strip())
    for m in re.findall(r"\(([^()]+)\)", str(s.get("title") or "")):
        if len(m) >= 4 and not re.search(r"\d", m):
            out.add(m.strip())
    return {str(x) for x in out if x and len(str(x)) >= 3}


def term_rx(term):
    """a term with capitals is matched as written, one in lower case in any case (as the workshop's IP check does)"""
    return re.compile(r"(?<![\w-])" + re.escape(term) + r"(?![\w-])", 0 if term != term.lower() else re.I)


def unbound(path, text, ids):
    """the text of a file without the source ids its bindings name: `binds[].source`, in a record or an overlay"""
    if not path.endswith((".yml", ".yaml")):
        return text
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError:
        return text
    out = []

    def walk(x, in_binds=False):
        if isinstance(x, dict):
            for k, v in x.items():
                if in_binds and k == "source" and v in ids:
                    continue
                out.append(str(k))
                walk(v, k == "binds")
        elif isinstance(x, list):
            for v in x:
                walk(v, in_binds)
        elif x is not None:
            out.append(str(x))
    walk(data)
    return chr(10).join(out)


def jurisdictional(j):
    """a source of law of one jurisdiction, national or regional (`de`, `se`, `eu`); only `global`, the standards no
    jurisdiction enacts, is jurisdiction-neutral (R31)"""
    return isinstance(j, str) and j.strip() != "" and j != "global"


def jurisdiction_binds(d):
    """(record, binding, file) of every binding in `knowledge/jurisdictions/<j>.yml`: research, never offer (R31)"""
    for p in sorted(glob.glob(os.path.join(d, "knowledge", "jurisdictions", "*.y*ml"))):
        data = yml(p) or {}
        for bd in data.get("bindings") or [] if isinstance(data, dict) else []:
            for b in (bd.get("binds") or []) if isinstance(bd, dict) else []:
                if isinstance(b, dict):
                    yield bd.get("record"), b, p


def rejected_terms(glossary=None):
    """the discipline's rejected words, each with its kind (`rejected.py`)"""
    return rejected_words.entries(glossary)


def rejected_in(r, check, path, text, where, terms, report=None):
    """R14: an offer speaks Commons language, its depth included, read by sense (`rejected.py`): a name fails in its
    text, its slugs and its file name, a key only in its place, a word is a should. `report` is how a fail is told, a
    fail unless the reader says otherwise"""
    report = report or r.fail
    for level, msg in rejected_words.findings(path, text, where, terms):
        (report if level == "fail" else r.should)(check, msg)


def catalogue(r, m, name=None, root=None):
    """MODEL's check `catalogue` (R28, R29) on a model made for every commons of its kind, in its folder `m`, either
    layout: its records in MODEL's grammar as a catalogue; every kind whole, nothing bound that it does not hold; the
    thirteen families, a family no stream reaches the maker's gap, each reached one with its steering loop; the depth;
    a starting set, and every stream in its family's `order` and only those. Returns (records, depth)"""
    name = name or os.path.basename(os.path.abspath(m))
    reg = layout.records(m)
    if os.path.isdir(reg):
        for o, c, t in check_model.check(check_model.load(reg), extension=True).items:
            if o == "fail":
                r.fail("catalogue", f"`{name}`: {c}: {t}")
    recs = records(reg)
    missing = {}                                 # every kind whole (R28): a binding to a record it does not hold fails
    for k, (rec, _) in recs.items():
        if "/" not in k and isinstance(rec, dict):
            for ref in set(reaches(rec)):
                if ref not in recs:
                    missing.setdefault("step" if "/" in ref else ref.split(":", 1)[0], set()).add(ref)
    for kind in sorted(missing, key=lambda x: KINDS.index(x) if x in KINDS else len(KINDS)):
        refs = sorted(missing[kind])
        r.fail("catalogue", f"`{name}` binds {len(refs)} {kind} it does not hold, e.g. `{refs[0]}`: a catalogue holds "
                            f"every record it binds, each kind whole (R28)")
    if not any(k.startswith("value-stream:") and "/" not in k for k in recs):
        r.fail("catalogue", f"`{name}` holds no value stream")
    canon = json.load(open(MODEL_SCHEMA, encoding="utf-8"))["x-dimension-of"]
    have = loops(layout.model_loops(m))
    named = {rec.get("family") for k, (rec, _) in recs.items() if k.startswith("value-stream:") and "/" not in k}
    for fam in canon:                            # a catalogue stands in all 13 families (R28; Holger, #109 6571926000)
        if fam not in named:
            r.gap("catalogue", f"`{name}` does not reach the family `{fam}`: no stream of it, a gap of the maker (R28)")
        elif f"_family.{fam}" not in have:
            r.fail("catalogue", f"`{name}` holds streams of `{fam}` and no steering loop `loops/_family.{fam}.loop.yml` (R28)")
    deep = depth(r, root or m, name, recs, m)
    if isinstance((yml(layout.model_file(m)) or {}).get("variant"), dict):
        variants(r, m, recs, name)
    fam_of = {k.split(":", 1)[1]: rec.get("family") for k, (rec, _) in recs.items() if k.startswith("value-stream:") and "/" not in k}
    order = (yml(layout.model_file(m)) or {}).get("order") or {}
    for s, fam in sorted(fam_of.items()):        # the starting set and the order of each family (R29), shoulds
        if s not in (order.get(fam) or []):
            r.should("catalogue", f"`{name}`: the stream `{s}` stands in no place of its family's `order` (`{fam}`) (R29)")
    for fam, slugs in sorted(order.items()):
        for s in slugs or []:
            if fam_of.get(s) != fam:
                r.should("catalogue", f"`{name}`: the `order` of `{fam}` names `{s}`, "
                                      + (f"a stream of `{fam_of[s]}`" if s in fam_of else "which it does not hold") + " (R29)")
    start = {k: v for k, v in recs.items() if isinstance(v[0], dict) and v[0].get("start") is True}
    if not start:
        r.should("catalogue", f"`{name}` marks no starting set (`start: true`) (R29)")
    for k, (rec, _) in start.items():
        for st in rec.get("steps") or []:
            for cap in st.get("capabilities") or []:
                if f"capability:{cap}" not in recs:
                    r.should("catalogue", f"`{name}`: the starting record `{k}` binds the capability `{cap}`, which it does not hold (R29)")
    return recs, deep


def semkey(v):
    return tuple(int(x) for x in re.findall(r"\d+", v.split("-rc.")[0])) + ((0, int(v.split("-rc.")[1])) if "-rc." in v else (1, 0))


def variants_at_hand(m):
    """{name: folder}: the other variants of a model's domain that lie beside it, the CORE's other emulations, the other
    variants of an installed domain, or the latest release of each other variant in a library (MODEL R30); none where
    the model is no variant"""
    me = yml(layout.model_file(m)) or {}
    if not isinstance(me.get("variant"), dict):
        return {}
    m = os.path.abspath(m)
    up = os.path.dirname(m)
    if SEM.match(os.path.basename(m)):              # a release `<model>/<variant>/<version>/`
        cands = []
        for v in sorted(os.listdir(os.path.dirname(up))):
            q = os.path.join(os.path.dirname(up), v)
            vs = sorted((u for u in os.listdir(q) if SEM.match(u)), key=semkey) if os.path.isdir(q) else []
            if vs and os.path.normcase(q) != os.path.normcase(up):
                cands.append(os.path.join(q, vs[-1]))
    else:
        cands = [os.path.join(up, x) for x in sorted(os.listdir(up)) if os.path.normcase(os.path.join(up, x)) != os.path.normcase(m)]
    out = {}
    for c in cands:
        y = yml(layout.model_file(c)) if os.path.isdir(c) else None
        if isinstance(y, dict) and y.get("id") == me.get("id") and isinstance(y.get("variant"), dict) and y["variant"].get("name"):
            out[y["variant"]["name"]] = c
    return out


def variants(r, m, recs, name):
    """MODEL's check `variants` (R30, R31), for a model with `variant`, against the other variants of its domain at
    hand, else a gap: they stand in one line, the variant it comes after being one of them and no two coming after the
    same one; a slug two variants hold names the same kind, a stream the same family; and a record it shares with
    another names no Body that only the other holds (R31)"""
    me = (yml(layout.model_file(m)) or {}).get("variant") or {}
    others = variants_at_hand(m)
    if not others:
        r.gap("variants", f"`{name}` is the variant `{me.get('name')}`, and no other variant of its domain is at hand to read it against (R30)")
        return
    line = {n: (yml(layout.model_file(d)) or {}).get("variant") or {} for n, d in others.items()}
    after = me.get("after")
    if after and after not in line:
        r.fail("variants", f"`{name}` comes after `{after}`, which is no variant of its domain at hand (R30)")
    beside = sorted(n for n, v in line.items() if v.get("after") == after)
    if beside:
        r.fail("variants", f"`{name}` and {', '.join(f'`{n}`' for n in beside)} both come "
                           + (f"after `{after}`" if after else "first") + ": a domain's variants stand in one line (R30)")
    kinds = lambda rs: {k.split(":", 1)[1]: {x.split(":", 1)[0] for x in rs if "/" not in x and x.split(":", 1)[1] == k.split(":", 1)[1]}
                        for k in rs if "/" not in k}
    mine = kinds(recs)
    for n, d in sorted(others.items()):
        theirs = records(layout.records(d))
        held = kinds(theirs)
        for s in sorted(set(mine) & set(held)):
            if not mine[s] & held[s]:
                r.fail("variants", f"`{s}` is a {'/'.join(sorted(mine[s]))} in `{name}` and a {'/'.join(sorted(held[s]))} in `{n}`: "
                                   f"a slug two variants hold names the same kind (R30)")
        for k in sorted(x for x in recs if x.startswith("value-stream:") and "/" not in x and x in theirs):
            a, b = (recs[k][0] or {}).get("family"), (theirs[k][0] or {}).get("family")
            if a != b:
                r.fail("variants", f"`{k}` stands in `{a}` in `{name}` and in `{b}` in `{n}`: a stream two variants hold stands in one family (R30)")
        for k in sorted(x for x in recs if "/" not in x and x in theirs):
            rec = recs[k][0] if isinstance(recs[k][0], dict) else {}
            named = set(bound(rec))
            if rec.get("kind") == "post" and str(rec.get("accountable") or "").startswith("body:"):
                named.add(f"body:{rec['accountable'][5:]}")
            for ref in sorted(x for x in named if x.startswith("body:") and x not in recs and x in theirs):
                r.fail("variants", f"`{k}`, which `{name}` shares with `{n}`, names the Body `{ref[5:]}`, which only `{n}` holds; "
                                   f"in `{name}` it is a stakeholder and no Body (R31)")


def emulation_of(d, model=None):
    """the model a [domain].core makes: `models/emulation/<model>/`, the only one where `model` is not named, else its
    earlier place `offer/` (CORE R6, R4)"""
    emus = layout.emulations(d)
    if model:
        return emus.get(model) or os.path.join(d, "models", "emulation", model)
    own = [v for k, v in emus.items() if k != "offer"]
    return own[0] if len(own) == 1 else emus.get("offer") or os.path.join(d, "offer")


def check(d, r=None, model=None):
    """a [domain].core: a CORE first, then its offer (R4, R29) and its research (R30, R31)"""
    r = r or Report()
    name = os.path.basename(os.path.abspath(d))
    cfg = yml(os.path.join(d, ".commons", "commons.yml"))
    off = emulation_of(d, model)
    inner = lambda p: os.path.relpath(p, off).replace(os.sep, "/")   # a path within the model

    # core (R7, R29): a well-formed CORE, and an offer in MODEL's grammar on MODEL's families
    earlier = yml(os.path.join(d, ".commons", "identity.yml"))
    if cfg is None and earlier is not None:
        r.gap("core", f"`{name}` is on an earlier layout (`.commons/identity.yml`): read as unmigrated, the CORE checks wait for its migration (CORE R4)")
        cfg = {"holder": earlier.get("founder"), "extensions": []}
    else:
        for o, c, t in check_core.check(d, offline=True).items:
            if o == "fail":
                r.fail("core", f"`{name}`: {c}: {t}")
    if cfg is None:
        r.fail("offer", f"`{name}` has no `.commons/commons.yml`")
        return r
    if not os.path.isdir(off):
        r.fail("offer", f"`{name}` holds no `offer/`: what a [domain].core offers is kept apart from its own model")
        return r
    # offer (R1, R4, R29): the offer as data, the licence, the holder; a missing primary is the gap of R9, read by `fit`
    offer = yml(layout.model_file(off))
    if offer is None:
        r.fail("offer", f"`{name}` has no `model.yml` in `{os.path.relpath(off, d)}`")
    else:
        valid(r, "offer", f"{name}/{os.path.relpath(layout.model_file(off), d)}", offer, None)
    if not os.path.exists(os.path.join(d, "LICENSE")):
        r.fail("offer", f"`{name}` has no `LICENSE`")
    if not cfg.get("holder"):
        r.fail("offer", f"`{name}` names no `holder`: a [domain].core is maintained by someone")

    # contents: nothing of the earlier format beside the offer
    for f in OLD_FORMAT:
        for where in (d, off):
            if os.path.exists(os.path.join(where, f)):
                r.fail("catalogue", f"`{os.path.relpath(os.path.join(where, f), os.path.dirname(d))}`: a model has no format of its own")
    if os.path.exists(os.path.join(off, "overlays")):
        r.fail("catalogue", f"`{name}` holds `offer/overlays/`: a model is jurisdiction-neutral, national law stays in `knowledge/` (CORE-KNOWLEDGE R20)")
    recs, deep = catalogue(r, off, name, root=d)
    every = dict(recs)                            # one research serves every variant of the domain (CORE-KNOWLEDGE R19)
    for other in variants_at_hand(off).values():
        every.update(records(layout.records(other)))

    # research (R30): every source says where it stands and what it informs
    src = yml(os.path.join(d, "knowledge", "sources.yml"))
    sources = {s.get("id"): s for s in (src or {}).get("sources") or [] if isinstance(s, dict)}
    if src is None:
        r.gap("research", f"`{name}` holds no `knowledge/sources.yml`: its research is not at hand")
    for sid, s in sources.items():
        own = s.get("relation") == "own"           # the commons' own synthesis: a design with its derivation, no lenses
        need = [x for x in RESEARCH if not (own and x == "verified")] + (["derivation"] if own else [])
        miss = [x for x in need if not s.get(x)]
        if miss:
            r.fail("research", f"`{name}`: the source `{sid}` lacks {miss}")
        if s.get("relation") and s["relation"] not in RELATIONS:
            r.fail("research", f"`{name}`: the source `{sid}` has the relation `{s['relation']}`, not one of {sorted(RELATIONS)}")
        if own and s.get("standing") != "design":
            r.fail("research", f"`{name}`: the source `{sid}` is the commons' own and states no `standing: design`")
        v = s.get("verified") or {}
        if not own and s.get("verified") and not (isinstance(v, dict) and v.get("confirmation") and v.get("refutation")):
            r.fail("research", f"`{name}`: the source `{sid}` is not verified under both lenses, confirmation and refutation")
        for i in s.get("informs") or []:
            if i not in every:
                r.fail("research", f"`{name}`: the source `{sid}` informs `{i}`, which the offer does not hold"
                                   + (", nor any other variant of its domain (CORE-KNOWLEDGE R19)" if len(every) > len(recs) else ""))

    # binds (R31): every binding names a source of the research, with its edition and jurisdiction, and, optionally,
    # the part of the source it rests on; never an edition that is only scheduled
    held = [(k, os.path.join(d, f), b) for k, (it, f) in deep.items() for b in it.get("binds") or []]
    for k, f, b in list(binds_of(recs)) + held:
        s = sources.get(b.get("source")) if isinstance(b, dict) else None
        where = os.path.relpath(f, d)
        if isinstance(b, dict) and "part" in b and not (isinstance(b["part"], str) and b["part"].strip()):
            r.fail("binds", f"`{where}`: a binding's `part` names no part of `{b.get('source')}`")
        if s is None:
            r.fail("binds", f"`{where}` binds `{b}`, which is no source in `knowledge/sources.yml`")
        elif jurisdictional(s.get("jurisdiction")):
            r.fail("binds", f"`{where}` binds `{b.get('source')}` of the jurisdiction `{s.get('jurisdiction')}`: an extension is jurisdiction-neutral, the law of a jurisdiction stays in `knowledge/jurisdictions/` (R31)")
        elif str(b.get("edition")) in {str(e.get("edition")) for e in s.get("scheduled") or [] if isinstance(e, dict)}:
            r.fail("binds", f"`{where}` binds `{b.get('source')}` at `{b.get('edition')}`, an edition not yet in force (SPECIFICATION R28)")
        elif str(b.get("edition")) != str(s.get("edition")) or b.get("jurisdiction") != s.get("jurisdiction"):
            r.fail("binds", f"`{where}` binds `{b.get('source')}` at {b.get('edition')}/{b.get('jurisdiction')}, and the source is {s.get('edition')}/{s.get('jurisdiction')}")

    # research (R30): coverage. Every offered record is grounded by a source it binds or that informs it, or a claim
    # about it, since what no standard reaches is held as claims; one grounded by none of them
    # is a gap, counted per kind
    if src is not None:
        # a source of the relation `own` is the [domain].core's own word: it grounds a record only through a claim about it
        grounded = {i for s in sources.values() if s.get("relation") != "own" for i in s.get("informs") or []} | {k for k, _, _ in binds_of(recs)}
        grounded |= {k for k, _, _ in jurisdiction_binds(d)}
        slugs = {}
        for k in recs:
            slugs.setdefault(k.split(":", 1)[-1], []).append(k)
        for c in (yml(os.path.join(d, "knowledge", "claims.yml")) or {}).get("claims") or []:
            for a in (c.get("about") or []) if isinstance(c, dict) else []:
                grounded |= {a} if ":" in str(a) else set(slugs.get(str(a), []))
        open_ = {}
        for k in recs:
            if "/" not in k and k not in grounded:
                open_.setdefault(k.split(":", 1)[0], []).append(k)
        for kind, ks in sorted(open_.items()):
            total = sum(1 for k in recs if "/" not in k and k.startswith(kind + ":"))
            r.gap("research", f"`{name}`: {len(ks)} of {total} offered {kind} records are grounded by neither a source nor a claim: "
                              f"{', '.join(sorted(ks)[:5])}{', …' if len(ks) > 5 else ''} (R30)")

    # jurisdictions (R31): the law of one jurisdiction binds offered records only in the research, one file per
    # jurisdiction, at the edition in force
    for p in sorted(glob.glob(os.path.join(d, "knowledge", "jurisdictions", "*.y*ml"))):
        data, where = yml(p) or {}, os.path.relpath(p, d)
        j = os.path.basename(p).rsplit(".", 1)[0]
        if not isinstance(data, dict) or data.get("jurisdiction") != j or not isinstance(data.get("bindings"), list):
            r.fail("research", f"`{where}` is no `{{jurisdiction: {j}, bindings: [...]}}`")
            continue
    for k, b, p in jurisdiction_binds(d):
        where, j = os.path.relpath(p, d), os.path.basename(p).rsplit(".", 1)[0]
        s = sources.get(b.get("source"))
        if k not in every:
            r.fail("research", f"`{where}` binds `{k}`, which the offer does not hold"
                               + (", nor any other variant of its domain (CORE-KNOWLEDGE R19)" if len(every) > len(recs) else ""))
        if s is None:
            r.fail("research", f"`{where}`: `{b.get('source')}` is no source of `knowledge/sources.yml`")
        elif s.get("jurisdiction") != j:
            r.fail("research", f"`{where}`: `{b.get('source')}` is of `{s.get('jurisdiction')}`, not `{j}`")
        elif str(b.get("edition")) != str(s.get("edition")):
            r.fail("research", f"`{where}`: `{b.get('source')}` is bound at `{b.get('edition')}`, and the edition in force is `{s.get('edition')}`")
        if b.get("relation") and b["relation"] not in RELATIONS:
            r.fail("research", f"`{where}`: the relation `{b['relation']}` is not one of {sorted(RELATIONS)}")
        if "part" in b and not (isinstance(b["part"], str) and b["part"].strip()):
            r.fail("research", f"`{where}`: a binding's `part` names no part of `{b.get('source')}`")

    # scheduled (R30): an edition enacted and not yet in force has its place, so that the currency loop raises it before
    # its date; the check reads the form, not the date of reading. With `affects`, it reaches only the bindings that
    # name an affected part, and every binding of the source that names no part
    every = [(k, b) for k, _, b in binds_of(recs) if isinstance(b, dict)] + [(k, b) for k, b, _ in jurisdiction_binds(d)]
    bound_to = {(k, b.get("source")) for k, b in every}
    every += [(i, {"source": sid}) for sid, s in sources.items() for i in s.get("informs") or []
              if (i, sid) not in bound_to]                               # informed and not bound: no part known
    for sid, s in sources.items():
        sch = s.get("scheduled")
        if sch is None:
            continue
        if not isinstance(sch, list):
            r.fail("research", f"`{name}`: the source `{sid}` lists `scheduled` as no list")
            continue
        editions = {str(s.get("edition"))}
        for e in sch:
            e = e if isinstance(e, dict) else {}
            ed, date, aff = str(e.get("edition") or ""), str(e.get("in_force") or ""), e.get("affects")
            if not ed or ed in editions:
                r.fail("research", f"`{name}`: a scheduled edition of `{sid}` names no edition id of its own (`{ed}`)")
            editions.add(ed)
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
                r.fail("research", f"`{name}`: the scheduled edition `{ed}` of `{sid}` has no `in_force` date")
            if aff is not None and not (isinstance(aff, list) and all(isinstance(x, str) and x for x in aff)):
                r.fail("research", f"`{name}`: `affects` of the scheduled edition `{ed}` of `{sid}` is no list of parts")
                aff = None
            reached = sorted({k for k, b in every if b.get("source") == sid and (not aff or not b.get("part") or b.get("part") in aff)})
            r.notes.append(f"research: `{sid}` `{ed}`, in force from {date}: the currency loop raises {len(reached)} record(s): {', '.join(reached) or 'none'}")

    # ip (R14): in the offer, a source is never named, under any of its terms: its records, loops and views speak
    # Commons language. The research, the maker's own model and its workshop (candidates and probes included) are not
    # the offer, and a binding refers to a source by its id, which is no naming (R31)
    terms = sorted({x for s in sources.values() for x in source_terms(s)}, key=len, reverse=True)
    deep_at = {os.path.normcase(os.path.abspath(p)) for p in layout.depth_files(off)}
    for p, t in texts(off):
        rel = os.path.relpath(p, d).replace(os.sep, "/")
        if inner(p).startswith("specs/"):
            continue
        if os.path.normcase(os.path.abspath(p)) in deep_at:   # a system-of-record names standards where its subject is (R14)
            data = yml(p) if p.endswith((".yml", ".yaml")) else None
            if isinstance(data, dict) and isinstance(data.get("items"), list):
                t = yaml.safe_dump([{k: v for k, v in it.items() if not (it.get("aspect") == "system-of-record" and k in NAMED)}
                                    if isinstance(it, dict) else it for it in data["items"]], allow_unicode=True)
        body = unbound(p, t, set(sources))
        for x in terms:
            if term_rx(x).search(body):
                r.fail("ip", f"`{os.path.relpath(p, d)}` names `{x}`, which belongs only in `knowledge/sources.yml`")

    # ip (R14; EXTENSION part 6, D1 commons.o#109 6569859571): the discipline's rejected words, in no text and no slug
    # of the offer, the depth included
    rejected = rejected_terms()
    for p, t in texts(off):
        rel = os.path.relpath(p, d).replace(os.sep, "/")
        if not inner(p).startswith("specs/"):
            rejected_in(r, "ip", p, t, f"`{rel}`", rejected)

    # private (R14)
    for p, t in texts(off):
        if EMAIL.search(t) or PHONE.search(t):
            r.fail("private", f"`{os.path.relpath(p, d)}` holds an e-mail address or a telephone number")

    # specs (R21): the kind's specifications, released with the essentials, never redefine the discipline's
    own = sorted(glob.glob(os.path.join(off, "specs", "*.md")))
    if own:
        import check_spec  # noqa: E402
        ids = commons_spec_ids()
        for path in own:
            sp = os.path.relpath(path, d)
            for o, c, t in check_spec.check(path).items:
                if o == "fail":
                    r.fail("specs", f"`{name}/{sp}` does not follow SPECIFICATION: {c}: {t}")
            fm = yaml.safe_load(open(path, encoding="utf-8").read().split("---")[1]) or {}
            if fm.get("id") in ids:
                r.fail("specs", f"`{name}/{sp}` takes the id `{fm.get('id')}` of a specification of the discipline: it may extend, never redefine")
            for w in fm.get("supersedes") or []:
                if str(w).split(":")[-1].split("/")[-1].removesuffix(".md") in ids:
                    r.fail("specs", f"`{name}/{sp}` supersedes `{w}`, a specification of the discipline: it may extend, never redefine")
    return r


def released(r, at, ref, version, expect=None):
    """release (R1, R12, R31): an installed copy is a release, its essentials only, checked again by the same
    code as in its library (LIBRARY R9), against the record digest its lock took from the library's index"""
    import check_library  # noqa: E402
    rel = yml(os.path.join(at, "release.yml"))
    if rel is None:
        r.fail("release", f"`{ref}` is installed without its release record `release.yml`: nothing unreleased is installed")
        return {}
    named = layout.ref_of({"id": f"{rel.get('library')}/{layout.release_id(rel)}", "variant": rel.get("variant")})
    if named != ref and not (layout.release_id(rel) in layout.ESSENTIALS and ref.split("/")[-1] in layout.ESSENTIALS):
        r.fail("release", f"`{ref}`: the release record names `{named}`")
    if str(rel.get("version")) != str(version):
        r.fail("install", f"`{ref}` is pinned at {version}, and the installed copy is the release {rel.get('version')}")
    for part in ("knowledge", "workshop", "overlays"):   # the depth is part of the model (MODEL part 5); research stays with its maker
        if os.path.exists(os.path.join(at, part)):
            r.fail("install", f"`{ref}` installs `{part}/`: the research stays in the [domain].core, served only under a grant (CORE R39)")
    check_library.check_copy(r, at, at, f"`{ref}`", expect=expect, installed=True)
    if not expect:
        r.gap("release", f"`{ref}`: the lock gives no `record` digest from the library's index; the copy agrees with itself, and whether it is the release the library holds is unverified (LIBRARY R9)")
    return records(layout.records(at))


ASPECTS = {   # the three shared aspects, declared once for every kind (the run's forms, part B): on, required, optional
    "measure": ({"value-stream", "step"},
                ["slug", "title", "type", "definition", "unit", "direction"], ["numerator", "denominator", "data", "computable"]),
    "pattern": ({"family", "value-stream", "step", "capability", "entity"},
                ["context", "problem", "solution"], ["forces", "implementation", "consequences", "related", "binds", "slug"]),
    "system-of-record": ({"entity"}, ["system"], ["also_held_in", "exchange", "record", "binds", "notes"]),
}
CHOICES = {("measure", "type"): {"outcome", "process", "structure"},
           ("measure", "direction"): {"higher-is-better", "lower-is-better", "target"}}
NAMED = ("exchange", "record", "notes")   # where alone a standard is named: a system-of-record's subject (R14)


def depth(r, d, name, recs, m=None):
    """contents (R4, R8; EXTENSION part 5): the depth in `offer/enhanced/`, each item a deeper record or an aspect of
    an offered record or step in the table of part 5, cut into files as the maker likes, read by content; a standard
    named outside a system-of-record's subject is `ip` (R14); the depth hangs on the essentials,
    never the reverse. Returns the items by id, `(item, file)`, for the bindings check."""
    m = m or os.path.join(d, "offer")
    items, aspects = {}, []
    for p in sorted(set(layout.depth_files(m)) | set(layout.depth_earlier(m))):   # known by content, `enhanced/` earlier
        data = yml(p)
        where = os.path.relpath(p, d)
        if not (isinstance(data, dict) and isinstance(data.get("items"), list)):
            r.gap("catalogue", f"`{where}` holds no `items:`: depth in an earlier form, not read as depth")
            continue
        for n, it in enumerate(data["items"]):
            if not isinstance(it, dict):
                r.fail("catalogue", f"`{where}`, item {n}: no mapping")
                continue
            if it.get("aspect"):
                aspects.append((it, where))
                continue
            if not (it.get("kind") and it.get("slug")):
                r.fail("catalogue", f"`{where}`, item {n}: neither a deeper record (`kind`, `slug`) nor an aspect (`of`, `aspect`)")
                continue
            k = f"{it['kind']}:{it['slug']}"
            if k in recs:
                r.fail("catalogue", f"`{where}`: the deeper record `{k}` takes the id of an offered record")
            elif k in items:
                r.fail("catalogue", f"`{where}`: `{k}` is held twice in the depth")
            items[k] = (it, where)
    families = {(rec or {}).get("family") for k, (rec, _) in recs.items() if k.startswith("value-stream:") and "/" not in k}

    def offered(ref):
        """whether an id names an offered record, a step, or a family an offered stream names"""
        return ref in recs or (ref.startswith("family:") and ref.split(":", 1)[1] in families)
    for k, (it, where) in items.items():          # a deeper record's parent chain reaches an offered record
        seen, at = {k}, it
        while True:
            par = at.get("parent")
            ref = f"{at.get('kind')}:{par}" if par else None
            if ref in recs:
                break
            if ref is None or ref in seen or ref not in items:
                r.fail("catalogue", f"`{where}`: the parent chain of `{k}` reaches no offered record ({ref or 'no parent'})")
                break
            seen.add(ref)
            at = items[ref][0]
    standards = sorted({str(x.get("standard")) for it, _ in aspects if it.get("aspect") == "system-of-record"
                        for f in ("exchange", "record") for x in it.get(f) or [] if isinstance(x, dict) and x.get("standard")},
                       key=len, reverse=True)
    for it, where in aspects:
        a, of = it.get("aspect"), str(it.get("of") or "")
        decl = ASPECTS.get(a)
        if decl is None:
            r.fail("catalogue", f"`{where}`: the aspect `{a}` is not declared (`{'`, `'.join(ASPECTS)}`)")
            continue
        on, need, may = decl
        target = "step" if of.startswith("value-stream:") and "/" in of else of.split(":", 1)[0]
        aid = f"{of}~{a}" + (f":{it['slug']}" if it.get("slug") else "")
        if target not in on:
            r.fail("catalogue", f"`{where}`: `{aid}`: a `{a}` is on {sorted(on)}, not on `{target}`")
        elif not offered(of):
            r.fail("catalogue", f"`{where}`: `{aid}`: `of: {of}` is no record of this offer" + (" (a family resolves where an offered stream names it)" if target == "family" else ""))
        for f in need:
            if it.get(f) in (None, "", []):
                r.fail("catalogue", f"`{where}`: `{aid}` lacks `{f}`")
        for f in sorted(set(it) - set(need) - set(may) - {"of", "aspect"}):
            r.fail("catalogue", f"`{where}`: `{aid}` has `{f}`, which the aspect `{a}` does not declare")
        for (asp, f), allowed in CHOICES.items():
            if asp == a and it.get(f) is not None and it[f] not in allowed:
                r.fail("catalogue", f"`{where}`: `{aid}`: `{f}: {it[f]}` is not one of {sorted(allowed)}")
        if aid in items:
            r.fail("catalogue", f"`{where}`: `{aid}` is held twice in the depth")
        items[aid] = (it, where)
        for e in it.get("data") or [] if a == "measure" else []:
            if f"entity:{e}" not in recs and f"entity:{e}" not in items:
                r.gap("catalogue", f"`{where}`: `{aid}` reads `{e}`, which the offer holds no entity for")
        for x in it.get("related") or [] if a == "pattern" else []:
            t = str((x or {}).get("target") if isinstance(x, dict) else "")
            if not (isinstance(x, dict) and x.get("rel") and ":" in t):
                r.fail("catalogue", f"`{where}`: `{aid}`: a relation is `{{rel, target: <kind>:<slug>}}`, not `{x}`")
            elif not (offered(t) or t in items):
                r.gap("catalogue", f"`{where}`: `{aid}` relates to `{t}`, which neither depth holds")
        if a == "system-of-record":
            for s in [it.get("system")] + list(it.get("also_held_in") or []):
                if s and f"solution:{s}" not in recs:
                    r.gap("catalogue", f"`{where}`: `{aid}` names the system `{s}`, which the offer holds no solution for")
        for f, v in it.items():                   # a standard is named only where a system-of-record's subject is
            if a == "system-of-record" and f in NAMED or f in ("of", "aspect", "binds", "slug"):
                continue
            body = yaml.safe_dump(v, allow_unicode=True) if not isinstance(v, str) else v
            for s in standards:
                if term_rx(s).search(body):
                    r.fail("ip", f"`{where}`: `{aid}` names `{s}` in `{f}`; a standard is named only in a system-of-record's {', '.join(NAMED)} (R14)")
    # the depth hangs on the essentials, never the reverse: no offered record binds what only the depth holds
    deep = set(items)
    for k, (rec, f) in recs.items():
        if "/" in k or not isinstance(rec, dict):
            continue
        refs = set(bound(rec)) | {f"entity:{x.get('target')}" for x in rec.get("relations") or [] if isinstance(x, dict)}
        for ref in sorted(refs & deep):
            r.fail("catalogue", f"`{os.path.relpath(f, d)}` binds `{ref}`, which only the depth holds: the depth hangs on the essentials, never the reverse")
    if items:
        r.notes.append(f"contents: `{name}` holds {sum(1 for k in items if '~' not in k)} deeper records and "
                       f"{sum(1 for k in items if '~' in k)} aspects on {len({str(i.get('of')) for i, _ in aspects})} offered records")
    return items


RECORD_SCOPE = ("stakeholder", "journey", "touchpoint", "value-exchange", "capability", "entity", "solution", "body", "post")


def one_record(scope):
    """whether a scope is one record, `<kind>:<slug>` (R34; D1, commons.o#109 6570350870)"""
    return str(scope).split(":", 1)[0] in RECORD_SCOPE and ":" in str(scope)


def streams_in(scope, offered):
    """the offered streams a scope of an activation reaches, `value-stream:<s>` (the run's forms, part D)"""
    every = sorted(k for k in offered if k.startswith("value-stream:") and "/" not in k)
    if scope == "whole":
        return every
    if str(scope).startswith("family:"):
        return [k for k in every if (offered[k] or {}).get("family") == scope.split(":", 1)[1]]
    return [scope] if scope in every else []


def closure(offered, streams):
    """R34's closure of streams: each stream, the capabilities its steps bind with their parent chain, and the entities
    they reference; returns what the release offers of it, and what it binds and the release does not offer"""
    required, unresolved = [], []

    def need(k):
        if k in required or k in unresolved:
            return
        if k not in offered:
            unresolved.append(k)
            return
        required.append(k)
        if k.startswith("capability:") and offered[k].get("parent"):
            need(f"capability:{offered[k]['parent']}")
    for key in streams:
        need(key)
        for st in offered[key].get("steps") or []:
            for field, target in (("capabilities", "capability"), ("entities", "entity")):
                for v in (st.get(field) or []) if isinstance(st, dict) else []:
                    need(f"{target}:{v}")
    return required, unresolved


KINDS = ("stakeholder", "journey", "touchpoint", "value-exchange", "value-stream", "step", "capability", "entity", "solution",
         "body", "post")   # the nine elements, a stream's steps beside it and a Body's Posts, in the order they are read
CARRIED_BINDS = ("stakeholder", "journey", "body")   # what a carried record brings along with it, so that it stands whole


def serving(offered):
    """the steps that serve each touchpoint, `<stream>/<step>` by touchpoint slug: a step's `serves` (MODEL R22), and a
    touchpoint's `steps` of the earlier layout (Holger, commons.o#109 6571926000)"""
    out = {}
    for k, rec in offered.items():
        if k.startswith("value-stream:") and "/" not in k:
            for st in rec.get("steps") or []:
                for tp in (st.get("serves") or []) if isinstance(st, dict) else []:
                    out.setdefault(tp, set()).add(f"{rec.get('slug')}/{st.get('slug')}")
        elif k.startswith("touchpoint:"):
            out.setdefault(rec.get("slug"), set()).update(s for s in rec.get("steps") or [] if isinstance(s, str))
    return out


def proposals(offered, touchpoints=None):
    """the solution proposals at each touchpoint (EXTENSION R34, CORE-VIEWS R22): the offered streams whose steps serve
    it, `value-stream:<s>` by `touchpoint:<t>`, for the touchpoints given or every one"""
    serve = serving(offered)
    tps = touchpoints if touchpoints is not None else sorted(k for k in offered if k.startswith("touchpoint:"))
    return {t: sorted({f"value-stream:{s.split('/', 1)[0]}" for s in serve.get(t.split(":", 1)[1], ())} & set(offered))
            for t in tps}


def touchpoints_of(offered, key):
    """the touchpoints a stakeholder-side record leads to: its own, a value exchange's, a journey's, a stakeholder's"""
    kind, slug = key.split(":", 1)
    tps = {k: rec for k, rec in offered.items() if k.startswith("touchpoint:")}
    if kind == "touchpoint":
        return [key] if key in tps else []
    if kind == "value-exchange":
        return [k for k in [f"touchpoint:{(offered.get(key) or {}).get('touchpoint')}"] if k in tps]
    if kind == "journey":
        return sorted(k for k, rec in tps.items() if rec.get("journey") == slug)
    if kind == "stakeholder":
        js = {rec.get("slug") for k, rec in offered.items() if k.startswith("journey:") and rec.get("stakeholder") == slug}
        return sorted(k for k, rec in tps.items() if rec.get("journey") in js or rec.get("stakeholder") == slug)
    return []


def carried(offered, streams, taken):
    """what binds to what is taken (EXTENSION R34): the touchpoints its steps serve, the value exchanges at those
    touchpoints, the solutions that carry a taken capability, and the Bodies that hold one with their Posts; each with
    the stakeholders, journeys and Bodies it names, a touchpoint its journey and stakeholder"""
    steps = {f"{s.split(':', 1)[1]}/{st.get('slug')}" for s in streams for st in offered[s].get("steps") or [] if isinstance(st, dict)}
    serve = serving(offered)
    taken = set(taken)
    caps = {k.split(":", 1)[1] for k in taken if k.startswith("capability:")}
    out = []
    for k, r in offered.items():
        kind = k.split(":", 1)[0]
        if "/" in k or k in taken:
            continue
        if (kind == "touchpoint" and steps & serve.get(r.get("slug"), set())
                or kind == "solution" and caps & set(r.get("carries") or []) or kind == "body" and caps & set(r.get("holds") or [])):
            out.append(k)
    tps = {k.split(":", 1)[1] for k in out if k.startswith("touchpoint:")}
    bodies = {k.split(":", 1)[1] for k in out if k.startswith("body:")}
    out += [k for k, r in offered.items() if "/" not in k and k not in taken and k not in out and (
        k.startswith("value-exchange:") and r.get("touchpoint") in tps or k.startswith("post:") and r.get("of") in bodies)]
    grew = True
    while grew:                                  # what the carried records name, Bodies up their `part_of` chain
        grew = False
        for k in list(out):
            for ref in bound(offered[k]):
                if ref.split(":", 1)[0] in CARRIED_BINDS and ref in offered and ref not in taken and ref not in out:
                    out.append(ref)
                    grew = True
    return out


def package(offered, scope, without=()):
    """one scope's package (the run's forms, part D): `whole` is every offered record; any other scope is its streams'
    bound part (R34's closure and the stakeholders a stream names, required) and its carried part. A stream in `without`
    is not selected with its package: only what the streams left reach is taken, and with `whole` also what no stream
    reaches. Returns the records, what they bind and the release does not offer, and what they bind outside the package"""
    if scope == "none":
        return [], [], []
    if one_record(scope):                        # one record: what MODEL has it bind, transitively; nothing carried
        if scope in without or scope not in offered:
            return [], [], []
        take, unresolved, todo = [], [], [scope]
        while todo:
            k = todo.pop(0)
            if k in take or k in unresolved:
                continue
            if k not in offered:
                unresolved.append(k)
                continue
            take.append(k)
            todo += list(bound(offered[k]))
        return take, unresolved, []
    every = sorted(k for k in offered if "/" not in k)
    streams = streams_in(scope, offered)
    left = [s for s in streams if s not in without]
    bound_, unresolved = closure(offered, left)
    for s in left:
        for x in offered[s].get("stakeholders") or []:
            k = f"stakeholder:{x}"
            if k in offered and k not in bound_:
                bound_.append(k)
            elif k not in offered and k not in unresolved:
                unresolved.append(k)
    take = bound_ + carried(offered, left, bound_)
    if scope == "whole":
        reached = set(closure(offered, streams)[0])
        reached |= set(carried(offered, streams, list(reached)))
        take += [k for k in every if k not in reached and k not in take and k not in without]
    held = set(take)
    unresolved += sorted({ref for k in take for ref in bound(offered[k]) if ref not in offered} - set(unresolved))
    beyond = sorted({ref for k in take for ref in bound(offered[k]) if ref in offered and ref not in held})
    return take, unresolved, beyond


def activation(offered, scope, not_select=(), before=(), origins=(), refers=None):
    """one activation as a commons would take it, derived once (R34; the run's forms, part D): what build.py
    writes, and what render_blueprint shows of a stream before anything is activated (D1, commons.o#109 6569487111,
    rule B). `not_select` is what a person does not select now, an id or `<kind>:*`; `before` what earlier answers did
    not select; `origins` the offered ids the commons already holds; `refers` the bindings a kind's specification declares
    (`x-refers`). What stays unresolved or beyond is derived after what is not selected (commons.o#109 6567072980).
    Raises ValueError for an id outside the scope"""
    whole = package(offered, scope)[0]
    asked = []
    for x in not_select:
        if not x.endswith(":*") and x not in whole:
            raise ValueError(f"`{x}` (--not-select) is no record of this scope")
        # `<kind>:*` is the tool's shorthand: it expands to the ids of that kind in the package, and the event lists the ids
        ids = [k for k in whole if k.split(":", 1)[0] == x[:-2]] if x.endswith(":*") else [x]
        asked += [k for k in ids if k not in asked]
    # a Post comes and goes with its Body (D1, commons.o#109 6566763628): a Body not selected takes its Posts, listed
    for b in [k for k in asked if k.startswith("body:")]:
        asked += [k for k in whole if k.startswith("post:") and k not in asked and offered[k].get("of") == b.split(":", 1)[1]]
    take = package(offered, scope, without=[k for k in asked if k.startswith("value-stream:")])[0]
    streams = [k for k in take if k.startswith("value-stream:")]
    bound_ = set(take) if one_record(scope) else set(closure(offered, streams)[0]) | {k for k in take if k.startswith("stakeholder:")}
    for field, target in (refers or {}).get("value-stream", {}).items():
        for s in streams:
            for v in offered[s].get(field) or []:
                if f"{target}:{v}" in offered and f"{target}:{v}" not in take:
                    take.append(f"{target}:{v}")
    unselected = [k for k in asked if k in whole] + [k for k in take if k in before and k not in origins and k not in asked]
    take = [k for k in take if k not in unselected]
    fresh = [k for k in take if k not in origins]
    refs = {ref for k in take for ref in bound(offered[k])}
    side = proposals(offered, touchpoints_of(offered, scope)) if one_record(scope) else {}
    return {"proposals": side, "take": take, "bound": [k for k in fresh if k in bound_], "carried": [k for k in fresh if k not in bound_],
            "reused": [k for k in take if k in origins], "not_selected": unselected,
            "unresolved": sorted(x for x in refs if x not in offered),
            "beyond": sorted(x for x in refs if x in offered and x not in take and x not in unselected)}


def not_selected(act):
    """the ids a decision does not select; `declined` is the key of the run's earlier candidates (EXTENSION part 5)"""
    return [str(x) for x in act.get("not_selected", act.get("declined")) or []]


def bound(rec):
    """`<kind>:<slug>` of every record a record binds: MODEL's bindings (check_model.FIELDS) and the step bindings"""
    for field, target in check_model.FIELDS.get(rec.get("kind"), []):
        if target in ("accountable", "step"):
            continue
        for v in rec.get(field) if isinstance(rec.get(field), list) else [rec.get(field)]:
            if isinstance(v, str) and v:
                yield f"{target}:{v}"
    if rec.get("kind") == "value-stream":
        for st in rec.get("steps") or []:
            for field, target in (("capabilities", "capability"), ("entities", "entity"), ("serves", "touchpoint")):
                for v in (st.get(field) or []) if isinstance(st, dict) else []:
                    yield f"{target}:{v}"


def reaches(rec):
    """what a record binds (`bound`), and what else it names: the steps of the earlier layout a touchpoint lies on, as
    `value-stream:<stream>/<step>`, and the entities an entity's fields (`reference(<entity>)`) and relations name
    (D1, commons.o#109 6569390384, 6569467351); read for what stays open, never for what an activation takes"""
    yield from bound(rec)
    if rec.get("kind") == "touchpoint":
        for s in rec.get("steps") or []:
            if isinstance(s, str) and "/" in s:
                yield f"value-stream:{s}"
    if rec.get("kind") == "entity":
        for a in rec.get("attributes") or []:
            m = REFERENCE.match(str(a.get("type"))) if isinstance(a, dict) else None
            if m:
                yield f"entity:{m[1]}"
        for x in rec.get("relations") or []:
            if isinstance(x, dict) and x.get("target"):
                yield f"entity:{x['target']}"


def changed(src, rec, path=""):
    """what an activated record changed against its archetype, by path (`steps[<slug>].title`); a field written as null
    differs from a field left absent (Q-b): presence is part of the difference. A list of mappings is read by each
    item's `slug` or `name`, any other list as a whole. The commons' own fields, a Body's `mandate` and a Post's
    `held_by`, are never compared: activation writes their gap form, and filling them is the commons' act"""
    skip = {"origin", "adopted_from", "start", "binds", "mandate", "held_by"} if not path else set()   # the commons' own (D1, #109)
    out = []
    for x in sorted(set(src) | set(rec)):
        if x in skip:
            continue
        here = f"{path}.{x}" if path else x
        a, b = src.get(x), rec.get(x)
        if (x in src) != (x in rec):
            out.append(here)
        elif isinstance(a, dict) and isinstance(b, dict):
            out += changed(a, b, here)
        elif isinstance(a, list) and isinstance(b, list) and a and b and all(isinstance(i, dict) for i in a + b):
            key = next((k for k in ("slug", "name") if all(k in i for i in a + b)), None)
            if key is None:
                out += [here] if a != b else []
                continue
            ia, ib = {i[key]: i for i in a}, {i[key]: i for i in b}
            for n in sorted(set(ia) | set(ib)):
                at = f"{here}[{n}]"
                if (n in ia) != (n in ib):
                    out.append(at)
                else:
                    out += changed(ia[n], ib[n], at)
            if [i[key] for i in a if i[key] in ib] != [i[key] for i in b if i[key] in ia]:
                out.append(f"{here} (order)")
        elif a != b:
            out.append(here)
    return out


def fit(core, r, ids=False):
    """fit (R9), install (R12) and adopt (R13, R12, R28): what a commons pins, installs and adopts"""
    cfg = yml(os.path.join(core, ".commons", "commons.yml")) or {}
    pins = {layout.ref_of(x): x for x in layout.pins(cfg)}   # a variant as `<library>/<model>/<variant>` (MODEL R30)
    domain = [i for i in pins if "/" in str(i) and str(i).split("/", 1)[1] not in layout.ESSENTIALS]   # the grammar is no extension of a kind (R9)
    prim = [i for i, x in pins.items() if x.get("primary")]
    if [i for i in prim if i not in domain]:      # the grammar answers for no kind (R9)
        r.fail("fit", f"the CORE marks {[i for i in prim if i not in domain]} primary: Commons Essentials is never a commons' primary (R9)")
    # several extensions side by side, at most one the primary (Holger, commons.o#109 6574765768: "b")
    if len(prim) > 1:
        r.fail("fit", f"the CORE marks {prim} primary: at most one, the extension of its kind (R9)")
    elif not [i for i in prim if i in domain]:   # the grammar alone, or no extension of its kind chosen yet
        r.gap("fit", "no primary yet: the CORE marks no extension of its kind as its primary beside Commons Essentials (R9)")
    libraries = set((cfg.get("libraries") or {}).keys())
    lock = yml(os.path.join(core, ".commons", "lock.yml")) or {}
    locked = {layout.ref_of(x): x for x in layout.pins(lock)}

    offers = {}
    for ref in [i for i in pins if "/" in str(i)]:
        lib = ref.split("/")[0]
        if lib not in libraries and lib == EARLIER:
            r.gap("install", f"`{ref}` comes from `{lib}`, which the CORE does not name in `libraries:`: unmigrated, it is no longer built in")
        elif lib not in libraries:
            r.fail("install", f"`{ref}` comes from the library `{lib}`, which the CORE does not name in `libraries:`")
        at = layout.copy(core, ref)
        if not os.path.isdir(at):
            r.fail("install", f"`{ref}` is pinned and not installed under `{os.path.relpath(layout.copy_target(core, ref), core)}/`")
            continue
        offers[ref] = released(r, at, ref, pins[ref].get("version"), locked.get(ref, {}).get("record"))
        on = sorted({str(check_model.origin(rec)).split("@")[0] for rec, _ in offers[ref].values()
                     if isinstance(rec, dict) and check_model.origin(rec)})
        if on:                                   # each holds the whole view of its domain (R9)
            r.fail("fit", f"`{ref}` stands on {', '.join(f'`{x}`' for x in on)}: its records name an origin; no extension stands on another (R9)")

    # origin (CORE R6, MODEL part 5): a record built from an installed model names its record there; what it changes
    # against it is derived, never listed
    seen = {}
    for k, (rec, f) in records(layout.runtime(core)).items():
        o = check_model.origin(rec)
        if not o:
            continue
        where = os.path.relpath(f, core)
        m = ORIGIN.match(str(o))
        if not m:
            r.fail("origin", f"`{where}`: `origin: {o}` is not `<library>/<model>@<version>#<kind>:<slug>`")
            continue
        ref = f"{m['library']}/{m['ext']}" + (f"/{m['variant']}" if m["variant"] else "")
        if ref not in pins:
            r.fail("origin", f"`{where}` is built from `{ref}`, which the CORE does not pin")
            continue
        if m["version"] != str(pins[ref].get("version")):
            rec_at = yml(os.path.join(layout.copy(core, ref), "release.yml")) or {}
            gone = {str(x.get("id")) for x in rec_at.get("retires") or [] if isinstance(x, dict)}
            if f"{m['kind']}:{m['slug']}" in gone and f"{m['kind']}:{m['slug']}" not in offers.get(ref, {}):
                r.gap("origin", f"`{where}` keeps its origin `{ref}@{m['version']}`, which {pins[ref].get('version')} retires: "
                                f"retired where it stands, the commons' own to keep or drop (MODEL part 5, CORE R39)")
                continue
            r.fail("origin", f"`{where}` is built from `{ref}@{m['version']}`, and the CORE pins {pins[ref].get('version')}")
        seen[o.split("@")[0] + "#" + o.split("#", 1)[1]] = where
        if ref in offers:
            src = offers[ref].get(f"{m['kind']}:{m['slug']}")
            if src is None:
                r.fail("origin", f"`{where}`: `{ref}` holds no `{m['kind']}:{m['slug']}`")
                continue
            diff = changed(src[0], rec)
            r.notes.append(f"origin: {where}: {'changed: ' + ', '.join(diff) if diff else 'unchanged'}")
        if rec.get("kind") == "body":
            if rec.get("mandate") is None:
                r.gap("origin", f"`{where}`: the Body's mandate is not resolved here; a null or absent mandate creates none (Q-b)")
            if "part_of" not in rec:
                r.gap("origin", f"`{where}`: where the Body stands in this commons (`part_of`) is not resolved here")
        if rec.get("kind") == "post" and not rec.get("held_by"):
            r.gap("origin", f"`{where}`: no one serves this Post here; building it appoints no one (Q-b)")

    # open (CORE R6): what a record built from a model binds and the commons does not hold is derived when it is read,
    # *not yet, offered* where an installed model holds it, else *not yet*, one line per kind, the ids on request; what
    # no record names stays on the shelf, neither a gap nor a decision. A recorded `decision` with `activates` and a
    # `not-selected` event are history: their words are read as notes and never checked (Holger 6610425987, 33)
    local = records(layout.runtime(core))
    held = set(local)                            # the commons' records, and the steps of its streams
    named, unselected = {}, {}
    for f in sorted(glob.glob(os.path.join(core, "lifecycle", "events", "*.y*ml"))):
        ev = yml(f) or {}
        if ev.get("kind") == "decision":
            eid = ev.get("id") or os.path.relpath(f, core)
            act = ev.get("activates") if isinstance(ev.get("activates"), dict) else {}
            named.update({str(x): eid for x in (ev.get("open") or []) + (act.get("open") or [])})
            unselected.update({str(x): eid for x in not_selected(act)})
    derived = {}
    for k, (rec, f) in local.items():
        if "/" in k or not check_model.origin(rec):
            continue
        for ref in sorted(set(reaches(rec))):
            if ref in held:
                continue
            why = "not yet, offered" if any(ref in o for o in offers.values()) else "not yet"
            if ref in unselected:
                r.notes.append(f"origin: {os.path.relpath(f, core)}: `{ref}` not selected, in the history ({unselected[ref]})")
            elif ref in named:
                r.notes.append(f"origin: {os.path.relpath(f, core)}: `{ref}` left open, in the history ({named[ref]}): {why}")
            else:
                derived.setdefault((why, "step" if "/" in ref else ref.split(":", 1)[0]), set()).add(ref)
    for (why, kind), refs in sorted(derived.items(), key=lambda x: (x[0][0], KINDS.index(x[0][1]) if x[0][1] in KINDS else len(KINDS))):
        r.gap("origin", f"open: {len(refs)} {kind} named by what the commons built from a model and not held: {why}"
                        + (f": {', '.join(sorted(refs))}" if ids else ""))

    # what is built, per family (CORE R6): derived, never kept
    for ref, recs in sorted(offers.items()):
        taken = {k.split("#", 1)[1] for k in seen if k.startswith(ref + "#")}
        for fam in sorted({(rec or {}).get("family") for k, (rec, _) in recs.items() if k.startswith("value-stream:") and "/" not in k} - {None}):
            fs = [k for k, (rec, _) in recs.items() if k.startswith("value-stream:") and "/" not in k and (rec or {}).get("family") == fam]
            r.notes.append(f"build: `{ref}` family `{fam}`: {sum(1 for k in fs if k in taken)} of {len(fs)} streams built from it")
    return r


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("domain_core", nargs="*")
    ap.add_argument("--core")
    ap.add_argument("--ids", action="store_true", help="with --core: the ids of every open binding, not only their counts")
    a = ap.parse_args()
    bad = 0
    runs = [(p, check(p)) for p in a.domain_core] + ([(a.core, fit(a.core, Report(), a.ids))] if a.core else [])
    for p, r in runs:
        n = {o: sum(1 for i in r.items if i[0] == o) for o in ("fail", "should", "gap")}
        print(f"# {p}: {n['fail']} fail · {n['should']} should · {n['gap']} gap")
        for o, c, t in r.items:
            print(f"{o}: {c}: {t}")
        for t in r.notes:
            print(f"note: {t}")
        bad += n["fail"]
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
