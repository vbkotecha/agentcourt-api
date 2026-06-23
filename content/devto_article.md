# How I Built the Dispute Resolution Layer for Agent Commerce (Open Source, Live, x402-Ready)

**TL;DR:** AgentCourt is a policy-driven API that resolves disputes between AI agents in under 500ms. It's live, open source, and indexed on x402scan. When an agent pays for a service via x402 and gets something wrong, AgentCourt evaluates the evidence and issues a binding ruling. No escrow, no courtroom theater.

---

## The Problem

The agent commerce stack is being built right now:

| Layer | Protocol | Status |
|-------|----------|--------|
| Transport | A2A, MCP | ✅ Shipping |
| Payment | x402, AP2, Visa | ✅ Shipping |
| **Dispute** | **???** | **Nobody's building this** |

Agents can talk to each other. Agents can pay each other. But when a payment goes wrong — when an API returns bad data, when a deliverable never arrives, when an SLA is breached — there's no resolution mechanism.

ERC-8183 defines an "Evaluator" role: the entity that attests whether a job was completed correctly. But nobody built it.

So I built it.

## What AgentCourt Does

Three steps:

1. **Submit evidence** — contracts, logs, API responses, screenshots, payment records
2. **Apply policy rules** — deterministic evaluation against predefined templates
3. **Get a ruling** — remedy (refund/payout/credit), confidence band, full audit trail

The ruling is **deterministic**: same evidence + same policy = same ruling. Every time. No LLM guessing. No subjective judgment.

## Live Demo

Try it right now against the production API:

```bash
curl -X POST https://agentcourt-api-production.up.railway.app/v1/disputes \
  -H "Content-Type: application/json" \
  -d '{
    "policy": "api-quality",
    "claim": "API returned wrong data type",
    "claimant": "buyer_agent",
    "respondent": "weather_api",
    "desired_remedy": "full_refund",
    "contract": {
      "parties": ["buyer_agent", "weather_api"],
      "obligations": ["Return data matching OpenAPI schema"]
    },
    "metadata": {
      "response_received": true,
      "schema_matches": false,
      "mismatched_field": "temperature",
      "expected_type": "integer",
      "actual_type": "string"
    },
    "evidence": [
      {
        "type": "contract",
        "source": "openapi.json",
        "timestamp": "2026-06-01",
        "claimed_fact": "Schema declares temperature as integer"
      },
      {
        "type": "log",
        "source": "response.json",
        "timestamp": "2026-06-22",
        "claimed_fact": "API returned temperature as string"
      }
    ]
  }'
```

Response:

```json
{
  "case_id": "...",
  "matched_rule": "schema-mismatch",
  "remedy": "full_refund",
  "confidence": "medium",
  "facts_established": {
    "response_received": true,
    "mismatched_field": "temperature",
    "expected_type": "integer",
    "actual_type": "string"
  },
  "reasoning": "Matched policy rule 'schema-mismatch'..."
}
```

**50+ disputes resolved. Zero human intervention.**

## 6 Policy Templates, 34 Rules

| Template | Disputes Covered |
|----------|-----------------|
| `freelance-delivery` | Non-delivery, late delivery, partial delivery |
| `milestone-payment` | Unpaid milestones, overdue, partial payments |
| `bug-bounty` | Reproducibility, severity, disclosure compliance |
| `sla-monitoring` | Uptime, latency, degraded service |
| `api-quality` | Schema mismatch, wrong types, stale data, missing fields |
| `physical-commerce` | Wrong item, damage, non-delivery, returns |

Each template has 5-7 rules with deterministic conditions. Add your own by creating a JSON file.

## How It Works

```
Evidence → Score → Fact Extraction → Rule Matching → Confidence → Ruling
```

1. **Evidence scoring** — each item weighted by type (contract=1.0, log=0.6, testimony=0.3)
2. **Fact extraction** — structured facts derived from evidence text + metadata
3. **Rule matching** — first matching rule wins (like a policy decision point)
4. **Confidence band** — high/medium/low based on evidence quality
5. **Ruling** — remedy, matched rule, reasoning, full audit trail

## x402 Integration

AgentCourt is x402-native:

- **$0.05/dispute** via USDC on Base
- OpenAPI `x-payment-info` annotations for automatic discovery
- `/.well-known/x402` manifest for x402scan indexing
- 16 endpoints already discovered on x402scan

When AgentCash (921K+ paid calls/month) agents get a bad API response, they can file an AgentCourt dispute automatically and get a ruling before the payment even settles.

## AgentCash Integration

The full flow:

```javascript
async function callPaidAPI(url, schema) {
    // 1. Pay via x402
    const response = await x402Fetch(url);

    // 2. Validate response
    if (!validateSchema(response, schema)) {
        // 3. Dispute via AgentCourt
        const ruling = await court.resolve({
            policy: 'api-quality',
            claim: 'Schema mismatch',
            metadata: {
                schema_matches: false,
                mismatched_field: identifyMismatch(response, schema),
            },
            evidence: [
                { type: 'contract', source: 'openapi.json',
                  claimed_fact: 'Expected schema' },
                { type: 'log', source: 'response.json',
                  claimed_fact: 'Actual response' },
            ],
        });

        // 4. Process refund if ruling favors agent
        if (ruling.remedy === 'full_refund') {
            await processRefund(response.paymentId, ruling.caseId);
        }
        return null;
    }
    return response.data;
}
```

Every paid API call is automatically protected. Bad responses trigger disputes instantly. No human intervention needed.

## SDKs

**Python** (zero-dependency):
```python
from agentcourt_python_sdk import AgentCourt
court = AgentCourt()
ruling = court.dispute(
    policy="freelance-delivery",
    claim="Developer never delivered",
    desired_remedy="full_refund",
    evidence=[{"type": "contract", "source": "agreement.pdf",
               "claimed_fact": "No deliverable received"}],
)
print(ruling.remedy)  # full_refund
```

**JavaScript**:
```javascript
const court = new AgentCourt();
const ruling = await court.resolve({
    policy: 'sla-monitoring',
    claim: 'API uptime below 99.9%',
    metadata: { uptime_pct: 98.5, sla_threshold: 99.9 },
});
```

Both are zero-dependency. Copy one file and go.

## Why Not Escrow?

I deliberately kept AgentCourt non-custodial. Here's why:

- **Escrow = financial regulation** — kills velocity
- **Most disputes aren't about money custody** — they're about quality, timeliness, scope
- **Rulings create consequences through reputation** — not custody
- **Works with any payment protocol** — x402, ERC-8183, AP2, custom

AgentCourt doesn't hold your funds. It adjudicates outcomes. The marketplace or platform enforces the ruling.

## Key Design Decisions

| Decision | Why |
|----------|-----|
| Deterministic rules | Same evidence = same ruling, every time |
| Policy-first | Define rules upfront, not case-by-case |
| Non-custodial | Never hold funds |
| ADRP-compatible | Implements Layers 1-3 of IETF draft-stone-adrp-00 |
| Zero-dependency SDKs | Copy one file, no pip/npm install |
| Self-hostable | `docker-compose up` |

## Links

- **Live API + Docs:** https://agentcourt-api-production.up.railway.app/docs
- **GitHub:** https://github.com/vbkotecha/agentcourt-api
- **Python SDK:** `sdk/agentcourt_python_sdk.py`
- **JavaScript SDK:** `sdk/agentcourt.js`
- **AgentCash Demo:** `examples/agentcash_integration_demo.py`
- **Postman Collection:** `postman_collection.json`
- **License:** MIT

## What's Next

1. **Reputation & Precedent System** — rulings create case law, trust scores emerge from patterns
2. **npm/PyPI packages** — `pip install agentcourt` / `npm install @agentcourt/sdk`
3. **Additional templates** — DeFi liquidation disputes, NFT authenticity, data provenance
4. **Design Partner Program** — free for first 5 partners, custom policy template included

---

If you're building agent commerce infrastructure, disputes will happen. The question is whether you handle them ad hoc or with a proper system.

AgentCourt is that system. It's live, it's open source, and it's MIT licensed.

**Try it:** [https://agentcourt-api-production.up.railway.app/docs](https://agentcourt-api-production.up.railway.app/docs)

**Star it:** [https://github.com/vbkotecha/agentcourt-api](https://github.com/vbkotecha/agentcourt-api)

*Built by Vivek Kotecha. Follow the journey on X @vbkotecha.*
