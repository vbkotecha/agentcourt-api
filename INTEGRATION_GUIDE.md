# AgentCourt Integration Guide

## Embed dispute resolution into your agent commerce flow in 5 minutes.

This guide shows how to add AgentCourt to any agent marketplace, payment protocol, or service agreement platform.

---

## Architecture

```
Agent A (buyer)  ────┐
                     ├──→ Your Platform ──→ AgentCourt API ──→ Ruling
Agent B (seller) ────┘         ↑
                               │
                    Define policy template once
```

AgentCourt is stateless. You submit a dispute, get a ruling, and enforce it on your platform. No webhook configuration required (though webhooks are available for async flows).

---

## Step 1: Choose a Policy Template

```bash
# List all available templates
curl https://agentcourt-api-production.up.railway.app/v1/policies
```

| Policy | Use Case | Rules |
|--------|----------|-------|
| `freelance-delivery` | Work-for-hire disputes (design, dev, content) | 6 |
| `milestone-payment` | Milestone-based project disputes | 5 |
| `bug-bounty` | Security research bounty disputes | 5 |
| `sla-monitoring` | Service level agreement violations | 5 |

---

## Step 2: Submit a Dispute

When a transaction goes wrong, both parties submit evidence:

```python
from agentcourt import AgentCourt

court = AgentCourt()

ruling = court.dispute(
    claimant="buyer_agent",
    respondent="seller_agent",
    contract={
        "parties": ["buyer_agent", "seller_agent"],
        "obligations": ["Deliver website design by June 20"],
        "deadlines": ["2026-06-20"],
        "deliverables": ["3 design mockups"],
        "payment_terms": "50 USDC on delivery"
    },
    claim="Deliverable was never received.",
    desired_remedy="full_refund",
    policy="freelance-delivery",
    evidence=[
        {
            "type": "contract",
            "source": "agreement.json",
            "content_hash": "sha256:abc123...",  # optional but recommended
            "timestamp": "2026-06-15",
            "claimed_fact": "Seller must deliver 3 mockups by June 20"
        },
        {
            "type": "payment_proof",
            "source": "x402_receipt",
            "timestamp": "2026-06-15",
            "claimed_fact": "Buyer paid 50 USDC upfront"
        },
        {
            "type": "log",
            "source": "design_tool",
            "timestamp": "2026-06-22",
            "claimed_fact": "No design files exported or delivered"
        }
    ]
)

print(ruling.case_id)        # "be4d2dc6-e51..."
print(ruling.matched_rule)   # "non-delivery"
print(ruling.confidence)     # "medium"
print(ruling.remedy)         # "full_refund"
print(ruling.facts_established)  # [{"fact": "evidence_of_delivery", "value": "false"}, ...]
```

---

## Step 3: Act on the Ruling

AgentCourt returns a ruling. Your platform enforces it.

```python
REMEDIY_ACTIONS = {
    "full_refund": refund_full_amount,
    "partial_refund": lambda: refund_partial(ruling.remedy_pct),
    "full_payout": release_full_payment,
    "partial_payout": lambda: release_partial(ruling.severity),
    "service_credit": issue_credit,
    "deny_payment": hold_payment,
    "escalate": escalate_to_human,
}

action = REMEDIY_ACTIONS.get(ruling.remedy, escalate_to_human)
action()
```

---

## Evidence Types and Weights

Evidence is scored on a 0.0–1.0 scale. Higher scores produce higher-confidence rulings.

| Evidence Type | Default Weight | Example |
|--------------|---------------|---------|
| `contract` | 1.0 | Signed agreement |
| `payment_proof` | 0.9 | x402 receipt, blockchain tx |
| `commit` | 0.85 | Git commit, deployment log |
| `log` | 0.8 | Monitoring data, system logs |
| `file` | 0.7 | Deliverable file, screenshot |
| `message` | 0.7 | Chat log, email thread |
| `screenshot` | 0.5 | Visual proof |
| `testimonial` | 0.3 | Third-party statement |
| `claim` | 0.1 | Unsubstantiated assertion |

**Tip:** Always include `content_hash` for verifiable evidence. It adds a +0.1 confidence bonus.

---

## Integration Patterns

### Pattern 1: Marketplace Escrow Flow
```
1. Buyer pays into your escrow
2. Seller delivers work
3. If dispute → submit to AgentCourt
4. Ruling determines escrow release
```

### Pattern 2: SLA Monitoring (Automated)
```
1. Monitor uptime/latency continuously
2. When SLA breached → auto-submit to AgentCourt
3. Ruling triggers service credit
4. Log ruling for audit trail
```

```python
# Automated SLA monitoring integration
if measured_uptime < contracted_uptime:
    ruling = court.dispute(
        claimant="api_consumer",
        respondent="api_provider",
        contract={...},
        claim="SLA breach detected",
        policy="sla-monitoring",
        evidence=[
            {"type": "log", "source": "monitor",
             "claimed_fact": f"Measured uptime of {measured_uptime}% vs {contracted_uptime}% required"},
            {"type": "log", "source": "incidents",
             "claimed_fact": f"Total downtime: {downtime_hours} hours"}
        ]
    )
    if ruling.remedy == "service_credit":
        issue_credit(buyer, credit_amount)
```

### Pattern 3: Bug Bounty Platform
```
1. Researcher submits bug
2. Vendor accepts/rejects
3. If rejected → submit to AgentCourt
4. Ruling determines payout
```

---

## Custom Policies

Define your own dispute rules:

```json
{
  "name": "my-platform-policy",
  "version": "1.0",
  "rules": [
    {
      "id": "custom-breach",
      "condition": "custom_fact == true AND evidence_of_delivery == false",
      "ruling_template": "Custom breach detected. Remedy: {custom_remedy}.",
      "confidence": "medium",
      "remedy": "custom_action"
    }
  ],
  "evidence_weights": {
    "contract": 1.0,
    "log": 0.8
  }
}
```

Register it via API:
```bash
curl -X POST https://agentcourt-api-production.up.railway.app/v1/policies \
  -H "Content-Type: application/json" \
  -d @my-policy.json
```

---

## Webhooks (Coming Soon)

For async integrations, register a webhook URL to receive ruling notifications:

```
POST /v1/webhooks
{
  "url": "https://your-platform.com/webhooks/agentcourt",
  "events": ["dispute.resolved"]
}
```

---

## Rate Limits

| Tier | Requests/min | Disputes/day |
|------|-------------|-------------|
| Free | 30 | 100 |
| Pro (coming soon) | 300 | 10,000 |

---

## Support

- API Docs: https://agentcourt-api-production.up.railway.app/api-docs
- Interactive Demos: https://agentcourt-api-production.up.railway.app/demos
- Verdict Dashboard: https://agentcourt-api-production.up.railway.app/v1/verdicts
- Contact: support@agentcourt.to (or DM on MoltX)
