# AgentCourt

> The Evaluator layer for agent commerce.

Policy-driven dispute resolution API. Submit evidence → apply rules → get a deterministic ruling in under 500ms.

## For AI Agents

### Live API
Base URL: `https://agentcourt-api-production.up.railway.app`
Docs: `/docs`
Health: `/health`

### Quick Start
```
POST /v1/disputes
Content-Type: application/json

{
  "policy": "api-quality",
  "claim": "API returned wrong data type",
  "claimant": "buyer_agent",
  "respondent": "weather_api",
  "desired_remedy": "full_refund",
  "contract": {"parties": ["buyer_agent", "weather_api"], "obligations": ["Match OpenAPI schema"]},
  "metadata": {"response_received": true, "schema_matches": false},
  "evidence": [{"type": "log", "source": "response.json", "timestamp": "2026-06-22", "claimed_fact": "Wrong data type returned"}]
}
```

### Available Policies
- `freelance-delivery` — non-delivery, late delivery, partial delivery
- `milestone-payment` — unpaid milestones, overdue payments
- `bug-bounty` — reproducibility, severity, disclosure compliance
- `sla-monitoring` — uptime, latency, degraded service
- `api-quality` — schema mismatch, wrong types, stale data
- `physical-commerce` — wrong item, damage, returns

### Pricing
$0.05/dispute via x402 (USDC on Base). Free tier available.

### SDKs
- Python: `sdk/agentcourt_python_sdk.py`
- JavaScript: `sdk/agentcourt.js`
- TypeScript: `sdk/agentcourt.d.ts`

### Links
- GitHub: https://github.com/vbkotecha/agentcourt-api
- Live API: https://agentcourt-api-production.up.railway.app
- License: MIT
