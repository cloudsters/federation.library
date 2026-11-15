#!/usr/bin/env python3
"""check_health_model.py — the own checks of health-model.md. Read-only.

  fields    every field of a record of the model is MODEL's, `binds`, or declared for its kind (R1)
  schema    every declared field has its shape (R2)
  overlays  overlays are named for their jurisdiction and bind records of the model to sources of it (R3, R4)
  forms     a Body or Post of the model names no holder (R5)
  bindings  a touchpoint's `journey` lists it in its `stages`, a value exchange's `touchpoint` names it among its `exchanges` (R6)

  refs      every rule the spec cites resolves to a rule of the Commons model's specs (O1-CE)

Usage:  check_health_model.py CORE [--model model.schema.json]
        MODEL's schema is read from the CORE's installed `specs/schemas/`, else from `commons.core` beside it, or `commons.o` under its former name (CORE R20).
Exit 0 when clean, 1 with findings otherwise.
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
ELEMENTS = ("bodies", "capabilities", "entities", "journeys", "posts", "solutions", "stakeholders", "touchpoints",
            "value-exchanges", "value-streams")
OWN = json.load(open(os.path.join(HERE, "health-model.schema.json"), encoding="utf-8"))


def yml(p):
    return yaml.safe_load(open(p, encoding="utf-8")) if os.path.exists(p) else None


def model_fields(path):
    s = json.load(open(path, encoding="utf-8"))
    d = s.get("$defs") or {}
    common = set((d.get("record") or {}).get("properties") or {})
    return {k: common | set((v.get("properties") or {})) for k, v in d.items()}, common


SPEC_NAMES = r"MODEL|CORE-KNOWLEDGE|CORE-VIEWS|CORE|LIBRARY-PATTERNS|LIBRARY|MCP|GRAPH-ENGINE|GRAPH|FLOW-BODIES|FLOW-GRAPH|FLOW-WORKSHOPS|FLOW|FABRIC|LEARN|SPECIFICATION|EXTENSION"
REF = re.compile(r"(?:`(" + SPEC_NAMES.lower() + r")`|\b(" + SPEC_NAMES + r")\b)\s*\(?((?:R\d+)(?:\s*,\s*R\d+)*)")


def refs(spec, specs):
    """every `<spec>` Rn and SPEC Rn the spec cites, outside its change log, resolves to a rule of `specs`"""
    out = []
    have = {}
    for n, line in enumerate(open(spec, encoding="utf-8").read().split("\n"), 1):
        if line.startswith("| 20"):                  # the change log is history
            continue
        for m in REF.finditer(line):
            name = (m.group(1) or m.group(2)).lower()
            if name not in have:
                f = os.path.join(specs, f"{name}.md")
                have[name] = set(re.findall(r"(?m)^\| (R\d+) \|", open(f, encoding="utf-8").read())) if os.path.exists(f) else None
            for rid in re.findall(r"R\d+", m.group(3)):
                if have[name] is None:
                    out.append(f"fail: refs: line {n} cites `{name}` {rid}, and the Commons model has no specification `{name}`")
                elif rid not in have[name]:
                    out.append(f"fail: refs: line {n} cites `{name}` {rid}, a rule `{name}` does not hold")
    return out


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("core")
    ap.add_argument("--model")
    ap.add_argument("--specs", help="the specs of the Commons model the spec's rules resolve against")
    a = ap.parse_args()
    core = a.core
    mp = a.model or next((p for p in (os.path.join(core, "specs", "schemas", "model.schema.json"),
                                      os.path.join(core, "..", "commons.core", "specs", "schemas", "model.schema.json"),
                                      os.path.join(core, "..", "commons.o", "specs", "schemas", "model.schema.json"))
                          if os.path.exists(p)), None)
    if mp is None:
        print("gap: fields: MODEL's schema is not at hand; the fields are not checked")
        return 0
    model, common = model_fields(mp)
    out = []
    recs = {}
    files = glob.glob(os.path.join(core, "offer", "registry", "*", "*.y*ml"))   # structure 0.3.0, the earlier place
    if not files:                                    # 0.4.0: the emulation's element folders (CORE R6)
        roots = [core] if os.path.exists(os.path.join(core, "model.yml")) else glob.glob(os.path.join(core, "models", "emulation", "*"))
        files = [f for r in roots for e in ELEMENTS for f in glob.glob(os.path.join(r, e, "*.y*ml"))]
    for f in sorted(files):
        rec = yml(f) or {}
        if not isinstance(rec, dict) or not rec.get("kind"):
            continue
        kind, where = rec["kind"], os.path.relpath(f, core)
        recs[f"{kind}:{rec.get('slug')}"] = rec
        declared = set(((OWN["$defs"].get(kind) or {}).get("properties") or {}))
        allowed = model.get(kind, common) | {"binds"} | declared
        for k in rec:
            if k not in allowed:
                out.append(f"fail: fields: `{where}` carries `{k}`, which neither MODEL nor part 5 declares for `{kind}`")
        if declared:
            sub = {k: v for k, v in rec.items() if k in declared}
            for e in jsonschema.Draft202012Validator({"$defs": OWN["$defs"], "$ref": f"#/$defs/{kind}"}).iter_errors(sub):
                out.append(f"fail: schema: `{where}`: {'/'.join(map(str, e.absolute_path))}: {e.message[:100]}")
        if kind in ("body", "post") and (rec.get("held_by") or rec.get("holder")):
            out.append(f"fail: forms: `{where}` names a holder: a {kind} of the model is a form")

    for key, rec in recs.items():
        if rec["kind"] == "touchpoint" and rec.get("journey"):
            j = recs.get(f"journey:{rec['journey']}") or {}
            if rec.get("slug") not in {t for s in j.get("stages") or [] for t in s.get("touchpoints") or []}:
                out.append(f"fail: bindings: `{key}` names the journey `{rec['journey']}`, whose stages do not pass through it")
        if rec["kind"] == "value-exchange" and rec.get("touchpoint"):
            tp = recs.get(f"touchpoint:{rec['touchpoint']}") or {}
            if rec.get("slug") not in (tp.get("exchanges") or []):
                out.append(f"fail: bindings: `{key}` names the touchpoint `{rec['touchpoint']}`, whose `exchanges` do not name it")

    sources = {s.get("id"): s for s in (yml(os.path.join(core, "knowledge", "sources.yml")) or {}).get("sources") or []}
    overlaid = set()
    for f in sorted(glob.glob(os.path.join(core, "knowledge", "jurisdictions", "*.y*ml"))
                   or glob.glob(os.path.join(core, "offer", "overlays", "*.y*ml"))):   # offer/overlays/ earlier
        ov, where = yml(f) or {}, os.path.relpath(f, core)
        name = os.path.basename(f).rsplit(".", 1)[0]
        overlaid.add(name)
        for e in jsonschema.Draft202012Validator({"$defs": OWN["$defs"], "$ref": "#/$defs/overlay"}).iter_errors(ov):
            out.append(f"fail: overlays: `{where}`: {'/'.join(map(str, e.absolute_path))}: {e.message[:100]}")
        if ov.get("jurisdiction") != name:
            out.append(f"fail: overlays: `{where}` states the jurisdiction `{ov.get('jurisdiction')}`")
        for b in ov.get("bindings") or []:
            if b.get("record") not in recs:
                out.append(f"fail: overlays: `{where}` binds `{b.get('record')}`, which the model does not hold")
            for x in b.get("binds") or []:
                s = sources.get(x.get("source"))
                if s is None:
                    out.append(f"fail: overlays: `{where}`: `{x.get('source')}` is no source of `knowledge/sources.yml`")
                elif s.get("jurisdiction") != name:
                    out.append(f"fail: overlays: `{where}`: `{x.get('source')}` is of `{s.get('jurisdiction')}`, not `{name}`")
                elif str(s.get("edition")) != str(x.get("edition")):
                    out.append(f"fail: overlays: `{where}`: `{x.get('source')}` is bound at `{x.get('edition')}`, and the source holds `{s.get('edition')}`")
    for key, rec in recs.items():
        for x in rec.get("binds") or []:
            s = sources.get(x.get("source")) if isinstance(x, dict) else None
            if s and s.get("jurisdiction") in overlaid:
                out.append(f"fail: overlays: `{key}` binds `{x.get('source')}` of `{s.get('jurisdiction')}` in its base: it belongs in that overlay")
    spec = os.path.join(HERE, "health-model.md")
    sp = a.specs or next((p for p in (*glob.glob(os.path.join(core, "models", "commons", "*", "commons", "specs")),
                                      os.path.join(core, "..", "commons.core", "specs")) if os.path.exists(os.path.join(p, "model.md"))), None)
    if sp is None:
        out.append("gap: refs: no Commons model's specs at hand; the rules the spec cites are not resolved")
    else:
        out += refs(spec, sp)

    for line in out:
        print(line)
    print(f"# {core}: {sum(1 for l in out if l.startswith('fail'))} fail")
    return 1 if any(l.startswith("fail") for l in out) else 0


if __name__ == "__main__":
    sys.exit(main())
