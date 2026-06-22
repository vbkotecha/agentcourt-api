# AgentCourt

**The dispute layer for agent commerce.**

Submit evidence. Apply policy rules. Get a ruling. No escrow, no courtroom theater.

## Live API

**Base URL:** `https://agentcourt-api-production.up.railway.app`
**Docs:** `https://agentcourt-api-production.up.railway.app/docs`

## Quick Start

```python
from agentcourt import AgentCourt

court = AgentCourt()

ruling = court.dispute(
    claimant="ClientCorp",
    respondent="DevStudio",
    contract={
        "obligations": ["Build mobile app"],
        "deadlines": ["2026-07-01T23:59:00Z"],
        "deliverables": ["iOS app", "Android app"],
    },
    claim="Developer never delivered the app",
    desired_remedy="Full refund of deposit",
    policy="freelance-delivery",
    evidence=[
        {
            "type": "contract",
            "source": "ClientCorp",
            "timestamp": "2026-06-01T10:00:00Z",
            "claimed_fact": "Signed contract, no deliverable received",
            "reliability": "high",
        }
    ],
)

print(ruling.confidence)  # high
print(ruling.remedy)      # full_refund
print(ruling.ruling)      # The respondent failed to deliver...
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/disputes` | Submit a dispute, get a ruling |
| `GET` | `/v1/cases` | List all cases |
| `GET` | `/v1/cases/{id}` | Get a specific case |
| `GET` | `/v1/policies` | List policy templates |
| `GET` | `/v1/policies/{name}` | Get policy details |
| `GET` | `/health` | API health check |
| `GET` | `/docs` | Interactive API docs (Swagger) |

## Policy Templates

### freelance-delivery
Disputes over digital work delivery: non-delivery, late delivery, scope issues.

**Rules:** non-delivery, late-delivery-accepted, late-delivery-rejected, partial-delivery, default-no-match

### milestone-payment  
Disputes over milestone payments: unpaid milestones, overdue payments, partial payments.

**Rules:** milestone-completed-unpaid, milestone-completed-paid-on-time, milestone-incomplete-payment-justified, milestone-overdue-disputed, default-no-match

### bug-bounty
Disputes over bug bounty claims: reproducibility, severity, disclosure compliance.

**Rules:** valid-bug-full-payout, non-reproducible-bug, severity-below-threshold, non-compliant-disclosure, default-no-match

## How It Works

1. **Submit evidence** — contracts, commits, logs, screenshots, payment records
2. **Evidence scoring** — each item weighted by type, reliability, recency, and hash verification
3. **Fact extraction** — structured facts derived from evidence + metadata
4. **Policy matching** — facts evaluated against policy rules (deterministic)
5. **Confidence band** — high/medium/low based on evidence quality and fact completeness
6. **Ruling generated** — with remedy, full audit trail, and explainable reasoning

## Key Design Decisions

- **No escrow required** — rulings create consequences through reputation and enforcement, not custody
- **Deterministic** — same evidence + policy always produces the same ruling
- **Explainable** — every ruling shows which rule matched, which facts were established, and evidence scores
- **Policy-first** — define rules upfront, not case-by-case
- **API-first** — REST + SDK, integrate in minutes

## SDK

### Python (zero-dependency)

```bash
pip install agentcourt  # coming soon to PyPI
```

Or copy `sdk/agentcourt.py` — zero dependencies, standard library only.

### JavaScript / TypeScript

```bash
npm install @agentcourt/sdk  # coming soon to npm
```

```javascript
const { AgentCourt } = require('@agentcourt/sdk');

const court = new AgentCourt();
const ruling = await court.resolve({
  policy: 'freelance-delivery',
  claimant: 'buyer_agent',
  respondent: 'seller_agent',
  claim: 'Deliverable never received',
  desiredRemedy: 'full_refund',
  contract: { parties: ['buyer_agent', 'seller_agent'] },
  evidence: [{ type: 'contract', source: 'agreement.json', claimedFact: 'Deadline missed' }],
});
```

Or copy `sdk/npm/index.js` — zero dependencies, works in Node 18+ and browsers.

## MCP Server

AgentCourt ships with an MCP (Model Context Protocol) server. Any MCP-aware agent framework can call AgentCourt directly.

```bash
python3 mcp_server.py
```

**5 MCP Tools:**
- `resolve_dispute` — Submit a dispute, get a ruling
- `list_policies` — See available policy templates
- `get_policy` — Read rules of a specific policy
- `get_case` — Retrieve a past case by ID
- `health_check` — Verify API status

Compatible with Letta, Claude, and any MCP-compatible agent framework.

## Architecture

```
├── src/
│   ├── main.py              # FastAPI app with REST endpoints
│   ├── engine/
│   │   └── policy_engine.py # Deterministic rule evaluation engine
│   └── policies/
│       ├── freelance-delivery.json
│       ├── milestone-payment.json
│       └── bug-bounty.json
├── sdk/
│   ├── agentcourt.py        # Python SDK (zero-dependency)
│   └── npm/                 # JavaScript/TypeScript SDK
│       ├── index.js
│       ├── index.d.ts
│       └── test.js
├── mcp_server.py            # MCP server (stdio transport)
├── clawmart/
│   └── SKILL.md             # ClawMart marketplace listing
└── landing/
    └── index.html           # Landing page
```

## Why AgentCourt Exists

The agentic economy is rapidly building payment rails:

- **x402** (Coinbase) — protocol for AI agents to pay each other via USDC on Base. No dispute mechanism.
- **ERC-8183** (Ethereum draft, Feb 2026) — conditional payments and escrow for agent transactions. Explicitly states: *"no dispute resolution within the core spec."*
- **AP2** (Google) — Agent Payments Protocol. Moves money, doesn't resolve disagreements.
- **ClawBank + Shodai** — First AI-to-AI Ricardian contracts on Ethereum. Milestone logic is live. No adjudication layer.

Every major protocol handles payments, escrow, and execution. None of them handle **what happens when two agents disagree**.

AgentCourt is the missing layer. Submit evidence, apply policy rules, get a binding ruling.

**Works with any commerce protocol** — x402, ERC-8183, AP2, or custom agreements. AgentCourt doesn't hold funds. It adjudicates outcomes.

## How We Differ

| | AgentCourt | Arbitova | Synmerco |
|---|---|---|---|
| **Model** | Standalone judgment layer | Escrow + bundled arbitration | Full-stack marketplace |
| **Custody** | Never. Non-custodial. | Holds funds in escrow contract | Holds funds in escrow |
| **Pricing** | Per dispute resolution call | 0.5% per release + 2.0% per dispute | 3.25% per settled deal |
| **Determinism** | Policy rules — same evidence = same ruling | AI arbiter — subjective | Internal system |
| **Integration** | API + SDK + MCP server. Works with any platform | Use their escrow contract | Use their marketplace |
| **Auditable** | Every ruling public with matched rules and evidence scores | Public verdicts | Internal |
| **Lock-in** | None. Bring your own escrow, marketplace, payment rail | Must use their escrow contract | Must use their platform |

AgentCourt is not an escrow company. We don't compete with payment protocols. We are the judgment layer that any of them can call.

## Pricing

**Design Partner Program (Now):** Free for first 5 partners. Full API access. Custom policy template included.

**Production (Post-Launch):** Per-dispute pricing. No transaction fees. No custody fees. No platform fees. You only pay when you need a ruling.

## License

MIT
