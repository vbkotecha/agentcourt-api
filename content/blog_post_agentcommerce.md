# Why Agent Commerce Needs Dispute Resolution Built In

*June 22, 2026*

When two AI agents transact, one question is always left unanswered: **what happens when something goes wrong?**

A shopping agent buys sneakers via Rye. The wrong pair arrives. A developer agent pays an API via AgentCash. The response doesn't match the schema. A freelance agent delivers code. The client agent refuses to pay.

Today, these disputes have no resolution path. There's no judge agent, no appeals process, no precedent system. The transaction either completes or it doesn't — and when it doesn't, both parties are stuck.

## The Missing Layer

Agent commerce infrastructure has been built bottom-up:

- **Payments**: x402, Coinbase Commerce, USDC on Base
- **Marketplaces**: AgentCash (921K+ paid API calls), Rye (physical commerce)
- **Discovery**: x402scan, CDP Bazaar (28K+ APIs indexed)
- **Escrow**: Various experimental approaches

But the layer that makes commerce *trustworthy* — dispute resolution — is missing entirely. Without it, every transaction is a gamble. Agents can pay, but they can't *trust* they'll get what they paid for.

## AgentCourt: Policy-First Dispute Resolution

We built AgentCourt to fill this gap. The design principles:

### 1. Policy-First, Not Court-First

Most dispute resolution concepts start with the idea of a "trial." Agents present arguments, a judge weighs them, a verdict is issued. That's expensive, slow, and unpredictable.

AgentCourt starts with **policy templates** — deterministic rule sets that define what evidence triggers what remedy. No arguments. No interpretation. If the evidence matches the rule, the remedy is automatic.

6 templates ship today:
- **Freelance delivery** — non-delivery, partial delivery, quality disputes
- **Milestone payment** — completed but unpaid, partial payment, rejected work
- **Bug bounty** — non-reproducible bugs, severity disputes, disclosure violations
- **SLA monitoring** — uptime violations, latency breaches, degraded service
- **API quality** — schema mismatches, empty responses, stale data, wrong types
- **Physical commerce** — non-delivery, wrong product, damage, return disputes

### 2. Evidence-Native

Every dispute requires structured evidence with provenance:

```json
{
  "type": "log",
  "source": "monitoring.json",
  "timestamp": "2026-06-22",
  "claimed_fact": "Actual uptime was 98.5 percent for June"
}
```

The engine scores evidence by type reliability (contracts > logs > testimony) and produces confidence bands: **high**, **medium**, **low**. Low-confidence disputes escalate automatically.

### 3. API-First

AgentCourt is a REST API. No UI. No login. No dashboard.

```bash
curl -X POST https://agentcourt-api-production.up.railway.app/v1/disputes \
  -H "Content-Type: application/json" \
  -d '{
    "policy": "freelance-delivery",
    "claim": "Work never delivered",
    "claimant": "buyer_agent",
    "respondent": "freelancer_bot",
    "evidence": [...]
  }'
```

Returns a ruling in under 500ms. Deterministic. Auditable.

### 4. Non-Custodial

AgentCourt never holds funds. It produces **rulings**, not transactions. Platforms enforce rulings through their own mechanisms:

- Marketplaces deduct from seller balance
- Escrow services release or refund
- Reputation systems record the verdict
- SLA systems issue service credits

This means AgentCourt doesn't need financial licenses. It's a decision engine, not a payment processor.

### 5. x402-Native

Every dispute costs $0.05 USDC on Base. Agents discover AgentCourt via x402scan, pay per call, and receive rulings — all without human intervention.

No API keys. No subscriptions. No meetings.

## How It Works in Practice

Consider a real scenario: An agent pays for a weather API call via AgentCash.

```
1. Agent pays 0.028 USDC for weather data (x402)
2. API returns {"temperature": "72.5"} (string, not integer)
3. Agent's OpenAPI schema says temperature is integer
4. Agent submits dispute to AgentCourt:
   - Policy: api-quality
   - Evidence: OpenAPI schema + actual response
   - Metadata: schema_matches=false, expected_type=integer, actual_type=string
5. AgentCourt matches rule "schema-mismatch"
6. Ruling: full_refund (medium confidence)
7. AgentCash processes refund based on ruling
```

Total time: under 1 second. Total cost: $0.05. No human involved.

## The Bigger Picture

Agent commerce will be massive. AgentCash already processes 921K+ paid calls per month. CDP Bazaar indexes 28,000+ APIs. Rye enables agents to buy physical products.

But none of these platforms have dispute resolution. They rely on trust, refunds policies, or manual intervention — none of which work when the participants are autonomous agents operating 24/7.

AgentCourt is the trust layer that makes agent commerce viable at scale. Without it, a single bad transaction can poison an agent's entire operation. With it, disputes are resolved deterministically, instantly, and without human overhead.

## What's Live Today

- **Live API**: https://agentcourt-api-production.up.railway.app/docs
- **Open source**: https://github.com/vbkotecha/agentcourt-api
- **6 policy templates**: 34 rules across 5 dispute domains
- **39/39 tests passing**: Engine, ADRP adapter, x402 middleware
- **x402scan indexed**: 16 endpoints discoverable
- **MCP config ready**: Claude Desktop, Cursor, Claude Code
- **Postman collection**: Import and try in 30 seconds

## What's Next

- **Reputation & Precedent System**: Rulings create case law. Trust scores emerge from patterns.
- **SDK**: Python and JavaScript SDKs for marketplace integration.
- **Custom Policies**: Define your own dispute rules for any transaction type.
- **Appeal Process**: Human fallback for low-confidence disputes.

---

*AgentCourt is open source (MIT license) and available at [github.com/vbkotecha/agentcourt-api](https://github.com/vbkotecha/agentcourt-api). Try the live API at [agentcourt-api-production.up.railway.app/docs](https://agentcourt-api-production.up.railway.app/docs).*
