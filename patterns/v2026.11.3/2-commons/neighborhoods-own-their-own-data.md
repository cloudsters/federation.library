---
id: pat_bd49b7720fbc44f49d374433
slug: neighborhoods-own-their-own-data
title: Neighborhoods Own Their Own Data
summary: A neighborhood collectively manages residents' digital identities—each person holds the keys to their own data while
  the city verifies who they are. This unlocks access to services and economic opportunity without surveillance or corporate
  control.
aliases: []
orbital_layer: 2
gravitational_hubs:
- polycentric-fractal-organisation
- collective-action-and-governance
- reciprocity-and-fairness
- subsidiarity-and-local-empowerment
ontology:
  domain: neighbourhood-digital-identity-commons
  cross_domains: []
  search_hints:
    primary_tension: Individual privacy & autonomy vs. collective verification & service access
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

> A neighborhood collectively manages residents' digital identities—each person holds the keys to their own data while the city verifies who they are. This unlocks access to services and economic opportunity without surveillance or corporate control.

---

### Section 1: Context

Digital identity has become infrastructural—required for economic participation, service access, and social verification. Yet most residents have no control over their digital identities: state systems treat identity as government property; corporate platforms treat it as extractive assets to be monetized and surveilled. This creates a commons problem: identity data about residents is created by residents' own presence and activity, yet custody and benefit flow to external authorities. Neighbourhood Digital Identity Commons invokes the principle of Subsidiarity—decisions about identity governance should rest at the scale where residents actually live and interact. It also invokes Polycentric Organisation: identity verification can be distributed across neighbourhood institutions (cooperatives, community organizations, municipal notaries) rather than concentrated in a single authority. The lineage runs through Self-Sovereign Identity (cryptographic control by the individual), Municipal Anchoring (verification as a service, not authority), and Cooperative Custody (collective stewardship with distributed oversight).

---

### Section 2: Problem

> **The core conflict is Individual privacy & autonomy vs. collective verification & service access.**

The core tension: residents need identity verification to access services, secure housing, open accounts, establish creditworthiness. Yet every current verification pathway—state ID systems, corporate platform accounts, credit bureaux—concentrates custody and control away from residents. This creates two harms. First, surveillance risk: centralized identity data becomes a target for state monitoring, commercial targeting, and breach. Second, portability trap: identity data locked in one system (municipal, corporate, national) cannot move with residents if they relocate, change citizenship, or need alternatives. Residents also face identity fraud, data broking, and exclusion from services when they cannot or will not comply with centralized identity regimes. The deeper conflict: identity should be alive and adaptive (reflecting residents' evolving circumstances, names, credentials), yet centralized systems are brittle—they ossify identity into static records, resist corrections, and serve institutional needs rather than resident needs. How can residents hold custody of their own identity data while still enabling the verification that services legitimately require?

---

### Section 3: Solution

Neighbourhood Digital Identity Commons operates as a cooperative governance structure at neighbourhood scale. The core mechanism has three layers: (1) Individual Cryptographic Custody: Each resident holds their own identity data in encrypted, local-first vaults—neighbourhood-hosted infrastructure (not state or corporate). Residents retain cryptographic keys; only they can decrypt or release their data. (2) Community Stewardship & Verification: The neighbourhood cooperative (or federated network of community institutions) serves as custodian and verifier—not owner. The cooperative holds encrypted backups; manages dispute resolution when identity attributes are challenged; provides notarization and attestation services to municipal and commercial services that need verification. The cooperative operates under multi-signature governance: major decisions (data access policies, fee structures, service partnerships) require votes from resident members and independent community trustees. (3) Attribute Release & Portability: Residents control what identity attributes they share with any service. Release happens through cryptographic proofs that can be verified without exposing underlying data. A resident can prove "I am a resident of this neighbourhood" without revealing their address to every merchant. Credentials are stackable and portable—a learning credential issued by a neighbourhood education cooperative can be verified by any service, reducing vendor lock-in. Revenue Model: When identity attributes are legitimately used (e.g., municipal verification services, credit decisioning), a portion flows back to the cooperative and is distributed to resident members. This aligns stewardship incentives—the cooperative benefits from responsible, widely-used identity infrastructure. Governance Structure: The cooperative operates as a polycentric federation—individual neighbourhoods manage their own identity systems but interoperate through common cryptographic standards. Dispute resolution: disagreements over identity attributes (e.g., residency claims) are arbitrated by neighbourhood assemblies, not remote authorities. This pattern resolves the tension by making identity a shared commons: residents retain individual control; the neighbourhood provides collective verification infrastructure; municipal and commercial services access identity data only with resident consent and through the cooperative's verification layer. Identity remains alive and adaptive—residents can update their attributes, correct errors, and port their data across services—while neighbourhood institutions ensure that verification serves residents' interests, not institutional extraction.

---

### Section 4: Implementation

The work begins with technical infrastructure, but treat it as infrastructure for human flourishing—like building a well or a meeting hall.

**Start with cryptographic custody.** A neighbourhood establishes a self-hosted identity vault system—open-source software running on neighbourhood servers (or distributed across residents' devices). Each resident generates their own keypair; the neighbourhood never holds the private keys. This is non-negotiable. The technology should be simple enough that a resident with moderate technical skill can verify what's happening, but residents don't need to be cryptographers to use it.

**Design the verification layer.** Create a lightweight attestation process where trusted neighbourhood members (elected or rotated) verify basic facts: "Yes, I know this person, they live here." Not state-level documentation—just human recognition at neighbourhood scale. This becomes a credential the resident controls and can share selectively. A neighbour attesting to your presence is fundamentally different from a database recording it.

**Build selective disclosure.** The resident decides what identity attributes they reveal for each transaction. A landlord needs proof of residence and income verification—but not your health data or political affiliations. A bank needs creditworthiness signals—but not your address history. Each disclosure is a conscious choice, logged by the resident themselves.

**Establish governance.** Who maintains the servers? Who updates the software? Who arbitrates disputes? Create explicit agreements—written plainly, not legal-ese—about how the neighbourhood makes decisions. Rotate responsibilities. Keep it small enough that people understand it.

**Connect to service providers.** Work with local government, banks, cooperatives, housing providers to accept neighbourhood-issued credentials. This is the hardest part: institutions are habituated to centralized identity. Start with services where neighbourhood verification is genuinely better (local housing, community credit, emergency services). Win trust through demonstrated reliability.

**Document, iterate, teach.** Create guides residents can actually read. Run workshops. Expect the system to break and improve iteratively. The goal isn't perfection—it's resident control.

---

### Section 5: Consequences

**What flourishes:** Residents gain negotiating power. Without your data, institutions must treat you as a person, not a profile. People can move between neighborhoods without losing identity history—your credentials travel with you because you own them. Economic opportunity becomes less dependent on corporate platform gatekeeping or state surveillance. Trust becomes visible: you know who's attesting to your identity. Small informal economies (care work, repairs, teaching) can formalize without exposing participants to state taxation or corporate data extraction.

**Risks if neglected:** The system becomes a new form of gatekeeping if verification standards are opaque or exclusionary. Early users gain advantage; late adopters are disadvantaged. If the neighbourhood collective becomes coercive—using identity access as social control—you've simply moved surveillance from state/corporate to community level. Technical maintenance becomes a burden on volunteers; burnout is a real threat. Service providers may collude to set impossible verification standards, leaving residents worse off than before. Data can still leak if residents' personal devices are compromised. The system only works if multiple neighbourhoods exist and can interoperate—isolation makes it fragile.

---

### Section 6: Cognitive Era

As AI systems proliferate, neighbourhood data sovereignty becomes more critical—and more complex.

**The risk:** Machine-learning systems trained on centralized identity data create predictive profiles that residents never consented to and can't see. An AI system trained on state identity registries can infer health conditions, criminality risk, or creditworthiness in ways that are impossible to audit or contest. If residents don't control their identity data, they cannot control what AI systems infer about them.

**The opportunity:** Residents who hold their own data can choose *which* inferences to enable. You control whether an AI can predict your credit risk (you choose to share transaction history) but not your health status (you don't). Neighbourhood AI systems trained on collective data—with explicit resident consent—could produce better local insights than centralized systems: hyperlocal housing predictions, neighbourhood-specific resource allocation, community-designed credit metrics that replace discriminatory corporate models.

**The shift:** The pattern requires a fundamental reframing: identity is not a dataset to be optimized globally, but a relationship to be negotiated locally. As AI increasingly mediates identity (determining who you are, what you can do), the right to *refuse* certain kinds of identity inference becomes as important as the right to privacy.

---

### Section 7: Vitality

**Signs of health:**
- Residents regularly update and verify their own identity data (not administrators doing it for them).
- Service providers *compete* to accept neighbourhood credentials because they're reliable and reduce their own compliance burden.
- New residents join the system easily; established residents mentor newcomers.
- The neighbourhood can articulate *why* they made each governance choice, and people actually know the answers.
- Data breaches, when they happen, affect only the individual resident whose device was compromised—not the entire system.
- Residents use their credentials to access multiple services; the system is materially useful, not theoretical.

**Signs of decay:**
- Verification becomes an insider practice; newcomers or outsiders face higher barriers.
- The technical layer requires constant expert intervention; nobody but one person understands how it works.
- Service providers gradually stop accepting credentials; residents revert to state ID or corporate platforms.
- Governance decisions are made in closed meetings or by unelected stewards.
- The system becomes a tool for neighbourhood social control (exclusion, shaming, gatekeeping).
- Residents are *required* to participate; opt-out is costly or socially punished.

**Diagnostic question:** Can a resident leave the neighbourhood and take their identity with them, or does their identity dissolve if they move? If identity is truly theirs, it moves with them. If it's tied to the neighbourhood collective, it's not really theirs at all.
