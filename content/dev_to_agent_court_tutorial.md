# Build an x402-Powered Dispute Resolution System for Your AI Agents

When AI agents transact autonomously via x402 payments, things will go wrong. An agent pays for an API call, gets a schema mismatch, and... there's no chargeback mechanism. No dispute process. No resolution.

That's why I built **AgentCourt** — an open-source, policy-driven dispute resolution API that processes agent commerce disputes in under 500ms.

## What AgentCourt Does

AgentCourt evaluates disputes between agents (or humans) using deterministic policy templates. No ML, no opinions — just rules.

**7 policy templates available:**
- `api-quality` — schema mismatches, wrong response formats
- `freelance-delivery` — non-delivery of work
- `milestone-payment` — disputed milestone completions  
- `bug-bounty` — disputed bug severity and payout
- `sla-monitoring` — uptime violations
- `scope-dispute` — project scope exceedance
- `physical-commerce` — damaged/wrong items

## Quick Start (30 Seconds)

```bash
# File a dispute (free tier — 100/month)
curl -X POST https://agentcourt-api-production.up.railway.app/v1/disputes \
  -H "Content-Type: application/json" \
  -d '{
    "policy": "api-quality",
    "claim": "Response schema does not match agreed format",
    "claimant": "buyer-agent",
    "respondent": "seller-api",
    "desired_remedy": "full_refund",
    "contract": {
      "parties": ["buyer-agent", "seller-api"],
      "obligations": ["return JSON with fields: id, name, price"]
    },
    "metadata": {
      "response_received": true,
      "schema_matches": false
    },
    "evidence": [
      {
        "type": "log",
        "source": "api-monitor",
        "timestamp": "2026-06-23T10:00:00Z",
        "claimed_fact": "Response was XML, not JSON"
      }
    ]
  }'
```

**Response:**
```json
{
  "case_id": "case_abc123",
  "policy": "api-quality",
  "ruling": "full_refund",
  "confidence": 0.95,
  "reasoning": "Schema mismatch confirmed: response format violates contract obligation"
}
```

## How It Works

1. **Define the contract** — What were the parties supposed to do?
2. **Submit metadata** — Structured facts (did they deliver? did the schema match?)
3. **Submit evidence** — Logs, screenshots, timestamps
4. **Get a ruling** — Deterministic, <500ms, same inputs = same output

## Why Deterministic?

Human arbitration takes days and costs hundreds of dollars. AgentCourt rulings are instant because they're rule-based, not opinion-based. The same evidence will always produce the same ruling.

This makes AgentCourt rulings auditable, predictable, and — importantly — cheap enough for agent-scale micro-transactions.

## x402 Integration

AgentCourt is x402-native. The `/.well-known/x402` manifest is live:

```json
{
  "name": "AgentCourt",
  "network": "base-mainnet",
  "currency": "USDC",
  "endpoints": [
    {"path": "/v1/disputes", "method": "POST", "price": "$0.05"},
    {"path": "/v1/policies", "method": "GET", "price": "$0.00"},
    {"path": "/v1/verdicts", "method": "GET", "price": "$0.00"}
  ],
  "free_tier": {"requests_per_month": 100}
}
```

Agents can discover AgentCourt via x402 protocol, try 100 disputes free, then pay $0.05 USDC per dispute on Base.

## Links

- **Live API:** https://agentcourt-api-production.up.railway.app/docs
- **GitHub:** https://github.com/vbkotecha/agentcourt-api
- **Landing:** https://vbkotecha.github.io/agentcourt-api/
- **Tutorial:** https://github.com/vbkotecha/agentcourt-api/discussions/2

MIT licensed. Self-hostable. Production-ready.

---

*AgentCourt is the only dispute resolution service in the entire x402 ecosystem. If your agents are transacting, they need a court.*
