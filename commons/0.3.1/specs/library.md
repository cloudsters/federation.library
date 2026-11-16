---
id: library
title: Commons LIBRARY
status: decided
lang: en
touches: [specification, core, core-knowledge, model, graph, graph-engine, library-patterns, mcp, flow]
terms: [commons, commons-library, model, variant, pattern, orbit, visibility-class, commons-core, part, where-used]
schema: schemas/library.schema.json
check: tools/check_library.py
supersedes:
  - Commons-Engineering/workshop@main:_specifications/COMMONS_EXTENSION_SPEC.md
  - ../commons/specs/PACK_SPEC.md
  - Commons-Engineering/workshop@main:_manifests/COMMONS_CORE_MANIFEST.md
  - Commons-Engineering/workshop@main:_specifications/COMMONS_CORE_SPEC.md
  - Commons-Engineering/workshop@main:_specifications/PATTERN_PIPELINE_SPEC.md
  - Commons-Engineering/commons-library@main:README.md
  - Commons-Engineering/commons-patterns@main:README.md
---

# Commons LIBRARY

*What a commons releases for others to install: each release a copy of its own, through one gate, and never changed.*

## 1 · Goal

A commons that has learned something others can use releases it, and a commons that installs it must be able to rely on it: the same checks wherever it came from, the same text tomorrow, and a record of where it came from and what changed. A library holds such releases as copies of its own, apart from the CORE they were made in: models and extracts of patterns. It publishes and never authors. This specification decides two things: **whether something is releasable**, meaning it passed the one gate and carries its provenance, its licence and no one's private data, and **where a commons finds what it may install, and which versions**.

## 2 · Boundary

**Belongs here:** what a library is and holds; the release record, the one release record of every library, which is a model's bill; what makes a model releasable; versions, their states and their end; the library's index; the gate; the check at install, the one check every installing commons runs; publication; where answers about a release go.

**Does not belong here:**

| Matter | Where it belongs |
|---|---|
| what a model is, a catalogue and its depth | `model` |
| installing a model and building from it | `core` |
| a model's research, its sources and their binding | `core-knowledge` |
| a pattern's form, orbits, known uses, promotion, the extract's index | `library-patterns` |
| where a CORE keeps what it installed, its lock, its `release` events | `core` |
| the graph run an extract is cut from | `graph-engine` |
| serving, grants, and how a commons sends an answer | `mcp` |
| the change brief a receiving commons computes, its decisions | `flow`, `core` |
| who operates a library, its hosting, its keys, its staff and what it announces | the operating commons |

**Touches** `specification`, `core`, `core-knowledge`, `model`, `graph`, `graph-engine`, `library-patterns`, `mcp` and `flow`. **Rests on** Holger's words: L1, L3, E2 and E5 (commons.o#90, comments 6464648757, 6464676842 and 6464808164); each commons the source of its change record (commons.o#91, comment 6466913268); a library as part of a CORE first and a repository of its own only later (commons.o#89); LIBRARY before MCP (commons.o#91, comment 6468952146); the KISS pass (commons.o#98). The joint position on change communication (commons.o#91, comment 6468978984) gives part 5's release fields.

## 3 · Terms

All terms resolve in the glossary. *Release*, *version*, *source* and *licence* keep their ordinary meaning, made precise by part 5; *library* is the glossary's `commons-library` in general.

## 4 · Requirements

| ID | Level | Requirement | Why | Check |
|---|---|---|---|---|
| R1 | MUST | A library is one repository, or at the first tier a folder of the CORE that holds it, with `library.yml` at its root naming its id, its holder and the releases it withholds, and the same layout at both tiers; it needs no permission to exist, only the gate, and a commons installs only from a library it names, under the id it gives it. | Moving to a repository of its own must change a location, never a record. What a library releases is trusted for the gate it passed, not for the address it came from. | layout |
| R2 | MUST | A library holds releases of two kinds, the models COREs release and the extracts of patterns, each a copy of its own in a folder named by its id and version, never a pointer into the CORE it was made in, with nothing of it leading outside, by a path, a step up, a link or a junction; and its index, its records and every public file can be read from a clone. | What was released must be readable without its maker, and what lies outside the copy is not what was pinned. A commons must be able to leave its host and keep what it installed. | layout |
| R3 | MUST | Every release has a record `release.yml`, generated from the `release` event of its source, that names what it is and its version, where it was made and at which commit, the gate's result with the checker that ran it, its parts, each with its visibility class and digest, its licence, the board where answers about it go and, for a major version, the rename map; the copy holds its one `public` part, and every other part is held only by the service that serves it. | One record says where a release came from, what it passed and what it changed, and a part's digest lets each holder verify the part it may hold without receiving the depth it may not. A release is half of an exchange, and a way back that names no place is none. | release |
| R4 | MUST | A version is semantic, released once and never changed or deleted: it ends by a date in the `retires` of a later record and stays installable by a commons that pins it; and a release that carries a private datum, an unauthorised part or a licence the library may not give is withheld by an entry in `library.yml`, after which the library no longer distributes its files while its record and its place in the lineage stay, and nothing is recalled or rewritten (`core` R10). | A commons that installed a version must be able to rely on it tomorrow and decides itself when it moves. Keeping a lineage is no duty to go on distributing what should never have been released. | immutable |
| R6 | MUST | The index `index.yml` lists every release with the path and digest of its record, its state, `candidate`, `released` or `retired`, and whether it is withheld, generated from the records and `library.yml` and never kept by hand; only a version that passed the gate is `released`, and a candidate `-rc.n` is installed only when pinned by its full version. | The index is how a commons sees a newer release, by reading it itself, and a state kept by hand drifts. A candidate is how a release is proved; it must never arrive by accident. | index |
| R8 | MUST | The gate is one code for every library, the checks of `model` in its catalogue mode, of `core-knowledge` on bindings, of `library-patterns` and of part 6, the same on a copy in the library, alone and at install, read without its maker; and no library adds a rule to it or drops one. | The gate decides what may be installed, not the address, and a check that is weaker where a commons installs is no check. A library that changed the gate would be another discipline. | release |
| R9 | MUST | A commons installs a release only after running the gate's checks of a copy again on its own copy, against the record digest its lock took from the library's index, and what fails there is not installed; what needs the maker, its research and the authority of its event, is checked at the maker's gate. | A library can be wrong or compromised, and a copy that agrees with itself proves no origin. A commons checks what it installs against what it pinned. | release |
| R10 | MUST | A release holds no name of a person or an organisation outside its provenance fields, `sources.yml` and a pattern's `contributors`, and no contact, commercial or credential datum; the names it is checked against are the discipline's rejected words and a list kept outside git. | A release is copied into every commons that installs it, and what it carries cannot be called back. A list finds the names on it and proves no text anonymous, so the reading stays human. | private |
| R11 | MUST | Every release names its licence by an SPDX identifier or by a `LicenseRef-` whose text it carries in its own `LICENSES/`, and the discipline's own releases stay free. | A commons may only use what it may use, and a licence without its text grants nothing wherever the copy went. | licence |
| R12 | MUST | A library publishes and never authors: its records are generated from the change records of their sources, it holds no research, no workshop, no decision's content and nothing of who installed what, and what it makes public becomes public only by its holder's editorial step, never one to one. | Each commons is the source of its own changes, and the library must never learn what a commons built. Released is not public. | review |
| R18 | MUST | A withholding reaches the commons that hold a copy through their own where-used (`graph` R27): each finds the lines of its bill whose release is withheld and decides what follows, while the library computes none and recalls nothing. | Only the commons that installed a release can see where it lies, and only it may decide. | where-used |
| R19 | MUST | A model is released only from an emulation of the CORE that makes it, with a person accountable for it, as a whole catalogue (`model` R28), each variant a release of its own (`model` R30), holding nothing that rests on a source its maker may not give out; it speaks Commons language, with no word in the sense the glossary rejects and no key in its place, names a third party's framework, code, trademark or proprietary structure only in its sources, binds only sources no jurisdiction enacts, `global`, and carries its attribution list `sources.yml` and its kind's specifications; and what commons build from it returns to its maker only where they release it, as an aggregate (`graph`). | Practice is extracted, never copied, and a word or datum that passes the gate is copied into every commons that installs it. Law that holds in one place is no part of a model of a kind, and a model learns from its reception only as far as a commons lets it. | model |
| R20 | MUST | A library's index is readable from the library's repository by every commons that names the library, from a public library without an account, so that each commons can compare its pins with it (`core` R40). | A commons can only notice a newer, retired or withheld release in an index it can read. | review |

R19 comes from EXTENSION R1, R8, R13, R14 and R31, as EXTENSION dissolves (part 8). R5, R7, R14, R15 and R17 are merged into the requirement that now holds them, R13 is folded into R12, and R16 is the operation of the commons that holds a library (part 8); none is reused.

## 5 · Structure

The schema is `schemas/library.schema.json`. Its root is `library.yml`; its `$defs` hold `index`, `release`, `extract` and `parts`.

```
library.yml                       id, holder, withheld
index.yml                         generated from the release records and library.yml
<model>/<version>/                a model's release (R19)
<model>/<variant>/<version>/      a variant's release (R19, `model` R30)
patterns/<version>/               an extract's release (library-patterns part 5)
<release>/LICENSES/<ref>.txt      the text of a licence the release names by reference
README.md, CONTRIBUTING.md        what the library is
```

| Field of `library.yml` | Holds |
|---|---|
| `id` | the library's id, lowercase with hyphens |
| `holder` | who holds the library, answers for it and gives the editorial word (R12) |
| `withheld` | `[{release, from, reason}]`: a release `<id>@<version>`, a variant's `<id>/<variant>@<version>`, the library no longer distributes, from a date, for `private-data`, `unauthorised` or `licence` (R4) |

**A release record** (`$defs/release`), the one release record of a model or an extract. A record of kind `model` without `source` or `written_in` fails the gate:

| Field | Holds |
|---|---|
| `kind` | `model` or `extract`; `extension` is its earlier value |
| `model` | for a model: its id; `extension` is its earlier key |
| `variant` | for a variant: its name, as its `model.yml` gives it (`model` R30) |
| `source` | for a model: the emulation it was cut from, `owner/repo@commit:models/emulation/<name>`, `<name>` the emulation's folder, a variant's name for a variant (R19) |
| `event` | the source's `release` event, `owner/repo@sha:lifecycle/events/<id>.yml` |
| `gate` | `result`, and `check`, the checker at the commit that ran, `owner/repo@sha:path` |
| `parts` | its one part, `model` or, for an extract, `patterns`, with its `class`, `public` or `member`, and its `digest`, `sha256:` over its files but the record, path by path, whatever the line endings; a model's part holds `model.yml`, the records, the loops, the depth, the specifications, `sources.yml` and the licence (`model` part 5); `essentials` is its earlier name, and an earlier `enhanced` part is history |
| `written_in` | for a model: the Commons model it is written in, `<library>/commons@<version>`, generated from the maker's lock or pins; a grammar, no model it stands on |
| `licence` | an SPDX identifier, or `LicenseRef-<name>` with its text in the release's `LICENSES/` |
| `answers` | the board where answers about the release go, `owner/repo` (R3) |
| `retires` | `[{id, from}]`: an earlier version of this library, `<id>@<version>`, a variant's id being `<model>/<variant>`, or a record an earlier version offered, and the date `YYYY-MM-DD` from which it is `retired` |

A model's `made_in` names the commit it was cut at, `owner/repo@commit`, and its `source` the emulation, `owner/repo@commit:models/emulation/<name>`. An extract's record (`$defs/extract`) has `kind: extract` and, in place of `source`'s emulation, the pattern source at its commit, the released graph run, the extractor, the extraction policy, the scope and the digest of its index (`library-patterns` R17).

**A release as a part:** its record is its single-level bill, its `parts` the lines and `made_in` the level below (`graph` R26).

**An index entry** (`$defs/index`): `id` (a model's id, or `patterns` for an extract), `variant` for a variant, `kind`, `version`, `record` (the path), `digest` (`sha256:` over the record), `state` and, for a withheld release, `withheld: {from, reason}`. The state is derived: `candidate` for `-rc.n`, `retired` from a `retires` date on, else `released`. Being withheld is no state: a withheld version keeps its state and its place in the lineage, and is no longer distributed.

**Installing** (R9): a commons resolves a release from the library's index at a revision and keeps in its lock the release, its origin and `record`, the digest the index gives (CORE R28). At install it runs the gate's checks of a release copy on the copy it received, against that digest: a copy whose files and record were changed together agrees with itself and still fails there.

**What a commons reads of a change** is the index, by reading it itself; the change is the source's `release` event (CORE), and the brief for a receiving commons is computed by that commons (`core`, `flow`). An answer arrives at the board in `answers` as one item, a commons' through its MCP's `propose` (`mcp` R12); no answer is *unknown*, never agreement.

## 6 · Checks

`tools/check_library.py <library>` reads one library: its `library.yml`, its index and every release in it, with the checks of `library-patterns` for each extract. It reports **fail**, **should** or **gap**, and exits with 1 only on a fail. `--names <file>` reads the list of names R10 checks against, from outside git; without it, that part of `private` is a gap. `--release <folder>` checks one release copy where it lies, as a commons does at install, with `--expect <digest>` the record digest its pin gives; `check_core.py` runs the same code on every installed copy, with the `record` of the lock (`core` R39). A copy's checks are one function in all three places: everything below but `layout`, `index` and `immutable`, which read a library.

| Check | Tests |
|---|---|
| `layout` | `library.yml` validates and every date in `withheld` is a date; the root holds only the entries of part 5; every release folder is `<id>/<version>/`, `<id>/<variant>/<version>/` or `patterns/<version>/` (R1, R2) |
| `release` | nothing of a copy leads outside it, links and junctions resolved; every release record validates, names this library, its folder's id, variant and version, a passing gate, a checker at a commit and where answers go; its one part is `model` or `patterns`, `public` or `member`, and its digest is that of the copy's files; at install, its record has the digest of the lock; every `retires` date is a date and names an earlier version this library holds, or a record an earlier version offered; a withheld release is held by the library and its folder holds its record alone; a model's release holds `model.yml`, `sources.yml` and its element folders, with at least one value stream that passes `model`'s checks in catalogue mode and a steering loop for every family it holds streams of, names its `written_in`, and binds only attributed sources, whose terms it never names; the Commons model may hold `specs/` alone while its records are not stated; every specification in a release follows SPECIFICATION but for what only the maker's estate resolves (R3, R4, R8, R9) |
| `model` | a model's release was cut from an emulation; nothing in it binds what it does not hold, and a variant passes `model`'s check `variants` (`model` R30); no word in the sense the glossary rejects and no key in its place, as the glossary's kinds say, quotations and source texts exempt; no term of a source outside its sources and bindings; only `global` sources bound (R19) |
| `immutable` | in git, every file of a released version is the one first released, and no released version has left the library but the files of a withheld one; outside git, a gap (R4) |
| `index` | `index.yml` is the one generated from the release records and `library.yml`, digest by digest, state by state and withholding by withholding; a candidate is never `released` (R6) |
| `private` | no e-mail address, telephone number or credential in any release; no served part, `knowledge/`, `workshop/`, `_authoring/` or `overlays/` in a copy; with `--names`, no listed name outside the provenance fields (R3, R10, R12) |
| `licence` | every release names an SPDX identifier, or a `LicenseRef-` with its text in its own `LICENSES/` (R11) |
| `where-used` | with `--core`, each line of that CORE's bill whose release is withheld is a `should` with its date and reason; a CORE without a bill is a gap with its failures, and each withheld pin its lock declares is named, unverified; nothing is written to the library (R18) |
| `review` | a reading by the human accountable, or by an agent that has only this file, of R10 beyond the list, R2 and R12 |

**Not built yet** (R28): the release tool that makes a release from a source's `release` event, and the verification that a record came from that event and that the event was authorised: until it exists, a well-formed `event` and `gate.result: pass` are the maker's statement, every check reports this as a gap, and E3 made its candidates with a script of its own (commons.o#96), whose records predate `parts`, `record` and `answers`. The first release under this gate is Commons Essentials 0.2.0; what its `specs/` holds of `tools/tests/`, whose fixtures carry contact data by design, is the release tool's to settle.

## 7 · Example

**Minimal:** a library that holds nothing yet. Its `library.yml`:

```yaml
id: tool-library-releases
holder: the tool library
```

**Complete:** [a library with one model and one extract](examples/library/demo.library/library.yml): the garden model in two versions, the second retiring a record and renaming another, and an extract of three patterns with its index. `check_library.py` reads it with 0 fail.

## 8 · Decision log

| Date | Kind | Decision | Word |
|---|---|---|---|
| 2026-10-26 | commissioned | LIBRARY: what a commons keeps for reuse and releases; a part of the CORE first, a repository of its own later | Holger, commons.o#91 (*"LIBRARY an D4-CE"*); commons.o#89 |
| 2026-10-28 | revised | Taken up after GRAPH, before MCP, on the decided inputs L1, L3, E2, E5, the change-record principle and E3's account | Holger, commons.o#91, comment 6468952146 |
| 2026-10-28 | revised | `commons-library` public, prepared in four steps (sight, archive the earlier canon, list what becomes public, switch on Holger's word); a note per period (O1) with no adoption counts (O2); one intake with two doors (O3); an extension's release carries no `overlays/` | Holger, commons.o#91, comment 6470680520 |
| 2026-10-28 | revised | KISS: one release record and one check at install for every library (R3, R9); three states and `withheld`; `policy.yml`, the `gate` field of `library.yml` and collections dropped; R13 folded into R12; R14 and R17 written for any commons, a library a commons names (R14), a release naming in `answers` where answers go (R17); R16, the period note, with the intake's staffing and `commons-library`'s publication the operation of the commons that holds it; the ids of folded rules retired, never reused (SPECIFICATION R7) | Holger, commons.o#98 (*"Ja, alle"*) |
| 2026-10-29 | revised | The EA's read of #91: containment, nothing of a copy and no path its index names leading outside it, by an absolute path, `..` or a link or junction, checked by the one check of a copy in its library, alone and at install (R2, R9); withholding stops distribution and recalls nothing, earlier commits and clones keeping the files, no history rewritten (R5); the install description cites CORE R29. Adopted 29 October 2026 ([commons.o#98, comment 6505618412](https://github.com/Commons-Engineering/commons.o/issues/98#issuecomment-6505618412)) | the EA, commons.o#91; commons.o#98 |
| 2026-10-29 | adopted | Adopted 29 October 2026 | Holger, [commons.o#98, comment 6505618412](https://github.com/Commons-Engineering/commons.o/issues/98#issuecomment-6505618412) |
| 2026-10-30 | revised | Step 2 of the bill of materials: a release record as the release's single-level bill (part 5); a withholding reaches the commons that hold a copy through their own where-used, the library computing none (R18; the check `where-used`). Adopted 30 October 2026 ([commons.o#107, comment 6521463793](https://github.com/Commons-Engineering/commons.o/issues/107#issuecomment-6521463793)) | Holger, commons.o#107 (step 1 adopted, comment 6519835234; D4-CE's reading, comment 6516687963) |
| 2026-10-30 | adopted | Adopted 30 October 2026 | Holger, [commons.o#107, comment 6521463793](https://github.com/Commons-Engineering/commons.o/issues/107#issuecomment-6521463793) |
| 2026-10-30 | revised | The EA's reading of step 2: without a bill, the check `where-used` names the withheld pins the lock declares, unverified, beside the CORE's failures, never certifying them and never making a second bill (R18). Adopted 30 October 2026 ([commons.o#98, comment 6526694766](https://github.com/Commons-Engineering/commons.o/issues/98#issuecomment-6526694766)) | the EA, commons.o#107, comment 6522100364; Holger, comment 6522699919 |
| 2026-10-30 | adopted | Adopted 30 October 2026 | Holger, [commons.o#98, comment 6526694766](https://github.com/Commons-Engineering/commons.o/issues/98#issuecomment-6526694766) |
| 2026-11-02 | revised | **Written for adoption, not yet adopted.** Read against the end-to-end run of commons.o#109, which proved R3, R6, R9 and the served depth, then lightened by weight, no requirement's intent changed: R14 merged into R1, R15 into R2, R17 into R3, R5 into R4, R7 into R6; the reach of `answers` from a public cut of a private maker stays with Holger's editorial step (O9) | D1-CE, commons.o#109: the bill 6569529481, stations 2 to 8 (6569492729); Holger 6572334454; adoption is Holger's |
| 2026-11-02 | adopted | The revision of commons.o#109 adopted as merged in `56cbfd5`: the three acts, the library, every kind offered whole with the stakeholder side on its own, the weight pass, and Holger's words of that day folded in | Holger, [commons.o#109, comment 6574646061](https://github.com/Commons-Engineering/commons.o/issues/109#issuecomment-6574646061) (*"sonst ja"*) |
| 2026-11-03 | revised | **Written for adoption, not yet adopted.** From the models note of commons.o#109 and the migration to 0.4.0 (#110): a library holds models and extracts (R2); the record is a model's bill, its `kind` `model`, its `profile` retired, its parts the two tiers and its `written_in` the Commons model (part 5); the gate names `model`'s catalogue mode and `core-knowledge` (R8); **R19** new, a model's release (decisions 30 and 35), from EXTENSION R1, R8, R13, R14 and R31, as EXTENSION dissolves; the check `model` | commons.o#109, the models note; Holger 6600137634, 6602880861, 6603340647, 6605938212 and 6610425987; adoption is Holger's |
| 2026-11-04 | adopted | The revision of 3 November adopted with the merge of structure 0.4.0 into `main` (A1, A2) | Holger, commons.o#110, comment 6625957149 |
| 2026-11-07 | revised | **Drafted for Commons 0.3.0, not yet adopted.** T1: R19 and the release's one part, `model` or `patterns`, `essentials` its earlier name; each variant a release of its own in `<model>/<variant>/<version>/`, its record and index entry naming the variant; the checks `layout`, `release` and `model`; N1; the terms | Holger, commons.core#110, comments 6626305178, 6626536835 and 6627102753 (V1–V3, T1, N1, VR-1 to VR-6), 6705288611 (F-4 b, F-5 a) and 6706321253 (S-a, VN-a, PO-a, RS-a), as `instance/workshop/run-110/commons-030.md` lists; adoption is Holger's |
| 2026-11-15 | revised | **Written for adoption, not yet adopted.** **R20** new: the index readable from the library's repository by every commons that names the library, from a public library without an account, for the comparison of `core` R40 | Holger, commons.core#110, comments 6892413220 (AL-1, AL-3) and 6892504427 (FM-1) |
| 2026-11-15 | revised | **Written for adoption, for Commons 0.3.1; adopted with the merge of release/0.3.1.** Part 5: `retires` names a variant's release as `<model>/<variant>@<version>`; `made_in` is the bare commit and `source` the emulation, `models/emulation/<name>`, a variant's folder named by its variant, as the schema and the release tool hold them; corrections, no new requirement (D2, D3 of the audit) | the independent audit of schemas against tools, through the Office, commons.core#110 (RL-8′, comment 6900063493) |

**Open for Holger** (proposals, not decided): **O4** the text of `LicenseRef-cloudsters-served` and the licence expression of the Commons models (E6; commons.o#69); the EA recommends that an operator's service terms never become the discipline's licence nor make Commons Enhanced proprietary, which no conformance check can decide (commons.o#91, 6470762650); **O5** whether business 2.0.0 keeps `released` while it carries third-party titles (commons.o#69). O1–O3 are decided (6470680520; O1 also 6470576685) and, after the KISS pass, are the operation of the commons that holds a library.

What this specification supersedes, and what it carries of it, is in [`carry-over/library.md`](carry-over/library.md).
