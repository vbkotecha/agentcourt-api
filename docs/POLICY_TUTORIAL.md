# Creating Custom Dispute Policies — Step by Step

This tutorial walks through creating a new dispute policy from scratch.

## Prerequisites

- Read the [Policy Contribution Guide](../CONTRIBUTING_POLICY.md)
- Understand [how the policy engine works](architecture.md)

## Step 1: Identify the Dispute Type

Start with a real scenario. Example: **"An AI agent books a flight but the airline doesn't honor the booking."**

What are the possible outcomes?
- Booking confirmed, ticket issued → No dispute
- Booking confirmed, no ticket → Full refund
- Booking confirmed, wrong flight → Partial refund
- Booking failed but payment charged → Full refund

## Step 2: Define the Metadata Fields

What facts does the engine need to evaluate?

```json
{
  "booking_confirmed": true,
  "ticket_issued": false,
  "payment_charged": true,
  "correct_flight": true,
  "amount_paid": "$450.00"
}
```

## Step 3: Write the Rules

Each rule has a condition (Python expression), ruling template, confidence, and remedy.

```json
{
  "id": "no-ticket-after-payment",
  "condition": "booking_confirmed == true AND\nticket_issued == false AND\npayment_charged == true\n",
  "ruling_template": "Booking was confirmed and payment was charged, but no ticket was issued.\nAmount paid: {amount_paid}\n\nFull refund owed.",
  "confidence": "high",
  "remedy": "full_refund",
  "facts_required": ["booking_confirmed", "ticket_issued", "payment_charged"]
}
```

### Condition Syntax

Conditions are Python boolean expressions evaluated against the metadata dict:

| Operator | Example | Meaning |
|----------|---------|---------|
| `==` | `ticket_issued == false` | Equality |
| `!=` | `http_status != 200` | Inequality |
| `>` / `<` | `uptime_percentage < 99.9` | Numeric comparison |
| `>=` / `<=` | `http_status >= 500` | Numeric comparison |
| `AND` | `a == true AND b == false` | Both must be true |
| `OR` | `a == true OR b == true` | Either can be true |
| `null` | `field != null` | Field exists |

### Confidence Levels

| Level | Meaning | When to Use |
|-------|---------|-------------|
| `high` | Facts are deterministic | Boolean checks (received/not received) |
| `medium` | Facts require judgment | Partial compliance, subjective quality |
| `low` | Facts are circumstantial | Heuristics, indirect evidence |

## Step 4: Combine into a Policy File

```json
{
  "name": "flight-booking",
  "version": "1.0",
  "description": "Disputes for AI agent flight bookings — non-delivery, wrong flight, overcharge",
  "rules": [
    {
      "id": "no-ticket-after-payment",
      "condition": "booking_confirmed == true AND\nticket_issued == false AND\npayment_charged == true\n",
      "ruling_template": "Booking confirmed, payment charged, no ticket issued.\nAmount: {amount_paid}\n\nFull refund owed.",
      "confidence": "high",
      "remedy": "full_refund",
      "facts_required": ["booking_confirmed", "ticket_issued", "payment_charged"]
    },
    {
      "id": "wrong-flight",
      "condition": "booking_confirmed == true AND\nticket_issued == true AND\ncorrect_flight == false\n",
      "ruling_template": "Ticket issued for wrong flight.\nExpected: {expected_flight}\nReceived: {actual_flight}\n\nPartial refund owed.",
      "confidence": "high",
      "remedy": "partial_refund",
      "facts_required": ["booking_confirmed", "ticket_issued", "correct_flight"]
    },
    {
      "id": "valid-booking",
      "condition": "booking_confirmed == true AND\nticket_issued == true AND\ncorrect_flight == true\n",
      "ruling_template": "Booking is valid. Ticket issued for correct flight.\nNo remedy owed.",
      "confidence": "high",
      "remedy": "none",
      "facts_required": ["booking_confirmed", "ticket_issued", "correct_flight"]
    }
  ]
}
```

## Step 5: Test Your Policy

```bash
# Using the API
curl -X POST https://agentcourt-api-production.up.railway.app/v1/disputes \
  -H "Content-Type: application/json" \
  -d '{
    "policy": "flight-booking",
    "claim": "No ticket issued after payment",
    "desired_remedy": "full_refund",
    "metadata": {
      "booking_confirmed": true,
      "ticket_issued": false,
      "payment_charged": true,
      "amount_paid": "$450.00"
    }
  }'
```

Expected response:
```json
{
  "case_id": "...",
  "ruling": "Booking confirmed, payment charged, no ticket issued...",
  "confidence": "high",
  "remedy": "full_refund",
  "matched_rule": "no-ticket-after-payment"
}
```

## Step 6: Submit

1. Save as `src/policies/your-policy.json`
2. Run `python3 tests/test_policy_engine.py` to validate
3. Open a PR with title `policy: add your-policy-name`
4. Use the [Policy Request issue template](https://github.com/vbkotecha/agentcourt-api/issues/new) if you want us to build it

## Template Gallery

| Policy | Rules | Remedies |
|--------|-------|----------|
| `api-quality` | 7 | refund, partial_refund, none |
| `freelance-delivery` | 6 | refund, partial_refund, none |
| `milestone-payment` | 5 | release, hold, partial_release |
| `bug-bounty` | 5 | payout, partial_payout, reject |
| `sla-monitoring` | 5 | refund, penalty, none |
| `scope-dispute` | 5 | renegotiate, partial_refund, none |
| `physical-commerce` | 6 | refund, replace, partial_refund |
