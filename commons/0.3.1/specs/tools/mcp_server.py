#!/usr/bin/env python3
"""mcp_server.py — the transport of a commons' MCP: the reference pipeline (serve_mcp.py, mcp.md R2) served to an MCP
client over stdio, or over Streamable HTTP, by JSON-RPC 2.0. It holds no record, no source and no state of its own
(R20): every call goes through `serve_mcp.call`, whose grant, cut, envelope and use record stay what they are.

- **stdio** (the default): one JSON-RPC message per line on stdin, one per line on stdout, as the MCP stdio transport
  has it, so that any MCP client starts this CORE's MCP from a clone of it (R22). The session is local and trusted:
  the account it works as is the one `--as` names, a user of `access.yml`, else the caller is no user and holds
  ROAM's `public` grant (R3).
- **HTTP** (`--http PORT`): one endpoint, `POST /mcp`, that takes a message or a batch and answers `application/json`;
  a notification is answered `202`, and `GET` is `405`, since the server opens no stream. It is a general adapter
  with nothing of one host in it: a deployment, the Federation's Worker among them, puts it behind the protocol's
  authorisation and hands over the account, the address, the claims the sign-in reports and whether it verified the
  address, and the client it signed in (`account_of(headers) -> (account, address, claims, verified, client)`),
  validating tokens issued for itself (R22); DOCK matches only a verified address (R27). A request that signed in
  through a client `access.yml` does not admit under `clients` is answered `403` and nothing is served, not even the
  handshake (R29). A licence the
  sign-in reports as a claim reaches its shell through an entry by claim of `access.yml` (SI-B). For a CORE behind an
  OAuth server that issues JWTs for it, `jwt_account_of(issuer, audience, jwks)` is that callable: RS256 against the
  issuer's keys, `iss`, `aud`, `exp` and `nbf`, the client id from `azp`, `client_id` or `appid`; a request without a
  token is a caller that is no user, and one with a token that does not hold is answered `401`. Run here, it binds
  127.0.0.1, refuses a request whose `Origin` is not local, and works as `--as` or as no user, through a local client.

The three tools are R2's, `answer`, `node` and `propose`, each answered with its envelope as `structuredContent` and as
text, and a refusal as `isError`. The operational state lies in `--state`, outside the repository, by default in the
system's temporary folder under the CORE's id.

Usage:  mcp_server.py CORE [--as ACCOUNT] [--address ADDRESS] [--state DIR] [--http PORT]
        e.g. in `.mcp.json`: {"command": "python", "args": ["specs/tools/mcp_server.py", ".", "--as", "account:ada"]}
"""
import argparse
import base64
import hashlib
import hmac
import http.server
import json
import os
import sys
import tempfile
import time
import urllib.parse

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True   # the tools never write into the install they lie in (SPECIFICATION R29; CORE R39)
sys.path.insert(0, HERE)
import serve_mcp  # noqa: E402

VERSIONS = ("2025-06-18", "2025-03-26", "2024-11-05")          # the protocol versions this transport speaks, newest first
TOOLS = {
    "answer": ("Answer a question from this CORE's graph, within the caller's grant: a few candidates, each naming its file, "
               "and the cut, runs and method the answer rests on (graph R12; mcp R2).",
               {"question": {"type": "string", "description": "the context and the problem, in words"}}, ["question"]),
    "node": ("One thing of the graph and its relations, within the caller's grant: the record itself, its visible edges and, "
             "for a record of a model, its depth (mcp R6, D-a).",
             {"id": {"type": "string", "description": "a node id, e.g. `capability:sowing` or `<library>/pat_...`"}}, ["id"]),
    "propose": ("Propose a change: one item in this commons' Commons or Model Workshop, or privately on the board a "
                "release's record names, and never a write into a record (mcp R12, R13).",
                {k: {"type": "string"} for k in ["request", *sorted(serve_mcp.PAYLOAD)]}, ["request", "to", "text"]),
}


def tools():
    return [{"name": n, "description": d, "inputSchema": {"type": "object", "properties": p, "required": req, "additionalProperties": False}}
            for n, (d, p, req) in TOOLS.items()]


def core_id(core):
    p = os.path.join(core, ".commons", "commons.yml")
    cfg = (yaml.safe_load(open(p, encoding="utf-8")) or {}) if os.path.isfile(p) else {}
    return str(cfg.get("id") or os.path.basename(os.path.abspath(core)))


def error(mid, code, text):
    return {"jsonrpc": "2.0", "id": mid, "error": {"code": code, "message": text}}


def handle(core, msg, who="", address=None, state=None, claims=(), verified=False):
    """one JSON-RPC message; returns its response, or None for a notification"""
    if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0" or not isinstance(msg.get("method"), str):
        return error(msg.get("id") if isinstance(msg, dict) else None, -32600, "not a JSON-RPC 2.0 request")
    mid, method, params = msg.get("id"), msg["method"], msg.get("params") or {}
    if "id" not in msg:                              # a notification, `notifications/initialized` among them
        return None
    if method == "initialize":
        asked = str(params.get("protocolVersion") or "")
        return {"jsonrpc": "2.0", "id": mid, "result": {
            "protocolVersion": asked if asked in VERSIONS else VERSIONS[0],
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": f"{core_id(core)} CORE", "version": "commons-mcp/1"},
            "instructions": "This CORE's MCP: answer, node and propose, each within your grant; every result names what it rests on."}}
    if method == "ping":
        return {"jsonrpc": "2.0", "id": mid, "result": {}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": mid, "result": {"tools": tools()}}
    if method == "tools/call":
        name, args = params.get("name"), params.get("arguments") or {}
        if name not in TOOLS:
            return error(mid, -32602, f"`{name}` is no tool of this MCP; its tools are {', '.join(TOOLS)}")
        env = serve_mcp.call(core, who or "", name, {k: v for k, v in args.items()}, state or default_state(core), address=address, claims=claims, verified=verified)
        return {"jsonrpc": "2.0", "id": mid, "result": {
            "content": [{"type": "text", "text": serve_mcp.readable(core, env)}],   # the envelope is structuredContent (R28)
            "structuredContent": env, "isError": "refused" in env}}
    return error(mid, -32601, f"no method `{method}`")


def default_state(core):
    return os.path.join(tempfile.gettempdir(), "commons-mcp", core_id(core))


def stdio(core, who="", address=None, state=None):
    """the stdio transport: one message per line, one answer per line, until stdin closes"""
    out = sys.stdout
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            msg = json.loads(line)
        except ValueError:
            reply = error(None, -32700, "not JSON")
        else:
            reply = [r for r in (handle(core, m, who, address, state, (), bool(address)) for m in msg) if r] if isinstance(msg, list) \
                else handle(core, msg, who, address, state, (), bool(address))   # a local session vouches for its --address
        if reply:
            out.write(json.dumps(reply, ensure_ascii=False) + "\n")
            out.flush()


def b64url(s):
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


SHA256_INFO = bytes.fromhex("3031300d060960864801650304020105000420")   # DigestInfo of SHA-256 (RFC 8017 9.2)


def rs256_ok(signed, sig, n, e):
    """an RSASSA-PKCS1-v1_5 signature with SHA-256 (RFC 8017 8.2.2), with no package"""
    k = (n.bit_length() + 7) // 8
    if len(sig) != k:
        return False
    em = pow(int.from_bytes(sig, "big"), e, n).to_bytes(k, "big")
    want = b"\x00\x01" + b"\xff" * (k - 3 - len(SHA256_INFO) - 32) + b"\x00" + SHA256_INFO + hashlib.sha256(signed).digest()
    return hmac.compare_digest(em, want)


class Unauthorised(Exception):
    """a token that was sent and does not hold: the request is answered 401, never served as no user"""


def jwt_account_of(issuer, audience, jwks, leeway=60, now=None, redirects_of=None):
    """`account_of` for a CORE behind an OAuth server that issues JWTs for it: the bearer token's RS256 signature
    against the issuer's keys `jwks` (`{"keys": [...]}`), its `iss`, `aud`, `exp` and `nbf`; the account
    `account:<issuer's host>:<sub>`, the address `email` or `preferred_username`, the claims `roles`, the address
    verified only where the token says `email_verified: true` for its `email`, and the client the token was issued
    to, `azp`, `client_id` or `appid`, with the redirects it registered where the deployment's `redirects_of(client
    id)` knows them, from its identity provider's registration (R22, R27, R29, SI-B)"""
    keys = {k.get("kid"): k for k in (jwks or {}).get("keys") or [] if k.get("kty") == "RSA"}
    host = urllib.parse.urlparse(issuer).hostname or issuer

    def account_of(headers):
        auth = str(headers.get("Authorization") or "")
        if not auth:
            return "", None, ()
        if not auth.startswith("Bearer "):
            raise Unauthorised("a bearer token is expected")
        try:
            h64, p64, s64 = auth[7:].strip().split(".")
            head, claims = json.loads(b64url(h64)), json.loads(b64url(p64))
            key = keys.get(head.get("kid")) or (next(iter(keys.values())) if len(keys) == 1 and not head.get("kid") else None)
            ok = head.get("alg") == "RS256" and key and rs256_ok(f"{h64}.{p64}".encode(), b64url(s64),
                                                                  int.from_bytes(b64url(key["n"]), "big"), int.from_bytes(b64url(key["e"]), "big"))
        except (ValueError, KeyError, TypeError):
            raise Unauthorised("the token cannot be read")
        t = now if now is not None else time.time()
        aud = claims.get("aud") if isinstance(claims.get("aud"), list) else [claims.get("aud")]
        if not ok or claims.get("iss") != issuer or audience not in aud or not claims.get("sub") \
                or float(claims.get("exp") or 0) + leeway < t or float(claims.get("nbf") or 0) - leeway > t:
            raise Unauthorised("the token does not hold: signature, issuer, audience or time")
        roles = claims.get("roles") if isinstance(claims.get("roles"), list) else []
        verified = bool(claims.get("email")) and claims.get("email_verified") is True
        client = next((str(claims[k]) for k in ("azp", "client_id", "appid") if claims.get(k)), None)
        reds = redirects_of(client) if client and redirects_of else None
        return (f"account:{host}:{claims['sub']}", claims.get("email") or claims.get("preferred_username"),
                tuple(str(x) for x in roles), verified, {"id": client, "redirects": list(reds)} if reds else client)
    return account_of


def adapter(core, account_of, state=None, local=True):
    """the HTTP adapter: a request handler for `POST /mcp`; `account_of(headers)` gives (account, address, claims,
    verified, client) as the deployment's sign-in reports them, the first two at least, and raises `Unauthorised` for a
    token that does not hold. A request that signed in, through a client the commons does not admit or one the sign-in
    does not report, is refused with `403` before anything is served (R29)"""
    class Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self, *a):                   # no caller, question or answer is logged (R21)
            pass

        def send(self, code, body=None):
            self.send_response(code)
            if body is not None:
                data = json.dumps(body, ensure_ascii=False).encode("utf-8")
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            else:
                self.send_header("Content-Length", "0")
                self.end_headers()

        def do_GET(self):
            self.send(405)

        def do_DELETE(self):
            self.send(405)

        def do_POST(self):
            if self.path.split("?")[0] != "/mcp":
                return self.send(404)
            body = self.rfile.read(int(self.headers.get("Content-Length") or 0))   # read whole before any answer, refusals too
            origin = self.headers.get("Origin")
            if local and origin and not origin.split("://")[-1].split(":")[0] in ("localhost", "127.0.0.1", "[::1]"):
                return self.send(403, error(None, -32600, "a local MCP takes no request from another origin"))
            try:
                msg = json.loads(body or b"null")
            except ValueError:
                return self.send(400, error(None, -32700, "not JSON"))
            try:
                who, address, *rest = account_of(self.headers)
            except Unauthorised as e:
                self.send_response(401)
                self.send_header("WWW-Authenticate", f'Bearer error="invalid_token", error_description="{e}"')
                self.send_header("Content-Length", "0")
                self.end_headers()
                return None
            claims = tuple(rest[0]) if rest else ()
            verified = bool(rest[1]) if len(rest) > 1 else False   # unverified unless the deployment says so (R27)
            client = rest[2] if len(rest) > 2 else None             # unreported unless the deployment says so (R29)
            if who and not serve_mcp.client_admitted(serve_mcp.access_of(core), client):
                cid = (client.get("id") if isinstance(client, dict) else client) or "unreported"
                return self.send(403, error(None, -32600, f"the client `{cid}` is not one this commons admits (R29)"))
            if isinstance(msg, list):
                replies = [r for r in (handle(core, m, who, address, state, claims, verified) for m in msg) if r]
                return self.send(200, replies) if replies else self.send(202)
            reply = handle(core, msg, who, address, state, claims, verified)
            return self.send(200, reply) if reply else self.send(202)
    return Handler


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("core")
    ap.add_argument("--as", dest="who", default="", help="the account of a trusted local session, a user of access.yml")
    ap.add_argument("--address", help="the verified address of that account")
    ap.add_argument("--state", help="the folder of the operational state, outside the repository")
    ap.add_argument("--http", type=int, metavar="PORT", help="serve Streamable HTTP on 127.0.0.1:PORT instead of stdio")
    a = ap.parse_args()
    if a.http is None:
        stdio(a.core, a.who, a.address, a.state)
        return 0
    server = http.server.ThreadingHTTPServer(("127.0.0.1", a.http), adapter(a.core, lambda headers: (a.who, a.address, (), bool(a.address), "local"), a.state))
    print(f"# {core_id(a.core)} CORE's MCP at http://127.0.0.1:{server.server_address[1]}/mcp", file=sys.stderr)
    server.serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
