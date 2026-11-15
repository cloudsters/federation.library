#!/usr/bin/env python3
"""rejected.py — the discipline's rejected words, read by sense, never by string alone (EXTENSION R14, `library-patterns`
R8; the models note part 11, decided: Holger, commons.o#109 6602880861, decision 27). Read-only; a module of the checks.

Every entry of `glossary/rejected.yml` names its `kind`, and the kind says how it is read:

- **name**, a token with no meaning outside its former use, fails by its string: in text, in slugs and in file names;
- **key**, an ordinary word retired in one structural place, fails only where its `where` says: `key` (a mapping key of
  a record), `value_of` (the value of a record's field), `prefix` (an id's prefix) or `file` (a file name). It is
  never sought in prose or in slugs, where the same word is mostly live;
- **word**, an ordinary word retired in one sense of prose, never fails. It is one should per word and file, with its
  count, its `sense` and the first sentence, for a person to read; its `forms` are read with it.

Exempt, nothing reported: a quotation, by its form alone (a `>` block quote, a span in quotation marks); a compound
and every other word that shares the letters, since a word boundary is no sense; and what the callers never pass,
source texts and history. An entry in the earlier form, with no `kind`, is read as it was: a term without a
parenthesis as a name, one with its sense in parentheses by people alone.
"""
import os
import re

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
KINDS = ("name", "key", "word")
PLACES = ("key", "value_of", "prefix", "file")
QUOTED = re.compile(r"\"[^\"\n]*\"|“[^”\n]*”|„[^“”\n]*[“”]|«[^»\n]*»")
BLOCK = re.compile(r"^[ \t]*>.*$", re.M)


def term_rx(term):
    """a term with capitals is matched as written, one in lower case in any case; a hyphen on either side makes it a
    compound, which is not the term"""
    return re.compile(r"(?<![\w-])" + re.escape(term) + r"(?![\w-])", 0 if term != term.lower() else re.I)


def entries(glossary=None):
    """the entries of `rejected.yml`, each with its `kind`; one in the earlier form is read as it was"""
    p = os.path.join(glossary or os.path.join(HERE, "..", "glossary"), "rejected.yml")
    doc = yaml.safe_load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
    out = []
    for x in (doc or {}).get("rejected") or []:
        x = x if isinstance(x, dict) else {"term": x}
        t = str(x.get("term") or "").strip()
        if not t:
            continue
        if x.get("kind") in KINDS:
            out.append({"term": t, "kind": x["kind"], "sense": x.get("sense"), "where": x.get("where") or {},
                        "forms": [str(f) for f in x.get("forms") or []]})
        elif "kind" not in x and "(" not in t:
            out.append({"term": t, "kind": "name", "sense": None, "where": {}, "forms": []})
    return sorted(out, key=lambda e: len(e["term"]), reverse=True)


def unquoted(text):
    """the text without what it quotes"""
    return QUOTED.sub(" ", BLOCK.sub("", text))


def sentence(text, m):
    a = max(text.rfind(c, 0, m.start()) for c in ".!?\n") + 1
    b = min([i for i in (text.find(c, m.end()) for c in ".!?\n") if i >= 0] or [len(text)])
    return " ".join(text[a:b + 1].split())


def walk(data, path=()):
    """every (key path, key, value) of a parsed file"""
    if isinstance(data, dict):
        for k, v in data.items():
            yield path, k, v
            yield from walk(v, path + (k,))
    elif isinstance(data, list):
        for v in data:
            yield path, None, v
            yield from walk(v, path)


def findings(path, text, where, ents=None):
    """what a file says against the rejected words: (`fail` | `should`, message)"""
    ents = entries() if ents is None else ents
    data, prose = None, text
    if path.endswith((".yml", ".yaml")):
        try:
            data = yaml.safe_load(text)
        except yaml.YAMLError:
            data = None
        if data is not None:                     # the prose of a file is its values; its keys are read for names
            strs = [v for _, _, v in walk(data) if isinstance(v, str)] + [data] * isinstance(data, str)
            keys = [str(k) for _, k, _ in walk(data) if k is not None]
            prose = "\n".join(unquoted(s) for s in strs) + "\n" + "\n".join(keys)
    else:
        prose = unquoted(text)
    out = []
    slugs = sorted({v for p, k, v in walk(data) if k == "slug" and isinstance(v, str)}) if data is not None else []
    base = os.path.splitext(os.path.basename(path))[0]
    for e in ents:
        t, k = e["term"], e["kind"]
        if k == "name":
            if term_rx(t).search(prose):
                out.append(("fail", f"{where} uses `{t}`, a rejected word of the glossary (R14)"))
            w = t.lower().replace(" ", "-").split("-")
            for s in slugs + [base]:
                parts = s.lower().split("-")
                if any(parts[i:i + len(w)] == w for i in range(len(parts) - len(w) + 1)):
                    what = f"the slug `{s}`" if s in slugs else f"the file name `{os.path.basename(path)}`"
                    out.append(("fail", f"{where}: {what} holds `{t}`, a rejected word of the glossary (R14)"))
                    break
        elif k == "key":
            hit = None
            pl = e["where"] if isinstance(e["where"], dict) else {}
            if pl.get("file") and os.path.basename(path) == pl["file"]:
                hit = f"is named `{pl['file']}`"
            for _, key, v in walk(data) if data is not None and not hit else ():
                if pl.get("key") and str(key) == pl["key"]:
                    hit = f"holds the key `{key}`"
                elif pl.get("value_of") and str(key) == pl["value_of"] and isinstance(v, str) and \
                        v.lower().replace(" ", "-") == t.lower().replace(" ", "-"):
                    hit = f"holds `{key}: {v}`"
                elif pl.get("prefix") and isinstance(v, str) and v.startswith(pl["prefix"]):
                    hit = f"holds `{v}`"
                if hit:
                    break
            if hit:
                out.append(("fail", f"{where} {hit}: `{t}` is retired in that place (R14)"))
        else:
            ms = [m for f in [t] + e["forms"] for m in term_rx(f).finditer(prose)]
            if ms:
                m = min(ms, key=lambda m: m.start())
                out.append(("should", f"{where}: `{t}` ×{len(ms)}, retired for {e['sense'] or 'a sense not stated'}; is "
                                      f"that what is meant? e.g. '{sentence(prose, m)}' (R14)"))
    return out
