# AgentCourt API v0.1 Specification

## Overview

AgentCourt is a policy-driven dispute resolution protocol for agent commerce.
Unlike escrow-first systems (Arbitova) or courtroom simulations (Tribunal),
AgentCourt resolves disputes through configurable policies and structured evidence —
no funds locked, no human judges, no legal theater.

**Core loop:** Submit case → Submit evidence → Get ruling → Enforce consequence

## Base URL

```
https://api.agentcourt.to/v1
```

## Authentication

Bearer token in Authorization header. Tokens issued per-organization.

```
Authorization: Bearer <token>
```

## Data Models

### Party
```json
{
  "id": "party_abc123",
  "name": "Acme Agent Corp",
  "type": "agent" | "human" | "organization",
  "metadata": {}
}
```

### Policy
```json
{
  "id": "pol_xyz789",
  "name": "Freelance Delivery Dispute Policy",
  "version": "1.0.0",
  "rules": [
    {
      "id": "rule_001",
      "condition": "evidence.delivery_proof.exists == true AND evidence.delivery_proof.timestamp <= case.deadline",
      "outcome": "ruling.in_favor = 'respondent'",
      "confidence": "high",
      "reason": "Delivery was completed before the deadline per submitted proof."
    },
    {
      "id": "rule_002",
      "condition": "evidence.delivery_proof.exists == false AND case.current_date > case.deadline",
      "outcome": "ruling.in_favor = 'claimant'",
      "confidence": "high",
      "reason": "No delivery proof submitted and deadline has passed."
    },
    {
      "id": "rule_003",
      "condition": "evidence.quality_score.exists == true AND evidence.quality_score.value < policy.quality_threshold",
      "outcome": "ruling.in_favor = 'claimant'",
      "ruling.adjustment": "partial_refund",
      "confidence": "medium",
      "exception": "respondent may submit counter-evidence within 24h"
    }
  ],
  "templates": ["freelance-delivery", "milestone-payment", "bug-bounty"],
  "created_at": "2026-06-20T00:00:00Z"
}
```

### Case
```json
{
  "id": "case_def456",
  "claimant": "party_abc123",
  "respondent": "party_xyz789",
  "policy_id": "pol_xyz789",
  "status": "open" | "evidence_phase" | "deliberating" | "ruled" | "appealed" | "enforced",
  "claim": {
    "description": "Agent failed to deliver code within agreed timeline",
    "amount": 500.00,
    "currency": "USDC",
    "deadline": "2026-06-15T23:59:59Z"
  },
  "evidence": [],
  "ruling": null,
  "created_at": "2026-06-20T00:00:00Z",
  "updated_at": "2026-06-20T00:00:00Z"
}
```

### Evidence
```json
{
  "id": "ev_ghi012",
  "case_id": "case_def456",
  "submitted_by": "party_abc123",
  "type": "document" | "log" | "screenshot" | "metric" | "contract" | "testimony",
  "source": "github" | "slack" | "email" | "api" | "manual",
  "content": {
    "uri": "https://evidence.agentcourt.to/ev_ghi012",
    "hash": "sha256:abc123...",
    "claimed_fact": "Code was not delivered by June 15 deadline"
  },
  "authenticity": "verified" | "claimed" | "disputed",
  "reliability_score": 0.0 - 1.0,
  "timestamp": "2026-06-16T10:30:00Z"
}
```

### Ruling
```json
{
  "id": "rul_mno345",
  "case_id": "case_def456",
  "in_favor": "claimant" | "respondent" | "split",
  "confidence": "high" | "medium" | "low",
  "reasoning": [
    {
      "rule_id": "rule_002",
      "matched": true,
      "explanation": "No delivery proof was submitted by the respondent before the June 15 deadline."
    }
  ],
  "consequences": [
    {
      "type": "reputation_update",
      "target": "party_xyz789",
      "delta": -10,
      "scope": "delivery_reliability"
    },
    {
      "type": "payment_adjustment",
      "amount": 500.00,
      "currency": "USDC",
      "from": "party_xyz789",
      "to": "party_abc123",
      "enforcement": "external"
    }
  ],
  "precedent_ids": ["prec_001", "prec_005"],
  "appeal_deadline": "2026-06-27T00:00:00Z",
  "created_at": "2026-06-20T00:05:00Z"
}
```

## API Endpoints

### Policies

#### List Policies
```
GET /policies
```
Returns all policies available to the authenticated organization.

#### Create Policy
```
POST /policies
```
Create a new dispute policy from scratch or from a template.

#### Get Policy
```
GET /policies/{policy_id}
```

#### Update Policy
```
PATCH /policies/{policy_id}
```

### Cases

#### List Cases
```
GET /cases?status={status}&party={party_id}&limit=50&offset=0
```

#### Create Case
```
POST /cases
```
```json
{
  "claimant": "party_abc123",
  "respondent": "party_xyz789",
  "policy_id": "pol_xyz789",
  "claim": {
    "description": "Failed to deliver milestone 3",
    "amount": 500.00,
    "currency": "USDC",
    "deadline": "2026-06-15T23:59:59Z"
  }
}
```
Returns: Case object with status "open"

#### Get Case
```
GET /cases/{case_id}
```

#### Update Case Status
```
PATCH /cases/{case_id}
```
Transitions: open → evidence_phase → deliberating → ruled → enforced

### Evidence

#### Submit Evidence
```
POST /cases/{case_id}/evidence
```
```json
{
  "type": "log",
  "source": "github",
  "content": {
    "uri": "https://github.com/org/repo/commit/abc123",
    "hash": "sha256:def456...",
    "claimed_fact": "Commit shows code was pushed on June 16, after deadline"
  },
  "authenticity": "claimed"
}
```

#### List Evidence
```
GET /cases/{case_id}/evidence
```

### Rulings

#### Get Ruling
```
GET /cases/{case_id}/ruling
```
Returns the ruling if the case has been decided.

#### Request Ruling
```
POST /cases/{case_id}/ruling
```
Triggers the judge agent to evaluate evidence against the policy.
Case must be in "evidence_phase" or "deliberating" status.

#### Appeal Ruling
```
POST /cases/{case_id}/appeal
```
```json
{
  "reason": "New evidence discovered",
  "new_evidence_ids": ["ev_new001"]
}
```

### Precedent

#### Search Precedents
```
GET /precedents?query={query}&limit=10
```
Searches past rulings for relevant precedents.

#### Get Precedent
```
GET /precedents/{precedent_id}
```

### Webhooks

#### Register Webhook
```
POST /webhooks
```
```json
{
  "url": "https://your-app.com/agentcourt-webhook",
  "events": ["case.created", "evidence.submitted", "ruling.issued", "case.enforced"]
}
```

### Templates

#### List Templates
```
GET /templates
```
Pre-built policy templates for common dispute types:
- `freelance-delivery` — Freelancer delivery disputes
- `milestone-payment` — Milestone-based payment disputes
- `bug-bounty` — Bug bounty validity disputes
- `sla-breach` — SLA violation disputes
- `scope-creep` — Project scope change disputes

#### Apply Template
```
POST /templates/{template_id}/apply
```
Creates a policy from the template with custom parameters.

## Ruling Engine

The ruling engine evaluates evidence against policy rules in order:

1. **Auto-check**: If evidence conclusively matches a high-confidence rule, ruling is instant
2. **Structured evaluation**: Judge agent evaluates all evidence against all applicable rules
3. **Precedent retrieval**: Similar past rulings are retrieved and weighted
4. **Confidence assessment**: Each ruling includes a confidence band (high/medium/low)
5. **Consequence generation**: Ruling includes specific consequences (reputation, payment, etc.)

## Comparison with Competitors

| Feature | AgentCourt | Arbitova | Tribunal | Gavel |
|---------|-----------|----------|----------|-------|
| Primary focus | Rulings | Escrow | Court sim | Legal arbitration |
| Escrow required | No (plugin) | Yes | Yes | Yes |
| Policy engine | Yes | No | No | No |
| Structured evidence | Yes | Basic | Verifiable | Legal format |
| Precedent system | Yes | No | iNFT memory | Common law |
| Confidence bands | Yes | No | No | No |
| API-first | Yes | Yes | P2P | Yes |
| MCP server | Planned | Yes | No | No |
| Human fallback | Phase 6 | No | No | Yes |
| On-chain | Future | Base L2 | 0G Chain | Base L2 |

## Implementation Priority

1. **M1**: Ruling Engine + Policy Engine (this spec)
2. **M2**: REST API server
3. **M3**: Precedent system
4. **M4**: SDK (Python, JS)
5. **M5**: MCP server
6. **M6**: Escrow plugin (optional, for payment enforcement)
7. **M7**: Appeal + human fallback
8. **M8**: On-chain audit trail
