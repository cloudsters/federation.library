#!/usr/bin/env python3
"""graph_run.py — the reference run of the Graph Engine for the method `stated-only` (graph-engine R1–R7; LIBRARY-PATTERNS
R17; Holger, commons.core#110 6627102753, X-1 to X-3).

A run of the method `stated-only` computes no edge: the joins a commons states are read from its sources by every
reader (`graph` R6), so its package holds an empty `edges.jsonl` and `proposals.yml`. What it gives is the record:
the cut, each source at a revision with its digest, so that an extract can name the run it was cut from and anyone
can retrace what that run read. No model is called (R2).

Two acts, each writing into `graph/runs/<run>/` and nowhere else (R4):
  graph_run.py CORE --id RUN [--sources a,b] [--parent RUN]
        orders and computes the run: every named source of the register (default: all but a pinned extract) read
        at HEAD, which must hold it unchanged, its digest taken; states `ordered` and `computed`
  graph_run.py CORE --id RUN --release --by WHO --where ITEM
        appends `released`, only on the commons' word, naming who gave it and where it is recorded (R7). The
        package is then committed alone (graph R4)
"""
import argparse
import datetime
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)
import answer_graph as ag  # noqa: E402
from check_graph import run_key  # noqa: E402

METHOD = {"kind": "stated-only", "procedure": "stated-only@1", "params": {}, "models": [],
          "tools": ["graph_run.py", "answer_graph.py readers, graph.md part 5"]}
HEAD = "# one run package of the Graph Engine (graph-engine R4, R5); only the engine writes here\n"


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def dump(path, doc):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(HEAD)
        yaml.safe_dump(doc, f, sort_keys=False, allow_unicode=True, width=120)


def order(core, rid, sources=None, parent=None):
    """the run ordered and computed; returns its folder"""
    register = ag.register_of(core)
    if not register:
        sys.exit(f"`{core}` has no register `graph/sources.yml` (graph R1)")
    pick = [e for e in register if (e["id"] in sources if sources else e.get("pin") != "lock")]
    if sources and len(pick) != len(sources):
        sys.exit(f"not in the register: {', '.join(sorted(set(sources) - {e['id'] for e in pick}))}")
    rev = (ag.git(core, "rev-parse", "HEAD") or b"").decode().strip()
    if not rev:
        sys.exit(f"`{core}` is not in git; a run reads its sources at a revision (R1)")
    for e in pick:
        if ag.dirty(core, register, e):
            sys.exit(f"the source `{e['id']}` has changes not committed; commit them first, so that the cut names what was read (R1)")
    pd = os.path.join(core, "graph", "runs", rid)
    if os.path.exists(pd):
        sys.exit(f"`graph/runs/{rid}/` exists: a run is never ordered twice (R6)")
    tree = ag.at(core, rev)
    cut = [{"source": e["id"], "rev": rev, "digest": ag.digest(tree, register, e)} for e in pick]
    tool = (ag.git(HERE, "rev-parse", "--short=7", "HEAD") or b"").decode().strip() or "unknown"
    remote = (ag.git(HERE, "remote", "get-url", "origin") or b"").decode().strip().removesuffix(".git").rstrip("/")
    engine = f"{'/'.join(remote.split('/')[-2:]) or 'Commons-Engineering/commons.core'}@{tool}"
    run = {"id": rid, "engine": engine, "cut": cut, "method": METHOD,
           "policy": {"classes": {e["id"]: e["class"] for e in pick}, "where": "local",
                      "budget": "none needed: a program, no model call"},
           "parent": parent, "states": [{"state": "ordered", "at": now()}]}
    os.makedirs(pd)
    open(os.path.join(pd, "edges.jsonl"), "w", encoding="utf-8", newline="\n").close()
    with open(os.path.join(pd, "proposals.yml"), "w", encoding="utf-8", newline="\n") as f:
        f.write("proposals: []\n")
    run["states"].append({"state": "computed", "at": now()})
    run["findings"] = [f"stated-only: no computed edge, no proposal; {len(cut)} source(s) read at {rev[:7]}"]
    run["ledger"] = {"model_calls": 0}
    run["outputs"] = {f: {"digest": f"sha256:{ag.filehash(os.path.join(pd, f))}"} for f in ("edges.jsonl", "proposals.yml")}
    run["key"] = run_key(run)
    dump(os.path.join(pd, "run.yml"), run)
    return pd


def release(core, rid, by, where):
    """the run released on the commons' word (R7)"""
    p = os.path.join(core, "graph", "runs", rid, "run.yml")
    run = ag.yml(p) if os.path.isfile(p) else None
    if not run:
        sys.exit(f"no run `{rid}` in `graph/runs/`")
    if ag.state(run) != "computed":
        sys.exit(f"the run `{rid}` is `{ag.state(run)}`; only a computed run is released (R6)")
    run["states"].append({"state": "released", "at": now(), "by": by, "where": where})
    dump(p, run)
    return p


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("core")
    ap.add_argument("--id", required=True)
    ap.add_argument("--sources")
    ap.add_argument("--parent")
    ap.add_argument("--release", action="store_true")
    ap.add_argument("--by")
    ap.add_argument("--where")
    a = ap.parse_args()
    if a.release:
        if not (a.by and a.where):
            sys.exit("--release needs --by and --where: who gave the word and where it is recorded (R7)")
        print(f"# released: {release(a.core, a.id, a.by, a.where)}")
    else:
        print(f"# computed: {order(a.core, a.id, a.sources.split(',') if a.sources else None, a.parent)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
