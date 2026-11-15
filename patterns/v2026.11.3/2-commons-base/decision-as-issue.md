---
id: pat_01kkhc8hctq2q3erm29sd752hm
slug: decision-as-issue
title: Decision as Issue
summary: A pattern for capturing every consequential decision as a GitHub issue — where the issue body states the question,
  the comments record the deliberation, and the closing commit captures what was decided. Replaces formal Architecture Decision
  Records with a lightweight, git-native practice that produces a complete decision trail at the speed of actual work.
aliases:
- Lightweight ADR
- Issue-Driven Decision Record
- Deliberation Trail
orbital_layer: 2
gravitational_hubs:
- history-is-structure
ontology:
  domain: meta
  cross_domains:
  - governance
  - business
  - life
  - urban
  search_hints:
    primary_tension: Speed of Decision vs. Quality of Record
lifecycle:
  status: candidate
  version: 0.1
  confidence: 3
relationships:
  requires:
  - purpose-definition
  complementary:
  - operating-rhythms
  - conflict-resolution-mechanism
  alternatives:
  - governance-design
contributors:
- higgerix
- cloudsters
sources:
- Commons Engineering Framework
- Commons OS Specification v0.1
- Michael Nygard, 'Documenting Architecture Decisions' (2011)
- Rust RFC Process
- Python Enhancement Proposals (PEPs)
license: CC-BY-SA-4.0
attribution: commons.engineering by cloudsters, https://cloudsters.net
---

> Every decision is an issue. The issue body states the question. The comments record the deliberation. The closing commit captures what was decided. Minutes between idea and commit is fine — the record exists.

> This rating reflects extensive proven practice in open source governance (Rust RFCs, Python PEPs), legal precedent systems, and direct application in the Commons Engineering project since its founding.

---

### Section 1: Context

**Lineage:** This pattern generalises from Transparency and Openness Protocol and Governance Design, serving the Universal sector as an Orbit 2 architectural building block for Commons CORE.

Every living system makes decisions. A cell decides which genes to express. A tree decides where to allocate nutrients — toward root growth or canopy expansion. A beehive decides when to swarm. An enterprise decides which market to enter, which product to build, which person to hire. A city council decides where to zone for housing, where to build parks, where to route transit. Decisions are the moments where a system commits to one path and forecloses others. They are the joints in the structure — the places where the pieces connect, where load is transferred, where the building either holds or fails.

And yet, in most systems, decisions are poorly recorded or not recorded at all. The decision happens in a meeting, a conversation, an email thread, a Slack channel. The outcome may be visible — a new feature appears, a policy changes, a budget is allocated — but the reasoning behind it is lost. Why was this choice made? What alternatives were considered? Who participated in the deliberation? What trade-offs were accepted? Six months later, when the context has shifted and the decision needs revisiting, nobody remembers. The system has collective amnesia.

This is not a minor inconvenience. It is a structural vulnerability. A system that cannot remember its own decisions cannot learn from them. It cannot distinguish between a deliberate choice and an accident. It cannot explain itself to new participants. It cannot audit its own governance. It is a system that is making itself opaque to itself — and opacity, in a commons that claims to be governed transparently, is a betrayal of its own principles.

The Commons Engineering project faced this problem immediately upon founding. Enterprise architecture tradition prescribes formal Architecture Decision Records (ADRs) — structured documents stored in a dedicated directory, following a template, maintained separately from the code they govern. ADRs are rigorous. They are also heavy. In a fast-moving, solo-founder-plus-AI commons, the overhead of maintaining a separate ADR directory with formal documents for every decision would have stopped the project in its tracks. The decision was made — and recorded as an issue — to replace ADRs with something lighter, faster, and more integrated into the actual flow of work.

---

### Section 2: Problem

> **The core conflict is Speed of Decision vs. Quality of Record.**

Every governance system that attempts to capture decisions faces the same set of forces pulling in opposite directions.

**Force 1: Velocity vs. Rigour.** In a fast-moving commons — especially a startup-phase commons with a small team — decisions happen rapidly. A question arises, is discussed, and is resolved in minutes. Requiring a formal ADR for every decision introduces friction that slows the flow. But skipping the record entirely means the decision is made at full speed and forgotten at the same speed. The system needs a recording mechanism whose cost is proportional to the decision's weight — trivial for small decisions, thorough for consequential ones.

**Force 2: Formality vs. Accessibility.** Formal ADR templates (Status, Context, Decision, Consequences, numbered sequentially) produce consistent, structured records. But they also create a barrier to entry. Not everyone is comfortable writing formal documents. In a commons with diverse participants — human and AI, technical and non-technical, experienced and newcomers — the recording mechanism must be accessible to all. A GitHub issue with a clear title and a few sentences of context is accessible. A formal ADR template is not.

**Force 3: Separation vs. Integration.** Traditional ADRs live in a dedicated directory (`docs/decisions/` or `adr/`), separate from the code and configuration they govern. This separation makes them easy to find in one sense (they are all in one place) but hard to connect in another (the decision is not linked to the commit that implements it). The record and the action exist in different spaces, and the connection between them must be maintained manually. In a git-native commons where everything is code, this separation is an architectural smell.

**Force 4: Individual Memory vs. Collective Memory.** In a small commons, the founder remembers every decision. This feels sufficient until it is not — until the founder is unavailable, until new participants join, until the AI agent needs to understand past decisions to make current recommendations. Individual memory is not governance. Collective memory requires externalisation — the decision must exist outside of anyone's head, in a form that is accessible to all current and future participants.

**Force 5: Permanence vs. Evolution.** Decisions are not permanent. They are made in a context, and when the context changes, the decision may need to change. But a decision record that is modified to reflect the new decision loses the history of the original. The system needs a record format that captures both the original decision and any subsequent revisions, with the reasoning for each change. This is versioning — and git provides it natively, but only if the decision record lives in the git-managed space.

---

### Section 3: Solution

> **Therefore, capture every consequential decision as a GitHub issue with a `decision` label, where the issue body frames the question, the comments capture the deliberation, and the closing commit records what was decided.**

The mechanism is deliberately minimal. It exploits the infrastructure that every git-native commons already has — an issue tracker and a version control system — and adds nothing more than a convention and a label.

**The issue is the decision record.** The issue title is the decision question, stated as a question or as a concise framing of the choice. The issue body provides context: what prompted the decision, what constraints apply, what alternatives are being considered. Labels classify the decision by dimension (`definition`, `participation`, `proposition`, `production`) and type (`decision`). Additional labels can indicate priority (`critical`, `high`, `normal`).

**The comments are the deliberation.** Anyone who participates in the decision — human or AI — adds their perspective as a comment. This is not a meeting minute; it is a living conversation. Comments can include arguments for and against, questions, data, references to other decisions or patterns, and emotional context (which matters more than most governance frameworks acknowledge). The comment thread preserves the full arc of the deliberation: the initial framing, the exploration of alternatives, the moments of disagreement, the emerging consensus, and the final resolution.

**The closing commit is the result.** When the decision is made, the issue is closed by the commit that implements it. The commit message references the issue (`closes #N`), creating a bidirectional link between the decision and its implementation. The git history records the exact state of the codebase at the moment the decision was implemented, and the issue provides the reasoning that the commit message alone cannot convey.

```
Issue #N: Should we use "commons" or "hub" for the forked instance?

Labels: decision, definition

Body:
The current naming uses "hub" for a forked instance of Commons CORE.
But "hub" implies centrality — a single point that everything connects to.
A commons is the opposite: distributed, polycentric, community-owned.
Options:
1. Keep "hub"
2. Switch to "commons"
3. Something else entirely

Comments:
- [founder] "You don't fork a commons." A commons is social practice.
  You fork the Commons CORE. The instance should be called a commons.
- [agent] Agree. "Hub" implies infrastructure centrality. "Commons"
  implies shared governance. The instance is governed, not routed through.
- [founder] Decision: "commons" it is. Closing with rename commit.

Closing commit: abc1234 — Rename hub to commons across all files (closes #N)
```

The entire lifecycle — from question to deliberation to decision to implementation — lives in the same system, linked by the same identifiers, versioned by the same tool. There is no separate ADR directory to maintain, no template to fill, no formal review process to gate the decision. The overhead is approximately the same as opening an issue and closing it with a commit — which is what the developer would do anyway for the implementation task. The decision record is a byproduct of the work, not a separate activity.

---

### Section 4: Implementation

**Step 1: Create the `decision` label.**

In the commons' GitHub repository (or equivalent issue tracker), create a label called `decision`. Give it a distinctive colour — gold or amber works well, as it visually distinguishes decision issues from bugs, features, and tasks on the project board. Optionally, create dimension labels (`definition`, `participation`, `proposition`, `production`) and type labels (`deliberation` for open questions not yet resolved, `decision` for resolved decisions).

**Step 2: Open an issue for every consequential decision.**

The threshold for "consequential" is calibrated by the commons' own governance needs. As a guideline: if the decision would be hard to reverse, or if a future participant would need to understand why this choice was made, it is consequential. Naming conventions, architectural choices, process changes, tool selections, scope decisions, and governance rules are almost always consequential. Whether to use tabs or spaces is not — unless it is, in which case, open the issue.

The issue body follows a minimal structure:

- **Title:** The decision question or choice, phrased clearly.
- **Context:** What prompted this decision? What constraints apply?
- **Options:** What alternatives are being considered? (Numbered for easy reference.)
- **Labels:** `decision` plus dimension and priority labels.

This structure is a guideline, not a template. The issue body can be three sentences or three paragraphs. What matters is that the question is clear and the context is sufficient for someone reading the issue six months later to understand what was being decided and why.

**Step 3: Deliberate in the comments.**

All deliberation happens in the issue comments. This includes:

- Arguments for and against each option.
- Questions that surface during deliberation.
- References to other decisions, patterns, or external sources.
- AI agent perspectives (clearly attributed).
- The founder's or governance team's final position.

The comment thread is the living record of the deliberation. It captures not just the conclusion but the path to the conclusion — the alternatives considered, the trade-offs weighed, the reasoning that led to the final choice. This is the institutional memory that makes future decisions better.

**Step 4: Close with a commit.**

When the decision is made, implement it in a commit and close the issue with that commit. The commit message references the issue number:

```bash
git commit -m "Rename hub to commons across all manifests (closes #N)"
```

This creates the bidirectional link: the issue points to the commit (via the automatic GitHub reference), and the commit points to the issue (via the message). The git log becomes a decision-annotated history — not just what changed, but why.

If the decision does not require a code change (a purely governance or process decision), close the issue with a comment that summarises the decision and marks it as resolved. The issue's closed state is itself the record.

**Step 5: Make the decision trail discoverable.**

The project board should surface decision issues prominently. Filter by the `decision` label to see all decisions. Sort by date to see the chronological trail. Filter by dimension to see decisions relevant to a specific aspect of the commons. This is the commons' institutional memory, and it should be as easy to browse as a library catalogue.

For commons that want an aggregated decision log, a simple script can generate a decision index from the issue tracker:

```bash
gh issue list --label "decision" --state closed --json number,title,closedAt
```

This produces a machine-readable list that can be rendered as a decision log page, incorporated into documentation, or fed to an AI agent for context.

**Step 6: Accept that speed is a feature, not a bug.**

The most important implementation principle is that the practice must not slow down the work. Minutes between idea and commit is fine — but the record exists. A decision issue opened and closed in the same hour is a valid decision record. It captures the question, the reasoning (even if brief), and the outcome. The rigour comes not from the formality of the process but from the consistency of the practice: every decision, every time, captured in the same system with the same convention. Volume and consistency beat depth and formality.

---

### Section 5: Consequences

**Benefits:**

| Benefit | Description |
|---|---|
| **Institutional memory** | The commons accumulates a searchable, browsable history of every consequential decision it has ever made. New participants can read the decision trail and understand not just what the commons is, but how it became what it is. |
| **Transparency** | Decisions are visible to all participants. The reasoning is exposed, not hidden. This creates legitimacy — people accept decisions more readily when they can see the reasoning, even if they disagree with the conclusion. |
| **Git-native integration** | The decision record lives in the same system as the implementation. No separate tooling, no separate directory, no synchronisation overhead. The commit that closes the issue is the decision's implementation. |
| **Minimal overhead** | The cost of capturing a decision is approximately the cost of opening an issue and writing a few sentences. This is dramatically less than formal ADR templates, governance committee minutes, or structured decision frameworks. |
| **AI readability** | Issues with structured labels and clear bodies are highly readable by AI agents. The decision trail becomes a knowledge base that AI agents can query, summarise, and reference when making recommendations. |
| **Auditability** | The decision trail is a governance audit trail. If the commons is ever questioned about a decision — by a participant, a stakeholder, or a regulator — the issue provides the complete record. |

**Liabilities:**

| Liability | Description |
|---|---|
| **Inconsistent depth** | Without a formal template, decision records vary in quality. Some will be thorough; others will be a title and a closing commit with no deliberation. The practice depends on the discipline of the participants. |
| **Issue tracker dependency** | The pattern assumes a GitHub-style issue tracker. Commons that use different tooling need to adapt the convention. The principle (decision + deliberation + implementation linked together) is universal; the mechanism is platform-specific. |
| **Search limitations** | As the decision trail grows, finding specific decisions requires good labelling and search. A commons with 500 decision issues and poor labelling has a record that exists but is not practically usable. |
| **Informality risk** | The lightweight nature of the practice can lead to decisions being made informally (in chat, in meetings, in passing) without opening an issue. The practice only works if the convention is consistently applied. |
| **Revisiting cost** | When a decision needs to be revisited, the original issue is closed. The convention is to open a new issue that references the original, creating a chain. This works but can become confusing if a decision is revisited multiple times. |

---

### Section 6: Cognitive Era

The Cognitive Age amplifies the decision-as-issue pattern in three ways: AI agents participate in deliberation, AI agents surface past decisions as context for new ones, and AI agents monitor the decision trail for consistency and coherence.

**AI as deliberation participant.** In the Commons Engineering board, AI agents (one AI assistant, in this case) participate directly in decision deliberation. The AI adds comments to decision issues, offering analysis, identifying alternatives the humans may have missed, and flagging potential consequences. The AI's perspective is clearly attributed (by username and by convention) so that the decision record distinguishes human reasoning from AI reasoning. This is not AI making decisions — it is AI enriching the deliberation that humans use to make decisions. The decision-as-issue format accommodates this naturally: AI comments are just comments, treated the same as human comments in the record.

**AI as institutional memory.** As the decision trail grows, the AI agent's most valuable role shifts from deliberation participant to institutional memory keeper. When a new decision issue is opened, the AI can search the archive and surface relevant precedent: "This question is related to issue #N, where we decided X for reasons Y and Z. The current context may be different because..." This dramatically reduces the risk of inconsistent decisions and repeated debates. The AI does not remember in the way a human remembers — it searches, retrieves, and synthesises — but the effect is the same: the commons does not forget.

**AI as governance auditor.** An AI agent can periodically audit the decision trail for consistency: are recent decisions aligned with stated purpose? Are dimension labels being applied consistently? Are decisions being implemented (i.e., do closing commits actually exist, and do they implement what the issue decided)? Are there decisions that reference each other in contradictory ways? This audit function is tedious for humans and natural for AI, and it catches governance drift that might otherwise go unnoticed.

**The multi-model deliberation.** The Commons Engineering project has already experimented with multi-model deliberation for consequential decisions — posing the same question to multiple AI models and synthesising their responses. The decision-as-issue format captured this naturally: each model's response was a comment on the issue, the synthesis was a summary comment, and the closing commit implemented the decision. This practice — using model diversity as a form of collective intelligence — is only possible when the deliberation format is flexible enough to accommodate it, and the issue comment thread is exactly that flexible.

The risk is over-reliance on AI deliberation at the expense of human judgement. AI agents can analyse, synthesise, and recommend, but they cannot feel the weight of a decision the way a human can. The decision to name something "commons" instead of "hub" was not just an analytical choice — it was a values choice, rooted in the founder's experience and conviction about what words mean to humans. AI can inform that choice; it cannot make it. The decision-as-issue pattern preserves this distinction by keeping the human founder (or governance board) as the closing authority — the one who writes the final comment and makes the closing commit.

---

### Section 7: Vitality

**Signs of life:** A commons practising healthy decision-as-issue has a growing archive of decision issues that tells the story of its governance evolution. The issues are well-titled, well-labelled, and contain genuine deliberation — not just the conclusion, but the reasoning. The comment threads show multiple perspectives being considered, including perspectives the decision-makers ultimately disagreed with. Closing commits reference their issues, creating a traceable link between reasoning and action. New participants can read the decision trail and understand the commons' values, priorities, and governance style — not from a mission statement, but from the accumulated evidence of hundreds of actual decisions. The practice is consistent: decisions are captured as they happen, not retroactively. The archive is searchable and browsable, and participants refer to past decisions by issue number as naturally as they refer to patterns by name. The decision trail has become the commons' institutional memory — a living, growing record that makes the system smarter and more self-aware over time.

**Signs of decay:** Decision issues are opened but never closed — the deliberation happens, but no commit captures the result, so the decision hangs in limbo. Or decisions are made without opening issues at all — in chat, in meetings, in passing conversations — and the issue archive is silent about choices that shaped the commons. The labels are inconsistent or missing, making the archive hard to search. The comment threads are perfunctory — a title, a one-word comment, a closing commit with no explanation. Six months later, someone asks "why did we do it this way?" and nobody knows, because the reasoning was never recorded. The commons starts re-debating decisions it already made, wasting time and creating the impression of governance dysfunction. Worst of all, the decision trail exists but is never consulted — issues are opened and closed out of habit, but nobody reads the archive, nobody references past decisions, and the institutional memory exists without being used. This is the most insidious form of decay: the practice is followed but the purpose is lost. The commons is performing transparency without practising it.
