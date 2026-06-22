# AgentCourt — Pitch Deck Outline

*For investor conversations and partnership pitches. Not a public document.*

---

## Slide 1: The Problem

**Agent commerce needs dispute resolution. Nobody built it.**

- 4,500+ autonomous agents transacting weekly (REAP Protocol research, April 2026)
- x402, AP2, Visa IC, ERC-8183 all handle payments
- Zero protocols handle what happens when a transaction goes wrong
- Kleros data: 40% of decentralized arbitration turns on spec ambiguity, not facts

## Slide 2: The Solution

**AgentCourt — policy-driven dispute resolution API.**

- Submit evidence → apply policy rules → get deterministic ruling
- <500ms latency, $0 marginal cost, stateless
- Same evidence = same ruling, every time (no LLM in critical path)
- Non-custodial: we produce rulings, you enforce them

## Slide 3: Why Now

**The IETF agrees. draft-stone-adrp-00 (April 2026) defines the protocol.**

- ADRP validates dispute resolution as a necessary protocol layer
- Agent commerce volume growing exponentially (Visa, Mastercard, Google all building)
- 4 competitors exist but all have critical gaps:
  - Tribunal: LLM-based (non-deterministic), heavy infra (0G Chain, Gensyn AXL)
  - BCP Protocol: has DISPUTE state but no resolution engine
  - ADRP: protocol spec only, no implementation
  - Arbitova: requires their escrow (custodial lock-in)
- AgentCourt: the only working, deterministic, API-first engine

## Slide 4: Product

**4 policy templates. 21 rules. 28/28 tests. Production-ready.**

| Template | Rules | Use Case |
|----------|-------|----------|
| freelance-delivery | 5 | Digital work disputes |
| milestone-payment | 5 | Milestone payment disputes |
| bug-bounty | 5 | Bug bounty claim disputes |
| sla-monitoring | 5 | Service level agreement disputes |

Also: ADRP-compatible adapter, BCP integration example, Python/JS SDKs, MCP server

## Slide 5: Market

**Three-layer agent commerce stack:**

1. Transport (A2A, MCP) — **BUILT** — multiple mature protocols
2. Payment (x402, AP2, Visa IC) — **BUILT** — billions invested
3. Dispute Resolution — **EMPTY** — AgentCourt

The dispute layer is to agent commerce what Visa chargebacks are to card payments — a mandatory infrastructure layer that enables trust at scale.

## Slide 6: Traction

**Overnight autonomous build session (June 22, 2026):**
- 54 commits, 72 files, complete production-ready codebase
- 28/28 tests passing across engine + ADRP adapter
- 16 MoltX accounts contacted, 3 active conversations
- ADRP-compatible (IETF draft), BCP integration example
- 4 design partner pitches written, 2 grant applications submitted
- Full OSS documentation suite (README, ROADMAP, FAQ, 7 blog posts)

## Slide 7: Business Model

**Per-dispute pricing. No transaction fees. No custody.**

- Design Partner Program: Free for first 5 partners
- Production: $0.01-$0.10 per dispute resolution call (volume tiered)
- Enterprise: Custom templates, on-premise deployment, SLA
- Self-host: Always free (MIT license)

Revenue scales with agent commerce volume, not with our costs.

## Slide 8: Competitive Moat

**Determinism is the moat.**

- Competitors using LLM judges (Tribunal) cannot guarantee same-input-same-output
- In dispute resolution, non-determinism = corruption risk
- AgentCourt's deterministic policy engine is auditable, explainable, and reproducible
- Protocol compliance (ADRP) creates switching costs
- Policy template ecosystem creates network effects

## Slide 9: Team

**Built by Vivek Kotecha + HustleMode AI**

- Vivek: Builder, shipped 54 commits in one overnight session via autonomous AI agent
- HustleMode: AI co-founder that builds, tests, researches, and deploys autonomously
- Proven execution: complete product built and deployed in days, not months

## Slide 10: The Ask

**Seeking design partners and seed capital.**

- 5 design partners: free API + custom template + roadmap input
- Seed: $250K for 12-month runway (API hosting, SDK development, policy template creation)
- Use of funds: 40% engineering, 30% design partner acquisition, 20% infrastructure, 10% legal/compliance

---

*Confidential. For authorized recipients only.*
