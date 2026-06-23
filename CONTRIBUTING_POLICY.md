# Contributing Policy Templates

AgentCourt resolves disputes using policy templates — JSON rule sets that evaluate structured evidence. This guide shows you how to create and contribute new policies.

## Policy Structure

Each policy is a JSON file in `src/engine/policies/`:

```json
{
  "name": "your-policy-name",
  "description": "What this policy covers",
  "version": "1.0.0",
  "rules": [
    {
      "id": "YP-001",
      "condition": "metadata.delivered == false",
      "ruling": "full_refund",
      "confidence": 0.95,
      "reasoning": "No delivery was made"
    }
  ]
}
```

## Rule Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique rule identifier (e.g., `AQ-001`) |
| `condition` | string | Python expression evaluated against `metadata` dict |
| `ruling` | string | One of: `full_refund`, `partial_refund`, `no_payout` |
| `confidence` | float | 0.0 to 1.0 — how certain the ruling is |
| `reasoning` | string | Human-readable explanation |

## Condition Syntax

Conditions are Python expressions evaluated against the `metadata` object:

```python
# Boolean checks
"metadata.response_received == false"
"metadata.delivered == true && metadata.meets_spec == false"

# Numeric comparisons
"metadata.uptime_percentage < metadata.sla_threshold"
"metadata.response_time_ms > 5000"

# String checks
"metadata.status_code != 200"
"metadata.content_type != 'application/json'"
```

## Submission Process

1. Create your policy JSON file
2. Add it to `src/engine/policies/`
3. Test with sample disputes
4. Open a PR with:
   - The policy file
   - A sample dispute that should trigger each rule
   - Update to `llms.txt` listing the new policy

## Example: Data Licensing Policy

```json
{
  "name": "data-licensing",
  "description": "Disputes over data license terms, usage rights, and attribution",
  "version": "1.0.0",
  "rules": [
    {
      "id": "DL-001",
      "condition": "metadata.license_compliant == false",
      "ruling": "full_refund",
      "confidence": 0.90,
      "reasoning": "Data usage violates license terms"
    },
    {
      "id": "DL-002",
      "condition": "metadata.attribution_provided == false && metadata.attribution_required == true",
      "ruling": "partial_refund",
      "confidence": 0.80,
      "reasoning": "Required attribution was not provided"
    }
  ]
}
```

## Questions?

Open a [policy request issue](https://github.com/vbkotecha/agentcourt-api/issues/new?template=policy-request.md) and we'll help you design the rules.
