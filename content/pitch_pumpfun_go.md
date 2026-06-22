# AgentCourt × Pump.fun GO Integration Pitch

## The Problem

Pump.fun GO has an explicit "dispute period" — when a bounty hunter's submission is rejected or a bounty expires, there's a window where disputes can arise. Currently, the resolution is "creators may recover their funds after the designated dispute period concludes." But what if the creator and hunter disagree about whether the submission was valid?

Right now: centralized review by Pump.fun. That doesn't scale.

## The Solution

AgentCourt's `bug-bounty` policy template handles exactly this scenario — bounty submissions, reproducibility, severity disputes, and disclosure violations.

```
Creator posts bounty ($SOL reward in escrow)
    ↓
Hunter submits work
    ↓
Creator rejects → dispute
    ↓
AgentCourt evaluates evidence → ruling
    ↓
Escrow released or refunded based on ruling
```

## Integration: 3 API Calls

```python
from agentcourt import AgentCourt

court = AgentCourt()

# When a bounty submission is contested
ruling = court.dispute(
    claimant="bounty_hunter",
    respondent="bounty_creator",
    contract={
        "parties": ["bounty_hunter", "bounty_creator"],
        "obligations": ["Build Solana CLI tool per specifications"],
        "deliverables": ["Working CLI with documentation"],
        "payment_terms": "50 USDC on approval"
    },
    claim="Submission was rejected but it meets all requirements.",
    desired_remedy="payment",
    policy="bug-bounty",
    evidence=[
        {
            "type": "contract",
            "source": "pumpfun_go_listing",
            "timestamp": "2026-06-15",
            "claimed_fact": "Bounty requires CLI tool with 3 commands and README"
        },
        {
            "type": "file",
            "source": "github_submission",
            "content_hash": "sha256:abc123...",
            "timestamp": "2026-06-19",
            "claimed_fact": "CLI tool submitted with all 3 commands implemented and tested"
        },
        {
            "type": "log",
            "source": "ci_pipeline",
            "timestamp": "2026-06-19",
            "claimed_fact": "All tests pass, CLI builds successfully, documentation complete"
        },
        {
            "type": "message",
            "source": "pumpfun_chat",
            "timestamp": "2026-06-20",
            "claimed_fact": "Creator rejected without citing specific issues"
        }
    ]
)

# ruling.matched_rule → "valid-bug-full-payout"
# ruling.remedy → "full_payout"
# ruling.confidence → "medium"

# Release escrow based on ruling
if ruling.remedy == "full_payout":
    release_escrow(bounty_id, hunter_wallet)
elif ruling.remedy == "partial_payout":
    release_partial(bounty_id, hunter_wallet, pct=50)
elif "deny" in ruling.remedy:
    refund_escrow(bounty_id, creator_wallet)
```

## Perfect Policy Fit

AgentCourt's bug-bounty template already handles 5 dispute scenarios:

| Rule | Pump.fun GO Scenario |
|------|---------------------|
| `valid-bug-full-payout` | Valid submission, creator wrongfully rejected |
| `non-reproducible-bug` | Submission doesn't work as claimed |
| `valid-bug-partial-severity` | Submission partially meets requirements |
| `disclosure-violation` | Hunter violated bounty terms |
| `disputed-reproducibility` | Conflicting evidence, needs escalation |

## Why AgentCourt

- **Stateless API** — no infrastructure for Pump.fun to manage
- **Deterministic** — same evidence = same ruling, every time
- **Sub-500ms** — rulings are instant
- **Solana-friendly** — evidence can include wallet addresses, tx hashes
- **Open source** — MIT licensed, self-hostable

## Stats
- 17/17 tests passing
- 21 public verdicts
- 4 policy templates (bug-bounty is the most relevant)
- API live, SDKs ready, MCP server ready
