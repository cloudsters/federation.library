#!/usr/bin/env python3
"""extract.py — the extractor: cuts the patterns of orbits 0 to 3 from the stock of a CORE, under a policy, from one
released graph run, with the agents' index (LIBRARY-PATTERNS R17, R18, part 5; Holger, commons.core#110 6627102753,
X-1 to X-3; 6704790380, X-b). release.py calls it to release an extract; run alone, it cuts into a folder for reading.

The policy (`policy.yml`) names the register's source that holds the stock, the folders of it the extract takes, its
scope and its licence:

    source: patterns
    folders: [0-singularity, 1-principles, 2-commons-base]
    scope: orbits 0-3
    licence: CC-BY-SA-4.0

What it does:
- reads the run: it must be `released`, and the source must be in its cut with the digest the stock has now (R17);
- takes every pattern of orbit 0 to 3 in the policy's folders, at its release path `<folder>/<file>`;
- leaves out every pattern with a fail of the pattern checks, until none is left (X-3): an incomplete pattern fails
  closed (R5), and nothing goes in that fails. An `archived` pattern stays in the stock and is left out too (R10, X-b).
  Each one left out is named, and the cut is counted: the stock read, the archived, the others left out and the
  patterns cut, in all and by folder, as the release record states them (R17);
- writes the index: a head line naming the release, the run, the extractor, the policy, the scope and the licence,
  then one line per pattern, its families and dimensions those it holds `ratified` (R18), its links the curated
  relations inside the extract (`by: stated`) and the run's computed edges between its patterns, and `beyond` at most
  five ids outside it.

Usage:  extract.py CORE --run RUN --policy POLICY --into FOLDER --release owner/library@version [--names FILE] [--terms FILE]
        --names and --terms are the lists the library's gate reads (LIBRARY R10, LIBRARY-PATTERNS R6, R8), kept
        outside git; a pattern that names one is left out.
"""
import argparse
import json
import os
import re
import shutil
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)
import answer_graph as ag  # noqa: E402
import check_library  # noqa: E402
from check_core import Report  # noqa: E402

CURATED = ("requires", "complementary", "alternatives")
FILE = re.compile(r"^`([^`]+)`")


def yml(p):
    return yaml.safe_load(open(p, encoding="utf-8")) if os.path.isfile(p) else None


def ref_of(d, rel):
    """`owner/repo@rev:path` of a file in the repository a folder lies in"""
    remote = (ag.git(d, "remote", "get-url", "origin") or b"").decode().strip().removesuffix(".git").rstrip("/")
    repo = "/".join(remote.replace(":", "/").split("/")[-2:]) or "local/unknown"
    rev = (ag.git(d, "rev-parse", "--short=7", "HEAD") or b"").decode().strip() or "0000000"
    pre = (ag.git(d, "rev-parse", "--show-prefix") or b"").decode().strip()
    return f"{repo}@{rev}:{pre}{rel}".replace(os.sep, "/")


def clean(text, inside, principles):
    """the copy of a pattern as the extract holds it (QA-1): its curated relations name only patterns of the extract and
    its hubs only principles of it, the others dropped from the front matter, an item whole with its further lines; an
    emptied list becomes `[]`"""
    end = text.index("\n---", 4)
    head, body = text[:end].split("\n"), text[end:]
    out, i = [], 0
    while i < len(head):
        line = head[i]
        if line in ("  requires:", "  complementary:", "  alternatives:"):
            indent, known = "  ", inside
        elif line == "gravitational_hubs:" and principles is not None:
            indent, known = "", principles
        else:
            out.append(line)
            i += 1
            continue
        start = len(out)
        out.append(line)
        j = i + 1
        while j < len(head) and head[j].startswith(indent + "- "):
            item = [head[j]]
            j += 1
            while j < len(head) and head[j].startswith(indent + "  ") and not head[j].startswith(indent + "- "):
                item.append(head[j])
                j += 1
            names = set()
            for x in item:
                x = re.sub(r"^\s*-?\s*", "", x).strip()
                m = re.match(r"^(id|slug|hub_id):\s*(.+)$", x)
                names.add((m[2] if m else x).strip().strip("'\""))
            if names & set(known):
                out += item
        if len(out) == start + 1:
            out[start] = line + " []"
        i = j
    return "\n".join(out) + body


def select(folder, names=None, terms=None):
    """the patterns of a folder with no fail of the pattern checks: each file with a fail leaves, each pattern of a
    `requires` circle and each `archived` one, until none is left; returns (kept {release path: front matter}, left out {release path: first
    fail}, fails naming no file)"""
    left = {}
    while True:
        r = Report()
        pats = check_library.check_patterns(r, folder, folder, names, terms)
        where = {pid: check_library.rel(p, folder) for pid, (fm, p) in pats.items()}
        bad = {}
        for o, c, t in r.items:
            m = FILE.match(t)
            if o == "fail" and m and m[1].endswith(".md"):
                bad.setdefault(m[1], f"{c}: {t[m.end():].lstrip(': ')}")
            elif o == "fail" and c == "relations" and "runs in a circle" in t:
                for pid in re.findall(r"pat_[a-z0-9_]+", t):
                    if pid in where:
                        bad.setdefault(where[pid], "relations: it lies on a `requires` circle (R9)")
        for pid, (fm, _) in pats.items():
            if (fm.get("lifecycle") or {}).get("status") == "archived":
                bad.setdefault(where[pid], "lifecycle: it is `archived`, kept in the stock and not cut (R10, X-b)")
        if not bad:
            general = [f"{c}: {t}" for o, c, t in r.items if o == "fail"]
            kept = {check_library.rel(p, folder): fm for fm, p in pats.values()}
            return kept, left, general
        for f, why in bad.items():
            left[f] = why
            os.remove(os.path.join(folder, f))


ARCHIVED = "lifecycle: it is `archived`"


def counted(stock, kept, left):
    """the count of a cut, in all and by folder: the stock read, the archived, the others left out and the patterns cut,
    so that stock = archived + left_out + cut (R17; the Office, GO-3, on the count of v2026.11.3)"""
    by = {f: {"stock": n, "archived": 0, "left_out": 0, "cut": 0} for f, n in stock.items()}
    for rp, why in left.items():
        by[rp.split("/", 1)[0]]["archived" if why.startswith(ARCHIVED) else "left_out"] += 1
    for rp in kept:
        by[rp.split("/", 1)[0]]["cut"] += 1
    total = {k: sum(x[k] for x in by.values()) for k in ("stock", "archived", "left_out", "cut")}
    return {**total, "by_folder": by}


def cut(core, run_id, policy, into, release, extractor=None, policy_ref=None, lid=None, names=None, terms=None):
    """cuts the extract into `into`; returns (the index lines, the patterns left out, fails naming no file, the count)"""
    register = ag.register_of(core)
    pol = yml(policy) or {}
    e = next((x for x in register if x["id"] == pol.get("source")), None)
    if e is None:
        sys.exit(f"the policy's source `{pol.get('source')}` is not in the register `graph/sources.yml`")
    runs = ag.runs_of(core)
    if run_id not in runs:
        sys.exit(f"no run `{run_id}` in `graph/runs/`")
    run, edges, _ = runs[run_id]
    if ag.state(run) != "released":
        sys.exit(f"the run `{run_id}` is `{ag.state(run)}`: an extract is cut from a released run (R17)")
    c = next((x for x in run.get("cut") or [] if x.get("source") == e["id"]), None)
    if c is None:
        sys.exit(f"the run `{run_id}` did not read `{e['id']}` (R17)")
    if ag.digest(ag.Tree(core), register, e) != c.get("digest"):
        sys.exit(f"`{e['id']}` has changed since the run `{run_id}` read it: order a new run (R17)")
    stage = tempfile.mkdtemp(prefix=".extract-")
    try:
        base = os.path.join(core, e["ref"])
        for f in pol.get("folders") or []:
            for p in sorted(os.listdir(os.path.join(base, f))) if os.path.isdir(os.path.join(base, f)) else []:
                if not p.endswith(".md"):
                    continue
                fm, _ = check_library.front(os.path.join(base, f, p))
                if fm and isinstance(fm.get("orbital_layer"), int) and 0 <= fm["orbital_layer"] <= 3:
                    os.makedirs(os.path.join(stage, f), exist_ok=True)
                    shutil.copy2(os.path.join(base, f, p), os.path.join(stage, f, p))
        stock = {f: len(os.listdir(os.path.join(stage, f))) for f in pol.get("folders") or [] if os.path.isdir(os.path.join(stage, f))}
        kept, left, general = select(stage, names, terms)
        count = counted(stock, kept, left)
        lib = lid or release.split("@")[0].split("/")[-1]   # the library's id qualifies every pattern (R2)
        ids = {fm["id"]: rp for rp, fm in kept.items()}
        by_slug = {fm.get("slug"): fm["id"] for fm in kept.values()}
        computed = {}
        for x in edges:
            a, b = str(x.get("from", "")), str(x.get("to", ""))
            if a in ids and b in ids:
                computed.setdefault(a, []).append({"to": f"{lib}/{b}", "kind": x.get("kind") or "related", "by": "computed",
                                                   "method": x.get("method") or (run.get("method") or {}).get("kind")})
        head = {"kind": "index", "format": "agents-index/1", "release": release, "graph_run": run_id,
                "extractor": extractor or ref_of(HERE, "extract.py"), "policy": policy_ref or ref_of(os.path.dirname(os.path.abspath(policy)), os.path.basename(policy)),
                "scope": pol.get("scope") or "orbits 0-3", "licence": pol.get("licence") or "CC-BY-SA-4.0"}
        lines = [head]
        for rp, fm in sorted(kept.items()):
            vm = fm.get("value_model") or {}
            ratified = lambda k: [f"{k}:{a['slug']}" for a in vm.get(k) or [] if isinstance(a, dict) and a.get("status") == "ratified" and a.get("slug")]
            links, beyond = [], []
            for k in CURATED:
                for t in (fm.get("relationships") or {}).get(k) or []:
                    t = t.get("id") or t.get("slug") if isinstance(t, dict) else t
                    to = t if t in ids else by_slug.get(t)
                    if to:
                        links.append({"to": f"{lib}/{to}", "kind": k, "by": "stated"})
                    elif t not in beyond:
                        beyond.append(str(t))
            hints = (fm.get("ontology") or {}).get("search_hints") or {}
            lines.append({"kind": "pattern", "id": f"{lib}/{fm['id']}", "slug": fm.get("slug"), "orbit": fm["orbital_layer"],
                          "file": rp, "title": fm.get("title"), "tension": hints.get("primary_tension"), "summary": fm.get("summary"),
                          "context": {"labels": [], "dimensions": ratified("vsd"), "families": ratified("vsf")},
                          "hubs": [h.get("hub_id") if isinstance(h, dict) else h for h in fm.get("gravitational_hubs") or []],
                          "links": links + computed.get(fm["id"], []), "beyond": beyond[:5]})
        os.makedirs(into, exist_ok=True)
        principles = {fm.get(k) for rp, fm in kept.items() if rp.startswith("1-principles/") for k in ("id", "slug")}
        inside = set(ids) | set(by_slug)
        for rp, fm in kept.items():
            os.makedirs(os.path.dirname(os.path.join(into, rp)), exist_ok=True)
            text = open(os.path.join(stage, rp), "rb").read().decode("utf-8").replace("\r\n", "\n")   # LF, whatever the checkout
            anchored = not rp.startswith(("0-singularity/", "1-principles/"))
            text = clean(text, inside, principles if anchored else None)
            open(os.path.join(into, rp), "wb").write(text.encode("utf-8"))
        with open(os.path.join(into, "index.jsonl"), "w", encoding="utf-8", newline="\n") as f:
            for x in lines:
                f.write(json.dumps(x, ensure_ascii=False) + "\n")
        return lines, left, general, count
    finally:
        shutil.rmtree(stage, ignore_errors=True)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("core")
    ap.add_argument("--run", required=True)
    ap.add_argument("--policy", required=True)
    ap.add_argument("--into", required=True)
    ap.add_argument("--release", required=True)
    ap.add_argument("--names")
    ap.add_argument("--terms")
    a = ap.parse_args()
    lines, left, general, count = cut(a.core, a.run, a.policy, a.into, a.release,
                               names=check_library.wordlist(a.names), terms=check_library.wordlist(a.terms))
    for f, why in sorted(left.items()):
        print(f"left out: {f}: {why}")
    for t in general:
        print(f"fail: {t}")
    print(f"# {count['cut']} of {count['stock']} patterns cut, {count['archived']} archived, {count['left_out']} left out")
    return 1 if general else 0


if __name__ == "__main__":
    sys.exit(main())
