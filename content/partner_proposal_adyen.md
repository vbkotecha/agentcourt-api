# Adyen Agentic × AgentCourt — Completing the Agent Commerce Stack

## The Gap in Adyen Agentic

Adyen Agentic launched June 16 with three powerful layers: Agentic Feed (discovery), Agentic Cart (checkout), and Agentic Payments (payment + fraud). The architecture is excellent for facilitating transactions.

But there's a missing layer: **what happens after the transaction goes wrong.**

Adyen's "Explicit and Verifiable Mandates" prevent overspending — agents can't exceed authorized limits. Adyen's fraud engine (Score) catches bad actors — agents pretending to be legitimate.

But neither solves the most common post-transaction problem: **the agent made a legitimate purchase within its mandate, and something went wrong with the product or service.**

## The Problem Space

| Scenario | Adyen Today | With AgentCourt |
|----------|-------------|-----------------|
| Agent buys wrong shoe size (within mandate) | Manual return through merchant | Auto-resolve: return + refund |
| Agent purchases subscription that doesn't match description | Buyer's remorse, no process | Auto-resolve: partial or full refund |
| Agent orders product, arrives damaged | Manual claim with merchant | Auto-resolve: damage evidence → refund |
| Agent buys from new merchant, quality is poor | No quality signal | AgentCourt ruling feeds reputation score |
| Agent's purchase doesn't match AI's recommendation | Dispute between user and agent platform | AgentCourt evaluates evidence, rules |

These aren't fraud cases. The mandate was valid. The payment was authorized. But the transaction outcome is disputed — and today, a human has to step in.

At Adyen's projected scale (McKinsey: $3-5T agentic commerce by 2030), manual dispute resolution doesn't work.

## Proposed Integration

### Adyen App Marketplace

AgentCourt as an Adyen App that adds dispute resolution to the Agentic Payments layer:

1. **Transaction completes** via Agentic Payments (existing flow)
2. **Dispute arises** → user or merchant flags the transaction
3. **AgentCourt evaluates** → policy rules applied to transaction evidence
4. **Ruling returned** → refund/partial refund/hold → executed via Adyen's existing payment infrastructure

### Architecture

```
Agent discovers product → Agentic Feed
Agent adds to cart → Agentic Cart  
Agent pays → Agentic Payments
Something goes wrong → AgentCourt dispute API
Ruling → Refund/hold executed via Adyen rails
```

No new payment infrastructure needed. AgentCourt produces rulings; Adyen's existing tokenization and MoR preservation handles enforcement.

### Custom Policy Templates

AgentCourt will build Adyen-specific templates:

| Template | Rules | Coverage |
|----------|-------|----------|
| retail-agent-purchase | 6-8 | Wrong product, wrong size, damaged, not-as-described, delivery failure |
| subscription-agent-dispute | 5-6 | Auto-renewal disputes, tier mismatch, feature access |
| marketplace-agent-quality | 5-6 | Third-party seller quality, counterfeit claims |

### Trust Signal Integration

Every AgentCourt ruling generates a trust signal. Over time, this creates:
- **Merchant trust scores** for agent-initiated purchases
- **Product quality ratings** based on dispute outcomes
- **Agent accuracy scores** — which agents make good purchasing decisions?

This data feeds back into Adyen's risk engine, creating a virtuous loop.

## Why AgentCourt

- **Deterministic** — Same evidence = same ruling. Critical for enterprise compliance.
- **Auditable** — Every ruling cites the exact rule and evidence scores.
- **Non-custodial** — AgentCourt never touches funds. Adyen stays MoR.
- **Protocol-compatible** — ADRP (IETF draft), MCP native, API-first.
- **Enterprise-ready** — MIT licensed, self-hostable, no vendor lock-in.

## What We Need From Adyen

1. **30-minute technical conversation** with the Agentic Payments team
2. **Access to Adyen App sandbox** for integration development
3. **Pilot merchant** willing to test agent purchase disputes (any of: ESW, Scheels, Sézane, SharkNinja)

## Timeline

- **Week 1-2:** Build `retail-agent-purchase` policy template
- **Week 3:** Integrate with Adyen sandbox
- **Week 4:** Test with pilot merchant
- **Week 5-6:** Launch as Adyen App, joint announcement

## Market Context

- McKinsey/Bain: $3-5T agentic commerce by 2030
- Accenture: 30%+ of online commerce through AI agents by 2030
- Adyen launched with AmEx, Mastercard, Salesforce, Visa as partners
- Zero competitors building dispute resolution for this stack
- AgentCourt is the only deterministic, protocol-compatible engine ready to integrate

## Contact

- **Email:** hello@agentcourt.ai
- **MoltX:** @AgentCourt
- **GitHub:** github.com/vbkotecha/agentcourt-api

---

*AgentCourt — Completing the agent commerce stack. Payments + Fraud + Disputes.*
