---
id: urban-model
title: Urban model — the fields of its records
status: draft
lang: en
touches: [model]
terms: [model, commons]
schema: urban-model.schema.json
check: check_urban_model.py
supersedes: []
---

# Urban model

*What the model of `urban.core` adds to MODEL's records (MODEL R20). A draft.*

## 1 · Goal

An urban commons builds from records that say more than MODEL's grammar holds, such as what triggers a value stream, what a stakeholder seeks and brings, and the states an entity passes through; this specification declares those fields once, with their shape, so that a commons can read, check and build from them without guessing.

## 2 · Boundary

**Belongs here:** the fields of the model's records beyond MODEL's, per kind; that a Body or Post of the model is a form.

**Does not belong here:**

| Matter | Where it belongs |
|---|---|
| the fields every record has, and the grammar | MODEL |
| `binds`, the release, the research in `knowledge/` | CORE-KNOWLEDGE (`core-knowledge` R19, R20), LIBRARY (`library` R10, R19) |
| whether a Body forms and who holds a Post in a commons that builds from it | FLOW (`flow-bodies` R19, R22) |

It extends MODEL and redefines nothing of it (`model` R20). Its fields are the health and business models', so that the models stay comparable; a jurisdiction's law stays in `knowledge/jurisdictions/`.

## 3 · Terms

No new terms.

## 4 · Requirements

| ID | Level | Requirement | Why | Check |
|---|---|---|---|---|
| R1 | MUST | Every field a record of the model carries is MODEL's, `binds` (`core-knowledge` R20), or declared for its kind in part 5. | A field nobody declared is read differently by every commons that builds from it. | fields |
| R2 | MUST | A declared field has the shape the schema `urban-model.schema.json` gives it. | Shape is what lets a tool compare a record built from it with its origin. | schema |
| R3 | MUST | A Body or Post of the model is a form: it names no holder, and a Post of the model carries no `held_by`. | Whether a Body forms and who serves a Post is for the commons that builds from it to decide, never for the model. | forms |
| R4 | MUST | A touchpoint's `journey` lists it in its `stages`, and a value exchange's `touchpoint` lists it in its `exchanges`. | MODEL's one binding is one of the model's many; a journey that does not pass through its touchpoint states a path no one walks. | bindings |

## 5 · Structure

The schema is `urban-model.schema.json`, next to this file: one definition per kind under `$defs`, holding only the fields this model adds.

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


## 6 · Checks

`check_urban_model.py <urban.core>` runs the checks; it exits with 1 on a fail.

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

**Complete:** this CORE's emulation, `models/emulation/urban/`.

## 8 · Decision log

| Date | Kind | Decision | Word |
|---|---|---|---|
| 2026-11-03 | commissioned | the fields beyond MODEL of the urban offer, the business offer's, so that the offers stay comparable; the urban model is authored in `workshop/` and carried into `offer/` | the maker |
| 2026-11-15 | revised | the spec in the names and rules in force of 0.3.0: `urban-model` for `urban-offer`, the model for the offer, build for activate and adopt, and the rules EXTENSION held cited where they now stand (`model` R20, `core-knowledge` R19, R20, `library` R10, R19); the substance unchanged | the maker |
