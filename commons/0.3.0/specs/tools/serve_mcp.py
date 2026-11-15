#!/usr/bin/env python3
"""serve_mcp.py — the reference pipeline of a commons' MCP (mcp.md R2): identity to grant, grant to the permitted cut,
the cut to a result, the result to its envelope, and one use record per call.

It is the semantics of the serving contract, not a server: a transport hands it the account the sign-in reports, a
platform account or a key, with the verified address the sign-in reports, and serves what it returns. The account is
one user of `access.yml`, in one shell, and its grant is its shell's, narrowed by its own; a technical user holds no
more than the human accountable for it, and an agent works as the user it works under. An account that is no user is
admitted by an entry of DOCK that matches the domain of its address (R27). At an address that requires sign-in, only
a client `access.yml` names under `clients`, by the way it registers, is admitted, `local` clients where it names none
(R29, `client_admitted`);
the transport refuses any other before it serves anything. Its three tools, and only these, are
`answer` and `node` over GRAPH's reader (answer_graph.py), `node` returning the record itself, and `propose`, which
writes one item into a local outbox standing in for the platform's board and returns a receipt, a maker's board
resolved from the installed release's own record (R2). What it serves of a release is the release whole, as the
graph reads it, the canon and an installed extract of patterns among the sources (R18); a model's depth is part of
the model, so no tool of its own serves it (MODEL part 5): `node` returns a record's depth with it, the aspects and
deeper records the installed model its `origin` names holds for it, within the budget of nodes (D-a).

What the server writes into an item, destination, user, request and state, it builds itself; a caller's payload is
taken field by field from a list, and a field outside it refuses the write. A receipt's state is `sent` until the
board records more: the reference has no board, so it reports no later state. `--setup` prints what the set-up
generates from `access.yml`: the platform's teams and the ruleset of each repository, one per pair of shells (R26).

Usage:  serve_mcp.py CORE [--as ACCOUNT [--address ADDRESS]] --state DIR TOOL [key=value ...]
        serve_mcp.py CORE --stdio [--as ACCOUNT] --state DIR      the local MCP over stdio (mcp_server.py)
        serve_mcp.py CORE --http PORT --state DIR                  the general HTTP adapter, run locally
        serve_mcp.py CORE --setup
        e.g. serve_mcp.py tool-library.core --as account:ben --state /tmp/mcp answer question="who repairs tools"
"""
import argparse
import datetime
import glob
import hashlib
import json
import os
import re
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True   # the tools never write into the install they lie in (SPECIFICATION R29; `extension` R12)
sys.path.insert(0, HERE)
import answer_graph  # noqa: E402
import layout  # noqa: E402

SHELLS = ["SEED", "CORE", "PEER", "OPEN", "DOCK", "ROAM"]          # MODEL's, from the centre outward
PAIRS = {("SEED", "CORE"): ["check_core"], ("PEER", "OPEN"): ["check_flow"]}   # a repository per pair, and its checks (R26)
CLASSES = {"public": "ROAM", "member": "OPEN", "practice": "PEER", "depth": "CORE", "emulation": "CORE"}   # S6 and SI-C, unless the commons says otherwise
BUDGET = {"depth": 2, "nodes": 5, "calls": 60}
KNOWLEDGE_DEPTH = ("knowledge", "depth")                           # a maker's depth, served under the class `depth` and never released (L-1)
TOOLS = ("answer", "node", "propose")                              # R2's three tools, and no other
PAYLOAD = {"to", "text", "anchor", "scope", "release", "record", "kind", "source"}   # what a caller may say (R12)
FIELDS = {"account", "match", "shell", "sources", "writes", "budget", "expires", "accountable"}
ROLED = ("CORE", "PEER", "OPEN")                                    # the shells a role the sign-in reports may map to (R3, SA-d)
DOMAIN = re.compile(r"^\*@[a-z0-9-]+(\.[a-z0-9-]+)+$")             # an entry of DOCK by pattern: one domain (R27)
RELEASE = re.compile(r"^(?P<library>[a-z0-9-]+)/(?P<id>[a-z0-9-]+)(/(?P<variant>[a-z0-9-]+))?@(?P<version>[^@\s]+)$")   # a variant's `<model>/<variant>` (MODEL R30)
BOARD = re.compile(r"^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$")             # where answers about a release go, `owner/repo` (library R3)


def yml(p):
    try:
        return yaml.safe_load(open(p, encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return None


def digest(x):
    return "sha256:" + hashlib.sha256(json.dumps(x, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def access_of(core):
    return yml(os.path.join(core, ".commons", "access.yml"))


def classes_of(acc):
    """each class to the outermost shell that reads it; an emulation's is CORE, which `access.yml` cannot move (R4)"""
    return {**CLASSES, **((acc or {}).get("classes") or {}), "emulation": "CORE"}


def visible(acc, shell):
    """the classes a grant of this shell sees: those whose outermost shell is this one or lies further out (R4)"""
    return sorted(c for c, s in classes_of(acc).items() if s in SHELLS and SHELLS.index(s) >= SHELLS.index(shell))


def budget_of(acc, grant):
    return {**BUDGET, **((acc or {}).get("budget") or {}), **(grant.get("budget") or {})}


def day(x):
    """a calendar date, or None for a spelling that is no date"""
    try:
        return datetime.date.fromisoformat(str(x))
    except ValueError:
        return None


def expired(e, today):
    """an expiry that is no calendar date counts as passed; the day of the expiry itself still holds (R3, R27)"""
    if not e.get("expires"):
        return False
    d = day(e["expires"])
    return d is None or d < day(today)


def users_of(acc):
    return [u for u in (acc or {}).get("users") or [] if isinstance(u, dict)]


def by_entry(u):
    """an entry that admits accounts by what their sign-in reports, an address's domain (R27)"""
    return u.get("match") is not None


def technical(u):
    return not by_entry(u) and (bool(u.get("accountable")) or str(u.get("account", "")).startswith("key:"))


def human(u):
    return not by_entry(u) and not technical(u)


def shell_grant(acc, shell):
    return {"shell": shell, **((((acc or {}).get("shells") or {}).get(shell)) or {})}


def offer(acc):
    """what a grant of each shell gets, from `access.yml` without its users: the classes it reads, the sources it is
    narrowed to, its writes and its budget; ROAM's is the `public` grant (R28)"""
    out = {}
    for sh in SHELLS:
        g = shell_grant(acc, sh) if sh != "ROAM" else ({"shell": "ROAM", **acc["public"], "writes": []} if isinstance((acc or {}).get("public"), dict) else None)
        out[sh] = {"reads": [], "writes": [], "budget": {}} if g is None else \
            {"reads": visible(acc, sh), **({"sources": g["sources"]} if g.get("sources") else {}), "writes": g.get("writes") or [], "budget": budget_of(acc, g)}
    return out


def roles_of(acc):
    """{role: shell}: a role the sign-in reports, as the identity provider names it, to the shell its account stands in,
    with no person; who holds which role is the identity provider's (SA-d). A role mapped to SEED or ROAM maps nowhere"""
    roles = (acc or {}).get("roles") if isinstance((acc or {}).get("roles"), dict) else {}
    return {str(r): s for r, s in roles.items() if s in ROLED}


LOOPBACK = re.compile(r"^http://(127\.0\.0\.1|localhost|\[::1\])(:\d+)?(/|$)")   # a redirect on the person's own device


def clients_of(acc):
    """the clients admitted at an address that requires sign-in (R29), each by the way it registers: `local`;
    `{name, cimd, redirects?}`; `{name, dcr: loopback | {redirects} | {redirect_hosts}}`; only `local` where
    `access.yml` names none"""
    cs = (acc or {}).get("clients")
    return cs if isinstance(cs, list) and cs else ["local"]


def _host(u):
    m = re.match(r"^[a-z][a-z0-9+.-]*://([^/:?#]+)", str(u))
    return m[1].lower() if m else None


def client_admitted(acc, client):
    """whether the client a sign-in reports is admitted (R29). `client` is `local` for a session on the person's own
    device; else its client id, or `{id, redirects}` where the deployment knows the redirects it registered. A
    client is admitted by an entry that fits the way it registered: `local` or `dcr: loopback`, every redirect a
    loopback address; `cimd`, its client id the document's address, and its redirects within the pinned ones where
    both are known; `dcr` with `redirects`, every redirect pinned; with `redirect_hosts`, every redirect's host
    listed. A client the sign-in does not report, or whose redirects it does not know where they decide, is refused"""
    if not client:
        return False
    cid = client.get("id") if isinstance(client, dict) else str(client)
    reds = list(client.get("redirects") or []) if isinstance(client, dict) else []
    loop = client == "local" or (bool(reds) and all(LOOPBACK.match(str(r)) for r in reds))
    for c in clients_of(acc):
        if c == "local" and loop:
            return True
        if not isinstance(c, dict):
            continue
        if c.get("cimd") and cid == c["cimd"] and (not reds or not c.get("redirects") or set(reds) <= set(c["redirects"])):
            return True
        d = c.get("dcr")
        if d == "loopback" and loop:
            return True
        if isinstance(d, dict) and reds:
            if d.get("redirects") and set(reds) <= set(d["redirects"]):
                return True
            if d.get("redirect_hosts") and all(_host(r) in {h.lower() for h in d["redirect_hosts"]} for r in reds):
                return True
    return False


def grant_of(acc, u):
    """a user's grant: its shell's, narrowed by the user's own sources, writes and budget (R3, R4)"""
    sh = shell_grant(acc, u.get("shell"))
    return {"shell": u.get("shell"), "sources": u.get("sources") or sh.get("sources"),
            "writes": u["writes"] if "writes" in u else sh.get("writes") or [],
            "budget": {**(sh.get("budget") or {}), **(u.get("budget") or {})}}


def wider(inner, outer, acc):
    """what one grant holds beyond another, as a list of reasons (R3): shell, sources, writes, budget"""
    out = []
    if inner.get("shell") in SHELLS and outer.get("shell") in SHELLS and SHELLS.index(inner["shell"]) < SHELLS.index(outer["shell"]):
        out.append(f"shell {inner['shell']} inside {outer['shell']}")
    if outer.get("sources") and not set(inner.get("sources") or ["*"]) <= set(outer["sources"]):
        out.append("sources beyond")
    if not set(inner.get("writes") or []) <= set(outer.get("writes") or []):
        out.append("writes beyond")
    ib, ob = budget_of(acc, inner), budget_of(acc, outer)
    out += [f"budget {k} above" for k in BUDGET if ib[k] > ob[k]]
    return out


def standing(acc, u, today):
    """why this user grants nothing, or None (R3, R27): a field the MCP does not read, more than its shell, and for a
    technical user or an entry by pattern no human accountable for it, or more than that human holds"""
    unknown = sorted(set(u) - FIELDS)
    if unknown:                                      # a user it cannot read is refused, never served wider
        return f"the user holds {', '.join(unknown)}, which this MCP does not read"
    why = wider(grant_of(acc, u), shell_grant(acc, u.get("shell")), acc)
    if why:
        return f"the user holds more than its shell: {'; '.join(why)}"
    if u.get("match") is not None:
        if u.get("shell") != "DOCK":
            return "an entry by pattern stands in DOCK, and nowhere else"
        if not DOMAIN.match(str(u["match"])):
            return "an entry by pattern matches the addresses of one domain, `*@<domain>`"
    elif human(u):
        return None
    what = "this entry by pattern" if u.get("match") else "this technical user"
    if not u.get("accountable") or not u.get("expires"):
        return f"{what} names the human accountable for it and an expiry"
    h = next((x for x in users_of(acc) if x.get("account") == u["accountable"]), None)
    if h is None:
        return f"the human accountable for {what} is no user"
    if not human(h):
        return f"{what} names no human accountable for it; only a human is accountable"
    if expired(h, today):
        return f"the human accountable for {what} grants nothing now"
    if by_entry(u) and h.get("shell") not in ("SEED", "CORE"):
        return f"the human accountable for {what} stands in CORE or further in"
    why = wider(grant_of(acc, u), grant_of(acc, h), acc)
    return f"{what} holds more than the human accountable for it: {'; '.join(why)}" if why else None


def resolve(acc, who, today, address=None, claims=(), verified=False):
    """step 1 (R3, R27): the one user whose account the sign-in reports and that has not expired, with its grant, else
    the innermost shell to which `roles` maps a role the sign-in reports, with no user named (SA-d), else the entry of
    DOCK that matches the domain of the account's verified address, which stands while its contract does, else the
    public grant, ROAM's, `none` unless the commons opened one; returns (grant, refusal). The class `public` is
    everyone's: an `access.yml` that maps it inside ROAM serves nothing, so that no cut is served wider than declared (R4)"""
    if classes_of(acc).get("public") != "ROAM":
        return None, "`access.yml` maps the class `public` inside ROAM; it is everyone's, and nothing is served"
    for u in users_of(acc):
        if not who or u.get("account") != who:
            continue
        if expired(u, today) and technical(u):           # DOCK admits humans only: an expired agent grants nothing (R27)
            return None, "this technical user has expired and grants nothing"
        if expired(u, today):
            continue
        why = standing(acc, u, today)
        return (None, why) if why else ({"id": u["shell"], "user": who, **grant_of(acc, u)}, None)
    held = {str(c) for c in claims or ()} if who else set()   # the roles the sign-in reports for an account (SA-d)
    shells = sorted({s for r, s in roles_of(acc).items() if r in held}, key=SHELLS.index)
    if shells:                                       # the innermost shell a reported role maps to, its grant, no person
        return {"id": shells[0], "user": who, **grant_of(acc, {"shell": shells[0]})}, None
    local, at, domain = str(address or "").partition("@")
    domain = domain.lower() if verified and who.startswith("account:") and at and local and "@" not in domain else None
    # DOCK matches only an address the transport marks as verified, a person's, with one `@` (R27); an unverified
    # address, such as an identity provider's mutable username, admits no one (the security review, MEDIUM 3)
    for u in users_of(acc):
        if domain and str(u.get("match", "")).lower() == f"*@{domain}" and not expired(u, today):
            why = standing(acc, u, today)
            return (None, why) if why else ({"id": u["shell"], "user": who, **grant_of(acc, u)}, None)
    pub = acc.get("public", "none")
    if not isinstance(pub, dict):
        return None, "this caller is no user, and nothing is public"
    return {"id": "public", "shell": "ROAM", "user": None, **pub, "writes": []}, None


def teams(acc, today):
    """the platform's teams (R26): per shell that has a repository, SEED to OPEN, the platform accounts of its users that
    have not expired and grant something; a key and an entry by pattern are in none, and DOCK and ROAM have no team"""
    out = {}
    for u in users_of(acc):
        a = str(u.get("account", ""))
        if a.startswith("account:") and u.get("shell") in SHELLS[:4] and not expired(u, today) and not standing(acc, u, today):
            out.setdefault(u["shell"], []).append(a.split(":", 1)[1])
    return {s: sorted(out[s]) for s in SHELLS if s in out}


def setup(acc, today):
    """what the set-up generates from `access.yml` (R26): the teams, and the ruleset of each repository, one per pair of
    shells: `main` changed only by a pull request, with no exception, that the inner shell's team, or one further in,
    merges once the checks have passed, the outer shell's team pushing branches, the branch deleted after the merge"""
    return {"teams": teams(acc, today),
            "repositories": {f"{i}|{o}": {"branch": "main", "change": "pull request", "bypass": "none",
                                          "merge": SHELLS[:SHELLS.index(i) + 1], "push": SHELLS[:SHELLS.index(o) + 1],
                                          "checks": checks, "merged": "delete branch"} for (i, o), checks in PAIRS.items()}}


def used(state, who, now):
    """this user's calls within the hour before now, counted apart from the use records, the user as a digest (R8, R20)"""
    p = os.path.join(state, "calls.jsonl")
    hour = (now - datetime.timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    n = sum(1 for l in open(p, encoding="utf-8") if l.strip() and (c := json.loads(l))["who"] == who and c["at"] > hour) if os.path.isfile(p) else 0
    with open(p, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({"who": who, "at": now.strftime("%Y-%m-%dT%H:%M:%SZ")}) + "\n")
    return n


def propose(core, state, grant, args, now):
    """R12, R13: the server builds the item, the caller only its payload; one item per user and operation; a request
    id reused for another operation is refused. Returns (receipt, provenance, refusal)"""
    req = str(args.get("request") or "")
    user = grant.get("user")
    if not user:
        return None, None, "a proposal needs a user"
    if not req:
        return None, None, "a proposal names its request id"
    payload = {k: str(v) for k, v in args.items() if k != "request"}
    extra = sorted(set(payload) - PAYLOAD)
    if extra:
        return None, None, f"a proposal takes no field {', '.join(extra)}"
    to = payload.get("to", "")
    miss = [k for k in ("to", "text") + (("release", "kind") if to == "maker" else ()) if not payload.get(k)]
    if miss:
        return None, None, f"a proposal names {', '.join(miss)}"
    if to not in ("commons", "model", "maker"):
        return None, None, "a proposal goes to `commons`, `model` or `maker`"
    if to not in (grant.get("writes") or []):
        return None, None, f"this grant proposes nothing to `{to}`"
    destination = f"{os.path.basename(os.path.abspath(core))}:{to}-workshop"
    if to == "maker":                                # the board the installed release's own record names (R12; library R3)
        m = RELEASE.match(payload["release"])
        if not m:
            return None, None, "a proposal to a maker names its release as <library>/<model>[/<variant>]@<version>"
        if payload["kind"] not in ("correction", "question", "proposal"):
            return None, None, "a proposal to a maker is a correction, a question or a proposal"
        ref = f"{m['library']}/{m['id']}" + (f"/{m['variant']}" if m["variant"] else "")
        rec = yml(os.path.join(layout.copy(core, ref), "release.yml")) or {}
        if (rec.get("library"), layout.release_id(rec), rec.get("variant"), str(rec.get("version"))) != (m["library"], m["id"], m["variant"], m["version"]) \
                or not BOARD.match(str(rec.get("answers") or "")):
            return None, None, "this commons has installed no such release whose record names where answers go"
        destination = f"{rec['answers']}:board"
    who, op = digest(["user", user]), digest([destination, payload])
    p = os.path.join(state, "receipts.jsonl")
    for l in open(p, encoding="utf-8") if os.path.isfile(p) else []:
        r = json.loads(l)
        if r["user"] == who and r["request"] == req:
            if r["op"] != op:
                return None, None, "this request id was used for another operation"
            return r["receipt"], r["provenance"], None
    os.makedirs(os.path.join(state, "outbox"), exist_ok=True)
    item = f"outbox/{len(os.listdir(os.path.join(state, 'outbox'))) + 1:04d}.yml"
    body = {"to": to, "destination": destination, "by": {"shell": grant["id"], "user": user}, "request": req,
            "state": "sent", "private": to == "maker", "payload": payload}
    open(os.path.join(state, item), "w", encoding="utf-8", newline="\n").write(yaml.safe_dump(body, sort_keys=False, allow_unicode=True))
    rec = {"request": req, "item": item, "to": to, "state": "sent", "at": now.strftime("%Y-%m-%dT%H:%M:%SZ")}
    prov = {"cut": [], "runs": [], "method": "write", "resolved": {"destination": destination}}
    with open(p, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({"user": who, "request": req, "op": op, "receipt": rec, "provenance": prov}, ensure_ascii=False) + "\n")
    return rec, prov, None


def depth_of(core, rec, nid, b):
    """the depth of a record as an installed model holds it (MODEL part 5; D-a): the aspects whose `of` is the record
    and the deeper records whose `parent` chain reaches it, read from the model its `origin` names, else from every
    model the CORE installs, and from the CORE's own `knowledge/depth/`, the depth a maker serves only through its MCP
    and never releases (L-1), within the budget of nodes (R8); None where none holds depth for it"""
    o = str((rec or {}).get("origin") or (rec or {}).get("adopted_from") or "")
    m = re.match(r"^(?P<ref>[a-z0-9-]+/[a-z0-9-]+(/[a-z0-9-]+)?)@[^#]+#(?P<id>.+)$", o)
    rid = m["id"] if m else nid
    copies = [layout.copy(core, m["ref"])] if m else list(layout.installed(core).values())
    files = sorted(glob.glob(os.path.join(core, *KNOWLEDGE_DEPTH, "*.yml")))
    for d in copies:
        files += sorted(set(layout.depth_files(d)) | set(layout.depth_earlier(d)))
    items = []
    for p in files:
        items += [x for x in (yml(p) or {}).get("items") or [] if isinstance(x, dict)]
    kind = rid.split(":", 1)[0]
    aspects = [x for x in items if x.get("of") == rid]
    below, grew = {rid}, True
    while grew:                                      # the deeper records whose parent chain reaches the record
        grew = False
        for x in items:
            k = f"{x.get('kind')}:{x.get('slug')}"
            if "of" not in x and k not in below and x.get("kind") == kind and f"{kind}:{x.get('parent')}" in below:
                below.add(k)
                grew = True
    deeper = [x for x in items if "of" not in x and f"{x.get('kind')}:{x.get('slug')}" in below - {rid}]
    if not aspects and not deeper:
        return None
    shown = (aspects + deeper)[:b["nodes"]]
    return {"aspects": [x for x in shown if "of" in x], "deeper": [x for x in shown if "of" not in x],
            "budget_cut": len(aspects) + len(deeper) - len(shown)}


def node(core, nid, classes, sources, b):
    """R6, R8: a node within the cut, its content as read at the cut, and its visible edges, one step deep and no more
    than the budget; one outside the cut is answered as one that does not exist. Returns (node, provenance)"""
    g = answer_graph.read(core)
    see, nodes, edges, withheld = answer_graph.project(g, classes, sources)
    n = nodes.get(nid)
    mine = [x for x in edges if n and nid in (x["from"], x["to"])]
    shown = mine[:b["nodes"]] if b["depth"] >= 1 else []
    prov = {"cut": [c for c in g.cut if c["source"] in see], "runs": sorted({x["run"] for x in shown if x.get("run")}), "method": "lookup"}
    if not n:
        return {"id": nid, "found": False, "unsighted": withheld}, prov
    out = {"id": nid, "file": n.get("file") or "", "content": json.loads(json.dumps(n.get("content"), default=str)),
           "edges": [answer_graph.show(x) for x in shown],
           "budget_cut": len(mine) - len(shown), "unsighted": withheld}
    deep = depth_of(core, n.get("content") if isinstance(n.get("content"), dict) else {}, nid, b) \
        if ":" in nid and "depth" in classes else None   # the depth of the models, class `depth` (SI-C)
    if deep:
        out["depth"] = json.loads(json.dumps(deep, default=str))
    return out, prov


def call(core, who, tool, args, state, today=None, now=None, address=None, claims=(), verified=False):
    """one call through the four steps as the account `who` (empty for a caller that signed in as no one), with the
    verified address the sign-in reports; returns the envelope, and leaves one use record in `state`"""
    now = now or datetime.datetime.now(datetime.timezone.utc)
    today = today or now.date().isoformat()
    os.makedirs(state, exist_ok=True)
    acc = access_of(core)
    env, prov, outcome = {"grant": "none"}, None, "refused"
    grant, why = (None, "no `.commons/access.yml`: nothing is served") if acc is None else resolve(acc, who, today, address, claims, verified)
    if grant is not None:
        env["grant"] = grant["id"]
        b = budget_of(acc, grant)
        if tool not in TOOLS:
            why = f"`{tool}` is no tool of this MCP"
        elif used(state, digest(["user", grant["user"]]) if grant["user"] else "public", now) >= b["calls"]:
            why, outcome = "the calls of this hour are used up", "budget"
        else:
            classes, sources = visible(acc, grant["shell"]), grant.get("sources")
            if tool == "answer":
                ans = answer_graph.answer(core, str(args.get("question") or ""), k=b["nodes"], classes=classes, sources=sources, depth=b["depth"])
                over = ans["candidates"][b["nodes"]:]       # the budget holds over the whole answer, within the caller's cut
                ans["candidates"] = ans["candidates"][:b["nodes"]]
                if over:
                    ans["silences"]["partial"].append({"why": "budget", "count": len(over)})
                env["answer"] = ans
                prov = {"cut": ans["cut"], "runs": ans["runs"], "method": ans["method"]}
            elif tool == "node":
                env["node"], prov = node(core, str(args.get("id") or ""), classes, sources, b)
            else:
                env["receipt"], prov, why = propose(core, state, grant, args, now)
            outcome = "refused" if why else "served"
    if why:
        env = {"grant": env["grant"], "refused": why}
    else:
        env["provenance"] = {**prov, "upstream": []}
    if acc is not None:                                  # what each shell gets, and what this caller gets, computed now (R28)
        env["offer"] = offer(acc)
        if grant is not None:
            env["gets"] = {"reads": visible(acc, grant["shell"]), **({"sources": grant["sources"]} if grant.get("sources") else {}),
                           "writes": grant.get("writes") or [], "budget": budget_of(acc, grant)}
    use = {"at": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "tool": tool, "grant": env["grant"], "outcome": outcome,
           "cut": digest([[c["source"], c["digest"]] for c in (prov or {}).get("cut") or []])}
    with open(os.path.join(state, "use.jsonl"), "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(use, ensure_ascii=False) + "\n")
    return env


NODE_SKIP = {"title", "summary", "definition", "description", "slug", "id", "relationships", "contributors", "sources",
             "license", "attribution", "value_model", "gravitational_hubs", "aliases", "ontology", "lifecycle"}


def readable(core, env):
    """the text of a result for a reader: each candidate or node in one line, `title — summary (id)`, then the grant
    once, compact; the envelope itself is the structured content (R28)"""
    def about(f):
        p = os.path.join(core, f or "")
        if not f or not os.path.isfile(p):
            return {}
        t = open(p, encoding="utf-8", errors="replace").read()
        try:
            doc = yaml.safe_load(t[4:t.index("\n---", 4)]) if t.startswith("---") else yaml.safe_load(t)
        except (yaml.YAMLError, ValueError):
            return {}
        return doc if isinstance(doc, dict) else {}
    one = lambda s: " ".join(str(s or "").split())
    lines = []
    if env.get("refused"):
        lines.append(f"refused: {env['refused']}")
    ans = env.get("answer") or {}
    for c in ans.get("candidates") or []:
        d = {} if c.get("title") else about(c.get("file"))   # the candidate's own title and summary, as the structure gives them
        title = one(c.get("title") or d.get("title")) or c["id"]
        summary = one(c.get("summary") or d.get("summary") or d.get("definition") or d.get("description"))
        lines.append(f"- {title}" + (f" — {summary[:240]}" if summary else "") + f" ({c['id']})")
    if ans and not ans.get("candidates"):
        lines.append("no candidate: the question shares no word with what this grant reads")
    n = env.get("node") or {}
    if n:
        c, therefore = n.get("content"), None
        if isinstance(c, str):                       # a pattern: its front matter, and its "Therefore" line
            m = re.search(r"(?m)^>?\s*\*\*Therefore[^\n]*", c)
            therefore = one(m[0].lstrip("> ").replace("**", "")) if m else None
            try:
                c = yaml.safe_load(c[4:c.index("\n---", 4)]) if c.startswith("---") else {}
            except (yaml.YAMLError, ValueError):
                c = {}
        d = c if isinstance(c, dict) else {}
        if not n.get("found", True):
            lines.append(f"not found: `{n.get('id')}` is not in what this grant reads")
        else:
            lines.append(f"{one(d.get('title')) or n.get('id')} ({n.get('id')})")
            if d.get("summary") or d.get("definition") or d.get("description"):
                lines.append(f"  {one(d.get('summary') or d.get('definition') or d.get('description'))[:600]}")
            if therefore:
                lines.append(f"  {therefore[:400]}")
            for k, v in d.items():                   # the record's own fields, each in one line
                if k in NODE_SKIP or v in (None, "", [], {}) or len(lines) > 24:
                    continue
                if isinstance(v, list):
                    v = "; ".join(one(x.get("title") or x.get("slug") or x.get("name") or x.get("target") or x) if isinstance(x, dict)
                                  else one(x) for x in v)
                elif isinstance(v, dict):
                    v = ", ".join(f"{a}: {one(b)}" for a, b in v.items() if not isinstance(b, (dict, list)))
                lines.append(f"  {k}: {one(str(v))[:300]}")
            if n.get("file"):
                lines.append(f"  file: {n['file']}")
            lines += [f"  edge: {x}" for x in (n.get("edges") or [])[:10]]
    if env.get("receipt"):
        lines.append(f"receipt: {json.dumps(env['receipt'], ensure_ascii=False)}")
    gets = env.get("gets") or {}
    method = ans.get("method") or (env.get("provenance") or {}).get("method")
    lines.append(f"[grant {env.get('grant')}; reads {', '.join(gets.get('reads') or []) or 'nothing'}"
                 + (f"; method {method}" if method else "") + "]")
    return "\n".join(lines)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("core")
    ap.add_argument("tool", nargs="?")
    ap.add_argument("args", nargs="*", help="key=value")
    ap.add_argument("--as", dest="who", default="", help="the account the sign-in reports; none for a caller that signed in as no one")
    ap.add_argument("--address", help="the verified address the sign-in reports for the account")
    ap.add_argument("--state", help="the folder of the service's operational state")
    ap.add_argument("--setup", action="store_true", help="print the teams and the ruleset generated from access.yml (R26)")
    ap.add_argument("--stdio", action="store_true", help="serve this CORE's MCP over stdio, as mcp_server.py does (R22)")
    ap.add_argument("--http", type=int, metavar="PORT", help="serve it over Streamable HTTP on 127.0.0.1:PORT (R22)")
    ap.add_argument("--today")
    ap.add_argument("--text", action="store_true", help="print the result for a reader, not the envelope")
    a = ap.parse_intermixed_args()                    # options before, between or after the tool and its key=value, alike
    if a.stdio or a.http is not None:                  # the transports of MCP part 5, by the names the spec gives them
        import mcp_server  # noqa: E402
        argv = [a.core] + (["--as", a.who] if a.who else []) + (["--address", a.address] if a.address else []) \
            + (["--state", a.state] if a.state else []) + (["--http", str(a.http)] if a.http is not None else [])
        sys.argv = [os.path.join(HERE, "mcp_server.py")] + argv
        return mcp_server.main()
    if a.setup:
        print(yaml.safe_dump(setup(access_of(a.core) or {}, a.today or datetime.date.today().isoformat()), sort_keys=False), end="")
        return 0
    if not a.tool or not a.state:
        ap.error("a call names its tool and --state")
    args = dict(x.split("=", 1) for x in a.args if "=" in x)
    env = call(a.core, a.who, a.tool, args, a.state, a.today, address=a.address, verified=bool(a.address))
    print(readable(a.core, env) if a.text else json.dumps(env, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
