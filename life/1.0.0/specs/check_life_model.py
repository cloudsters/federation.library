#!/usr/bin/env python3
"""check_life_model.py — the own checks of life-model.md. Read-only.

  fields    every field of a record of the model is MODEL's, `binds`, or declared for its kind (R1)
  schema    every declared field has its shape (R2)
  forms     a Body or Post of the model names no holder (R3)
  bindings  a touchpoint's `journey` lists it in its `stages`, a value exchange's `touchpoint` names it among its `exchanges` (R4)
  refs      every rule the spec cites resolves to a rule of the installed Commons model's specifications

Usage:  check_life_model.py CORE [--model model.schema.json]
        MODEL's schema is read from the installed Commons model, models/commons/<library>/commons/specs/schemas/, else from the CORE's `specs/schemas/`, else from `commons.core` beside it, or `commons.o` under its former name (CORE R20). The summary names how many records it read, and none read is a fail.
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
OWN = json.load(open(os.path.join(HERE, "life-model.schema.json"), encoding="utf-8"))


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
    """every `<spec>` Rn and SPEC Rn the spec cites, outside its decision log, resolves to a rule of `specs`"""
    out, have = [], {}
    for n, line in enumerate(open(spec, encoding="utf-8").read().split("\n"), 1):
        if line.startswith("| 20"):                  # the decision log is history
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
    a = ap.parse_args()
    core = a.core
    mp = a.model or next((p for p in (*sorted(glob.glob(os.path.join(core, "models", "commons", "*", "commons", "specs", "schemas", "model.schema.json"))),
                                      os.path.join(core, "specs", "schemas", "model.schema.json"),
                                      os.path.join(core, "..", "commons.core", "specs", "schemas", "model.schema.json"),
                                      os.path.join(core, "..", "commons.o", "specs", "schemas", "model.schema.json"))
                          if os.path.exists(p)), None)
    if mp is None:
        print("gap: fields: MODEL's schema is not at hand; the fields are not checked")
        return 0
    model, common = model_fields(mp)
    out = []
    recs = {}
    held = [f for f in glob.glob(os.path.join(core, "models", "emulation", "*", "*", "*.y*ml"))   # the emulation (CORE R6)
            if os.path.basename(os.path.dirname(f)) not in ("loops", "specs", "state", "views", "LICENSES")]
    held += glob.glob(os.path.join(core, "offer", "registry", "*", "*.y*ml"))            # its earlier place (CORE R4)
    for f in sorted(held):
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

    if not recs:                                       # a check that reads nothing passes nothing (QA-1)
        out.append("fail: records: no record of the emulation was read; the model is unchecked")
    sp = next((p for p in sorted(glob.glob(os.path.join(core, "models", "commons", "*", "commons", "specs")))
               if os.path.exists(os.path.join(p, "model.md"))), None)
    if sp is None:
        out.append("gap: refs: no Commons model's specs at hand; the rules the spec cites are not resolved")
    else:
        out += refs(os.path.join(HERE, "life-model.md"), sp)
    for line in out:
        print(line)
    print(f"# {core}: {sum(1 for l in out if l.startswith('fail'))} fail, {len(recs)} records read")
    return 1 if any(l.startswith("fail") for l in out) else 0


if __name__ == "__main__":
    sys.exit(main())
