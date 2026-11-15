---
id: health-model
title: Health model — the fields of its records, and its jurisdiction overlays
status: draft
lang: en
touches: [model]
terms: [model, commons]
schema: health-model.schema.json
check: check_health_model.py
supersedes: []
---

# Health model

*What the model of `health.core` adds to MODEL's records, and how it binds a record to a jurisdiction (MODEL R20; `core-knowledge` R19, R20 for the sources of standards and law it binds). A draft.*

## 1 · Goal

A health commons builds from records that say more than MODEL's grammar holds, such as what triggers a value stream, what a stakeholder seeks and brings, and the states an entity passes through, and it lives under national law that binds some records and not others; this specification declares those fields once, with their shape, and states how a record is bound in one jurisdiction, so that a commons can read, check and build from them without guessing.

## 2 · Boundary

**Belongs here:** the fields of the model's records beyond MODEL's, per kind; the jurisdiction overlays and their bindings; that a Body or Post of the model is a form.

**Does not belong here:**

| Matter | Where it belongs |
|---|---|
| the fields every record has, and the grammar | MODEL |
| `binds`, the release, the research in `knowledge/` | CORE-KNOWLEDGE (`core-knowledge` R19, R20), LIBRARY (`library` R10, R19) |
| whether a Body forms and who holds a Post in a commons that builds from it | FLOW (`flow-bodies` R19, R22) |

It extends MODEL and redefines nothing of it (`model` R20).

## 3 · Terms

No new terms.

## 4 · Requirements

| ID | Level | Requirement | Why | Check |
|---|---|---|---|---|
| R1 | MUST | Every field a record of the model carries is MODEL's, `binds` (`core-knowledge` R20), or declared for its kind in part 5. | A field nobody declared is read differently by every commons that builds from it. | fields |
| R2 | MUST | A declared field has the shape the schema `health-model.schema.json` gives it. | Shape is what lets a tool compare a record built from it with its origin. | schema |
| R3 | MUST | A jurisdiction overlay is one file `knowledge/jurisdictions/<jurisdiction>.yml` (`core-knowledge` R19, R20) whose `jurisdiction` is its file name and whose `bindings` name, per record of the model, the sources that bind it there, each by source id, edition id and relation. | The record is the same everywhere; what binds it differs by place, and that difference must be checkable. | overlays |
| R4 | MUST | Every overlay binding names a record the model holds and a source of `knowledge/sources.yml` of the overlay's jurisdiction at the edition the source holds, and no base `binds` names a source of a jurisdiction that has an overlay. | A national law in the base record would bind every commons everywhere; a refuted edition would watch the wrong text. | overlays |
| R5 | MUST | A Body or Post of the model is a form: it names no holder, and a Post of the model carries no `held_by`. | Whether a Body forms and who serves a Post is for the commons that builds from it to decide, never for the model. | forms |
| R6 | MUST | A touchpoint's `journey` lists it in its `stages`, and a value exchange's `touchpoint` lists it in its `exchanges`. | MODEL's one binding is one of the model's many; a journey that does not pass through its touchpoint states a path no one walks. | bindings |

## 5 · Structure

The schema is `health-model.schema.json`, next to this file: one definition per kind under `$defs`, holding only the fields this model adds.

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
| `post` | `type` (`executive`, `clinical-lead`, `role`) |

A value exchange's MODEL `touchpoint` is the one place where it is completed, and a touchpoint's `exchanges` names every exchange that meets there. A journey's `stages` name every touchpoint it passes through, and a touchpoint's MODEL `journey` the one it belongs to. A Body of the model's place is MODEL's `part_of`, and a Post of the model's line MODEL's `accountable`, as `body:<slug>`; neither is written twice. A Post holds no capability: its Body holds them (MODEL R14), and the Post answers inside it by its `responsibility`.

The pack's `standing` on a stakeholder is written `legal_form`, because *standing* is the word of a claim's standing and of the stakeholder register (CORE-KNOWLEDGE R4, R12). Its `seat_kind` is written `type`, because *seat* is a rejected word for element 9.

An overlay is one file per jurisdiction; its form is the definition `overlay` of the schema, and part 7 shows one.

## 6 · Checks

`check_health_model.py <health.core>` runs the checks; it exits with 1 on a fail.

| Check | Tests |
|---|---|
| `fields` | every field of a record of the model is MODEL's, `binds` or declared for its kind (R1) |
| `schema` | every declared field validates against its kind's definition (R2) |
| `overlays` | each overlay's name and `jurisdiction` agree; each binding names a record of the model and a source of that jurisdiction at its edition id; no base binding names a source of a jurisdiction with an overlay (R3, R4) |
| `forms` | no Body or Post of the model names a holder (R5) |
| `bindings` | each touchpoint stands in the stages of its `journey`, and each value exchange's `touchpoint` names it among its `exchanges` (R6) |

## 7 · Example

**Minimal:** an overlay for Germany that binds one capability of the model to a national source at its edition:

```yaml
jurisdiction: de
bindings:
- record: capability:technology-resilience-operations
  binds:
  - {source: src-066, edition: b3s-2024, relation: bind}
```

**Complete:** the family Perception to Mandate in this CORE's emulation, `models/emulation/health/`, with its overlays for `de` and `se` in `knowledge/jurisdictions/`.

## 8 · Decision log

| Date | Kind | Decision | Word |
|---|---|---|---|
| 2026-10-28 | commissioned | the fields beyond MODEL and the overlay form of the health offer, for E3 step 2 to 4; the overlay form is @DA-Extension's of step 3 | the maker |
| 2026-10-28 | revised | `summary` on every kind; `nature`, `legal_form` (for the pack's `standing`), `medium`, and `type` on Body and Post (for the pack's `seat_kind`), on the first gate run of steps 2 to 4 | the maker |
| 2026-11-01 | revised | the four forms: every value exchange holds its `touchpoint`, every touchpoint its `journey`, every Post `of`, `responsibility` and `accountable` (as `body:<slug>`), and every Body MODEL's `part_of` in place of `answers_to` (health `1.0.0-rc.4`) | the maker |
| 2026-11-01 | revised | `answers_to` leaves the Post as well, since `accountable` carries the line; with the Body `hospital-pharmacy`, three outermost Bodies and the chosen touchpoints and journeys, a content choice of the Federation inside that cycle, pending D1's reading | the maker |
| 2026-11-01 | revised | R6 and the check `bindings`: a touchpoint stands in the stages of its `journey`, a value exchange's `touchpoint` is among its `at`. Two journeys are offered, `supplier-competing-under-equal-rules` for `call-for-tender` and `patient-organisation-shaping-the-mission` for `patient-advisory-council`, and two touchpoints are placed in existing stages: `confidential-reporting-channel` in `staff-representation-raising-signals`, and `public-quality-report` in `planning-authority-designating-the-mandate`. These are the Federation's content choices | the maker |
| 2026-11-02 | revised | `holds` leaves the Post, from its 13 records and from part 5 and the schema, because MODEL R14 gives holding to the Body alone. Of the 51 Post `holds`, 32 were already held through the Body's subtree, 2 offered capabilities, `prehospital-and-emergency-networks` and `intensive-care`, move into `clinical-centre-board`, the Body their Posts are `of`, and 17 name capabilities this offer does not hold and leave with the field (health `1.0.0-rc.5`) | the maker |
| 2026-11-02 | revised | package A, prepared and not released: the five kinds whole from the pack, 1,061 records (52 stakeholders, 734 capabilities from L1 to L3, 212 entities, 23 solutions, 22 Bodies, 18 Posts), in the fields of part 5 and the four forms. A delegate's `sits_in` is its `of` and its `sent_by` its `accountable`. The pack's entities `payer` and `supplier` are written `payer-organisation` and `supplier-organisation`, because no slug is both a stakeholder and an entity (MODEL R12), and every reference to the entity follows. `staff-council` is an outermost Body; `family-steward` and `stream-operator` are of `performance-and-transformation-office`, and `family-steward` is accountable to `executive-board`; the 18 Posts' `responsibility` is condensed from their summaries. Form P moves 29 capabilities into `clinical-centre-board`. These are the Federation's content choices | the maker |
| 2026-11-02 | revised | package A onto the adopted specifications, `commons.o` main `56cbfd5`, whose tools forced two fixes. Commons Essentials is no longer marked primary in `.commons/commons.yml`, since the grammar is never a commons' primary (CORE R1, EXTENSION R9); the CORE has no primary yet, a gap, and `AGENT.md` is regenerated with it. A touchpoint's `steps` is the earlier layout: the 108 ties to offered steps are written on those 50 steps as `serves` (MODEL R9, R22), and the 305 ties to 244 steps of streams not yet offered leave with the field, because an offer binds nothing it does not hold (EXTENSION R7); they return as `serves` when their families are carried. Nothing is released | the maker |
| 2026-11-02 | revised | package B, first family, prepared and not released: Purpose to Portfolio whole from the pack, its 5 value streams with their 36 steps, the 22 journeys that walk them, 24 touchpoints and 35 value exchanges, in MODEL's layout: a journey writes no `mirrors` and a touchpoint no `steps`, and each step states the touchpoints it `serves` (105 ties); ties to steps and places of families not yet offered leave until those families are carried. A new touchpoint's `journey` is scored as in rc.4, and chosen where tied: `business-case` and `initiative-proposal` belong to `initiative-sponsor-journey`, `performance-dashboard`, `performance-dialogue` and `unit-objectives-agreement` to `department-head-strategy-journey`. A new value exchange's `touchpoint` is its one place, or, of 16 with several, the place where it is completed, as `carryB` lists. No `order` is written: the natural order of the streams is the extension's to deliver, in the form a review reads | the maker |
| 2026-11-02 | revised | package B, second family, prepared and not released: Value to Sustainability whole from the pack, its 9 value streams with their 60 steps, the 18 journeys that walk them, 32 touchpoints and 39 value exchanges, as the first family was carried (88 ties as `serves`). Two journeys whose pack slugs carry the rejected word are written `giving-to-the-commons` and `banking-and-lending-to-the-commons`, and a step's entity `payer` is written `payer-organisation`, as package A named it (MODEL R12). A new touchpoint's `journey` is chosen where tied: `allocation-notice` belongs to `receiving-research-and-teaching-funds`, `claim` to `settling-a-claim`, `controlling-report` to `steering-a-department-budget`, `scientific-publication` to `winning-and-running-a-grant`. Of 11 value exchanges with several places, each `touchpoint` is the place where it is completed, as `carryV` lists | the maker |
| 2026-11-02 | revised | `at` leaves the value exchange, since an exchange states one `touchpoint` (MODEL R9) and `at` on it is the earlier layout: dropped from all 224 offered exchanges, and from part 5, R6, the check `bindings` and the schema. R6 now reads that a value exchange's `touchpoint` lists it in its `exchanges`. Every other offered place of an exchange stays where it was already named, in that touchpoint's `exchanges`: 91 places beside the `touchpoint` of 79 exchanges. The 101 places on touchpoints not yet offered leave and return with their families' touchpoints. No exchange is split: each is one promise between one pair, with one `offered` and one `returned`, completed at its `touchpoint` and met at the others | the maker |
| 2026-11-02 | revised | package B, third family, prepared and not released: Portfolio to System whole from the pack, its 8 value streams with their 56 steps, the 20 journeys that walk them, 34 touchpoints and 47 value exchanges, as the first two families were carried (97 ties as `serves`), each exchange without `at`. A new touchpoint's `journey` is chosen where tied: `digital-demand-intake` belongs to `clinical-unit-shaping-the-digital-roadmap`, `go-live-support` and `system-training` to `clinical-users-receiving-a-new-system`, `supplier-portal` to `supplier-delivering-a-solution`. Of 17 value exchanges with several places, each `touchpoint` is the place where it is completed, as `carryP` lists; the other offered places stand in their touchpoints' `exchanges` | the maker |
| 2026-11-02 | revised | package B, fourth family, prepared and not released: Participant to Community whole from the pack, its 3 value streams with their 20 steps, the 9 journeys that walk them, 19 touchpoints and 17 value exchanges, as the families before it were carried (46 ties as `serves`), each exchange without `at`. One journey whose pack slug carries the rejected word is written `volunteering-in-the-commons`. A new touchpoint's `journey` is chosen where tied: `involvement-call` and `involvement-response-report` belong to `becoming-a-patient-partner`. Of 4 value exchanges with several places, each `touchpoint` is the place where it is completed, as `carryC` lists; the other offered places stand in their touchpoints' `exchanges` | the maker |
| 2026-11-02 | revised | package B, fifth family, prepared and not released: Collaboration to Automation whole from the pack, its 12 value streams with their 78 steps, the 15 journeys that walk them, 42 touchpoints and 27 value exchanges, as the families before it were carried (147 ties as `serves`), each exchange without `at`. A new touchpoint's `journey` is chosen where tied: `agent-oversight-console` belongs to `working-alongside-an-agent`, `simulation-centre` to `front-line-safety-practice`, `teaming-charter` to `agent-joining-a-care-team`. Of 9 value exchanges with several places, each `touchpoint` is the place where it is completed, as `carryA2` lists; the other offered places stand in their touchpoints' `exchanges` | the maker |
| 2026-11-02 | revised | package B, sixth family, prepared and not released: Contributor to Succession whole from the pack, its 12 value streams with their 84 steps, the 20 journeys that walk them, 41 touchpoints and 21 value exchanges, as the families before it were carried (148 ties as `serves`), each exchange without `at`. A new touchpoint's `journey` is chosen where tied: `employment-contract`, `job-advertisement`, `job-interview` and `unit-induction` belong to `joining-as-a-new-colleague`, `appointment-hearing` to `being-called-to-a-chair`, `appraisal-meeting` to `growing-in-the-role`, `course-catalogue` to `keeping-specialist-competence-current`, `pay-statement` to `being-paid-correctly`, `staffing-huddle` to `staffing-the-unit`. Of 14 value exchanges with several places, each `touchpoint` is the place where it is completed, as `carryS` lists; the other offered places stand in their touchpoints' `exchanges` | the maker |
| 2026-11-02 | revised | package B, seventh family, prepared and not released: Discovery to Usage whole from the pack, its 7 value streams with their 48 steps, the 10 journeys that walk them, 24 touchpoints and 13 value exchanges, as the families before it were carried (83 ties as `serves`), each exchange without `at`. The pack names one touchpoint, one step and one measure of the family's loop after a registered method name; they are written `translational-gate-review` (Translational Gate Review), `gate-review-and-reverse-translation` (Gate Review and Reverse Translation) and `gate-decided-on-time`, with every reference. A new touchpoint's `journey` is chosen where tied: `innovation-lab` belongs to `from-invention-to-use`, `research-ethics-committee-meeting` to `obtaining-approval-and-oversight-for-a-study`, `service-design-workshop` to `co-designing-a-service-with-patients`. Of 7 value exchanges with several places, each `touchpoint` is the place where it is completed, as `carryD` lists; the other offered places stand in their touchpoints' `exchanges` | the maker |
| 2026-11-02 | revised | `offer.yml` delivers the natural order of each offered family's streams, `order: {<family>: [<stream>, …]}` (EXTENSION R4 and R24 on `commons.o` main `ab223d3`): the 8 families offered, in MODEL part 5's order, each with its 63 streams in the maker's sequence as the pack lists them; no field on any stream | the maker |
| 2026-11-02 | revised | package B, eighth family, prepared and not released: Interest to Relationship whole from the pack, its 7 value streams with their 49 steps, the 14 journeys that walk them, 29 touchpoints and 8 value exchanges, as the families before it were carried (136 ties as `serves`), each exchange without `at`, and its streams in the offer's `order` in the maker's sequence. Two stage slugs that carry the rejected word are written `getting-to-know-the-commons` and `learning-whether-the-commons-can-help`. A new touchpoint's `journey` is chosen where tied: `appointment-service` belongs to `returning-patient-contact`, `partnership-review-meeting` to `partner-hospital-cooperation`; the one value exchange with several places, `responsiveness-for-candid-feedback`, is completed at `referrer-liaison-visit` | the maker |
| 2026-11-02 | revised | package B, ninth family, prepared and not released: Proposition to Audience whole from the pack, its 8 value streams with their 56 steps, the 16 journeys that walk them, 20 touchpoints and 8 value exchanges, as the families before it were carried (121 ties as `serves`), each exchange without `at`, and its streams in the offer's `order` in the maker's sequence. Three journeys whose pack slugs carry the rejected word are written `knowing-what-the-commons-offers`, `staying-informed-about-the-commons` and `reporting-on-the-commons`. A new touchpoint's `journey` is chosen where tied: `service-information-material` belongs to `knowing-what-the-commons-offers`, `shared-care-plan` to `sharing-care-for-enrolled-patients`. Of 4 value exchanges with several places, each `touchpoint` is the place where it is completed, as `carryPA` lists | the maker |
| 2026-11-02 | revised | package B, tenth family, prepared and not released: Demand to Fulfillment whole from the pack, its 33 value streams with their 221 steps, the 48 journeys that walk them, 69 touchpoints and 20 value exchanges, as the families before it were carried (529 ties as `serves` on the new steps, and 5 on offered steps of four streams that new touchpoints serve), each exchange without `at`, and its streams in the offer's `order` in the maker's sequence. One exchange whose pack slug carries the rejected word is written `learners-for-placements-beyond-the-commons`. Of 14 tied touchpoints, each `journey` and, of 11 value exchanges with several places, each `touchpoint` is chosen as `carryDF` lists | the maker |
| 2026-11-02 | revised | package B, eleventh family, prepared and not released: Source to Alliance whole from the pack, its 5 value streams with their 37 steps, the 14 journeys that walk them, 16 touchpoints and 10 value exchanges, as the families before it were carried (74 ties as `serves`), each exchange without `at`, and its streams in the offer's `order` in the maker's sequence. Two journeys and one stage whose pack slugs carry the rejected word are written `supplying-medicines-to-the-commons`, `working-with-the-commons-as-a-supplier` and `bring-the-commons-in`. The pack's supplier journeys stand beside the offered `supplier-competing-under-equal-rules`; no offered record is removed, and the overlap is an open content choice for the maker with B's release. Of 4 tied touchpoints, each `journey` and, of 7 value exchanges with several places, each `touchpoint` is chosen as `carrySA` lists | the maker |
| 2026-11-02 | revised | package B, twelfth and last family, prepared and not released: Acquire to Retire whole from the pack, its 6 value streams with their 45 steps, the 9 journeys that walk them, 36 touchpoints and 5 value exchanges, as the families before it were carried (108 ties as `serves` on the new steps, and 5 on offered steps of two streams that new touchpoints serve), each exchange without `at`, and its streams in the offer's `order` in the maker's sequence; with it every family of the pack is offered. Of 3 tied touchpoints, each `journey` and, of 3 value exchanges with several places, each `touchpoint` is chosen as `carryAR` lists | the maker |
| 2026-11-02 | revised | package B's release, items 8 to 10. `call-for-tender`'s `journey` is `bidding-in-a-supply-tender`, and it stays in both supplier journeys' stages. The 15 pack touchpoints that no journey walked are carried with the 7 exchanges that stand only at them, each touchpoint placed in the stages of its chosen journey whose step it serves, and 29 ties written as `serves`: `antimicrobial-stewardship-round`, `infection-control-committee` and `outbreak-team-meeting` in `protected-from-infection`; `blood-bank` in `transfusion-recipient-journey`; `capacity-huddle` in `waiting-for-a-bed-journey`; `central-store` and `supply-dashboard` in `keeping-the-ward-supplied`; `licence-statement` in `clinician-equipped-with-it`; `payroll-tax-filing` in `being-paid-correctly`; `permit-application` in `clinical-unit-moving-into-a-new-building`; `quality-data-submission` in `department-outcome-results`; `training-authorisation` in `becoming-a-specialist`; `waste-consignment-note` in `ward-team-relying-on-building-services`; and, where no journey's step is one it serves, `research-integrity-consultation` in the stage `staying-compliant` of `obtaining-approval-and-oversight-for-a-study` and `tax-return` in the stage `approve-and-discharge` of `approving-the-annual-accounts`. `mirrors` leaves the 21 offered journeys of Perception to Mandate, since `serves` ties them | the maker |
| 2026-11-03 | revised | a product name leaves the records, as in business: the capability the pack names after an AI product is written `ai-assistant-integration` (*AI Assistant Integration*), with its references in two solutions, twelve value streams and the research; the term it was carried from stands in `knowledge/translations.yml` | the maker |
| 2026-11-15 | revised | the spec in the names and rules in force of 0.3.0: `health-model` for `health-offer`, the model for the offer, build for activate and adopt, and the rules EXTENSION held cited where they now stand (`model` R20, `core-knowledge` R19, R20, `library` R10, R19); the substance unchanged | the maker |
