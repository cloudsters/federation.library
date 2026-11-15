#!/usr/bin/env python3
"""layout.py — where a CORE's parts live, by its structure definition (CORE R4, R6, R39; `structure.yml` 0.4.0).
Read-only; a module of the tools.

Every tool finds a part through this one reader, so a CORE on an earlier layout is read wherever its parts lie and
is reported as unmigrated, never refused, and a CORE moves to a new structure in one run with the tools that read it
(R4). A part moved by `locations` to a folder is read there; one moved to `owner/repo@rev:path` is resolved by
`check_core`'s `layout`, never here.

- **The areas of the CORE:** `models/runtime/`, the one active model, with its `loops/` and `state/`;
  `models/commons/<library>/<model>/`, each installed model whole and read-only, Commons Essentials as
  `models/commons/<library>/commons/`; `models/emulation/<name>/`, each model the CORE tries. Before 0.4.0 they were
  `registry/`, `operations/loops/` with `_state/`, `extensions/<library>/<extension>/` and `offer/`.
- **One layout of every model:** its element folders and `loops/` directly in its folder, and `model.yml`. A release
  copy's or an offer's `registry/` and `offer.yml` are their earlier places. A Post lies in its Body's folder,
  `bodies/`, and `posts/` is read as its earlier place; the depth has no folder of its own: a file holding `items:`
  anywhere in the model outside its element folders, `loops/` and `state/`, known by its content, `enhanced/` an
  earlier place of its files (MODEL part 5; `model.depth`).
- **Variants:** a variant of a domain is named `<library>/<model>/<variant>` wherever a model's id names an installed
  copy, a pin or an origin, and lies in `models/commons/<library>/<model>/<variant>/`, beside the others of its domain
  (MODEL R30, CORE R39).
"""
import glob
import os

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ESSENTIALS = ("commons", "commons-essentials")       # the essentials of the Commons model, and its earlier id


def yml(p):
    try:
        with open(p, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except (OSError, yaml.YAMLError):
        return None


def definition(core=None):
    """the structure definition at hand: the copy of Commons Essentials a CORE installs, else the one beside this tool"""
    for f in (sorted(glob.glob(os.path.join(core, "models", "commons", "*", "commons", "specs", "structure.yml"))) +
              sorted(glob.glob(os.path.join(core, "extensions", "*", "commons-essentials", "specs", "structure.yml")))
              if core else []) + [os.path.join(HERE, "..", "structure.yml")]:
        sd = yml(f)
        if isinstance(sd, dict) and sd.get("areas"):
            return sd
    return {}


SD = definition()


def entry(key, sd=None):
    sd = sd or SD
    return (sd.get("areas") or {}).get(key) or (sd.get("paths") or {}).get(key) or {}


def locate(core, key, sd=None):
    """(path, earlier): where the part `key` is, and the earlier place it was found at, or None; a part found nowhere
    is at its default place"""
    e = entry(key, sd)
    moved = ((yml(os.path.join(core, ".commons", "commons.yml")) or {}).get("locations") or {}).get(key)
    if isinstance(moved, str) and "@" not in moved:
        return os.path.join(core, moved), None
    default = e.get("path")
    if default and os.path.exists(os.path.join(core, default)):
        return os.path.join(core, default), None
    for old in e.get("earlier") or []:
        if os.path.exists(os.path.join(core, old)):
            return os.path.join(core, old), old
    return (os.path.join(core, default) if default else None), None


def path(core, key, sd=None):
    return locate(core, key, sd)[0]


def runtime(core):
    return path(core, "runtime")


def loops(core):
    return path(core, "loops")


def state(core):
    return path(core, "loop_state")


def provenance(core):
    return path(core, "provenance")


def provenance_dir(core):
    """the folder name the provenance record is written in: `.provenance`, else its earlier `.build` where only that is
    held, so a CORE moves in one run and never holds both (R4)"""
    return ".build" if os.path.isdir(os.path.join(core, ".build")) and not os.path.isdir(os.path.join(core, ".provenance")) \
        else ".provenance"


def release_id(rec):
    """the model a release record names: `model`, or its earlier key `extension` (LIBRARY part 5)"""
    return (rec or {}).get("model") or (rec or {}).get("extension") if isinstance(rec, dict) else None


def is_model(rec):
    """a release record of a model: `kind` `model`, or its earlier value `extension`"""
    return isinstance(rec, dict) and rec.get("kind") in ("model", "extension")


def pins(doc):
    """the models a `commons.yml` pins or a lock holds: `models`, or its earlier key `extensions` (CORE part 5, R4)"""
    doc = doc if isinstance(doc, dict) else {}
    return [x for x in (doc.get("models") if "models" in doc else doc.get("extensions")) or [] if isinstance(x, dict)]


def pin_key(doc):
    """the key a writer adds to: `models`, or `extensions` where a file holds that still, so one file has one key"""
    return "extensions" if isinstance(doc, dict) and "extensions" in doc and "models" not in doc else "models"


def canonical(ref):
    """a model's name with the Commons model's earlier id `commons-essentials` read as `commons` (CORE R4)"""
    parts = str(ref).split("/")
    i = 1 if len(parts) > 1 else 0
    if parts[i] in ESSENTIALS:
        parts[i] = ESSENTIALS[0]
    return "/".join(parts)


def ref_of(pin):
    """the name of a pinned or locked model: `<library>/<model>`, or `<library>/<model>/<variant>` for a variant
    (MODEL R30, part 5; CORE part 5, the lock)"""
    pin = pin if isinstance(pin, dict) else {}
    return f"{pin.get('id')}/{pin['variant']}" if pin.get("variant") else str(pin.get("id"))


def variant_of(d):
    """the name of the variant a model folder holds, from its `model.yml`, else None (MODEL R30)"""
    v = (yml(model_file(d)) or {}).get("variant")
    return v.get("name") if isinstance(v, dict) else None


def held_model(d):
    """whether a folder holds a model: its file, or a release record"""
    return os.path.isfile(model_file(d)) or os.path.isfile(os.path.join(d, "release.yml"))


def installed(core):
    """{`<library>/<model>` or `<library>/<model>/<variant>`: its folder}: every model the CORE installs, on either
    layout, a variant in its own folder under its domain's (CORE R39)"""
    out = {}
    for base in (os.path.join(core, "models", "commons"), os.path.join(core, "extensions")):
        for d in sorted(glob.glob(os.path.join(base, "*", "*", ""))):
            d = d[:-1]
            lib, m = os.path.basename(os.path.dirname(d)), os.path.basename(d)
            subs = [s[:-1] for s in sorted(glob.glob(os.path.join(d, "*", ""))) if held_model(s[:-1])]
            if not held_model(d) and subs:
                for s in subs:
                    out.setdefault(f"{lib}/{m}/{os.path.basename(s)}", s)
            else:
                out.setdefault(f"{lib}/{m}", d)
    return out


def copy(core, ref):
    """the folder of the installed model `<library>/<model>` or variant `<library>/<model>/<variant>`, where it lies,
    else where it would lie; Commons Essentials is found under either of its ids"""
    lib, m, *v = str(ref).split("/")
    names = ESSENTIALS if m in ESSENTIALS else (m,)
    for n in names:
        for d in (os.path.join(core, "models", "commons", lib, n, *v), os.path.join(core, "extensions", lib, n, *v)):
            if os.path.isdir(d):
                return d
    return os.path.join(core, "models", "commons", lib, names[0], *v)


def copy_target(core, ref):
    """where a model `<library>/<model>` or a variant `<library>/<model>/<variant>` is installed: `models/commons/`,
    or `extensions/` in a CORE that holds its copies there still, so that no second layout grows beside a filled one
    (R4)"""
    lib, m, *v = str(ref).split("/")
    if os.path.isdir(os.path.join(core, "extensions")) and not os.path.isdir(os.path.join(core, "models", "commons")):
        return os.path.join(core, "extensions", lib, m, *v)
    return os.path.join(core, "models", "commons", lib, "commons" if m in ESSENTIALS else m, *v)


def model_entry(key, sd=None):
    return ((sd or SD).get("model") or {}).get(key) or {}


def post_folder(sd=None):
    """the folder a Post is written in: its Body's, `bodies/`, as the structure definition's `model.posts` says, else
    the earlier `posts/` (MODEL R1, element 9; Holger, commons.core#110 6706321253, PO-a)"""
    return model_entry("posts", sd).get("path") or "posts"


MODEL_FILES = ("model.yml", "offer.yml", "release.yml", "sources.yml")   # a model folder's files beside its records
NOT_DEPTH = ("loops", "state", "specs", "views", "LICENSES", "registry")   # its folders that hold no depth


def depth_files(d, sd=None):
    """the files of a model's depth: every YAML file holding `items:` anywhere in the model outside its element folders,
    `loops/` and `state/`, known by its content and never by its path (MODEL part 5; `model.depth`, whose `path` is
    null); a file at an earlier place of the depth, `enhanced/`, is read there too. Returns their paths, sorted"""
    skip = set(record_folders(sd)) | {post_folder(sd)} | set(NOT_DEPTH)
    out = []
    for p in sorted(glob.glob(os.path.join(d, "**", "*.y*ml"), recursive=True)):
        rp = os.path.relpath(p, d).replace(os.sep, "/")
        if rp in MODEL_FILES or rp.split("/")[0] in skip:
            continue
        doc = yml(p)
        if isinstance(doc, dict) and isinstance(doc.get("items"), list):
            out.append(p)
    return out


def depth_earlier(d, sd=None):
    """the YAML files at an earlier place of the depth, `enhanced/`, whatever they hold (MODEL part 5)"""
    names = list(model_entry("depth", sd).get("earlier") or []) or ["enhanced"]
    return sorted(p for n in names for p in glob.glob(os.path.join(d, n, "**", "*.y*ml"), recursive=True))


def record_folders(sd=None):
    """the folders of a model's records: every element's, and `posts/`, the earlier place of a Post, read and reported
    as unmigrated; a Post lies in its Body's folder, `bodies/` (MODEL R1)"""
    return [e["folder"] for e in (sd or SD).get("elements") or []] + [x for x in ["posts"] + list(model_entry("posts", sd).get("earlier") or [])
                                                                      if x != post_folder(sd)][:1]


def element_dir(d, kind_folder):
    """the folder of one element in a model folder `d`"""
    return os.path.join(records(d), kind_folder)


def emulations(core):
    """{name: folder}: every model the CORE tries; an offer in the making, `offer/`, is one, read without opening a
    file (so that serving reads only the files it serves, MCP)"""
    out = {os.path.basename(d[:-1]): d[:-1] for d in sorted(glob.glob(os.path.join(core, "models", "emulation", "*", "")))}
    if os.path.isdir(os.path.join(core, "offer")):
        out.setdefault("offer", os.path.join(core, "offer"))
    return out


def model_file(d):
    """the file of a model folder: `model.yml`, else its earlier `offer.yml`"""
    for n in ("model.yml", "offer.yml"):
        if os.path.isfile(os.path.join(d, n)):
            return os.path.join(d, n)
    return os.path.join(d, "model.yml")


def records(d):
    """the folder that holds a model's element folders: the model's own, else its earlier `registry/`"""
    reg = os.path.join(d, "registry")
    return reg if os.path.isdir(reg) and not any(os.path.isdir(os.path.join(d, e["folder"]))
                                                 for e in SD.get("elements") or []) else d


def model_loops(d):
    return os.path.join(d, "loops")


def unmigrated(core):
    """the parts of a CORE found at an earlier place: [(key, earlier)]"""
    out = []
    for key in list((SD.get("areas") or {})) + list((SD.get("paths") or {})):
        p, old = locate(core, key)
        if old:
            out.append((key, old))
    return out
