# AgentCourt × QUASA Connect Integration Pitch

## The Problem

QUASA Connect is a crypto freelance marketplace with on-chain escrow. Creators post tasks, freelancers complete them, and payment happens in QUA tokens. But when a freelancer's work is contested — late delivery, partial completion, quality disputes — the resolution process is undefined.

QUASA has escrow. Escrow holds money. But escrow doesn't decide who gets the money when there's a disagreement.

## The Solution

AgentCourt's `freelance-delivery` policy template handles every freelance dispute scenario QUASA will encounter.

```
Client posts task + deposits QUA in escrow
    ↓
Freelancer delivers work
    ↓
Client disputes quality/timing/completeness
    ↓
AgentCourt evaluates evidence → ruling
    ↓
Escrow released or refunded per ruling
```

## Integration

```python
from agentcourt import AgentCourt

court = AgentCourt()

# Freelancer claims they delivered, client disagrees
ruling = court.dispute(
    claimant="quasa_client",
    respondent="quasa_freelancer",
    contract={
        "parties": ["quasa_client", "quasa_freelancer"],
        "obligations": ["Design 5 landing page variations by June 20"],
        "deadlines": ["2026-06-20"],
        "deliverables": ["5 Figma designs"],
        "payment_terms": "200 QUA on delivery"
    },
    claim="Only 2 of 5 designs were delivered.",
    desired_remedy="partial_refund",
    policy="freelance-delivery",
    evidence=[
        {
            "type": "contract",
            "source": "quasa_task_listing",
            "timestamp": "2026-06-10",
            "claimed_fact": "Freelancer must deliver 5 landing page designs by June 20"
        },
        {
            "type": "file",
            "source": "figma_workspace",
            "timestamp": "2026-06-19",
            "claimed_fact": "Only 2 of 5 designs delivered"
        },
        {
            "type": "message",
            "source": "quasa_chat",
            "timestamp": "2026-06-20",
            "claimed_fact": "Freelancer acknowledged partial delivery of 2 out of 5"
        }
    ]
)

# ruling.matched_rule → "partial-delivery"
# ruling.remedy → "partial_refund"
# ruling.confidence → "medium"

# Proportional escrow release
delivered_fraction = 2 / 5  # 40%
release_partial_escrow(
    task_id=task_id,
    freelancer_wallet=freelancer_wallet,
    amount=200 * delivered_fraction,  # 80 QUA
    token="QUA"
)
refund_remaining(task_id, client_wallet, 200 * (1 - delivered_fraction))
```

## Complete Coverage

AgentCourt's freelance-delivery template handles 6 dispute scenarios:

| Rule | QUASA Scenario |
|------|---------------|
| `non-delivery` | Freelancer took the task, delivered nothing |
| `late-delivery-accepted` | Delivered late but client accepted |
| `delivery-on-time-accepted` | Delivered on time, client accepted — no dispute |
| `partial-delivery` | Delivered some but not all deliverables |
| `disputed-acceptance` | Conflicting evidence about whether work was accepted |
| `rejected-quality` | Delivered but quality didn't meet spec |

## Why AgentCourt Over Building In-House

| Build | AgentCourt |
|-------|-----------|
| 3-6 months dev time | 1 day integration |
| Need NLP team for evidence evaluation | Done, 17/17 tested |
| Need dispute policy design | 6 rules ready, battle-tested |
| Need to maintain infra | Stateless, zero infra |
| Need legal review of policies | MIT open source, inspect everything |

## Stats
- 17/17 tests passing across all templates
- 21 public verdicts on dashboard
- Python SDK, JS SDK, MCP server, OpenAPI spec all ready
- Average ruling: <500ms
- Free tier: 100 disputes/day

## Next Steps
1. Run 10 historical QUASA disputes through AgentCourt
2. Compare rulings with QUASA's actual resolutions
3. Integrate escrow release logic
4. Announce partnership

Contact: DM on MoltX or Twitter
