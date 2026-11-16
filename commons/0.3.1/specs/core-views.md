---
id: core-views
title: Commons CORE — views
status: decided
lang: en
touches: [blueprint, core, core-knowledge, model, flow, library, mcp, learn]
terms: [commons, commons-core, blueprint, lighthouse, world, provenance-record]
schema: schemas/core-views.schema.json
check: tools/check_core.py
supersedes:
  - Commons-Engineering/workshop@main:_manifests/COMMONS_CORE_MANIFEST.md
  - Commons-Engineering/workshop@main:_specifications/COMMONS_CORE_SPEC.md
  - Commons-Engineering/workshop@main:_manifests/COMMONS_BLUEPRINT_MANIFEST.md
  - Commons-Engineering/workshop@main:_specifications/COMMONS_BLUEPRINT_SPEC.md
  - Commons-Engineering/workshop@main:_manifests/COMMONS_VALUE_CREATION_MANIFEST.md
---

# Commons CORE — views

*The views a CORE renders from its plan and its records.*

## 1 · Goal

A commons is read by its board, its people, its partners, the public and agents, each needing a different cut of one picture. A view selects and orders sections of the commons' plan, its blueprint (`blueprint`), for one audience, and renders their answers from the CORE's records and knowledge, never written beside them. This specification decides one thing: **whether what a CORE shows is a faithful rendering of what it holds**, for the reader it is meant for.

## 2 · Boundary

**Belongs here:** view definitions and their kinds; the outcome a rendering shows for each section; the rendering and its provenance record; what a view may say, and to whom.

**Does not belong here:**

| Matter | Where it belongs |
|---|---|
| the plan, its sections and their outcomes | `blueprint` |
| the records a view is rendered from | `core`, MODEL |
| the standing of a statement | `core-knowledge` |
| who renders, reviews and delivers, and when | FLOW |
| the records a model holds, which a primary model's sections bind | MODEL |
| a model's release, the editorial step before a page goes public | LIBRARY |
| serving views to machines | MCP |

## 3 · Terms

All terms resolve in the glossary. No term is new with this specification. The view kinds and the five outcomes of part 5 are words of this specification.

## 4 · Requirements

| ID | Level | Requirement | Why | Check |
|---|---|---|---|---|
| R5 | MUST | A view is a definition in `views/<name>/view.yml` naming its kind, its audience, its sections in order, what it promises its reader and where a correction goes, its formats, its languages, the commons' own first, and its host where it is delivered elsewhere; and an interactive view reads data and section ids, never prose, and a view renders the answers of the sections it names, never one of its own, showing a section's questions, reads and evidence rule only in the `gaps` view. | A view as data can be rendered, checked and compared, and a view without a way back cannot learn. Prose cannot be queried without guessing, and a briefing that shows authoring fields becomes a questionnaire. | views |
| R6 | MUST | The view kinds are `briefing` (full, summary, environment, futures), `lighthouse`, `spoken`, `portal`, `card`, `gaps` and `curriculum`, one path of sections whose `after` names the paths it presupposes (`learn` R2), and a commons may add a kind of its own. | Shared kinds keep views of different commons comparable; an own kind is a commons' right. | views |
| R8 | MUST | A rendering is generated from records, never edited by hand and never a source of fact, and names what produced it in a committed provenance record, its three definitions with their digests, the hash of its inputs and the origin of each expected picture; a rendering whose inputs changed is stale, never a defect. | A view written beside the model drifts from it. A reader must be able to tell what a view rests on and whether it is current. | provenance-record |
| R9 | MUST | A view writes about the commons and its world, never about the evidence trail: a statement's standing shows as a source in brackets, an assumption says so, a contested claim is named, and a figure without a source is not stated. | The reader learns the commons, and still sees how sure each sentence is. | review |
| R12 | MUST | A view shows the commons' state, our confidence and the relationship as three axes, never as one score, and never shows the relationship in a public view. | One score hides which of the three it measures. | review |
| R13 | MUST | A rendering is filtered by the reader's grant before it is composed, and a committed rendering has one audience. | What is composed cannot be filtered afterwards. | review |
| R14 | MUST | The full briefing opens with the purpose, stated precisely enough to be challenged, and reads who the commons is, how it works and where it is heading, in that order, its middle part generated from the runtime. | One reading order in every commons, and the working body never out of step with the model. | review |
| R15 | MUST | A futures view names and summarises worlds and their no-regret moves and never contains them, and every world it names has a world CORE behind it. | A world is a full instance of its slice, not a chapter. | review |
| R16 | MUST | The spoken view says the commons in seven beats (name, same, fame, pain, aim, game, exchange), keeps its two forms apart, and passes the repeat test: a stranger can give it back. | If a stranger cannot repeat the purpose, it is not precise enough. | review |
| R17 | MUST | A public face in a repository of its own is the structure key `views/<name>` pointing there, never a submodule. | The membrane between the private CORE and its public face is a declared location. | review |
| R20 | MUST | A deliverable of a milestone is a view committed at that milestone, and handing a CORE to its commons is an adoption, not a view. | A milestone is a moment; a handover is a change of who holds the CORE. | review |
| R21 | MUST | Three model cuts are generated from the one plan (`blueprint`) and never kept, each with every frame section: the value cut, families to streams in the order `commons.yml` states, else as its models deliver it in `model.yml`, in the order they are pinned (`model` R29), its own streams after them by title, then to steps and capabilities; the entity cut, each entity's shape and relations; and the element cut, the nine elements, a Body's Posts under it and the value exchanges at each touchpoint; every record shows its `origin` where it has one, and where it is *used in*, the steps that use it, read from MODEL's binding identities backwards (MODEL R22). | A commons reads its process, its information and its people from one model, and its business architecture is the library of what it uses, so it must see at any time which record serves which stream. A cut that drops a family or an element is no longer comparable. | cuts |
| R22 | MUST | The page of a model is a cut of the same plan over a release's own records, read from the stakeholder side: what the model gives and asks, its starting set, each touchpoint with the streams that serve it as proposals, and for each stream the records building it would take, derived as the building help derives them, and in a commons each record as used by its runtime or on the shelf; the depth is said to be served, never shown as installed; and the page is public only after an editorial step. | Read as the needs it meets and the proposals that meet them, a model can be chosen; read as a list of records, it is a phone book. A page that counts differently from the building help promises what building does not give. | cuts |

R2, R4, R7, R10, R11, R18 and R19 are merged into the requirement that now holds them (part 8), and R1 and R3 are carried to `blueprint` as its R1 and R11; none is reused.

## 5 · Structure

The schema is `schemas/core-views.schema.json`. Its root is a `views/<name>/view.yml`, a flat `view`; `views/blueprint.yml`, holding `sections`, is the plan's earlier place (`blueprint` part 5).

**The plan** a view renders, its three layers, its sections and their outcomes, is read as `blueprint` part 5 says. A section `on-shelf` shows its record as the expected picture.

**The renderings** of the blueprint are generated by `tools/render_blueprint.py <core>` into `views/briefing/`, `views/blueprint/` being their earlier place: `briefing.md`, the full briefing, and the three cuts `value-model.md`, `entity-model.md` and `element-model.md` (R21); with `--model <release>`, the page of a model `model.md` (R22).

**A view** lives in `views/<name>/`: its definition `view.yml`, and its renderings.

**Identity:** a view is known as `view:<name>`, by its folder, and a section as `section:<id>`, by its id (`blueprint` R5), wherever another specification reads them, as a graph does (`graph` R5).

**The provenance record** of a view is `.provenance/<name>/manifest.json`; `.build/` is its earlier location. It holds:
- `definitions`: the frame, the primary model's sections and the commons' own, each with its path and digest, the view definition and the structure;
- `inputs`: each input with its hash;
- `outcomes`: each section id with its outcome.

The outcomes are those of `blueprint` part 5 (its R11).

## 6 · Checks

`tools/check_core.py <core>` checks a CORE's views together with the rest of the CORE. Not yet built, each a gap until it is (commons.core#112): `render_blueprint.py` writing into `views/briefing/`, and `check_core.py` reading the renderings there rather than in `views/blueprint/`.

| Check | Tests |
|---|---|
| `views` | every `view.yml` validates, carries its folder's name, names sections that exist, and states its promise, way back and languages; a curriculum's `after` names curriculum views of the CORE; an unknown kind is reported, not failed (R5, R6) |
| `provenance-record` | every rendering has a provenance record that names its three definitions with their digests and its inputs, an outcome for each of its sections, among the five of `blueprint` R11, and the origin of each expected picture; an empty record is no provenance (R8) |
| `cuts` | the three cuts and the page of a model are generated, never edited, a family's streams in the order of R21, each with its provenance record and every frame section; every record of a cut shows its *used in*, derived, and its `origin`; the page of a model shows each touchpoint's proposals, its count per stream equals what the building help derives, and it names no installed depth (R21, R22) |
| `review` | a reading by the human accountable for this specification's mandate, against the Why of R5, R9, R12 to R17 and R20 |

## 7 · Example

**Minimal:** one view of kind `card`, its `views/card/view.yml`:

```yaml
name: card
kind: card
audience: anyone who meets the commons
promise: what the commons is and how to reach it
way_back: a proposal item in the Commons Workshop
sections: [d0.perception-to-mandate]
formats: [markdown]
languages: [en]
```

**Complete:** [the views of the tool library's CORE](examples/core/tool-library.core/views/card/view.yml), with a plan, a full briefing and a card, each with its provenance record.

## 8 · Decision log

| Date | Kind | Decision | Word |
|---|---|---|---|
| 2026-10-26 | commissioned | the views part of Commons CORE, split along its boundary | commons.o#89, opened on the word of the human accountable |
| 2026-10-26 | adopted | Adopted together with `core` and `core-knowledge`; empty build records are no provenance | Holger, commons.o#89, comment 6415733592 |
| 2026-10-29 | revised | R6 and the schema take the kind `curriculum` and its field `after`, to be adopted together with `learn` (R2), as the EA asked (commons.o#92, comment 6501201880). Adopted 29 October 2026 ([commons.o#98, comment 6505618412](https://github.com/Commons-Engineering/commons.o/issues/98#issuecomment-6505618412)) | Holger, commons.o#92, comment 6473604541 |
| 2026-10-29 | revised | Part 5: a view is known as `view:<name>` and a section as `section:<id>`, and the `views` check holds a view's `name` to its folder (part 6), so that a graph can serve a curriculum step to a learner outside the repository (`learn` R2). Adopted 29 October 2026 ([commons.o#92, comment 6509201761](https://github.com/Commons-Engineering/commons.o/issues/92#issuecomment-6509201761)) | D2-CE's demonstration, commons.o#92, comment 6505909477; the form agreed with @D4-CE |
| 2026-11-02 | revised | **Written for adoption, not yet adopted.** From station 7 of the end-to-end run of commons.o#109 and Holger's words on it, then lightened by weight: R1, three definitions each only adding, the frame never removed or renamed; R3, *not offered* beside `missing`; R8, the build record with its three definitions and each expected picture's origin; R21, three model cuts, every record showing where it is *used in*; R22, the offer page from the stakeholder side, its count per stream the activation package; R2 merged into R1, R4 into R3, R7 into R8, R10, R11 and R18 into R5, R19 into R6. *Where-used* stays the term for bills across commons (GRAPH R27) | commons.o#109: D1 6569467351, D3-CE 6569475840, settled 6569487111; Holger 6571926000 and 6572334454; adoption is Holger's |
| 2026-11-02 | adopted | The revision of commons.o#109 adopted as merged in `56cbfd5`: the three acts, the library, every kind offered whole with the stakeholder side on its own, the weight pass, and Holger's words of that day folded in | Holger, [commons.o#109, comment 6574646061](https://github.com/Commons-Engineering/commons.o/issues/109#issuecomment-6574646061) (*"sonst ja"*) |
| 2026-11-02 | revised | **Written for adoption, not yet adopted.** R21 and the check `cuts`: a family's streams in the order the commons states, else as its extensions deliver it, its own after them by title; a stream renamed keeps its place through `adopted_from` | Holger, commons.o#109, 6574765768 (*"Reihenfolge der VS innerhalb der VSF sollte von der Extension ausgeliefert werden. Von Nummern in den VS bin ich nicht so angetan"*), on D1's form reading 6574803729 with the Office's change |
| 2026-11-02 | adopted | R21, the cuts rendering a family's streams in the commons' order, else as its extensions deliver it, adopted as merged in `ab223d3` | Holger, [commons.o#109, comment 6577346808](https://github.com/Commons-Engineering/commons.o/issues/109#issuecomment-6577346808) (*"ja"*) |
| 2026-11-03 | revised | **Written for adoption, not yet adopted.** From the models note of commons.o#109 and the migration to 0.4.0 (#110): R1, the frame's section `loops` for `operations` and the primary model's sections; R3, the outcome `on-shelf` for `not-selected`, neither a gap nor a decision (decision 33), and `missing` where no installed model reaches; R8, the provenance record; R14, the runtime; R21, the order from `model.yml`, each record with its `origin`; R22, the page of a model and the building help; the check `provenance-record` for `build-record`; the examples follow D4-CE's tools | commons.o#109, the models note; Holger 6602880861, 6603340647 and 6610425987; adoption is Holger's |
| 2026-11-04 | adopted | The revision of 3 November adopted with the merge of structure 0.4.0 into `main` (A1, A2) | Holger, commons.o#110, comment 6625957149 |
| 2026-11-07 | revised | **Drafted for Commons 0.3.0, not yet adopted.** N1: the frame of the Commons model | Holger, commons.core#110, comment 6627102753 (N1), as `instance/workshop/run-110/commons-030.md` lists; adoption is Holger's |
| 2026-11-15 | revised | **Written for adoption, for Commons 0.3.1; adopted with the merge of release/0.3.1.** The blueprint leaves this specification for its own, `blueprint`, the building plan of the CORE: R1 and R3 carried there as its R1 and R11, the check `sections` with them; R5, a view renders the answers of its sections and shows authoring fields only in the `gaps` view (`blueprint` R20 carried here); the renderings in `views/briefing/`; part 1 and 2, the goal and boundary of views only; part 5 reads the plan from `blueprint`; R21 and R22 cut the one plan (BP-1) | Holger, commons.core#110, comments 6900063493 and 6900567786 |

**Rests on:** #79 A–E, C1 and C3 (Holger, 25 October 2026); H8 (#86).

What this specification supersedes, and what it carries of it, is in [`carry-over/core-views.md`](carry-over/core-views.md).
