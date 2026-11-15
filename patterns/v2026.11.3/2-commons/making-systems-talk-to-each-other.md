---
id: pat_dbffb57131854ec2add155e7
slug: making-systems-talk-to-each-other
title: Making Systems Talk to Each Other
summary: Connect your specialized tools so they work together naturally and adapt when things change, rather than forcing
  rigid connections that break under pressure.
aliases: []
orbital_layer: 2
gravitational_hubs:
- polycentric-fractal-organisation
- network-effects-and-multi-sided-platforms
- emergence-and-complexity
- feedback-and-adaptive-cycles
- orchestration-over-execution
- patterns-over-protocols
- reciprocity-and-fairness
ontology:
  domain: enterprise-system-integration
  cross_domains: []
  search_hints:
    primary_tension: System autonomy vs. coherent value flow
lifecycle:
  status: candidate
  version: '0.1'
  confidence: 2
contributors:
- higgerix
- cloudsters
sources: []
license: CC-BY-SA-4.0
attribution: commons.engineering by cloudsters, https://cloudsters.net
---

> Connect your specialized tools so they work together naturally and adapt when things change, rather than forcing rigid connections that break under pressure.

---

### Section 1: Context

Modern enterprises operate as living ecosystems of specialized systems—legacy infrastructure, cloud platforms, supply networks, partner integrations—each designed independently, each holding critical knowledge and capability. These systems were never meant to work together. They exist in a state of permanent fragmentation: manual data transfers, duplicated records, delayed decisions, cascading failures. The integration problem is not technical failure—it is the collision between two truths: specialization creates efficiency (each system excels at one thing), yet value flows across boundaries. The commons engineer inherits a landscape where a large share of IT budgets goes to integration debt, where a single failed handoff cascades through supply chains spanning continents, and where no actor controls the complete flow. The question is not whether to integrate, but how to cultivate integration as a living, adaptive commons rather than a brittle, centralized machine.

---

### Section 2: Problem

> **The core conflict is System autonomy vs. coherent value flow.**

Integration architectures face a fundamental tension. Tight coupling—forcing all systems into a single schema, a master database, a unified protocol—creates brittleness. When one system changes, everything downstream breaks. Loose coupling—leaving systems isolated—preserves autonomy but sacrifices coherence. Orders pile up unprocessed. Customer data fragments across incompatible platforms. Inventory falls out of sync with fulfillment. The real problem runs deeper: most integration approaches treat the network as a machine to be controlled, not as a living system to be stewarded. They assume a single source of truth is possible. They enforce consistency as an absolute. They centralize decision-making. They ignore that the systems themselves evolve—new requirements emerge, business units shift priorities, regulations change. And when they do, the rigid integration architecture becomes an obstacle, not an enabler. The result: systems that are simultaneously brittle (they break when change occurs) and inflexible (change itself becomes forbidden because the cost of modification cascades through dependencies).

---

### Section 3: Solution

Shift from integration-as-engineering to integration-as-stewardship. Design the network itself as a commons—a living, adaptive system that creates coherence without requiring central control.

**1. Protocol Over Prescription:** Define integration through lightweight, evolvable patterns rather than rigid specifications. Each system commits to a protocol (e.g., event formats, idempotency guarantees, error handling conventions) but retains freedom in implementation. Protocols are discovered through shared practice, not imposed from above. They evolve when the network learns they no longer serve.

**2. Reciprocal Flows, Not Command Chains:** Replace hierarchical data flows (master system commands subordinates) with reciprocal exchange. System A publishes events; System B consumes them and publishes responses. Both are publishers and subscribers. This distributes coupling across the network rather than concentrating it in a master.

**3. Eventual Consistency as Design Principle:** Accept that real-time synchronisation across all nodes is impossible. Instead, design for eventual consistency—the network's distributed state converges over time through feedback loops and reconciliation. This trades immediate certainty for resilience; when one system fails, others continue generating value and the network heals.

**4. Visible Duplication, Not Hidden Fragmentation:** Rather than pretending to a single source of truth, make duplication visible and manage it through de-duplication patterns and conflict resolution protocols. Every system maintains its own authoritative view of entities it owns (customer records in the CRM, inventory in the warehouse system); duplication in other systems is acknowledged and reconciled through periodic consensus checks.

**5. Distributed Governance, Not Centralized Control:** Create integration governance councils where each system's stewards negotiate shared standards, handle conflicts, and evolve protocols. Decisions scale through subsidiarity—local teams resolve issues at the lowest competent level. Conflicts that cannot be resolved locally escalate to the next level, but the default is distributed.

**6. Feedback as Commons Act:** Build continuous visibility into integration health. Every error, latency spike, or consistency drift becomes information fed back to the network. Systems learn from collective experience. Patterns emerge about what works and what breaks under load.

**7. Fractal Nesting:** Apply the same stewardship logic at multiple scales. A supply chain network coordinates across independent companies the same way a large enterprise coordinates across divisions—through reciprocal protocols, eventual consistency, and distributed governance. The pattern repeats; it scales.

---

### Section 4: Implementation

Start by mapping the conversation your systems are already having—the informal flows, the workarounds, the places where humans bridge the gaps. This map is your starting point, not your constraint. You're not automating what exists; you're formalizing what works.

**Layer 1: Protocol Definition.** Gather stewards from each system—not IT architects alone, but the people who live with the friction daily. Define three to five core protocols: event shapes (what gets communicated), timing guarantees (when), idempotency rules (what happens if a message arrives twice). Keep these lean. The protocol is a social contract, not a technical specification. Write it in plain language first. Use examples before formalism.

**Layer 2: Event Streams as Shared Consciousness.** Rather than point-to-point integrations, introduce a lightweight event backbone—a pub-sub pattern that lets systems broadcast what happened without knowing who's listening. When inventory changes, publish it. When an order ships, broadcast it. Systems subscribe to what matters to them. This decouples them while keeping them synchronized. Use tools like Kafka, or even simpler event logs, depending on your scale.

**Layer 3: Adapter Stewards.** Assign humans to each system boundary—people responsible for translating between local logic and shared protocols. They monitor the flow, catch anomalies, adjust mappings when systems change. They're not automated; they're vigilant. This prevents silent failures and keeps integration human-scale.

**Layer 4: Feedback Loops.** Build visibility into the network's health. When events back up, when translations fail, when latency spikes—make it visible to the stewards. Create forums for regular reflection: "What broke this week? What did we learn? What protocol adjustments do we need?" Integration improves through collective learning, not perfect planning.

**Layer 5: Gradual Expansion.** Start with one or two critical flows—order to fulfillment, customer data to marketing. Let them stabilize. Then expand. Each new connection teaches you something about your protocols; they evolve with use.

---

### Section 5: Consequences

**What Flourishes:**

When systems talk coherently, latency collapses. Orders flow to fulfillment in minutes instead of days. Customer service sees real-time inventory. Supply chains respond to demand rather than react to surprises. Decision-makers work with current information, not yesterday's snapshots. The organization moves faster because it thinks as one distributed mind.

Autonomy persists—each system evolves at its own pace, making local decisions—but those decisions propagate. Changes ripple through the network naturally. A new fulfillment warehouse joins the network without rewriting integration logic. A legacy system retires without cascading failures.

Humans shift from plumbing work to stewardship. Less manual data transfer, more thoughtful monitoring and adaptation. The organization learns why things fail and adjusts proactively.

**Risks That Emerge:**

Event overload. If you're not careful, the system generates more signals than humans can process. The network becomes noisy; stewards miss the important failures in the static.

Hidden coupling. Systems that should be independent become tightly synchronized at the data level. A subtle protocol assumption, baked into multiple systems, becomes difficult to change. You've traded visible brittleness for invisible brittleness.

Trust erosion. If the event stream becomes unreliable—dropped messages, out-of-order delivery, inconsistent state—systems stop trusting it. They revert to manual reconciliation and isolation. Integration dies from neglect.

Protocol drift. Without active governance, each system interprets shared protocols differently. The "same" event means subtly different things across the network. Data spreads, but understanding breaks.

---

### Section 6: Cognitive Era

AI and distributed intelligence change what's possible—and what's dangerous—about system-to-system communication.

**The Opportunity:** AI agents can now monitor event streams, detect anomalies humans miss, and suggest protocol adjustments before failures occur. A machine-learning system watching your integration network might notice that shipping latency spikes when inventory updates arrive out of order—a pattern invisible to human monitors. It can flag this, recommend a protocol tweak, and validate the fix.

Distributed intelligence also lets you move decision-making closer to events. Instead of centralizing all order-fulfillment logic, you can distribute small, trained models to edge systems. Each model makes local decisions (Should this order go to warehouse A or B?) while respecting shared protocols. The network becomes more responsive without becoming more fragile.

**The Danger:** AI systems can hallucinate coherence that doesn't exist. A language model analyzing event streams might infer causation where there's only correlation. It might "fix" a protocol in ways that preserve apparent synchronization while introducing subtle inconsistencies. The network looks healthy until it catastrophically fails.

Automated reconciliation at scale can hide manual human judgment. If an AI is constantly smoothing over protocol mismatches, you stop learning why they happen. The system becomes a black box. When it fails, you have no way to diagnose or repair it.

**The Path Forward:** Treat AI as a steward amplifier, not a replacement. Use it to surface anomalies and suggest changes, but keep humans—the protocol stewards—in the loop. Make all AI-assisted changes visible and auditable. Maintain the human practice of regular reflection and deliberate protocol evolution.

---

### Section 7: Vitality

A healthy integration network shows these signs:

- **Events flow cleanly.** You can trace how information moves from origin to destination. Latency is predictable; failures surface quickly and clearly.
- **Protocols evolve deliberately.** When a system needs to change, stewards discuss it, propose amendments, implement gradually. Change is visible and discussable.
- **Systems stay autonomous.** You can shut down a system, replace it, or upgrade it without triggering cascading failures across the network.
- **Stewards are engaged.** They can explain why events exist, what protocols mean, where the boundaries are. The network has living caretakers, not just infrastructure.

Signs of decay:

- **Silent failures.** Events disappear or arrive out of order with no visibility. Stewards discover problems days later through customer complaints.
- **Protocol sprawl.** Each system has its own interpretation of shared events. "Customer created" means different things in marketing vs. fulfillment.
- **Bloated events.** Events become so large and complex that systems struggle to process them. The network bogs down under its own weight.
- **Abandoned stewardship.** No one monitors the network. Changes happen without coordination. Integration becomes fragile and opaque.

**The diagnostic question:** Can you change one system without notifying three others, and have the network adapt gracefully? If yes, you have stewardship. If no—if change always cascades, always breaks something—the network is brittle, and integration has failed.
