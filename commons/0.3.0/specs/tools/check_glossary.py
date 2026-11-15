#!/usr/bin/env python3
"""check_glossary.py — the glossary is consistent with itself.

  * every entry matches schemas/glossary.term.schema.json (when the jsonschema package is present;
    otherwise the required fields and the closed vocabularies are checked by hand);
  * the file name is the id, and no id appears twice;
  * every term id named in `relations` exists;
  * every `use:` in rejected.yml names an existing term;
  * every rejected entry names its kind and what that kind needs: a word its `sense` (and may list `forms`), a key its
    `where` (its `text`, and at most one place a tool reads: `key`, `value_of`, `prefix` or `file`), a name
    neither; no sense in parentheses, and no entry that is a live term (its other senses are that
    term's `not:`);
  * a definition is one sentence.

Exit 0 when clean, 1 with a list of findings otherwise.

With `--since <rev>` it checks a replacement instead, made by meaning and never by string (part 11, point 4): it
lists every rejected term in the lines changed since `<rev>`, with its line, and every **new token**, one the added
lines hold that the tree at `<rev>` holds nowhere. The repository's own vocabulary is the dictionary, offline. It
reports and never writes, and always exits 0: the person or agent reads it before committing, and the gate again.

Usage:  check_glossary.py [--glossary DIR]
        check_glossary.py --since REV [--repo PATH] [--glossary DIR]
"""
import argparse
import glob
import io
import json
import os
import re
import subprocess
import sys
import tarfile

import yaml

sys.dont_write_bytecode = True   # the tools never write into the install they lie in (SPECIFICATION R29; `extension` R12)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rejected as rejected_words  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "..")
SCHEMA = os.path.join(BASE, "schemas", "glossary.term.schema.json")
TERMS = os.path.join(BASE, "glossary", "terms")
REJECTED = os.path.join(BASE, "glossary", "rejected.yml")
REJECTED_FIELDS = ("term", "kind", "sense", "where", "use", "forms", "note", "since")
NEEDS = {"name": (), "key": ("where",), "word": ("sense", "forms")}  # forms is optional on a word
PLACES = ("key", "value_of", "prefix", "file")  # where a tool can read a key's place; text alone is read by people


TOKEN = re.compile(r"[^\W\d_]{3,}")


def git(repo, *args, text=True):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=text, encoding="utf-8" if text else None,
                          errors="replace" if text else None, check=True).stdout


def vocabulary(repo, rev):
    """every token the tree at `rev` holds, in any text file"""
    words = set()
    with tarfile.open(fileobj=io.BytesIO(git(repo, "archive", "--format=tar", rev, text=False))) as tar:
        for m in tar.getmembers():
            if m.isfile():
                b = tar.extractfile(m).read()
                if b"\0" not in b[:8000]:
                    words.update(w.lower() for w in TOKEN.findall(b.decode("utf-8", errors="replace")))
    return words


def since(repo, rev, glossary=None):
    """the lines added since `rev`, the rejected terms among them and the tokens they bring new"""
    added, path, line = [], None, 0
    for d in git(repo, "diff", "-U0", "--no-color", rev, "--").splitlines():
        if d.startswith("+++ "):
            path = d[6:] if d.startswith("+++ b/") else None
        elif d.startswith("@@"):
            line = int(re.match(r"@@ -\S+ \+(\d+)", d).group(1))
        elif d.startswith("+") and path:
            added.append((path, line, d[1:]))
            line += 1
    known, ents = vocabulary(repo, rev), rejected_words.entries(glossary)
    terms, new = [], []
    for path, n, text in added:
        own, shown = rejected_words.unquoted(text), " ".join(text.split())[:160]   # a quotation is exempt (point 3)
        for e in ents:
            if any(rejected_words.term_rx(f).search(own) for f in [e["term"]] + e["forms"]):
                terms.append(f"rejected: {path}:{n}: `{e['term']}` ({e['kind']}{', ' + e['sense'] if e['sense'] else ''}): {shown}")
        for w in sorted({w for w in TOKEN.findall(own) if w.lower() not in known}):
            new.append(f"new: {path}:{n}: `{w}`: {shown}")
            known.add(w.lower())
    print(f"# since {rev}: {len(added)} added lines · {len(terms)} rejected terms · {len(new)} new tokens")
    for x in terms + new:
        print(x)
    return 0


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--since")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--glossary")
    a = ap.parse_args()
    if a.since:
        return since(a.repo, a.since, a.glossary)
    terms_dir = os.path.join(a.glossary, "terms") if a.glossary else TERMS
    rejected_file = os.path.join(a.glossary, "rejected.yml") if a.glossary else REJECTED
    schema = json.load(open(SCHEMA, encoding="utf-8"))
    try:
        import jsonschema
        validate = jsonschema.Draft202012Validator(schema).iter_errors
    except ImportError:
        validate = None
    findings, entries = [], {}
    for path in sorted(glob.glob(os.path.join(terms_dir, "*.yml"))):
        name = os.path.splitext(os.path.basename(path))[0]
        e = yaml.safe_load(open(path, encoding="utf-8"))
        if validate:
            for err in validate(e):
                findings.append(f"{name}: {err.message}")
        else:
            for k in schema["required"]:
                if k not in e:
                    findings.append(f"{name}: missing {k}")
            for k in ("layer", "kind", "statement", "status"):
                allowed = schema["properties"][k]["enum"]
                if k in e and e[k] not in allowed:
                    findings.append(f"{name}: {k} '{e[k]}' not in {allowed}")
        if e.get("id") != name:
            findings.append(f"{name}: id '{e.get('id')}' differs from the file name")
        if e.get("id") in entries:
            findings.append(f"{name}: id appears twice")
        entries[e.get("id")] = e
        d = e.get("definition", "")
        if len(re.findall(r"[.!?](\s|$)", d.strip())) > 1:
            findings.append(f"{name}: definition is more than one sentence")
    for name, e in entries.items():
        for rel, target in (e.get("relations") or {}).items():
            for t in ([target] if isinstance(target, str) else target):
                if t not in entries:
                    findings.append(f"{name}: relation {rel} → '{t}' is not a term")
    live = {str(e.get("term", "")).lower() for e in entries.values()}
    for r in (yaml.safe_load(open(rejected_file, encoding="utf-8")) or {}).get("rejected", []):
        t = str(r.get("term") or "")
        if r.get("use") not in entries:
            findings.append(f"rejected '{t}': use '{r.get('use')}' is not a term")
        for k in sorted(set(r) - set(REJECTED_FIELDS)):
            findings.append(f"rejected '{t}': unknown field `{k}`")
        kind = r.get("kind")
        if kind not in NEEDS:
            findings.append(f"rejected '{t}': kind must be name, key or word")
        else:
            for k in ("sense", "where", "forms"):
                if k in NEEDS[kind] and k != "forms" and not r.get(k):
                    findings.append(f"rejected '{t}': a {kind} needs its `{k}`")
                if k not in NEEDS[kind] and k in r:
                    findings.append(f"rejected '{t}': a {kind} carries no `{k}`")
            w = r.get("where")
            if kind == "key" and w:
                if not isinstance(w, dict) or not isinstance(w.get("text"), str) or not w["text"]:
                    findings.append(f"rejected '{t}': `where` is a mapping with its `text`")
                else:
                    places = sorted(set(w) - {"text"})
                    if set(places) - set(PLACES) or len(places) > 1 or any(not isinstance(w[p], str) for p in places):
                        findings.append(f"rejected '{t}': `where` names at most one place a tool reads, one of "
                                        + ", ".join(PLACES))
        if "(" in t:
            findings.append(f"rejected '{t}': the sense or the place goes into `sense` or `where`, not into parentheses")
        if t.lower() in live:
            findings.append(f"rejected '{t}': a live term; its other senses belong in that term's `not:`")
    for f in findings:
        print("✗", f)
    print(f"{len(entries)} terms · {len(findings)} findings" + ("" if validate else " (jsonschema not installed — basic checks)"))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
