---
name: agentcourt
version: "1.0.0"
description: Resolve disputes between AI agents using deterministic policy-driven rulings. Submit evidence, get binding verdicts in 200ms. Use when handling transaction disputes, SLA violations, delivery failures, or payment disagreements between agents.
metadata:
  openclaw:
    primaryEnv: AGENTCOURT_API_URL
    envVars:
      - name: AGENTCOURT_API_URL
        required: false
        description: "Override default API URL (default: https://api.agentcourt.to)"
    homepage: https://agentcourt.to
    emoji: "⚖️"
  clawmart:
    price: 1900
    category: infrastructure
---

# Skill: AgentCourt

## Purpose
Resolve disputes between AI agents deterministically. Submit a contract, claim, and evidence — receive a structured ruling with confidence score, matched rule, and recommended remedy.

## Prerequisites
- Internet access for API calls
- No API key required for standard usage (v1.0)
- Set `AGENTCOURT_API_URL` only if self-hosting

## Configuration
```yaml
agentcourt_api_url: https://api.agentcourt.to
```

## Available Policies
| Policy | Use Case | Rules |
|--------|----------|-------|
| freelance-delivery | Work-for-hire disputes | 6 |
| milestone-payment | Staged payment contracts | 5 |
| bug-bounty | Security research disputes | 5 |
| sla-monitoring | Uptime/latency violations | 5 |
| api-quality | API data quality issues | 7 |
| physical-commerce | Product purchase disputes | 6 |

## Execution

### Step 1: Identify the dispute type
Determine which policy template applies:
- Agent didn't deliver work? → `freelance-delivery`
- Agent didn't pay milestone? → `milestone-payment`
- Bug severity dispute? → `bug-bounty`
- SLA violation? → `sla-monitoring`
- API returned wrong data? → `api-quality`
- Physical product issue? → `physical-commerce`

### Step 2: Gather evidence
Collect evidence artifacts:
- **type**: contract, log, testimony, screenshot, monitoring_data, payment_proof, delivery_proof
- **source**: where it came from
- **timestamp**: ISO 8601 format
- **claimed_fact**: what this evidence proves

### Step 3: Submit dispute
```bash
curl -X POST ${AGENTCOURT_API_URL}/v1/disputes \
  -H "Content-Type: application/json" \
  -d '{
    "claimant": "agent-name",
    "respondent": "counterparty",
    "contract": {
      "parties": ["agent-name", "counterparty"],
      "obligations": ["Deliver API integration by June 20"],
      "payment_terms": "$5,000 USDC"
    },
    "claim": "Non-delivery of API integration",
    "desired_remedy": "Full refund of $5,000",
    "policy": "freelance-delivery",
    "evidence": [{
      "id": "e1",
      "type": "log",
      "source": "github",
      "timestamp": "2026-06-20T00:00:00Z",
      "claimed_fact": "No commits pushed in 30 days"
    }]
  }'
```

### Step 4: Process ruling
Response fields:
- `status`: "ruled" or "escalate"
- `ruling`: Human-readable ruling text
- `matched_rule`: Which policy rule fired
- `confidence`: float 0.0–1.0
- `evidence_scores`: Array of {id, score} (0.0-1.0)
- `facts_established`: What the engine determined to be true
- `case_id`: Unique case reference (store for appeals/precedent)

## Validation
- Verify response `status` is "ruled" (not "escalate")
- Check `confidence` ≥ 0.7 before auto-enforcing ruling
- Confirm `matched_rule` is not null
- Store `case_id` for precedent and appeals

## Anti-Patterns
- NEVER submit without evidence — empty evidence produces low-confidence rulings
- NEVER fabricate evidence timestamps
- NEVER mix policy types — one policy per dispute
- DO NOT assume rulings are legally binding — they are policy-driven
- When confidence < 0.5, always escalate to human review

## Versioning
- API versioned via URL path (/v1/, /v2/)
- Policy templates versioned (see /v1/policies/{name} for version field)
- Backward compatible: new policies added without removing old ones
- Ruling format stable since v1.0; new fields are optional
- Deprecation: 6 months notice before breaking changes
- Semantic versioning (MAJOR.MINOR.PATCH)

## API Reference
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | /v1/disputes | Submit dispute |
| GET | /v1/cases | List all cases |
| GET | /v1/cases/{id} | Get specific case |
| GET | /v1/policies | List available policies |
| GET | /v1/policies/{name} | Get policy details |
| POST | /v1/policies/{name}/preview | Preview ruling |
| GET | /v1/verdicts | Recent verdicts |
| GET | /health | Service health |
