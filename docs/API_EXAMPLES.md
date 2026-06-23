# AgentCourt API Examples

Complete request/response examples for every policy template.

## Base URL

```
https://agentcourt-api-production.up.railway.app
```

## 1. API Quality Dispute

**POST /v1/disputes**
```json
{
  "claimant": "buyer-agent",
  "respondent": "stock-api",
  "contract": {
    "parties": ["buyer-agent", "stock-api"],
    "obligations": ["Return JSON with fields: symbol, price, volume"]
  },
  "claim": "API returned XML instead of JSON",
  "desired_remedy": "full_refund",
  "evidence": [{
    "type": "log",
    "source": "api-monitor",
    "timestamp": "2026-06-23T10:00:00Z",
    "claimed_fact": "Response Content-Type was text/xml"
  }],
  "policy": "api-quality",
  "metadata": {
    "response_received": true,
    "schema_matches": false,
    "status_code": 200,
    "content_type": "text/xml"
  }
}
```

**Response:**
```json
{
  "case_id": "a1b2c3d4e5f6",
  "status": "resolved",
  "ruling": "full_refund",
  "confidence": "0.90",
  "reasoning": "Response schema does not match agreed format",
  "remedy": "Full refund recommended",
  "matched_rule_id": "AQ-002",
  "policy_name": "api-quality",
  "policy_version": "1.2.0",
  "engine_version": "1.2.0",
  "ruled_at": "2026-06-23T10:00:01Z"
}
```

## 2. Freelance Delivery Dispute

**POST /v1/disputes**
```json
{
  "claimant": "client-agent",
  "respondent": "freelancer-agent",
  "contract": {
    "parties": ["client-agent", "freelancer-agent"],
    "obligations": ["Deliver Python web scraper by June 20, 2026"],
    "deadlines": ["2026-06-20T23:59:00Z"]
  },
  "claim": "Work was never delivered",
  "desired_remedy": "full_refund",
  "evidence": [{
    "type": "log",
    "source": "project-management",
    "timestamp": "2026-06-22T00:00:00Z",
    "claimed_fact": "No deliverable submitted by deadline"
  }],
  "policy": "freelance-delivery",
  "metadata": {
    "delivered": false,
    "meets_spec": false,
    "response_received": false
  }
}
```

**Response:** `"ruling": "full_refund", "confidence": "0.95"`

## 3. SLA Monitoring Dispute

```json
{
  "claimant": "subscriber",
  "respondent": "api-provider",
  "contract": {
    "parties": ["subscriber", "api-provider"],
    "obligations": ["99.9% uptime SLA"]
  },
  "claim": "Service was down for 4 hours",
  "desired_remedy": "partial_refund",
  "evidence": [{
    "type": "log",
    "source": "uptime-monitor",
    "timestamp": "2026-06-23T00:00:00Z",
    "claimed_fact": "Service unavailable from 02:00 to 06:00 UTC"
  }],
  "policy": "sla-monitoring",
  "metadata": {
    "uptime_percentage": 83.3,
    "sla_threshold": 99.9,
    "downtime_minutes": 240
  }
}
```

## 4. Bug Bounty Dispute

```json
{
  "claimant": "project-owner",
  "respondent": "researcher",
  "contract": {
    "parties": ["project-owner", "researcher"],
    "obligations": ["Pay $500 for critical bugs that are reproducible"]
  },
  "claim": "Bug reported as critical is not reproducible",
  "desired_remedy": "no_payout",
  "evidence": [{
    "type": "test",
    "source": "ci-pipeline",
    "timestamp": "2026-06-23T10:00:00Z",
    "claimed_fact": "Bug does not reproduce on clean environment"
  }],
  "policy": "bug-bounty",
  "metadata": {
    "bug_reproducible": false,
    "severity_claimed": "critical",
    "severity_actual": "none"
  }
}
```

## 5. Milestone Payment Dispute

```json
{
  "claimant": "contractor",
  "respondent": "client",
  "contract": {
    "parties": ["contractor", "client"],
    "obligations": ["Pay $2000 upon completion of Milestone 3"]
  },
  "claim": "Client refuses to pay for completed milestone",
  "desired_remedy": "full_refund",
  "evidence": [{
    "type": "commit",
    "source": "github",
    "timestamp": "2026-06-20T15:00:00Z",
    "claimed_fact": "All milestone deliverables committed and reviewed"
  }],
  "policy": "milestone-payment",
  "metadata": {
    "milestone_completed": true,
    "completion_percentage": 100,
    "milestone_paid": false
  }
}
```

## 6. Scope Dispute

```json
{
  "claimant": "developer",
  "respondent": "client",
  "contract": {
    "parties": ["developer", "client"],
    "obligations": ["Build 5-page website for $3000"]
  },
  "claim": "Client demands 20 pages at same price",
  "desired_remedy": "no_payout",
  "evidence": [{
    "type": "message",
    "source": "email",
    "timestamp": "2026-06-22T14:00:00Z",
    "claimed_fact": "Client requested 15 additional pages without budget increase"
  }],
  "policy": "scope-dispute",
  "metadata": {
    "budget_exceeded": true,
    "scope_changed": true,
    "original_scope": "5 pages",
    "requested_scope": "20 pages"
  }
}
```

## 7. Physical Commerce Dispute

```json
{
  "claimant": "buyer",
  "respondent": "seller",
  "contract": {
    "parties": ["buyer", "seller"],
    "obligations": ["Deliver new product in original packaging"]
  },
  "claim": "Product arrived damaged",
  "desired_remedy": "full_refund",
  "evidence": [{
    "type": "screenshot",
    "source": "buyer",
    "timestamp": "2026-06-23T09:00:00Z",
    "claimed_fact": "Product has visible cracks and dents"
  }],
  "policy": "physical-commerce",
  "metadata": {
    "damaged": true,
    "as_described": false,
    "return_requested": true
  }
}
```

## Using curl

```bash
# File a dispute
curl -X POST https://agentcourt-api-production.up.railway.app/v1/disputes \
  -H "Content-Type: application/json" \
  -d '{
    "claimant": "buyer",
    "respondent": "seller",
    "contract": {"parties": ["buyer","seller"], "obligations": ["JSON API"]},
    "claim": "Wrong format",
    "desired_remedy": "full_refund",
    "evidence": [{"type":"log","source":"test","timestamp":"2026-01-01T00:00:00Z","claimed_fact":"XML returned"}],
    "policy": "api-quality",
    "metadata": {"response_received": true, "schema_matches": false}
  }'

# List policies
curl https://agentcourt-api-production.up.railway.app/v1/policies

# Health check
curl https://agentcourt-api-production.up.railway.app/health
```
