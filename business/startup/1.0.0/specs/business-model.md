---
id: business-model
title: Business model — the fields of its records
status: draft
lang: en
touches: [model]
terms: [model, commons]
schema: business-model.schema.json
check: check_business_model.py
supersedes: []
---

# Business model

*What the model of `business.core` adds to MODEL's records (MODEL R20). A draft.*

## 1 · Goal

A business commons builds from records that say more than MODEL's grammar holds, such as what triggers a value stream, what a stakeholder seeks and brings, and the states an entity passes through; this specification declares those fields once, with their shape, so that a commons can read, check and build from them without guessing.

## 2 · Boundary

**Belongs here:** the fields of the model's records beyond MODEL's, per kind; that a Body or Post of the model is a form.

**Does not belong here:**

| Matter | Where it belongs |
|---|---|
| the fields every record has, and the grammar | MODEL |
| `binds`, the release, the research in `knowledge/` | CORE-KNOWLEDGE (`core-knowledge` R19, R20), LIBRARY (`library` R10, R19) |
| whether a Body forms and who holds a Post in a commons that builds from it | FLOW (`flow-bodies` R19, R22) |

It extends MODEL and redefines nothing of it (`model` R20). Its fields are the health model's, so that the two models stay comparable; it holds no jurisdiction overlay, since the model binds no source yet.

## 3 · Terms

No new terms.

## 4 · Requirements

| ID | Level | Requirement | Why | Check |
|---|---|---|---|---|
| R1 | MUST | Every field a record of the model carries is MODEL's, `binds` (`core-knowledge` R20), or declared for its kind in part 5. | A field nobody declared is read differently by every commons that builds from it. | fields |
| R2 | MUST | A declared field has the shape the schema `business-model.schema.json` gives it. | Shape is what lets a tool compare a record built from it with its origin. | schema |
| R3 | MUST | A Body or Post of the model is a form: it names no holder, and a Post of the model carries no `held_by`. | Whether a Body forms and who serves a Post is for the commons that builds from it to decide, never for the model. | forms |
| R4 | MUST | A touchpoint's `journey` lists it in its `stages`, and a value exchange's `touchpoint` lists it in its `exchanges`. | MODEL's one binding is one of the model's many; a journey that does not pass through its touchpoint states a path no one walks. | bindings |

## 5 · Structure

The schema is `business-model.schema.json`, next to this file: one definition per kind under `$defs`, holding only the fields this model adds.

| Kind | Fields beyond MODEL |
|---|---|
| every kind | `summary`: what the record is, in a few sentences |
| `value-stream` | `trigger`, `outcome`, `stakeholders` |
| `stakeholder` | `nature` (`person`, `organisation`, `group`, `agent`, `more-than-human`), `legal_form`, `stance`, `seeks`, `brings`, `represented_by` |
| `entity` | `type`, `attributes`, `states`, `relations` |
| `journey` | `stages` |
| `touchpoint` | `medium` (`encounter`, `artefact`, `channel`, `place`), `exchanges` |
| `value-exchange` | `between` |
| `solution` | `role`, `holds` |
| `body` | `type` (`board`, `committee`, `management`, `function`, beside MODEL's `form`) |
| `post` | `type` (`executive`, `role`) |

A value exchange's MODEL `touchpoint` is the one place where it is completed, and a touchpoint's `exchanges` names every exchange that meets there. A journey's `stages` name every touchpoint it passes through, and a touchpoint's MODEL `journey` the one it belongs to. A Body of the model's place is MODEL's `part_of`, and a Post of the model's line MODEL's `accountable`, as `body:<slug>`; neither is written twice. A Post holds no capability: its Body holds them (MODEL R14), and the Post answers inside it by its `responsibility`.

The pack's `standing` on a stakeholder is written `legal_form`, because *standing* is the word of a claim's standing and of the stakeholder register (CORE-KNOWLEDGE R4, R12). Its seat `kind` is written `type`, because *seat* is a rejected word for element 9.

## 6 · Checks

`check_business_model.py <business.core>` runs the checks; it exits with 1 on a fail.

| Check | Tests |
|---|---|
| `fields` | every field of a record of the model is MODEL's, `binds` or declared for its kind (R1) |
| `schema` | every declared field validates against its kind's definition (R2) |
| `forms` | no Body or Post of the model names a holder (R3) |
| `bindings` | each touchpoint stands in the stages of its `journey`, and each value exchange's `touchpoint` names it among its `exchanges` (R4) |

## 7 · Example

**Minimal:** a Post of the model, a form without a holder:

```yaml
kind: post
slug: data-steward
title: Data Steward
summary: Answers for the definitions, quality and proper use of the data of one domain.
of: data-and-analytics
responsibility: Answers for the definitions, quality and proper use of the data of one domain.
accountable: body:data-and-analytics
type: role
```

**Complete:** this CORE's emulation, `models/emulation/business/`.

## 8 · Decision log

| Date | Kind | Decision | Word |
|---|---|---|---|
| 2026-11-02 | commissioned | the fields beyond MODEL of the business offer, as the health offer declares them (health-offer part 5), without its jurisdiction overlays; a Post's `type` is `executive` or `role`, the two kinds of the pack's Posts | the maker |
| 2026-11-02 | revised | package A, prepared and not released: the five kinds of the Business pack 2.0.0 whole in the offer, 1,381 records carried and never reworded (78 stakeholders, 899 capabilities from L0 to L3, 239 entities, 69 solutions, 54 Bodies, 42 Posts), in the fields of part 5 and the four forms, and the 13 family loops. Repairs only: the rejected words of the glossary (`specs/glossary/rejected.yml`) give way to the words it names, *commons*, *board* or *post* for element 9, *inquiry* for a prospective customer, *level* and *Commons Core*, and an investor of private equity is a *private equity firm*; every slug that carried one is renamed and every reference follows, so that the two governing Bodies are `governing-board` and `executive-board`; MODEL R12 (kinds-apart): the entities `supplier`, `partner`, `employee` and `shareholder` are written `supplier-organisation`, `partner-organisation`, `employee-record` and `shareholder-record`; an entity's pack code `id` is not carried. An element-9 record of the pack of kind board, committee, management or function is a Body, any other a Post; `owners-meeting` and `works-council` are outermost; the seven executives are of `executive-board` and accountable to the Body they answer to, `family-steward` and `stream-operator` are of `transformation-and-portfolio-office`; a Post's `responsibility` is its summary's first sentence. Form P: 3 capabilities a Post held and its Body did not hold through its subtree move into that Body. In the loops the trigger reads *activated, adapted or not selected*, and `adopted: true` leaves. Content choices of the Federation, collected for the maker's word at release | the maker |
| 2026-11-02 | revised | package B, first family, prepared and not released: Perception to Mandate whole from the pack, its six value streams with their 43 steps, the 18 journeys that walk them, 70 touchpoints and 152 value exchanges, in MODEL's layout (125 ties as `serves` on the new steps), each exchange without `at`, and its streams in the offer's `order` in the maker's sequence. Form 2: of 16 touchpoints whose journeys score alike, each `journey` is the journey of this family, then the pack's first; form 1: of 45 value exchanges with several offered places, each `touchpoint` is the first the pack names among those on the journey of a party to it. Every choice is listed in | the maker |
| 2026-11-02 | revised | package B, second family, prepared and not released: Purpose to Portfolio whole from the pack, its five value streams with their 32 steps, the 15 journeys that walk them, 26 touchpoints and 25 value exchanges, in MODEL's layout (76 ties as `serves` on the new steps), each exchange without `at`, and its streams in the offer's `order` in the maker's sequence. Form 2: of 6 touchpoints whose journeys score alike, each `journey` is the journey of this family, then the pack's first; form 1: of 11 value exchanges with several offered places, each `touchpoint` is the first the pack names among those on the journey of a party to it. Every choice is listed in | the maker |
| 2026-11-02 | revised | package B, third family, prepared and not released: Value to Sustainability whole from the pack, its eight value streams with their 54 steps, the 24 journeys that walk them, 36 touchpoints and 30 value exchanges, in MODEL's layout (107 ties as `serves` on the new steps), each exchange without `at`, and its streams in the offer's `order` in the maker's sequence. Form 2: of 3 touchpoints whose journeys score alike, each `journey` is the journey of this family, then the pack's first; form 1: of 13 value exchanges with several offered places, each `touchpoint` is the first the pack names among those on the journey of a party to it. Every choice is listed in | the maker |
| 2026-11-02 | revised | package B, fourth family, prepared and not released: Portfolio to System whole from the pack, its nine value streams with their 59 steps, the 27 journeys that walk them, 51 touchpoints and 31 value exchanges, in MODEL's layout (107 ties as `serves` on the new steps), each exchange without `at`, and its streams in the offer's `order` in the maker's sequence. Form 2: of 17 touchpoints whose journeys score alike, each `journey` is the journey of this family, then the pack's first; form 1: of 17 value exchanges with several offered places, each `touchpoint` is the first the pack names among those on the journey of a party to it. Every choice is listed in | the maker |
| 2026-11-02 | revised | package B, fifth family, prepared and not released: Participant to Community whole from the pack, its five value streams with their 31 steps, the 12 journeys that walk them, 30 touchpoints and 11 value exchanges, in MODEL's layout (65 ties as `serves` on the new steps), each exchange without `at`, and its streams in the offer's `order` in the maker's sequence. Form 2: of 1 touchpoints whose journeys score alike, each `journey` is the journey of this family, then the pack's first; form 1: of 6 value exchanges with several offered places, each `touchpoint` is the first the pack names among those on the journey of a party to it. Every choice is listed in | the maker |
| 2026-11-02 | revised | package B, sixth family, prepared and not released: Collaboration to Automation whole from the pack, its seven value streams with their 47 steps, the 21 journeys that walk them, 40 touchpoints and 21 value exchanges, in MODEL's layout (82 ties as `serves` on the new steps), each exchange without `at`, and its streams in the offer's `order` in the maker's sequence. Form 2: of 12 touchpoints whose journeys score alike, each `journey` is the journey of this family, then the pack's first; form 1: of 12 value exchanges with several offered places, each `touchpoint` is the first the pack names among those on the journey of a party to it. Every choice is listed in | the maker |
| 2026-11-02 | revised | package B, seventh family, prepared and not released: Contributor to Succession whole from the pack, its ten value streams with their 71 steps, the 27 journeys that walk them, 69 touchpoints and 33 value exchanges, in MODEL's layout (132 ties as `serves` on the new steps), each exchange without `at`, and its streams in the offer's `order` in the maker's sequence. Form 2: of 15 touchpoints whose journeys score alike, each `journey` is the journey of this family, then the pack's first; form 1: of 21 value exchanges with several offered places, each `touchpoint` is the first the pack names among those on the journey of a party to it. Every choice is listed in | the maker |
| 2026-11-02 | revised | package B, eighth family, prepared and not released: Discovery to Usage whole from the pack, its nine value streams with their 62 steps, the 27 journeys that walk them, 56 touchpoints and 41 value exchanges, in MODEL's layout (131 ties as `serves` on the new steps), each exchange without `at`, and its streams in the offer's `order` in the maker's sequence. Form 2: of 13 touchpoints whose journeys score alike, each `journey` is the journey of this family, then the pack's first; form 1: of 20 value exchanges with several offered places, each `touchpoint` is the first the pack names among those on the journey of a party to it. Every choice is listed in | the maker |
| 2026-11-02 | revised | package B, ninth family, prepared and not released: Interest to Relationship whole from the pack, its four value streams with their 29 steps, the 12 journeys that walk them, 25 touchpoints and 12 value exchanges, in MODEL's layout (73 ties as `serves` on the new steps), each exchange without `at`, and its streams in the offer's `order` in the maker's sequence. Form 2: of 7 touchpoints whose journeys score alike, each `journey` is the journey of this family, then the pack's first; form 1: of 6 value exchanges with several offered places, each `touchpoint` is the first the pack names among those on the journey of a party to it. Every choice is listed in | the maker |
| 2026-11-02 | revised | package B, tenth family, prepared and not released: Proposition to Audience whole from the pack, its six value streams with their 41 steps, the 18 journeys that walk them, 26 touchpoints and 16 value exchanges, in MODEL's layout (70 ties as `serves` on the new steps), each exchange without `at`, and its streams in the offer's `order` in the maker's sequence. Form 2: of 7 touchpoints whose journeys score alike, each `journey` is the journey of this family, then the pack's first; form 1: of 7 value exchanges with several offered places, each `touchpoint` is the first the pack names among those on the journey of a party to it. Every choice is listed in | the maker |
| 2026-11-02 | revised | package B, eleventh family, prepared and not released: Demand to Fulfillment whole from the pack, its seven value streams with their 44 steps, the 21 journeys that walk them, 38 touchpoints and 12 value exchanges, in MODEL's layout (97 ties as `serves` on the new steps), each exchange without `at`, and its streams in the offer's `order` in the maker's sequence. Form 2: of 8 touchpoints whose journeys score alike, each `journey` is the journey of this family, then the pack's first; form 1: of 7 value exchanges with several offered places, each `touchpoint` is the first the pack names among those on the journey of a party to it. Every choice is listed in | the maker |
| 2026-11-02 | revised | package B, twelfth family, prepared and not released: Source to Alliance whole from the pack, its four value streams with their 25 steps, the 11 journeys that walk them, 27 touchpoints and 11 value exchanges, in MODEL's layout (45 ties as `serves` on the new steps), each exchange without `at`, and its streams in the offer's `order` in the maker's sequence. Form 2: of 11 touchpoints whose journeys score alike, each `journey` is the journey of this family, then the pack's first; form 1: of 5 value exchanges with several offered places, each `touchpoint` is the first the pack names among those on the journey of a party to it. Every choice is listed in | the maker |
| 2026-11-02 | revised | package B, thirteenth family, prepared and not released: Acquire to Retire whole from the pack, its four value streams with their 24 steps, the 12 journeys that walk them, 23 touchpoints and 9 value exchanges, in MODEL's layout (51 ties as `serves` on the new steps, and 2 on offered steps of two streams that new touchpoints serve), each exchange without `at`, and its streams in the offer's `order` in the maker's sequence. Form 2: of 7 touchpoints whose journeys score alike, each `journey` is the journey of this family, then the pack's first; form 1: of 6 value exchanges with several offered places, each `touchpoint` is the first the pack names among those on the journey of a party to it. Every choice is listed in With it every family of the pack is offered. The one pack touchpoint no journey walks, `public-tender`, is carried as well, placed in the stage `receive-an-honest-offer` of `customer-journey`, the offered journey whose stage stands on a step it serves and whose stakeholder is party to its exchanges; its steps state it in `serves` | the maker |
| 2026-11-02 | revised | two product names leave the records, carried by the pack and found in the reviews' checks: the capability the pack names after an AI product is written `ai-assistant-integration` (*AI Assistant Integration*), with its references in one solution and two value streams, and `prompt-engineering-as-governance` names *the AGENT.md and agent mandates*, the commons' own agent file, in place of an AI client's. Repairs, not rewording; collected for the maker's word at release | the maker |
| 2026-11-15 | revised | the spec in the names and rules in force of 0.3.0: `business-model` for `business-offer`, the model for the offer, build for activate and adopt, and the rules EXTENSION held cited where they now stand (`model` R20, `core-knowledge` R19, R20, `library` R10, R19); the substance unchanged | the maker |
