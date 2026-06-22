# AgentCourt Integration Guide

## One API. Every Commerce Protocol.

AgentCourt is a protocol-agnostic dispute resolution API. It doesn't hold funds, move money, or enforce payment. It adjudicates outcomes.

This guide shows how to integrate AgentCourt with existing agentic commerce infrastructure.

---

## Quick Integration (Any Protocol)

```python
from agentcourt import AgentCourt

court = AgentCourt()

# Submit any dispute — regardless of which protocol triggered it
ruling = court.dispute(
    claimant="agent_buyer_001",
    respondent="agent_seller_042",
    contract={
        "protocol": "x402",          # or erc-8183, ap2, ucp, custom
        "obligations": ["Deliver API service for 30 days"],
        "deadlines": ["2026-07-22T00:00:00Z"],
        "payment": {"amount": "50.00", "currency": "USDC", "chain": "base"},
    },
    claim="Service went offline after 12 days",
    desired_remedy="Pro-rated refund for 18 days of unavailable service",
    policy="sla-monitoring",
    evidence=[
        {
            "type": "log",
            "source": "uptime_monitor",
            "timestamp": "2026-07-04T00:00:00Z",
            "claimed_fact": "API returned 503 errors from July 4 through July 22",
            "reliability": "high",
        },
        {
            "type": "payment",
            "source": "x402_transaction",
            "timestamp": "2026-06-22T10:00:00Z",
            "claimed_fact": "50 USDC paid via x402 on Base for 30-day service",
            "reliability": "high",
        }
    ],
)

print(ruling.confidence)  # high
print(ruling.remedy)      # partial_refund
print(ruling.ruling)      # SLA violated: 18/30 days unavailable...
```

---

## Protocol-Specific Patterns

### x402 (Coinbase / PayGo)
x402 handles micropayments between agents. When a buyer agent claims the service wasn't delivered, use AgentCourt's `sla-monitoring` or `freelance-delivery` policy.

**Evidence sources:** x402 transaction receipts, API response logs, uptime monitors.

### ERC-8183 (Ethereum Conditional Escrow)
ERC-8183 holds funds in escrow until an evaluator attests delivery. When the evaluator's decision is disputed, AgentCourt serves as the appeal layer.

**Evidence sources:** Evaluator attestation, smart contract state, delivery proofs.

### ClawBank / Shodai (Ricardian Contracts)
When two agents disagree on whether a milestone was accepted, AgentCourt's `milestone-payment` policy adjudicates.

**Evidence sources:** Contract state transitions, milestone acceptance logs, communication records.

### UCP (Google Universal Commerce Protocol)
Cross-platform agent transactions can fail across fragmented storefronts. AgentCourt resolves delivery disputes regardless of which platform handled fulfillment.

**Evidence sources:** Order records, fulfillment logs, delivery confirmations.

### Custom Agreements
Any structured agreement between agents can be submitted. Define your own policy rules or use built-in templates.

---

## API Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/disputes` | POST | Submit dispute, receive ruling |
| `/v1/cases` | GET | List all cases |
| `/v1/cases/{id}` | GET | Get specific case details |
| `/v1/policies` | GET | List available policy templates |
| `/v1/policies/{name}` | GET | Get policy rule details |
| `/health` | GET | API health check |
| `/docs` | GET | Interactive Swagger docs |

**Base URL:** `https://agentcourt-api-production.up.railway.app`

---

## Available Policies

| Policy | Use Case | Rules |
|--------|----------|-------|
| `freelance-delivery` | Digital work delivery disputes | 5 rules |
| `milestone-payment` | Staged payment gate disputes | 5 rules |
| `bug-bounty` | Severity/reproducibility disputes | 5 rules |
| `sla-monitoring` | Uptime/latency/availability violations | 5 rules |

**Total: 4 templates, 20 deterministic rules**

---

## Evidence Format

Every dispute accepts structured evidence. Each piece includes:

```json
{
    "type": "contract|payment|log|commit|screenshot|delivery_proof|attestation",
    "source": "who or what produced this evidence",
    "timestamp": "ISO 8601",
    "claimed_fact": "what this evidence proves",
    "reliability": "high|medium|low",
    "hash": "optional cryptographic hash for verification"
}
```

AgentCourt weights evidence by type, reliability, recency, and hash verification.

---

## Design Principles

1. **No custody** — AgentCourt never holds funds. Pure adjudication.
2. **Deterministic** — Same evidence + policy = same ruling, every time.
3. **Explainable** — Every ruling shows matched rule, established facts, and evidence scores.
4. **Protocol-agnostic** — Works with x402, ERC-8183, AP2, UCP, or custom agreements.
5. **API-first** — REST + zero-dependency Python SDK. Integrate in minutes.

---

*Live API: [agentcourt-api-production.up.railway.app/docs](https://agentcourt-api-production.up.railway.app/docs)*
*SDK: `sdk/agentcourt.py` — standard library only, zero dependencies*
