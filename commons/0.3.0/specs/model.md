---
id: model
title: Commons MODEL
status: decided
lang: en
touches: [specification, core, core-knowledge, library, graph, mcp, flow]
terms: [commons, scaffold, dimension, value-stream-family, value-stream, value-stream-step, capability, entity, stakeholder, journey, touchpoint, value-exchange, solution, body, post, loop, shell, address, variant]
schema: schemas/model.schema.json
check: tools/check_model.py
supersedes:
  - Commons-Engineering/workshop@main:_manifests/COMMONS_VALUE_CREATION_MANIFEST.md
  - Commons-Engineering/workshop@main:_specifications/COMMONS_MODEL_SPEC.md
  - Commons-Engineering/workshop@main:_specifications/ENTITY_SPEC.md
  - Commons-Engineering/workshop@main:_specifications/STAKEHOLDER_REGISTER_SPEC.md
  - Commons-Engineering/workshop@main:_specifications/ADDRESSING_SPEC.md
  - ../instance/workshop/bodies/D1/element-9-posts.md
---

# Commons MODEL

*The grammar of every model: the kinds of records, the loops that keep them true, and how they bind.*

## 1 · Goal

Every commons, and every specification that speaks about one, needs the same words for the same things. Without them, two commons cannot be compared, and an agent cannot tell a sentence about a commons from noise. This specification is that grammar. It names the nine elements of a commons, the loops that keep them true, the five dimensions and thirteen families its value streams belong to, the steps and the capability map they meet at, and the bindings between them. It decides one thing for its reader: **whether a statement about a commons is well-formed in the shared grammar**. It does not decide whether the statement is true. A commons keeps its own words beside the grammar, and a kind's specifications add to it without redefining it.

## 2 · Boundary

**Belongs here:**
- the kinds of record: the nine elements, the Post within a Body, and the loop;
- what a model made for every commons of a kind holds, a catalogue, and its file `model.yml`;
- the depth of a model: its deeper records and aspects;
- the closed vocabularies: dimensions, families, capability levels;
- the bindings every record must state, even when not yet known;
- the address by which anything outside the model points into it;
- the rules that keep the grammar universal.

**Does not belong here:**

| Matter | Where it belongs |
|---|---|
| where models live, how a commons installs them and builds its runtime and emulations from them, how they are versioned | CORE |
| how certain a statement is (expected · assumed · claimed · evidenced); a source and its binding | CORE-KNOWLEDGE |
| people: the party register, names and contacts | CORE |
| who takes part and how: function, lineage, client, Offices, Supplier Posts, rhythms | FLOW |
| which streams, capabilities and entities a domain proposes, its measures, patterns and systems of record | each model, and its kind's specifications |
| how a model is released and its bill | LIBRARY |
| a loop at work: what it delivers as items, its rhythm among the rhythms of work | FLOW |
| patterns, and how they come to be addressed | LIBRARY |
| how records connect over time and across commons | GRAPH |

**Touches** the specifications named in the front matter.

**Rests on** the decisions that formed this grammar: the thirteen families 4/3/3/3; D0 named *Perception & Identity* (14 October 2026); element 9 the Body with Posts (18 October 2026); Posts with serving and accountability (22 October 2026, P1–P5); the Body and Post records and the person reference (25 October 2026, S3.1, S3.2); the shell words (24 October 2026).

## 3 · Terms

All terms resolve in the glossary. Two are new with this specification and are added in the same change:
- [shell](glossary/terms/shell.yml);
- [address](glossary/terms/address.yml).

The terms `ring` and `orbit_level` go to the rejected list, in favour of *shell*.

## 4 · Requirements

| ID | Level | Requirement | Why | Check |
|---|---|---|---|---|
| R1 | MUST | A model is a set of records and of the loops that keep them true: each record names its `kind`, one of the nine elements, a `post` within a Body, or a `loop`, and validates against `model.schema.json`; and no slug is both a stakeholder and an entity. | A model regulates: its records say where the commons is heading, and its loops compare what is sensed with them and return the difference as work, every statement about a commons being about one of these kinds or not about its value creation. A stakeholder stands at the edge and is represented by entities, never one of them. | schema |
| R2 | MUST | Every record has a `slug`, unique among the records of its kind and never reused, and a `title`. | Bindings, addresses and other commons point at the slug; a reused slug silently changes what they point at. | slugs |
| R3 | MUST | The dimensions are `d0` to `d4` and the families the thirteen of part 5, each broad enough to hold all of its streams across every stakeholder and asset, and neither a commons nor an extension renames, adds or drops one; a quality the whole embodies is never a family or a dimension. | Identical families make every commons comparable with every other, so that no system can be played off against another. Families are decided and streams discovered. | schema |
| R4 | MUST | Every value stream names exactly one family, and a dimension written on it agrees with that family's. | The stream is where a commons is itself; the family is where it stays comparable. | family |
| R5 | MUST | Every value stream has at least one step, and every step states the capabilities it requires and the entities it acts upon. | The step is where the value streams meet the capability map; without it, a capability floats. | schema |
| R6 | MUST | A capability binds to a value stream only through a step, and a step or a solution binds capabilities at L3. | One capability serves many streams; a tree of copies under each stream hides that. | capability-map |
| R7 | MUST | Capabilities form one map from L0 to L5, in which every node below L0 names exactly one parent one level up. | One map lets a commons see the same ability carrying many streams at once. | capability-map |
| R8 | MUST | A capability or an entity states neither a dimension nor a family, because its position is derived from the steps that bind it. | An asserted position drifts from the work; a derived one cannot. | schema |
| R9 | MUST | A journey states its stakeholder, its title naming the need it pursues, and, where it states them, its steps in order; a touchpoint its journey, the step it stands `at`, and a stakeholder only as the journey's; a value exchange its touchpoint with what is offered and what returns; a step the touchpoints it serves, the one tie between a stream and the stakeholder side; a solution the capabilities it carries; and an entity, where it states them, its type, attributes, states and relations as part 5 says. | Each element is defined by what it binds, so a record without its bindings is prose about the commons, not a model of it. The stakeholder meets the commons at a touchpoint, and what happens behind it is the organisation's way of keeping the promise, so the tie runs from inside out and is stated once. | schema |
| R10 | MUST | A binding names a record of the model by slug, a step as `<stream>/<step>`, an entity's relation its target, an attribute of type `reference(<entity>)` that entity and a loop's `keeps` also a family or a dimension as `family:<f>` or `dimension:<d>`, and a binding that names nothing yet, or an empty list, is a gap. | Missing is a legitimate state and the next question to ask, not an error. | bindings |
| R11 | MUST | The model holds kinds, never individuals: no record holds a person's name, e-mail address or telephone number, and a person enters only by identifier, in a Post. | A model of value creation needs no personal data, so it holds none. | no-persons |
| R13 | MUST | A Body states its form, its `part_of`, the Body it is part of or `null` where it is outermost, and its mandate, where `null` is a gap; a model may hold several outermost Bodies; no Body is part of itself through its chain; and a Body whose Posts are all served by agents fails, while one with no Post held by a human yet is a gap. | The mandate persists while people, agents and work change; the Body carries it, inside a whole that closes, a commons held by more than one whole has more than one outermost Body, and a council of agents alone answers to no one. | bodies |
| R14 | MUST | Only a Body holds capabilities, only at L0 to L3, and holding a node holds its subtree; a Post holds none, and answers inside its Body by its responsibility and its accountability. | A Body answers for a scope, and an activity is not a scope; a second holder of the same capability writes one binding twice (R22). | capability-map |
| R15 | MUST | A Post states its Body, its responsibility, who serves it and who is accountable for it, a human by identifier or a Body as `body:<slug>`, which resolves through that Body's steward Post and then through `part_of` to a human; accountability that ends in a cycle, at an open end or outside the model is a gap; and no check of the model grants authority to act. | Serving can be shared with machines; accountability is never vacant. Describing a model and permitting an act are two things, and a green check is the first only. | accountable |
| R16 | MUST | Every serving entry names whether a human or an agent serves, by identifier, and an agent entry also names its brief. | Who acts must be visible, and an agent acts only on a written brief. | schema |
| R17 | MUST | A Post served by agents only carries safeguards: its evals, its kill switch, its scope and its review. | Where no human serves, the limits must be stated before anything acts. | safeguards |
| R18 | MUST | Whatever refers to the model from outside does so by an address naming its source in `from`, one node by kind and slug, a weight, a status and the method that produced it; an address whose target the grammar cannot hold fails, one whose target this model does not hold yet is a gap, and only a ratified address to a held target counts as recognition. | Recognising evidence as an element is a mapping with a certainty, and confirmed mappings are what the grammar learns from. A contradiction is an error, an absence is a question. | addresses |
| R19 | SHOULD | A stakeholder names the one shell it stands in, and only stakeholders, journeys, touchpoints and value exchanges name shells. | A shell is closeness to the model, and only those who meet the commons stand somewhere near it. | shells |
| R20 | SHOULD | A model adds value streams, steps, capabilities, entities and loops, a kind adds the fields and aspects it declares in a specification of its own (SPECIFICATION), and neither redefines an element, dimension, family or field of this grammar. | A domain is itself in its streams; it stays comparable in the grammar. | review |
| R21 | MUST | The families and dimensions of part 5 agree with the canon data from which models generate their records, which also holds each family's placement profile and grounding. | Two sources for the same thirteen names drift apart. | canon |
| R22 | MUST | Every binding has the derived identity `<kind>:<slug>#<field>:<target>`, a step's binding `value-stream:<stream>/<step>#<field>:<target>`, and no binding is stated twice. | Moving an ability to another solution or Body is a change of the model, and a loop can only review a change it can name. | binding-ids |
| R27 | MUST | A commons' own word for a record is kept beside it in `stated_as`, and the grammar's name is never renamed to match it. | The commons recognises itself in its words, and stays comparable in the grammar's. | review |
| R28 | MUST | A model made for every commons of a kind is a catalogue: it holds every kind of record whole, so that nothing in it binds what it does not hold, and stands in all thirteen families, a family no stream reaches being its maker's gap; each archetype holds every field this grammar requires but the commons' own, a Body's `mandate` and a Post's `held_by`, which a record built from it writes as `mandate: null` and `held_by: []` until the commons states them; what a catalogue holds and no step uses is no gap; and in a runtime, a capability, entity, solution or touchpoint that no step uses is a gap. | Stakeholders, capabilities and entities serve every stream an organisation of the kind can run, and the families are the same everywhere, so a catalogue cut by stream would leave a commons' own streams without ground and a family not reached is its maker's question. An archetype is complete enough to hold as it is, while whether a Body forms and who serves a Post are the commons' own acts, and a runtime holding a record for nothing raises a question. | catalogue |
| R29 | SHOULD | A catalogue marks the starting set a commons of its kind begins with by `start: true`, that set holding every capability its streams bind, and names every stream it holds, and only those, in its family's `order` in `model.yml`. | A catalogue without a beginning or a sequence is a phone book, or is read as an order to take everything. The maker knows the natural sequence of its domain. | catalogue |
| R30 | MUST | A domain's model may come in variants: whole models under the domain's one id, each with a name of its own and naming the one before it, in one line, sharing a core, the records all of them hold under the same slugs, each adding its own streams and all in the same thirteen families; and a commons grows into the next variant by an emulation built from it that a merge makes its runtime (CORE R6). | A startup needs another model than a corporation, and a ladder fixed for all domains fits none; the shared core keeps the variants comparable, and the one id keeps them one domain. | variants |
| R31 | MUST | A variant holds whole what the records it shares with another bind (R28), and a Body that only another variant holds is, where a shared record names it, a stakeholder there and no Body. | A shared record is the same record in every variant, so it cannot leave out what one of them lacks; a body a variant has no seat in still stands at its edge. | variants |

R12 is merged into R1, R23 into R15, R24 into R18, R25 into R9 and R26 into R3 (part 8); none is reused.

## 5 · Structure

The schema is `schemas/model.schema.json`. A model is `records`, optionally with `addresses`. Each record carries `kind`, `slug` and `title`, plus the bindings of its kind. A kind may add fields it declares (R20); the schema leaves room for them. A record that comes from a model names its `origin`, `<library>/<model>@<version>#<kind>:<slug>`, with the origin's slug even where the commons renames it; a record of the commons' own names none (CORE R6). A record is retired where the release its `origin` names retires it (LIBRARY part 5, `retires`), or where it lies in an emulation that was the runtime (CORE R6): a state read from where the record stands, never a field of it. `adopted_from` is the earlier key of `origin`, read and reported as unmigrated. A catalogue marks its starting set with `start` (R29). A commons marks a record that carries it with `essential: true`: its decisive selection, as the views read it.

**The archetype and the commons' own.** An extension's archetype holds every required field of the table below except two: a Body's `mandate` and a Post's `held_by`. These are the commons' own acts. A record built from the archetype writes them as `mandate: null` and `held_by: []`, which read as gaps until the commons states them (R28). A Post's `accountable` in an archetype names a Body, `body:<slug>`, never a person (R15).

| # | Element | States (required) | Optional |
|---|---|---|---|
| 1 | **stakeholder** | — | `shell` |
| 2 | **journey** | `stakeholder`; its `title` names the need | `steps` (each: `slug`, `title`), the stakeholder's own, in the order walked; `shells`, in the order crossed |
| 3 | **touchpoint** | `journey` | `at`, a step of its journey; `stakeholder`, which must be the journey's; `shell` |
| 4 | **value-exchange** | `touchpoint`, `offered`, `returned` | `shell` |
| 5 | **value-stream** | `family`, `steps` (each: `slug`, `title`, `capabilities`, `entities`, and optionally `serves`, the touchpoints it serves) | `dimension`, which must agree |
| 6 | **capability** | `level` (L0 to L5), `parent` (`null` at L0) | — |
| 7 | **entity** | — | `type` (`master`, `transactional`, `governance`, `intelligence`); `attributes` (each: `name`, `type`, `card` as `<min>..<max>`, where a `type` of `reference(<entity>)` binds that entity); `states`, in the order passed; `relations` (each: `type`, `target`, an entity) |
| 8 | **solution** | `carries` (L3 capabilities) | — |
| 9 | **body** | `form` (`governing-body`, `organisational-unit`), `part_of` (always written, `null` for each outermost Body), `mandate` (`null` is a gap) | `holds` (L0 to L3); absent is the same gap as `[]` |
| 9 | **post** | `of`, `responsibility`, `accountable`, `held_by` (each: `kind`, `id`, and `brief` for an agent; `[]` is a vacancy, a gap) | `safeguards` (`evals`, `kill_switch`, `scope`, `review`); never `holds` (R14) |
| — | **loop** | `keeps`, the node it keeps true (`<kind>:<slug>`, `value-stream:<stream>/<step>`, `family:<f>` or `dimension:<d>`); `carried_by`, a Body (`null` is a gap); `rhythm`, what brings it back (FLOW R25) | `escalates_to`; the rest of its contract: trigger events, what it measures and emits, its stop |

**The thirteen families**, by dimension:

| Dimension | Families |
|---|---|
| `d0` Perception & Identity | `perception-to-mandate` |
| `d1` Purpose & System | `purpose-to-portfolio` · `value-to-sustainability` · `portfolio-to-system` |
| `d2` Participation & Relationship | `participant-to-community` · `collaboration-to-automation` · `contributor-to-succession` |
| `d3` Proposition & Exchange | `discovery-to-usage` · `interest-to-relationship` · `proposition-to-audience` |
| `d4` Production & Resilience | `demand-to-fulfillment` · `source-to-alliance` · `acquire-to-retire` |

**The stakeholder side and the stream.** A stakeholder pursues a need on a journey, step by step, meets the commons at some of those steps, each a touchpoint, the agreed place of a mutual value promise, and exchanges value there. To the stakeholder the touchpoint is a black box. Behind it, the steps of the commons' streams keep the promise, and each says so in `serves`. The streams that serve a journey are derived from these, never written. In a catalogue, a `serves` is the typical tie its maker proposes; in a runtime, it is the commons' own realisation. A journey's former `mirrors` and a touchpoint's former `steps` are read as an earlier layout, a gap until they move to `serves`.

**A loop** keeps one node true: it senses through the Fabric and `knowledge/`, compares with the record, and returns the difference as work, a proposal or an escalation, never a write into the record (FLOW R24). It is a record like any other, with its slug, its bindings and their gaps. A loop is built with what it keeps, and the record of each of its runs is the runtime's state (FLOW R23).

**A model's file** is `model.yml` at its root, for every model but the runtime, whose settings are `commons.yml`'s (CORE part 5): `id`, `title`; for a catalogue also `kind`, `gives`, `asks` and `order` (`{<family>: [<stream>, …]}`, R29); `variant: {name: <name>, after: <name>}` only for a variant, its `id` the domain's and `after` omitted for the first (R30), a variant being named `<model>/<variant>` wherever a model's id names a release, an installed copy, an origin or a line of the bill; and `origin` where the model derives from another, a release, a revision of a runtime or another model. `offer.yml` is its earlier name.

**The depth** of a model is its deeper records and the aspects of its records, part of the model like any record, with no folder of its own: a file of the depth lies anywhere in the model outside its element folders, `loops/` and `state/`, holds `items:`, cut as the maker likes, and is known by that content, never by its path; `enhanced/` is an earlier place of its files. An item is either **a deeper record** in this grammar, whose `parent` chain reaches a record outside the depth, with the id `<kind>:<slug>`, or **an aspect** of a record or step: `of` (`<kind>:<slug>` or `value-stream:<stream>/<step>`), `aspect`, and `slug` only where a record has several of one aspect, with the id `<of>~<aspect>[:<slug>]`. A target that does not resolve is a gap. A kind adds an aspect only through a specification of its own (R20).

| Aspect | On | Required | Optional |
|---|---|---|---|
| `measure` | a value stream or a step | `slug`, `title`, `type` (`outcome`, `process`, `structure`), `definition`, `unit`, `direction` (`higher-is-better`, `lower-is-better`, `target`) | `numerator`, `denominator`, `data` (entities it reads), `computable` |
| `pattern` | a family (`family:<f>`, where a stream names it), a value stream, a step, a capability or an entity | `context`, `problem`, `solution` | `forces`, `implementation`, `consequences`, `related` (each `rel` and `target`), `binds` |
| `system-of-record` | an entity | `system` (a solution of the model; else a gap) | `also_held_in` (solutions), `exchange` and `record` (each `standard`, `structure`, `note`), `binds`, `notes` |

An aspect `pattern` is bound to one record and deterministic; it is no pattern of a library (LIBRARY-PATTERNS). Only a `system-of-record` names a public, global specification.

**A binding** is a field of a record that names another, and its identity is derived, with no catalogue of its own: `solution:lending-ledger#carries:loan-handling`, or for a step `value-stream:lending/hand-out#entities:tool`. **A changed binding** is one identity removed and another added. Moving loan handling to a new solution removes `solution:lending-ledger#carries:loan-handling` and adds `solution:loan-app#carries:loan-handling`. `check_model.py --bindings` lists them, so two revisions can be compared.

**Accountability** set to `body:<slug>` resolves to the `accountable` of that Body's steward Post, `<body>.steward`. Where the Body has none, it resolves to the Body it is `part_of`, until a human is reached. A cycle, an outermost Body without a steward Post, or a Body not in the model is a gap: the accountability is held outside the model, or not yet stated.

**An address** names `from` (a reference to what refers: a path, `owner/repo@rev:path` or a URL), `to` (a node: its `kind` and `slug`, a step as `<stream>/<step>`), a `weight` from 0 to 1, a `status` (`proposed`, `ratified`, `rejected`) and its `source`, meaning the method (`machine`, `curated`, `human`). A target the grammar cannot hold, such as a family that does not exist, is a **contradiction** and fails. A target this model does not hold yet is an **absence** and a gap. Only a ratified address to a held target counts as recognised.

**Two rules keep the families universal.** A family is broad enough to hold all of its streams, across every stakeholder and asset. A family is a function the commons performs, and a quality the whole embodies (resilience, justice, vitality) is never a family or a dimension.

## 6 · Checks

`tools/check_model.py <model>` reads a model, either one file with `records` or a folder of record files. It reports **fail**, **should** or **gap**, and exits with 1 only on a fail. **A green check describes the model; it grants no authority to act.** Its fixtures are in `tools/tests/model/`.

| Check | Tests |
|---|---|
| `schema` | the model validates against the schema, its loops included (R1, R3, R5, R8, R9, R16, R18) |
| `slugs` | no slug appears twice within a kind (R2) |
| `family` | a stream's written dimension agrees with its family's (R4) |
| `bindings` | every binding resolves, an entity's relations, `reference(…)` attributes, a step's `serves` and a touchpoint's `at` among its journey's steps included; what names nothing yet, an empty list or an absent `holds` is a gap (R10); a journey's `mirrors` and a touchpoint's `steps` are an earlier layout, a gap; without `--extension`, a capability, entity or solution no step uses and a touchpoint no step serves are gaps (R9, R28); with `--catalogue` (earlier `--extension`), a missing required field fails, except a Body's `mandate` and a Post's `held_by`, which are gaps (R28); a loop's `keeps` resolves to a record, step, family or dimension, and a missing `carried_by` is a gap (R10) |
| `binding-ids` | no derived binding identity appears twice (R22) |
| `capability-map` | parents one level up; steps and solutions bind L3; Bodies hold L0 to L3; a Post that holds capabilities fails; an L3 that no step binds is a gap, except with `--catalogue`, where it stands in the catalogue (R6, R7, R14, R28) |
| `no-persons` | no e-mail address or telephone number anywhere, and identifiers only in a Post (R11) |
| `kinds-apart` | no slug is both a stakeholder and an entity (R1) |
| `bodies` | no Body is part of itself through its `part_of` chain, several may be outermost; a Body whose Posts are all held by agents fails, and one with no Post held by a human yet, or with `mandate: null`, is a gap (R13) |
| `accountable` | a Post's Body resolves, and a `body:` accountability resolves to a human; a cycle, an open end or accountability outside the model is a gap, and so is a Post nobody serves now (R15) |
| `safeguards` | an agent-only Post carries all four safeguards (R17) |
| `addresses` | an address's target resolves to a node of its kind; a contradiction fails and an absence is a gap (R18) |
| `coherence` | a touchpoint's written stakeholder is its journey's (R9) |
| `shells` | shells only where R19 allows them, and on every stakeholder (R19) |
| `canon` | the families equal those of the canon data, `specs/value-creation-canon.yml` in the Commons model, when it is at hand (R21) |
| `catalogue` | with `--catalogue`: every kind of record whole, nothing bound that the model does not hold; each of the thirteen families no stream reaches a gap of the maker; every item of the depth reaches or resolves to a record, with a stable id (R28); a starting set marked and holding every capability its streams bind, every stream in its family's `order` and only those, else a should (R29) |
| `variants` | with `--catalogue`, for a model with `variant`, against the other variants of its domain where they are at hand, else a gap: the variant it comes after is one of them and no other comes after the same one; a slug two variants hold names the same kind, a stream the same family; a Body a shared record names that the variant does not hold is a stakeholder in it (R30, R31) |
| `review` | a reading by the human accountable for this specification's mandate, against the Why of R3, R20 and R27 |

## 7 · Example

**Minimal:** one value stream with one step. Its capabilities and its entities are not yet known, so the check reports two gaps and no fail. A step that serves no touchpoint is work inside the commons, and no gap:

```yaml
records:
  - kind: value-stream
    slug: grow-and-share
    title: Grow and share
    family: demand-to-fulfillment
    steps:
      - {slug: sow, title: Sow, capabilities: [], entities: []}
```

**Complete:** [a neighbourhood tool library](examples/model/tool-library.yml), with every element, both halves of its exchange, a capability map from L0 to L3, two Bodies (the outermost with `part_of: null`) and three Posts (a steward, and one served by an agent with its safeguards, accountable to its Body), and one address. The check reports 0 fail, 0 should and 0 gaps.

## 8 · Decision log

| Date | Kind | Decision | Word |
|---|---|---|---|
| 2026-10-26 | commissioned | Commons MODEL, the grammar of any commons, comes second of the eight, after SPECIFICATION; later iteration is expected | commons.o#88, opened on the word of the human accountable |
| 2026-10-26 | adopted | Adopted after six points: derived binding identities, accountability ending in a human, addresses with a source and resolving targets, the step address pattern, an absent `holds` as a gap, `part_of: null` stated and shown; and a green check | Holger, commons.o#88, comment 6414397147 |
| 2026-10-26 | revised | **Draft, contingent on the probe of commons.o#90 and not decided:** the record fields `adopted_from` and `start` (part 5); `essential`, the commons' own mark of a record that carries it, asked for by the Model Engine for Part II (6422822870); R28, the archetypes of an extension leave open what the commons binds (D4-CE's P2 of the probe) | Holger, commons.o#90 (the principle, contingent on the probe 6421206970; not yet decided) |
| 2026-10-29 | revised | R13: a Body is a council with at least one Post held by a human; a Body held by agents only fails, one without a human Post yet is a gap (part 6). Adopted 29 October 2026 ([commons.o#98, comment 6505618412](https://github.com/Commons-Engineering/commons.o/issues/98#issuecomment-6505618412)) | Holger, commons.o#100 (opening, verbatim: *"ist immer ein Gremium mit mindestens einem human-post"*) |
| 2026-10-29 | revised | The serving kind `machine` is renamed `agent`, in the grammar, its schema, its checks and every fixture (R13, R16, R17, part 5); an address's `source: machine` names a method and stays. Adopted 29 October 2026 ([commons.o#98, comment 6505618412](https://github.com/Commons-Engineering/commons.o/issues/98#issuecomment-6505618412)) | Holger, commons.o#100, comment 6495768947 (F4: *"ja, agent wird sich vermutlich als gebräuchlich durchsetzen"*) |
| 2026-11-02 | revised | **Written for adoption, not yet adopted.** From the end-to-end run of commons.o#109 and Holger's words on it, then lightened by weight: R28, an archetype holds every required field but a Body's `mandate` and a Post's `held_by`, the commons' own; what an offer holds and no step uses is no gap, while in a commons a capability, entity, solution or touchpoint no step uses is one; R14, only a Body holds capabilities; R13, several outermost Bodies; R9 and part 5, the stakeholder side on its own, a journey's own steps with a touchpoint `at` one of them, and a stream step's `serves` the one tie, the entity's shape as grammar; R12 merged into R1, R23 into R15, R24 into R18, R25 into R9, R26 into R3; the carry-over moved to `carry-over/model.md` | commons.o#109: forms part G 6562746253, P 6566646051, the bill 6569529481; Holger 6570298244, 6571926000, 6572334454 and 6573304095; D1 6571965126 and 6573363749; adoption is Holger's |
| 2026-11-02 | adopted | The revision of commons.o#109 adopted as merged in `56cbfd5`: the three acts, the library, every kind offered whole with the stakeholder side on its own, the weight pass, and Holger's words of that day folded in | Holger, [commons.o#109, comment 6574646061](https://github.com/Commons-Engineering/commons.o/issues/109#issuecomment-6574646061) (*"sonst ja"*) |

| 2026-11-03 | revised | **Written for adoption, not yet adopted.** From the models note of commons.o#109 and the migration to 0.4.0 (#110): R1, a model is records and the loops that keep them true, a loop a record kind beside the Post (Holger, decision 1, 6602880861); R10, a loop's `keeps`; R20, a model and a kind add, neither redefines; R28 widened to the catalogue, from EXTENSION R7 and R8; **R29** new, from EXTENSION R24; part 5, `origin` for `adopted_from` (decision 30), `model.yml` for `offer.yml`, the loop's row, and the depth with its aspects from EXTENSION part 5; part 6, the check `catalogue` and the mode `--catalogue`; EXTENSION dissolves (Holger 6603340647) | commons.o#109, the models note (`d1-ce/models-note` `b1bfb7d`), Holger 6602880861, 6603162848, 6603340647 and 6610425987; adoption is Holger's |
| 2026-11-04 | adopted | The revision of 3 November adopted with the merge of structure 0.4.0 into `main` (A1, A2) | Holger, commons.o#110, comment 6625957149 |
| 2026-11-07 | revised | **Drafted for Commons 0.3.0, not yet adopted.** T1, no tiers: the depth part of the model like any record, with no folder of its own, known by its `items:` (VR-5); **R30** new, a domain's variants under its one id, each with a name of its own, `<model>/<variant>` wherever a model's id is (VN-a), with `variant` in `model.yml`, its schema and the check `variants`; **R31** new, a variant holds whole what its shared records bind, a Body only another variant holds a stakeholder there (F-4 b), the rest on the shelf (S-a); part 5, a record retired by where it stands, never by a field (RS-a); the terms without `tier`, `essentials` and `enhanced`, with `variant` | Holger, commons.core#110, comments 6626305178, 6626536835 and 6627102753 (V1–V3, T1, N1, VR-1 to VR-6), 6705288611 (F-4 b, F-5 a) and 6706321253 (S-a, VN-a, PO-a, RS-a), as `instance/workshop/run-110/commons-030.md` lists; adoption is Holger's |
| 2026-11-15 | revised | **Written for adoption, not yet adopted.** The check `canon` names where the canon data lies: `specs/value-creation-canon.yml`, released with the Commons model, so that every installed CORE has it at hand (R21) | D4-CE, from the Office's newcomer run, commons.core#110 (GO-3) |

What this specification supersedes, and what it carries of it, is in [`carry-over/model.md`](carry-over/model.md).
