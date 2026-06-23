# AgentCourt Error Handling Guide

## HTTP Status Codes

| Code | Meaning | When |
|------|---------|------|
| `200` | OK | Successful dispute ruling returned |
| `402` | Payment Required | Free tier exceeded (100/month). Pay via x402. |
| `422` | Unprocessable Entity | Invalid input — missing required fields or wrong types |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Internal Server Error | Something went wrong on our end |
| `503` | Service Unavailable | API is down or deploying |

## Handling the 402 (Payment Required)

When you exceed the free tier, the API returns a 402 with x402 payment details:

```json
{
  "error": "PaymentRequiredError",
  "amount": "50000",
  "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
  "chain": "eip155:8453",
  "pay_to": "0x9863aB6242663FCc84c33632741711dB78f8Fd15"
}
```

**Python:**
```python
from agentcourt import AgentCourt
from agentcourt.exceptions import PaymentRequiredError

court = AgentCourt()

try:
    ruling = court.file_dispute(
        policy="api-quality",
        claim="API returned XML",
        desired_remedy="full_refund",
        metadata={"response_received": True, "schema_matches": False}
    )
    print(f"Ruling: {ruling.ruling}")

except PaymentRequiredError as e:
    print(f"Free tier exceeded. Pay {e.amount} wei USDC to {e.pay_to}")
    # Use x402 client to facilitate payment, then retry

except Exception as e:
    print(f"Unexpected error: {e}")
```

**JavaScript:**
```javascript
import { AgentCourt } from "@agentcourt/sdk";

const court = new AgentCourt();

try {
  const ruling = await court.fileDispute({...});
  console.log(ruling.ruling);
} catch (error) {
  if (error.status === 402) {
    console.log("Payment required", error.x402);
    // Handle x402 payment
  } else if (error.status === 422) {
    console.log("Invalid input", error.detail);
  } else {
    console.log("Unexpected error", error);
  }
}
```

## Handling 422 (Validation Error)

The API validates all inputs against Pydantic schemas. Common causes:

- Missing `policy` field
- Missing `claim` or `desired_remedy`
- Invalid `policy` name (must match one of the 7 templates)
- Wrong type for `metadata` fields (e.g., string instead of boolean)

```python
# Correct structure
{
    "policy": "api-quality",           # Must be valid policy name
    "claim": "API returned XML",       # String, required
    "desired_remedy": "full_refund",   # String, required
    "metadata": {                      # Dict, required
        "response_received": True,     # Boolean
        "schema_matches": False        # Boolean
    },
    "evidence": [                      # List, optional
        {
            "type": "log",             # String
            "source": "monitor",       # String
            "timestamp": "2026-01-01T00:00:00Z",  # ISO 8601
            "claimed_fact": "..."      # String
        }
    ]
}
```

## Retry Strategy

For transient failures (429, 500, 503), use exponential backoff:

```python
import time
from agentcourt import AgentCourt

court = AgentCourt()

def file_dispute_with_retry(dispute_data, max_retries=3):
    for attempt in range(max_retries):
        try:
            return court.file_dispute(**dispute_data)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait = 2 ** attempt  # 1s, 2s, 4s
            time.sleep(wait)
```
