---
id: blueprint
title: Commons blueprint
status: decided
lang: en
touches: [model, core, core-knowledge, core-views, library, mcp, flow-bodies, learn]
terms: [commons, commons-core, blueprint, frame, section, shell, world, five-qualities, domain-core, variant]
schema: schemas/blueprint.schema.json
check: tools/check_core.py
supersedes:
  - Commons-Engineering/workshop@main:_manifests/COMMONS_BLUEPRINT_MANIFEST.md
  - Commons-Engineering/workshop@main:_specifications/COMMONS_BLUEPRINT_SPEC.md
---

# Commons blueprint

*The building plan of a CORE: everything a commons wants to know about itself, section by section along the model's frame.*

## 1 · Goal

A CORE is built, researched, checked and grown along one plan, its blueprint: sections laid out along the model's frame, each asking its questions of one node and saying what answers them, when an answer counts, what an empty section means and who may see the answers. The plan holds no answers; the answers are the CORE's records and knowledge, and every briefing is a view derived from the plan and the knowledge together (`core-views`). The frame is the same in every commons, a domain adds what every commons of its kind is asked, and a commons adds its own, so every CORE stays comparable section by section. This specification decides one thing for its reader: **whether a commons' plan asks what it needs to know, and how far its CORE answers it**.

## 2 · Boundary

**Belongs here:** the plan and its three layers; a section, what it binds and how it is answered; the outcome of each section; the decisive selection of each family; the order in which research and authoring take sections.

**Does not belong here:**

| Matter | Where it belongs |
|---|---|
| the records that answer a section, and the frame's nodes | MODEL, `core` |
| the standing of a claim and its sources | `core-knowledge` |
| views, their kinds, rendering and provenance | `core-views` |
| the founding dialogue that walks the plan with a person | `core` R41 |
| shells, grants and access classes | `mcp` |
| who decides, and the purpose in a person's own words | `flow-bodies` |
| releasing a model with its layer | `library` |
| a curriculum path over sections | `learn` |

## 3 · Terms

The terms in the front matter resolve in the commons' glossary. Two of them are new with this specification and are added to the glossary in the same change:
- [frame](glossary/terms/frame.yml);
- [section](glossary/terms/section.yml).

The [blueprint](glossary/terms/blueprint.yml) term is revised with it. The cardinalities, evidence values and outcomes of part 5 are words of this specification.

## 4 · Requirements

| ID | Level | Requirement | Why | Check |
|---|---|---|---|---|
| R1 | MUST | A commons' plan is read from three layers, each only adding and none holding an answer: the frame of the Commons model, the layer of its primary domain model and the commons' own, every section lying `within` a section of its own or an earlier layer unless it is a top section of the frame. | The frame is the same in every commons, which keeps every CORE comparable, and a kind and a commons add what is theirs without taking anything away. The answers stay in the records and knowledge, where they are evidenced. | layers |
| R2 | MUST | The frame holds once every question asked of every commons, in the sections part 5 lists, each frame section with its questions and, unless its evidence is `computed`, the claim kinds its answers take. | What every commons answers is asked in one place, so no domain can redefine it and no commons can be played off against another. | frame |
| R3 | MUST | Every frame question reads sensibly for a life, an organisation, a settlement and an ecosystem, and a question that only one kind can answer belongs to that kind's domain layer. | A question only an organisation can answer bends every other kind to fit it. | review |
| R4 | MUST | Every layer validates against `blueprint.schema.json`. | The schema decides what a section is, so every tool and every reader reads it alike. | schema |
| R5 | MUST | A section id is unique across the three layers and is never renamed or reused. | Views, research runs and the history of coverage name a section by its id, and a changed id breaks all three without a word. | ids |
| R6 | MUST | A domain layer is released with its domain model, is shared by all the domain's variants, and holds only sections within the frame, faces for sections of the frame, a reading order and a default relevance per family or section. | A domain is itself in what lies within the frame, in its production, its mandate and its environment above all, while the frame stays the same everywhere. One layer per domain keeps a commons' plan and its history when it grows into the next variant. | layers |
| R7 | MUST | A commons' own layer adds sections within any section, faces, a reading order and the visibility of its own answers, never removes or renames a section, and answers a section that does not apply to it as a documented absence with its reason. | The commons shapes its plan under its own mandate, and comparability holds because nothing of the frame or the domain goes. | layers |
| R8 | MUST | A section binds by key and never by path, to one of the kinds part 5 lists. | A layout can change without the plan changing. | binds |
| R9 | MUST | The section `family` is asked of every family as one instance `<dimension>.<family>`, and a `per-selected` section has one instance `element.<kind>.<slug>` for each record the commons has selected. | Every family is asked alike and the frame stays sketchable, and ids that never change keep the history of each instance. | frame |
| R10 | MUST | A family's carrying stream is the commons' own decision, proposed by an agent and taken by a person or the Body answering for the dimension, and is written as `essential: true` on at most one stream of the family in the runtime. | The commons builds from exactly this selection, so it needs a place and a decider. Left to research, nobody makes it. | selection |
| R11 | MUST | Every section and every instance of it has one outcome, computed and never kept, as part 5 defines them, `covered` only where its answers meet its evidence rule and none rests on a contested claim left unresolved. | A gap is a question, an absence needs evidence, and what could not be read is neither; absence of evidence is not evidence of absence. | outcomes |
| R12 | MUST | Coverage, maturity and relevance are read apart and never combined into one score, coverage being a section's outcome and maturity and relevance claims about it. | One score hides whether the commons does not know something, does not do it well or does not need it. | review |
| R13 | MUST | A section's evidence rule is met by its answers as part 5 defines each value, `own-word`, `sourced`, `triangulated` or `computed`. | An answer counts only when its standing fits the question, and research learns which questions it may answer at all. | evidence |
| R14 | MUST | An answer rests only on sources whose access class reaches as far out as its section's visibility, a person's confirmed own word counting as released for the section it was given for, and in a CORE kept by an outside observer only on public sources. | What a section shows must not carry what its readers may not see, just as no inference may (`core-knowledge` R8). | evidence |
| R15 | MUST | A research or authoring run names its inputs by section and receives each input whole or with a declared cut. | A silently cut input gives a wrong answer that nobody can see. | review |
| R16 | MUST | Every section that a section `reads` exists in the plan, and `reads` forms no cycle. | Research and authoring follow `reads` in levels, so a missing or circular dependency leaves them without an order. | reads |
| R17 | SHOULD | What research takes up next is computed at each call and never kept: the sections not covered, level by level along `reads`, ordered within a level by the slice the agent names, the relevance of the family or section, the fading weight of earlier answers (`core-knowledge` R21) and signals, with an open decisive selection holding back whatever reads it. | A stored queue goes stale, while an order computed from the plan follows the commons as it changes. | review |
| R18 | SHOULD | A section's coverage over time is computed from the history in git and never kept, as whether answers existed at each commit with the evidence rule judged at the newest, and a clone without history shows no trend and says so. | The trend shows where knowledge grows or fades without a second record that drifts. | trend |
| R19 | MUST | A CORE kept by an outside observer uses the same plan, its `own-word` sections staying questions shown as not stated by the commons and never filled by inference, and its decisive selections standing as the observer's proposals. | A twin and the commons' own CORE stay comparable section by section, so a twin can be handed over as the commons' first plan. | review |
| R21 | MUST | A domain layer is authored by the domain's maker in its `[domain].core`. | Who answers for what every commons of a kind is asked must be known, and it is the one who knows the kind. | review |
| R25 | MUST | A face keeps the meaning of the section whose words it gives. | The face of a plan may differ per domain only while what is asked stays the same, or the comparison of commons fails unseen. | review |
| R22 | MUST | A domain's face sets a frame section's visibility only further in and its evidence rule only from `sourced` to `triangulated`, while a commons' own layer sets the visibility of its own answers in either direction. | A domain cannot know what a commons may share, so it can only protect; publishing is the commons' own act. | layers |
| R23 | MUST | A research run writes claims and proposals and never records. | Records carry the commons' decisions, which people take (`flow-bodies` R18). | review |
| R24 | MUST | No research run takes up an `own-word` section, which only the founding dialogue answers (`core` R41). | An own word inferred is a word put into someone's mouth. | review |

R20, what a view shows of the plan, is carried to `core-views` R5 and is never reused.

## 5 · Structure

The schema is `schemas/blueprint.schema.json`. It decides each layer, which holds `sections` and, for a domain or a commons, optionally:
- `faces`, for sections of an earlier layer: labels, and questions that replace the section's questions question by question in the same order and meaning (R25); a domain's stricter evidence rule; a visibility (R22);
- `order`, the reading order and the founding dialogue's starting point: the commons' own where it states one, else its domain's, else the frame's;
- for a domain, `relevance`, by family instance or section id, which the commons' own assessment overrides.

**The three layers** (R1):

| Layer | Where | Earlier place, read and reported as unmigrated |
|---|---|---|
| the frame | `specs/blueprint.yml` of the installed Commons model | `specs/views/blueprint.yml` |
| the domain's layer | `blueprint.yml` at the root of the primary domain model's installed copy | `views/blueprint.yml`, the layer derived at release, which adds no question |
| the commons' own | `blueprint.yml` at the CORE's root, structure key `blueprint` (structure 0.4.1) | `views/blueprint.yml`, moved by `migrate_core` |

**The frame** (R2) holds these sections, in this order, with their questions in [`blueprint.yml`](blueprint.yml):
- `identity`, and within it `identity.cores`;
- `mandate`, `purpose`, `values`, `qualities` (the five qualities), `situation` and `environment`;
- the dimensions `d0` to `d4`;
- `family`, the pattern for the thirteen families;
- the nine elements, `element.stakeholder` to `element.body`;
- `knowledge`;
- `lifecycle.path`, and within it `lifecycle.history`, `lifecycle.near-future` and `lifecycle.futures`;
- `loops`.

Its visibility is CORE, `environment` OPEN, so that a household's data stays in. A public portal shows only the sections whose visibility the commons has set to ROAM.

**A section** holds:

| Field | Holds |
|---|---|
| `id`, `within` | its stable id; the section it lies in |
| `binds` | what answers it, by key (below) |
| `cardinality` | `one`; `per-selected`, one instance `element.<kind>.<slug>` per selected record; `per-family`, one instance `<dimension>.<family>` per family (R9) |
| `labels` | per language |
| `questions` | what is asked, a shared starting point, never a closed questionnaire |
| `reads` | the sections whose answers it presupposes (R16) |
| `answers` | the claim kinds of `core-knowledge` an answer takes; none for a `computed` section |
| `evidence`, `empty`, `visibility` | its evidence rule; `question`, or `absence` where a documented absence may answer it; the outermost shell whose readers may see its answers |

**What a section binds** (R8):

| Kind | Resolves to |
|---|---|
| `dimension`, `family`, `element` | a node of MODEL's frame, and the runtime's records under it |
| a record kind, `body`, `loop` | the runtime's records of that kind, by `slug` where one is named |
| `identity` | a `field` of `commons.yml` |
| `knowledge` | the claims `about` a section or node, of one `claim` kind where one is named; without `about`, the whole claim register |
| `lifecycle` | the events or the stage (`of`) |
| `worlds` | the COREs among the repositories `commons.yml` names in `sources` whose `world_of` is this commons' id, never their content; none at hand reads `unsighted` |

**A section's answers** are what it binds and the claims whose `about` names its id or its `binds.about`. A bound field of `commons.yml` answers together with a claim about the section that carries its standing: the field holds the words, the claim the evidence. The founding dialogue writes a person's words for `purpose` into the field and records the confirmed own word beside it (`core` R41).

**The evidence values** (R13):

| Value | Met by |
|---|---|
| `own-word` | a `self-description` claim resting on a source of origin `given` whose `given_by` names the person of the party register who gave it and whose `confirmed` dates that person's confirmation |
| `sourced` | a claim with one source |
| `triangulated` | a claim with two distinct sources, neither a `copy_of` the other and at most one `about_itself`, or with one source and its `limitation` |
| `computed` | the runtime's records under what the section binds, at least one, each passing `check_model.py` with its bindings; a dimension, each family instance within it covered or a documented absence; the whole claim register, at least one claim, each valid |

A claim is contested and unresolved where its `contested_by` is not empty and no claim `supersedes` it. A source's access class reaches a shell through `classes` in `access.yml` (`mcp` part 5), in the order SEED, CORE, PEER, OPEN, DOCK, ROAM from the centre, so it compares with a section's visibility (R14); a source without a `class` counts as `public` where its origin is `public`, and as `personal` otherwise.

**The outcomes** (R11):

| Outcome | Means |
|---|---|
| `covered` | answered, the evidence rule met, nothing it rests on contested and unresolved |
| `on-shelf` | an installed model holds what it binds and the runtime has not built it: neither a gap nor a decision |
| `missing` | not answered, or answered below its evidence rule: a gap and a question; *not offered* where no installed model reaches it |
| `documented-absence` | a claim with `absence: true`, meeting the section's evidence rule, shows that what it asks about does not exist |
| `unsighted` | it could not be read under the access at hand |

## 6 · Checks

`tools/check_core.py <core>` checks a CORE's plan together with the rest of the CORE. **None of the checks below is built yet:** `layers`, `frame`, `ids`, `binds`, `selection`, `outcomes`, `evidence`, `reads` and `trend` are to be built with Commons 0.3.1 (commons.core#112), `trend` possibly later (BP-5), and each is a gap until it is, whatever name the tool already uses for something else.

| Check | Tests |
|---|---|
| `layers` | the three layers are read from their places, an earlier place reported as unmigrated; every `within` names a section of its own or an earlier layer; a domain layer holds only what R6 allows and its faces only narrow (R22); a commons' layer removes and renames nothing (R1, R6, R7, R22) |
| `frame` | the frame holds the sections of part 5, in order, each with its questions and, unless `computed`, its `answers`; `family` and every `per-selected` section yield their instances with the ids of R9 (R2, R9) |
| `ids` | ids are unique across the layers; with `--since <revision>`, no id is renamed or reused (R5) |
| `binds` | every binding resolves by key to what part 5 lists; a path is a fail (R8) |
| `selection` | at most one stream per family carries `essential: true`; none is an open selection, a question (R10) |
| `outcomes` | each section and instance has one of the five outcomes, `covered` only as R11 and part 5 say (R11) |
| `evidence` | each answer meets its section's evidence value, and its sources reach as far out as the section's visibility, only public ones in an observed CORE (R13, R14) |
| `reads` | every id in `reads` exists, and `reads` has no cycle (R16) |
| `trend` | coverage over the history, existence per commit and the evidence rule at the newest; without history, no trend and a note (R18) |
| `review` | a reading by the human accountable for this specification's mandate, against the Why of R3, R12, R15, R17, R19, R21, R23, R24 and R25 |

## 7 · Example

**Minimal:** a commons' own layer, `blueprint.yml` at its CORE's root, adding one section within the frame:

```yaml
sections:
- id: tool-library.lending-rules
  within: element.value-exchange
  binds: {kind: knowledge, about: tool-library.lending-rules, claim: self-description}
  cardinality: one
  labels: {en: Lending rules}
  questions:
    - Who may borrow which tool, and for how long?
  answers: [self-description]
  evidence: own-word
  empty: question
  visibility: OPEN
```

**A domain's layer**, `blueprint.yml` at a business model's root: a face, a stricter rule, a reading order, relevance and one section of its own:

```yaml
faces:
  purpose: {labels: {en: Purpose of the company, de: Bestimmung des Unternehmens}}
  identity: {evidence: triangulated}
order: [mandate, environment, identity, identity.cores, purpose, situation]
relevance: {d4.demand-to-fulfillment: high, d2.contributor-to-succession: medium}
sections:
- id: business.investors
  within: identity.cores
  binds: {kind: knowledge, about: business.investors}
  cardinality: one
  labels: {en: Investors}
  questions:
    - Who has invested in the company, and on which terms?
  answers: [fact]
  evidence: sourced
  empty: absence
  visibility: CORE
```

**Complete:** the frame, [`blueprint.yml`](blueprint.yml).

## 8 · Decision log

| Date | Kind | Decision | Word |
|---|---|---|---|
| 2026-11-15 | commissioned | The blueprint as a specification of its own: the building plan of the whole CORE, from which it is built, researched, checked for coverage and grown, and from which views are derived together with knowledge; thought further than the definition of 22 and 25 October; `core-views` keeps views only (BP-1) | Holger, commons.core#110, comment 6900063493 |
| 2026-11-15 | revised | **Written for adoption, for Commons 0.3.1, to be adopted under BP-8.** Written from the design with its choices C1 to C16 as recommended, `environment` a frame node, within the Commons SPECIFICATION (BP-5, BP-6); the plan's own place with structure 0.4.1 (BP-7, the Office under GO-3); R1 and R3 of `core-views` carried here as R1 and R11 | Holger, commons.core#110, comment 6900567786 (*"wie empfohlen, wir halten uns aber an unserer Spec der Specs, nicht wahr?"*) |
| 2026-11-15 | revised | **Written for adoption, for Commons 0.3.1, to be adopted under BP-8.** The independent review's findings: `computed` and the whole claim register defined, a bound field answering with its claim; R20 carried to `core-views` R5; R6 split (R21, R25) and R15 split (R23, R24); R22, a domain's face only narrowing; `needs`, `register` and `post` left out; the frame's questions widened and its visibility CORE, `environment` OPEN; a domain layer in part 7 | Holger, commons.core#113, comment 6900943440 (BP-8) |
| 2026-11-15 | adopted | Adopted under BP-8: the independent review's findings fixed and re-read with no blocking finding left, the structure 0.4.1 in the same change, check_spec 0 fail; in force with the merge of release/0.3.1 | Holger, commons.core#113, comment 6900943440 (*"Ja"*) |

**Rests on:** the blueprint definition, A1 to A7 (Holger, 22 and 25 October 2026, commons.core#79, comments 6346623945 and 6397521121). The options, their reasons and the mapping of every old fragment are in the design, `Commons-Engineering/commons.core@2ff7fbc6:instance/workshop/blueprint-spec/design.md` and `Commons-Engineering/commons.core@2ff7fbc6:instance/workshop/blueprint-spec/fragments.md`.

What this specification supersedes, and what it carries of it, is in [`carry-over/blueprint.md`](carry-over/blueprint.md).
