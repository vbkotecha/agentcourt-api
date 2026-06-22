# Changelog

All notable changes to AgentCourt are documented in this file.

## [1.0.0] — 2026-06-22

### Added
- **4 policy templates** (21 rules total):
  - `freelance-delivery` (6 rules): non-delivery, late delivery, on-time, partial, disputed acceptance, rejected quality
  - `milestone-payment` (5 rules): completed-unpaid, completed-paid, incomplete, partially-complete, disputed-completion
  - `bug-bounty` (5 rules): valid-full-payout, non-reproducible, partial-severity, disclosure-violation, disputed-reproducibility
  - `sla-monitoring` (5 rules): uptime-violation, latency-breach, partial-degradation, incidents-within-sla, insufficient-monitoring
- **Policy engine** with evidence scoring, fact extraction, and deterministic rule evaluation
- **REST API** with 5 endpoints: health, policies, disputes, verdicts, cases
- **Interactive Swagger UI** at `/swagger`
- **OpenAPI 3.0.3 spec** at `/openapi.yaml`
- **API documentation** at `/api-docs`
- **Interactive demos** at `/demos` for all 4 policy templates
- **Verdict dashboard** at `/verdicts` with 21 public rulings
- **Python SDK** (`agentcourt` on PyPI)
- **JavaScript/TypeScript SDK** (`@agentcourt/sdk` on npm)
- **MCP server** for Claude/AI agent integration
- **Postman collection** for one-click API testing
- **Integration guide** with 3 patterns (marketplace escrow, SLA monitoring, bug bounty)
- **Comprehensive test suite** — 17/17 tests passing across all policy templates
- **Landing page** with live ruling engine preview

### Engine Features
- Evidence scoring with type-based weights (0.0–1.0)
- Fact extraction from natural language evidence
- Content hash verification bonus (+0.1 confidence)
- Recency scoring (30-day window)
- Reliability multipliers (high/medium/low)
- Negative phrase detection for delivery, payment, and reproducibility
- Disputed acceptance handling (null vs true/false)
- Independent assessment preference for severity scoring
- SLA latency extraction that skips contract evidence
- Partial delivery detection with proportional remedies

### Infrastructure
- Deployed on Railway (auto-deploy from git)
- CORS enabled for all origins
- Stateless architecture (no database required for v1)
- Average ruling time: <500ms
