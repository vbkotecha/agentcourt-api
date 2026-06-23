# AgentCourt

**The Evaluator layer for agent commerce.**

ERC-8183 defines an "Evaluator" — the entity that attests whether a job was completed correctly, triggering payment release or refund. AgentCourt is that layer: policy-driven, deterministic, open source.

Submit evidence. Apply policy rules. Get a deterministic ruling in under 500ms. No escrow, no courtroom theater.

![Version](https://img.shields.io/badge/version-1.2.0-blue) ![Tests](https://img.shields.io/badge/E2E-12%2F12-green) ![License](https://img.shields.io/badge/license-MIT-blue) ![Status](https://img.shields.io/badge/status-live-success) ![Verdicts](https://img.shields.io/badge/verdicts-50+-orange) ![Policies](https://img.shields.io/badge/policies-7-purple)

> **Live API**: [agentcourt-api-production.up.railway.app/docs](https://agentcourt-api-production.up.railway.app/docs)
> **Landing Page**: [vbkotecha.github.io/agentcourt-api](https://vbkotecha.github.io/agentcourt-api/)
> **Tutorial**: [File Your First Dispute](https://github.com/vbkotecha/agentcourt-api/discussions/2)
> **Integration Examples**: [LangChain, CrewAI, Node.js](https://github.com/vbkotecha/agentcourt-api/tree/main/examples)
> **Architecture**: [Design Document](https://github.com/vbkotecha/agentcourt-api/blob/main/docs/architecture.md)
> **Comparison**: [AgentCourt vs Arbitova](https://github.com/vbkotecha/agentcourt-api/blob/main/docs/comparison.md)

## Why AgentCourt?

The agent commerce stack has three layers:
1. **Transport** — A2A, MCP (how agents talk)
2. **Payment** — x402, AP2, Visa Intelligent Commerce (how agents pay)
3. **Dispute** — **AgentCourt** (what happens when something goes wrong)

When an agent misfires, hallucinates a product, breaches an SLA, or delivers partial work — who resolves it? The existing card network dispute process wasn't designed for agent-initiated transactions. AgentCourt is purpose-built for this.

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

## Policy Templates (7 total, 39 rules)

| Policy | Rules | Use Case |
|--------|-------|----------|
| `freelance-delivery` | 6 | Non-delivery, late delivery, partial delivery |
| `milestone-payment` | 5 | Unpaid milestones, overdue payments, incomplete work |
| `bug-bounty` | 5 | Reproducibility, severity thresholds, disclosure compliance |
| `sla-monitoring` | 5 | Uptime violations, latency breaches, partial degradation |
| `api-quality` | 7 | Schema mismatch, empty response, wrong types, stale data |
| `physical-commerce` | 6 | Non-delivery, wrong item, damage, returns |
| `scope-dispute` | 5 | Agent mandate exceeded, budget exceeded, ambiguous scope |

| Template | Rules | Use Case |
|----------|-------|----------|
| `freelance-delivery` | 6 | Digital work disputes: non-delivery, late delivery, scope issues |
| `milestone-payment` | 5 | Staged payments: unpaid milestones, overdue, partial |
| `bug-bounty` | 5 | Security bounties: reproducibility, severity, disclosure |
| `sla-monitoring` | 5 | Service violations: uptime, latency, degraded service |
| `api-quality` | 7 | Paid API disputes: schema mismatch, wrong types, stale data |
| `physical-commerce` | 6 | Product purchases: wrong item, damage, non-delivery, returns |
| `scope-dispute` | 5 | Agent mandate violations: unauthorized actions, budget exceeded, ambiguous scope |

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

Copy [`sdk/agentcourt_python_sdk.py`](sdk/agentcourt_python_sdk.py) — standard library only, no pip install needed.

### JavaScript / TypeScript

Copy [`sdk/agentcourt.js`](sdk/agentcourt.js) — zero dependencies, works in Node 18+ and browsers.
TypeScript declarations in [`sdk/agentcourt.d.ts`](sdk/agentcourt.d.ts).

### Postman

Import [`postman_collection.json`](postman_collection.json) — 9 ready-to-run requests for all 5 dispute types.

## MCP Server

AgentCourt ships with MCP tool definitions compatible with Claude Desktop, Cursor, and Claude Code. See [`src/mcp_server_config.py`](src/mcp_server_config.py).

**3 MCP Tools:**
- `agentcourt_resolve_dispute` — Submit a dispute, get a ruling
- `agentcourt_list_policies` — See available policy templates
- `agentcourt_get_verdict` — Retrieve a past verdict by case ID

## x402 Payment

AgentCourt is x402-native. The [`x402_middleware.py`](src/x402_middleware.py) module enables per-call payments:

- **$0.05/dispute** via USDC on Base
- OpenAPI `x-payment-info` annotations for AgentCash discovery
- `/.well-known/x402` discovery document for x402scan indexing
- PaymentVerifier with replay protection

**Already indexed on x402scan** — 16 endpoints discovered via OpenAPI spec.

## Stats

- **7 policy templates** with **39 rules** across 7 dispute domains
- **39/39 tests passing** (17 engine + 11 ADRP adapter + 11 x402 middleware)
- **Live on x402scan** with 16 discoverable endpoints
- **ADRP-compatible** (IETF draft-stone-adrp-00)

## Architecture

```
├── src/
│   ├── main.py                 # FastAPI app with REST endpoints
│   ├── x402_middleware.py       # x402 payment layer ($0.05 USDC/dispute)
│   ├── mcp_server_config.py     # MCP tool definitions (Claude, Cursor, Claude Code)
│   ├── engine/
│   │   └── policy_engine.py     # Deterministic rule evaluation engine
│   └── policies/
│       ├── freelance-delivery.json
│       ├── milestone-payment.json
│       ├── bug-bounty.json
│       ├── sla-monitoring.json
│       ├── api-quality.json
│       ├── physical-commerce.json
│       └── scope-dispute.json
├── sdk/
│   ├── agentcourt_python_sdk.py # Python SDK (zero-dependency, dataclasses)
│   ├── agentcourt.js            # JavaScript SDK (ESM + CommonJS)
│   └── agentcourt.d.ts          # TypeScript declarations
├── tests/                       # 39/39 tests (engine + ADRP + x402)
├── content/                     # Blog posts, proposals, competitive analysis
├── postman_collection.json      # 9 ready-to-run Postman requests
└── Dockerfile                   # Production deployment
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

| | AgentCourt | Tribunal | ADRP (SwarmSync) | Arbitova |
|---|---|---|---|---|
| **Type** | API product | On-chain court | Protocol spec (IETF draft) | Escrow + arbitration |
| **Model** | Standalone judgment layer | Multi-agent trial (lawyers, clerk, judge) | Wire protocol + state machine | Escrow + bundled arbitration |
| **Determinism** | Policy rules — same evidence = same ruling | Jury of iNFT judges — subjective | Crypto (deterministic) + Semantic (arbitration) | AI arbiter — subjective |
| **Latency** | <500ms per ruling | Full trial process (minutes/hours) | Protocol-defined | Unknown |
| **Custody** | Never. Non-custodial. | Escrow via smart contract | EscrowDirective output for rails | Holds funds in escrow |
| **Infrastructure** | Stateless API, zero deps | P2P (Gensyn AXL), 0G Chain, iNFTs | Protocol — bring your own infra | Their escrow contract |
| **Integration** | REST + SDK + MCP. Works with any platform | Deploy their court contracts | Implement the protocol | Use their escrow contract |
| **Lock-in** | None. Bring your own escrow, marketplace, payment rail | Must deploy on 0G Chain | Protocol-defined | Must use their escrow contract |

AgentCourt is not an escrow company. We don't compete with payment protocols. We are the judgment layer that any of them can call.

**Note on ADRP (IETF draft-stone-adrp-00):** ADRP defines a wire protocol for agent dispute resolution. AgentCourt's engine could serve as a backend implementation of ADRP's Semantic-class dispute resolution — we produce the `RulingBundle` that ADRP's state machine requires. This is complementary, not competitive.

## Pricing

**Design Partner Program (Now):** Free for first 5 partners. Full API access. Custom policy template included.

**Production (Post-Launch):** Per-dispute pricing. No transaction fees. No custody fees. No platform fees. You only pay when you need a ruling.

## Self-Hosting

```bash
docker-compose up
# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

Or run directly:

```bash
pip install fastapi uvicorn pydantic
python3 -m uvicorn src.main:app --reload
```

## License

MIT
