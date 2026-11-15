---
id: life-model
title: Life model — the fields of its records
status: draft
lang: en
touches: [model]
terms: [model, commons]
schema: life-model.schema.json
check: check_life_model.py
supersedes: []
---

# Life model

*What the model of `life.core` adds to MODEL's records (MODEL R20). A draft.*

## 1 · Goal

A life commons builds from records that say more than MODEL's grammar holds, such as which family a stakeholder or a journey runs through, whether a relation succeeds by ending, how a touchpoint is met and what kind of other could hold a Body. This specification declares those fields once, with their shape, so that a commons can read, check and build from them without guessing.

## 2 · Boundary

**Belongs here:** the fields of the model's records beyond MODEL's, per kind; that a Body of the model is a form.

**Does not belong here:**

| Matter | Where it belongs |
|---|---|
| the fields every record has, and the grammar | MODEL |
| `binds`, the release, the research in `knowledge/` | CORE-KNOWLEDGE (`core-knowledge` R19, R20), LIBRARY (`library` R10, R19) |
| whether a Body forms and who holds it in a commons that builds from it | FLOW (`flow-bodies` R19, R22) |

It extends MODEL and redefines nothing of it (`model` R20). Its fields follow the Life pack's own shapes where they differ from the health and business models'. Where the three agree, the field is written alike, so that the models stay comparable.

## 3 · Terms

No new terms.

## 4 · Requirements

| ID | Level | Requirement | Why | Check |
|---|---|---|---|---|
| R1 | MUST | Every field a record of the model carries is MODEL's, `binds` (`core-knowledge` R20), or declared for its kind in part 5. | A field nobody declared is read differently by every commons that builds from it. | fields |
| R2 | MUST | A declared field has the shape the schema `life-model.schema.json` gives it. | Shape is what lets a tool compare a record built from it with its origin. | schema |
| R3 | MUST | A Body of the model is a form: it names no holder. | Who holds a Body of a life is the person's own evidence, never the model's. | forms |
| R4 | MUST | A touchpoint's `journey` lists it in its `stages`, and a value exchange's `touchpoint` lists it in its `exchanges`. | MODEL's one binding is one of the model's many; a journey that does not pass through its touchpoint states a path no one walks. | bindings |

## 5 · Structure

The schema is `life-model.schema.json`, next to this file: one definition per kind under `$defs`, holding only the fields this model adds.

| Kind | Fields beyond MODEL |
|---|---|
| every kind | `summary`: what the record is, in a few sentences, where the pack gives one |
| `value-stream` | `trigger`, `outcome`, `stakeholders` |
| `stakeholder` | `nature` (`person`, `organisation`, `group`, `agent`, `more-than-human`), `stance` (`served`, `serving`, `both`), `via` (the family it runs through), `represented_by`, `dissolves` (whether the relation succeeds by ending), `note` |
| `entity` | `type`, `attributes`, `states`, `relations` |
| `journey` | `stages`, `via` |
| `touchpoint` | `medium` (`place`, `moment`, `channel`, `document`, `gathering`), `mode` (`in-person`, `spoken`, `written`, `digital`, `shared-presence`), `exchanges` |
| `value-exchange` | `between`, `note` |
| `solution` | `role` (`system-of-record`, `system-of-engagement`, `system-of-insight`, `person`, `agent`, `institution`), `sovereignty` (`owned`, `hosted`, `third-party`, `held-by-another`), `holds` |
| `body` | `via`, `could_be_held_by` (the kinds of other who could hold it, never an individual) |

A value exchange's MODEL `touchpoint` is the one place where it is completed, and a touchpoint's `exchanges` names every exchange that meets there. A journey's `stages` name every touchpoint it passes through, and a touchpoint's MODEL `journey` the one it belongs to; the stakeholders met at a touchpoint are those of the journeys that pass through it (MODEL R9). A value exchange's `between` may name `self`, the life whose commons this is. A Body's place is MODEL's `part_of` (MODEL R13). The pack's thirteen seats hold capabilities, so each is a Body (MODEL R14); the life model holds no Post.

The pack's seat `kind` has no counterpart here, because the Life pack's seats carry none; *seat* is a rejected word for element 9. The pack's `held_by_self` names the holder, which a Body of the model never does (R3).

The starting set a life commons begins with is marked `start: true`: the eight streams of Perception to Mandate and every capability their steps bind (MODEL R29).

## 6 · Checks

`check_life_model.py <life.core>` runs the checks; it exits with 1 on a fail.

| Check | Tests |
|---|---|
| `fields` | every field of a record of the model is MODEL's, `binds` or declared for its kind (R1) |
| `schema` | every declared field validates against its kind's definition (R2) |
| `forms` | no Body of the model names a holder (R3) |
| `bindings` | each touchpoint stands in the stages of its `journey`, and each value exchange's `touchpoint` names it among its `exchanges` (R4) |
| `refs` | every rule this specification cites, outside its decision log, resolves to a rule of the installed Commons model's specifications |

## 7 · Example

**Minimal:** a Body of the model, one of the thirteen a person holds, a form without a holder:

```yaml
kind: body
slug: the-one-who-decides
title: The One Who Decides
summary: what this life commits to and what it declines
holds:
- purpose-and-priorities
- values-and-choices
- limits-and-boundaries
- many-footings
part_of: null
form: organisational-unit
via: purpose-to-portfolio
could_be_held_by:
- a partner, for what is decided together
- an appointed representative, when the person can no longer decide
```

**Complete:** this CORE's `models/emulation/life/`.

## 8 · Decision log

| Date | Kind | Decision | Word |
|---|---|---|---|
| 2026-11-02 | commissioned | the fields beyond MODEL of the life offer, as the Life pack 1.0.0 shapes its records: the business offer's where the packs agree, and the Life pack's own `via`, `dissolves`, `note`, `mode`, `sovereignty` and `could_be_held_by` where they differ; a touchpoint's `medium` and a solution's `role` take the Life pack's vocabularies; no Post | the steward of the Commons; the Federation's Office; the maker's domain Body |
| 2026-11-02 | revised | package A, prepared and not released: the five kinds of the Life pack 1.0.0 whole in the offer, 804 records carried and never reworded (21 stakeholders, 568 capabilities from L0 to L3, 134 entities, 68 solutions, 13 Bodies), in the fields of part 5, and the 13 family loops. The pack gives a stakeholder no title: its title is its slug, words capitalised, and no summary is written for it. MODEL R12 (kinds-apart): the 15 entities named as stakeholders are the relation, as the pack's note on element 1 says, and are written `<slug>-relation` with every reference following. The 13 element-9 records of the pack hold capabilities, so each is a Body (MODEL R14): outermost, `organisational-unit`, with its `via` and `could_be_held_by`; `held_by_self` names the holder and is not carried (R3); there is no Post. The rejected word of the glossary for a commons stands in this pack for the dwelling, and gives way to *home*: five slugs are renamed and their references follow. In the loops the trigger reads *activated, adapted or not selected*, and `adopted: true` leaves. Content choices of the Federation, collected for the steward's word | the steward of the Commons; the Federation's Office; the maker's domain Body |
| 2026-11-02 | revised | package B, first family, prepared and not released: Perception to Mandate whole from the pack, its eight value streams with their 47 steps, the four journeys that walk them, 9 touchpoints and 19 value exchanges, in MODEL's layout (22 ties as `serves` on the new steps), each exchange without `at`, and its streams in the offer's `order` in the maker's sequence. Form 2: of 0 touchpoints whose journeys score alike, each `journey` is the journey of this family, then the pack's first; form 1: of 5 value exchanges with several offered places, each `touchpoint` is the first the pack names among those on the journey of a party to it. Every choice is listed in the Federation's record of the package | the Federation's Office's brief, on a question of the steward of the Commons; the maker's domain Body |
| 2026-11-02 | revised | package B, second family, prepared and not released: Purpose to Portfolio whole from the pack, its six value streams with their 36 steps, the two journeys that walk them, 3 touchpoints and 8 value exchanges, in MODEL's layout (5 ties as `serves` on the new steps, and 2 on offered steps of one stream that new touchpoints serve), each exchange without `at`, and its streams in the offer's `order` in the maker's sequence. Form 2: of 0 touchpoints whose journeys score alike, each `journey` is the journey of this family, then the pack's first; form 1: of 1 value exchanges with several offered places, each `touchpoint` is the first the pack names among those on the journey of a party to it. Every choice is listed in the Federation's record of the package | the Federation's Office's brief, on a question of the steward of the Commons; the maker's domain Body |
| 2026-11-02 | revised | package B, third family, prepared and not released: Value to Sustainability whole from the pack, its six value streams with their 36 steps, the three journeys that walk them, 9 touchpoints and 3 value exchanges, in MODEL's layout (17 ties as `serves` on the new steps, and 2 on offered steps of two streams that new touchpoints serve), each exchange without `at`, and its streams in the offer's `order` in the maker's sequence. Form 2: of 0 touchpoints whose journeys score alike, each `journey` is the journey of this family, then the pack's first; form 1: of 2 value exchanges with several offered places, each `touchpoint` is the first the pack names among those on the journey of a party to it. Every choice is listed in the Federation's record of the package | the Federation's Office's brief, on a question of the steward of the Commons; the maker's domain Body |
| 2026-11-02 | revised | package B, fourth family, prepared and not released: Portfolio to System whole from the pack, its five value streams with their 31 steps, the five journeys that walk them, 9 touchpoints and 3 value exchanges, in MODEL's layout (32 ties as `serves` on the new steps, and 5 on offered steps of three streams that new touchpoints serve), each exchange without `at`, and its streams in the offer's `order` in the maker's sequence. Form 2: of 0 touchpoints whose journeys score alike, each `journey` is the journey of this family, then the pack's first; form 1: of 1 value exchanges with several offered places, each `touchpoint` is the first the pack names among those on the journey of a party to it. Every choice is listed in the Federation's record of the package | the Federation's Office's brief, on a question of the steward of the Commons; the maker's domain Body |
| 2026-11-02 | revised | package B, fifth family, prepared and not released: Participant to Community whole from the pack, its ten value streams with their 61 steps, the 11 journeys that walk them, 22 touchpoints and 7 value exchanges, in MODEL's layout (85 ties as `serves` on the new steps, and 2 on offered steps of two streams that new touchpoints serve), each exchange without `at`, and its streams in the offer's `order` in the maker's sequence. Form 2: of 3 touchpoints whose journeys score alike, each `journey` is the journey of this family, then the pack's first; form 1: of 4 value exchanges with several offered places, each `touchpoint` is the first the pack names among those on the journey of a party to it. Every choice is listed in the Federation's record of the package | the Federation's Office's brief, on a question of the steward of the Commons; the maker's domain Body |
| 2026-11-02 | revised | package B, sixth family, prepared and not released: Collaboration to Automation whole from the pack, its six value streams with their 36 steps, the four journeys that walk them, 5 touchpoints and 4 value exchanges, in MODEL's layout (40 ties as `serves` on the new steps, and 3 on offered steps of two streams that new touchpoints serve), each exchange without `at`, and its streams in the offer's `order` in the maker's sequence. Form 2: of 1 touchpoints whose journeys score alike, each `journey` is the journey of this family, then the pack's first; form 1: of 0 value exchanges with several offered places, each `touchpoint` is the first the pack names among those on the journey of a party to it. Every choice is listed in the Federation's record of the package | the Federation's Office's brief, on a question of the steward of the Commons; the maker's domain Body |
| 2026-11-02 | revised | package B, seventh family, prepared and not released: Contributor to Succession whole from the pack, its six value streams with their 41 steps, the six journeys that walk them, 5 touchpoints and 0 value exchanges, in MODEL's layout (28 ties as `serves` on the new steps, and 5 on offered steps of five streams that new touchpoints serve), each exchange without `at`, and its streams in the offer's `order` in the maker's sequence. Form 2: of 2 touchpoints whose journeys score alike, each `journey` is the journey of this family, then the pack's first; form 1: of 0 value exchanges with several offered places, each `touchpoint` is the first the pack names among those on the journey of a party to it. Every choice is listed in the Federation's record of the package | the Federation's Office's brief, on a question of the steward of the Commons; the maker's domain Body |
| 2026-11-02 | revised | package B, eighth family, prepared and not released: Discovery to Usage whole from the pack, its six value streams with their 39 steps, the four journeys that walk them, 7 touchpoints and 4 value exchanges, in MODEL's layout (29 ties as `serves` on the new steps, and 5 on offered steps of four streams that new touchpoints serve), each exchange without `at`, and its streams in the offer's `order` in the maker's sequence. Form 2: of 2 touchpoints whose journeys score alike, each `journey` is the journey of this family, then the pack's first; form 1: of 3 value exchanges with several offered places, each `touchpoint` is the first the pack names among those on the journey of a party to it. Every choice is listed in the Federation's record of the package | the Federation's Office's brief, on a question of the steward of the Commons; the maker's domain Body |
| 2026-11-02 | revised | package B, ninth family, prepared and not released: Interest to Relationship whole from the pack, its four value streams with their 24 steps, the three journeys that walk them, 2 touchpoints and 0 value exchanges, in MODEL's layout (22 ties as `serves` on the new steps, and 4 on offered steps of four streams that new touchpoints serve), each exchange without `at`, and its streams in the offer's `order` in the maker's sequence. Form 2: of 0 touchpoints whose journeys score alike, each `journey` is the journey of this family, then the pack's first; form 1: of 0 value exchanges with several offered places, each `touchpoint` is the first the pack names among those on the journey of a party to it. Every choice is listed in the Federation's record of the package | the Federation's Office's brief, on a question of the steward of the Commons; the maker's domain Body |
| 2026-11-02 | revised | package B, tenth family, prepared and not released: Proposition to Audience whole from the pack, its five value streams with their 30 steps, the two journeys that walk them, 3 touchpoints and 0 value exchanges, in MODEL's layout (36 ties as `serves` on the new steps, and 4 on offered steps of three streams that new touchpoints serve), each exchange without `at`, and its streams in the offer's `order` in the maker's sequence. Form 2: of 0 touchpoints whose journeys score alike, each `journey` is the journey of this family, then the pack's first; form 1: of 0 value exchanges with several offered places, each `touchpoint` is the first the pack names among those on the journey of a party to it. Every choice is listed in the Federation's record of the package | the Federation's Office's brief, on a question of the steward of the Commons; the maker's domain Body |
| 2026-11-02 | revised | package B, eleventh family, prepared and not released: Demand to Fulfillment whole from the pack, its nine value streams with their 57 steps, the three journeys that walk them, 2 touchpoints and 0 value exchanges, in MODEL's layout (28 ties as `serves` on the new steps, and 1 on offered steps of one stream that new touchpoints serve), each exchange without `at`, and its streams in the offer's `order` in the maker's sequence. Form 2: of 0 touchpoints whose journeys score alike, each `journey` is the journey of this family, then the pack's first; form 1: of 0 value exchanges with several offered places, each `touchpoint` is the first the pack names among those on the journey of a party to it. Every choice is listed in the Federation's record of the package | the Federation's Office's brief, on a question of the steward of the Commons; the maker's domain Body |
| 2026-11-02 | revised | package B, twelfth family, prepared and not released: Source to Alliance whole from the pack, its four value streams with their 24 steps, the four journeys that walk them, 4 touchpoints and 2 value exchanges, in MODEL's layout (25 ties as `serves` on the new steps, and 4 on offered steps of three streams that new touchpoints serve), each exchange without `at`, and its streams in the offer's `order` in the maker's sequence. Form 2: of 0 touchpoints whose journeys score alike, each `journey` is the journey of this family, then the pack's first; form 1: of 0 value exchanges with several offered places, each `touchpoint` is the first the pack names among those on the journey of a party to it. Every choice is listed in the Federation's record of the package | the Federation's Office's brief, on a question of the steward of the Commons; the maker's domain Body |
| 2026-11-02 | revised | package B, thirteenth family, prepared and not released: Acquire to Retire whole from the pack, its six value streams with their 39 steps, the four journeys that walk them, 4 touchpoints and 1 value exchanges, in MODEL's layout (37 ties as `serves` on the new steps, and 16 on offered steps of 12 streams that new touchpoints serve), each exchange without `at`, and its streams in the offer's `order` in the maker's sequence. Form 2: of 2 touchpoints whose journeys score alike, each `journey` is the journey of this family, then the pack's first; form 1: of 0 value exchanges with several offered places, each `touchpoint` is the first the pack names among those on the journey of a party to it. Every choice is listed in the Federation's record of the package With it every family of the pack is offered. The four pack touchpoints no journey walks are carried as well, each in a stage of an offered journey: `away-message` in `find-it-held` of `hearing-a-limit`, `bank-app` in `see-enough-named` of `sharing-the-money`, `talking-about-the-end` in `give-it-a-form` of `putting-wishes-into-form`, `counselling-room` in `carry-part-of-it` of `standing-by-in-upheaval`; `counselling-room` by the rule, as a stage of that journey stands on a step it serves, and the other three chosen, since no stage stands on their steps; their steps state them in `serves` | the Federation's Office's brief, on a question of the steward of the Commons; the maker's domain Body |
| 2026-11-15 | revised | renamed under the names in force (0.4.0; complete renames, the Office, GO-3): life-offer becomes life-model with its schema and check; the head names the model and MODEL R20 in place of the earlier offer and EXTENSION R21, every rule cited resolves to Commons 0.3.0, and the check `refs` reads it; the glossary's words (*offer*, *activate*) give way to the model and building from it; the starting set of Perception to Mandate stated (MODEL R29; Holger 6892291098, RL-4b); the substance untouched | the Office of Commons Engineering; Holger, commons.core#110 |
