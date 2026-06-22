# Agent Commerce Needs a Court, Not Escrow

**The case for policy-driven dispute resolution in the age of AI agents**

---

AI agents are starting to transact.

They're buying API access. Hiring other agents. Delivering work. Moving money. Making decisions with real financial consequences.

But there's a missing layer nobody's talking about.

## What happens when the agent is wrong?

Today, the answer is: **nothing good**.

- The buyer files a support ticket. Waits 5 business days. Gets a form response.
- The marketplace manually reviews the case. Takes 2 weeks. Rules inconsistently.
- The seller gets charged back. Disputes it. The cycle continues.

Or worse: nothing happens at all. No dispute mechanism exists. The buyer eats the cost. Trust erodes. The marketplace becomes a ghost town.

## The escrow illusion

The standard answer to this problem is escrow. Hold the money until both parties are satisfied.

But escrow doesn't solve disputes. **Escrow creates hostage situations.**

- Seller delivers work. Buyer claims it's not good enough. Money sits in escrow forever.
- Buyer pays upfront. Seller disputes the quality bar. Who decides what "done" means?
- Agent delivers output. The other agent disagrees. Now two bots are arguing over a locked wallet.

Escrow answers the wrong question. The real question isn't "who has the money?" — it's **"who's right?"**

That's a policy question, not a custody question.

## Policy-driven dispute resolution

This is the principle behind AgentCourt: **define the rules, evaluate the evidence, issue a ruling.**

Here's how it works:

### 1. Submit evidence

Contracts, commits, logs, timestamps, chat transcripts, payment records, screenshots, hashes. Any artifact that proves what happened.

### 2. Apply policy rules

Policy templates define what constitutes a valid dispute and what the remedy should be. For example:

- **Non-delivery**: If no deliverable was produced by the deadline → full refund
- **Late delivery**: If delivery was late but accepted → partial refund based on days late
- **Unpaid milestone**: If milestone was completed but payment is overdue → payment plus penalty
- **Non-reproducible bug**: If a bug claim can't be reproduced after N attempts → claim denied

Rules are explicit, deterministic, and auditable.

### 3. Get a ruling

The engine evaluates the evidence against the policy rules and produces:

- **Confidence band** (high / medium / low) — based on evidence quality and fact completeness
- **Ruling text** — human-readable explanation
- **Remedy** — what should happen next
- **Full audit trail** — which facts were established, which evidence supported them

## Why this works without escrow

Rulings create consequences through **reputation, precedent, and enforcement APIs** — not through custody.

- A marketplace can enforce rulings by adjusting seller ratings
- A protocol can use precedent to inform future automated resolutions
- A platform can integrate enforcement via webhooks

The ruling is the product. Escrow is just plumbing.

## The API is live

AgentCourt's API is live and publicly accessible:

```
POST https://agentcourt-api-production.up.railway.app/v1/disputes
```

Submit a dispute with evidence and a policy template. Get a ruling back in milliseconds.

Three policy templates are available today:
- **freelance-delivery** — disputes over digital work delivery
- **milestone-payment** — disputes over milestone payments
- **bug-bounty** — disputes over bug bounty claims

## The thesis

Agent commerce will be bigger than e-commerce. But it won't happen without trust infrastructure.

The internet didn't scale commerce because of escrow. It scaled because of **credit card chargebacks, merchant ratings, dispute resolution processes, and buyer protection policies**.

Agent commerce needs the same primitives — but programmable, deterministic, and API-native.

That's what AgentCourt is.

---

**We're looking for 5 design partners.** If you're building agent marketplaces, x402 payment flows, or AI service platforms, we want to talk. DM @vbkotecha or reach out at hello@agentcourt.to.

**Try the API:** [agentcourt-api-production.up.railway.app/docs](https://agentcourt-api-production.up.railway.app/docs)
