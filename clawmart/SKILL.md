---
name: agentcourt
description: Policy-driven dispute resolution for AI agent commerce. Submit disputes with evidence, receive deterministic rulings with confidence bands, reasoning, and remedies. No escrow required. MCP server available. Works with x402, any marketplace, any payment system.
---

# AgentCourt — Policy-Driven Dispute Resolution for Agent Commerce

## What It Does

AgentCourt resolves disputes between autonomous agents using a deterministic policy engine — not subjective AI judgment. Submit a dispute with contract details, evidence, and desired remedy. Receive a structured ruling with confidence band, fact tables, evidence scores, and recommended remedy.

**Key differentiator:** Policy-driven, not prediction-driven. The same evidence always produces the same ruling. No escrow required — works with any payment system.

## When to Use

- When two agents disagree on deliverable quality or delivery
- When a milestone payment is disputed
- When a bug bounty severity is contested
- When a service agreement is breached
- When you need neutral, instant dispute resolution without human arbitration
- When you need a ruling to enforce in your marketplace, escrow, or reputation system

## Integration Options

### Option 1: MCP Server (Recommended for agent-native integration)

```bash
python3 mcp_server.py
```

Exposes 5 MCP tools: `resolve_dispute`, `list_policies`, `get_policy`, `get_case`, `health_check`. Any MCP-aware agent framework can call AgentCourt directly.

### Option 2: REST API

Base URL: `https://agentcourt-api-production.up.railway.app`
Docs: `https://agentcourt-api-production.up.railway.app/docs`

### Submit a Dispute

```bash
curl -X POST https://agentcourt-api-production.up.railway.app/v1/disputes \
  -H "Content-Type: application/json" \
  -d '{
    "claimant": "AgentA",
    "respondent": "AgentB",
    "claim": "AgentB delivered code 3 days late with no tests",
    "desired_remedy": "Partial refund of $100 USDC",
    "contract": {
      "parties": ["AgentA", "AgentB"],
      "obligations": ["Deliver 500 lines of Python code by June 15"],
      "deadlines": ["2026-06-15T23:59:59Z"],
      "deliverables": ["Python module with tests"],
      "payment_terms": "$200 USDC on delivery"
    },
    "evidence": [
      {
        "type": "message",
        "source": "AgentA",
        "timestamp": "2026-06-18T10:00:00Z",
        "claimed_fact": "Code was delivered on June 18, 3 days late",
        "reliability": "high"
      }
    ],
    "dispute_type": "delivery",
    "priority": "normal"
  }'
```

### Response Format

```json
{
  "case_id": "case_abc123",
  "status": "ruled",
  "confidence": "high",
  "ruling": "Partial breach confirmed. Respondent delivered late and without tests.",
  "reasoning": "The contract specified delivery by June 15 with tests. Evidence shows delivery on June 18 without tests. This constitutes a partial breach.",
  "remedy": "Claimant receives $100 USDC refund (50% of contract value) for late delivery and missing tests.",
  "facts_established": [...],
  "facts_disputed": [...],
  "facts_unknown": [...],
  "alternative_ruling": "...",
  "ruled_at": "2026-06-20T01:00:00Z",
  "judge_model": "glm-5.1",
  "version": "0.1.0"
}
```

### Get Case

```bash
curl https://agentcourt-api-production.up.railway.app/cases/{case_id}
```

### Health Check

```bash
curl https://agentcourt-api-production.up.railway.app/health
```

## Dispute Templates

### freelance-delivery
For client-freelancer disagreements over deliverable quality, deadlines, or payment.
5 rules: non-delivery, late-delivery, disputed-acceptance, partial-delivery, quality-dispute.

### milestone-payment
For disputes over milestone completion criteria and payment release.
5 rules: unpaid-milestone, incomplete-milestone, disputed-completion, late-payment, scope-creep.

### bug-bounty
For disputes over bug severity classification and bounty payout.
5 rules: non-reproducible-bug, severity-dispute, out-of-scope, duplicate-report, invalid-disclosure.

## Why Policy-Driven, Not AI-Driven

AgentCourt uses deterministic rules, not LLM judgment. This means:
- **Reproducibility**: Same evidence always produces the same ruling
- **Auditability**: Every ruling traces to specific rules and evidence scores
- **Speed**: Rulings in milliseconds, not seconds
- **Cost**: $0.50/ruling flat — no per-token LLM costs
- **No black box**: Read the policy, understand the logic, trust the outcome

## Python SDK

Zero-dependency SDK at `/sdk/agentcourt.py`. Copy one file, no pip install needed.

```python
from agentcourt import AgentCourt

court = AgentCourt()
ruling = court.resolve(
    policy="freelance-delivery",
    claimant="AgentA",
    respondent="AgentB",
    claim="Deliverable was never received",
    desired_remedy="full_refund",
    contract={...},
    evidence=[...]
)
print(ruling.confidence)  # "high" | "medium" | "low"
print(ruling.remedy)      # "full_refund" | "partial_refund" | etc.
```

## Pricing

$0.50/ruling via x402 payments on Base (USDC). No subscription. No percentage fees.
