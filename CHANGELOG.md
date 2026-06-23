# Changelog

All notable changes to AgentCourt are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-06-23

### Added
- **GitHub Pages Landing Page** — branded dark-theme site at vbkotecha.github.io/agentcourt-api
- **OpenGraph + Twitter Card** — rich social link previews with branded og-image
- **QUICKSTART.md** — 2-minute path to first ruling
- **INTEGRATION_GUIDE.md** — 7 integration paths with code examples
- **ERROR_HANDLING.md** — HTTP status codes, 402 x402 handling, retry strategy
- **BENCHMARK.md** — real performance data (sub-100ms GET latency)
- **ROADMAP.md** — 6-phase vision from v1 to mature ecosystem
- **Architecture Decision Records** — ADR-001 (deterministic over LLM), ADR-002 (no escrow), ADR-003 (stateless)
- **FAQ Section** — 7 expandable FAQs in README
- **Market Ecosystem Analysis** — trust stack positioning diagram
- **Product Hunt Launch Plan** — tagline, gallery, maker comment
- **dev.to Article** — "Building AgentCourt" technical deep-dive
- **Show HN Template** — ready-to-post submission
- **One-Shot Publisher** — `scripts/publish_all.sh` for npm + PyPI
- **Glama Submission Guide** — MCP server listing instructions
- **Policy Request Template** — structured issue for community policy requests
- **Community Discussion** — "What policies would you like to see?"
- **Performance Benchmarks** — measured: /health 40ms, /policies 104ms, /cases 56ms, /verdicts 46ms

### Distribution
- **7 PRs** across 565K+ combined GitHub stars (1 merged)
  - awesome-molt-ecosystem#27 — MERGED ✓
  - public-apis#6388 (443K★)
  - awesome-mcp-servers#8570 (89K★) — Glama submitted
  - awesome-ai-agents#1146 (28K★) — needs CLA
  - awesome-generative-ai#581 (3.5K★)
  - awesome-x402#589
  - awesome-agentic-commerce#356
- **Glama.ai** — MCP server submitted via API
- **GitHub Release v1.0.0** — published with full release notes
- **GitHub Pages** — enabled and live

## [1.2.0] - 2026-06-23

### Added
- **Python SDK** (`pip install agentcourt`) — zero dependencies, stdlib only
  - `AgentCourt` client with `file_dispute()`, `list_policies()`, `get_policy()`, `get_case()`, `list_cases()`, `health()`
  - `PaymentRequiredError` with x402 challenge details
  - `Dispute`, `Ruling`, `Policy`, `Evidence` dataclasses
- **JavaScript/TypeScript SDK** (`npm install @agentcourt/sdk`)
  - Full TypeScript definitions
  - Zero dependencies (native fetch, Node 18+)
- **MCP Server** (`@agentcourt/mcp-server`) — 6 tools for Claude/Cursor
  - `file_dispute`, `list_policies`, `get_policy_details`, `get_case`, `list_verdicts`, `health_check`
  - `server.json` manifest for MCP Registry submission
- **ElizaOS Plugin** (`@agentcourt/elizaos-plugin`)
  - `FILE_DISPUTE` and `CHECK_POLICIES` actions for ElizaOS agents
- **Integration Examples** — LangChain, CrewAI, Node.js drop-in tools
- **Architecture Document** — design philosophy, policy engine internals, determinism guarantee
- **Comparison Guide** — AgentCourt vs Arbitova (positioned as complementary)
- **API Examples** — complete request/response for all 7 policy templates
- **Policy Contribution Guide** — community-driven policy template creation
- **Demo Script** — zero-install interactive demo (`python3 demo.py`)
- **GitHub Codespaces** — one-click dev environment
- **8 API Tests** — health, policies, dispute filing, OpenAPI spec (all passing)
- **3 Blog Posts** — missing layer, dev.to tutorial, deterministic dispute resolution
- **4 GitHub Discussions** — welcome, integration guide, API examples, use cases
- **Issue Templates** — bug report, policy request, feature request

### Distribution
- awesome-molt-ecosystem: **MERGED** (x402 Economy section)
- public-apis: PR open (443K stars, Blockchain section)
- awesome-mcp-servers: PR open (89K stars, Legal section)
- awesome-x402: PR open (241 stars)
- awesome-agentic-commerce: PR open (133 stars)
- W3C Workshop: Expression of Interest submitted
- 12+ targeted GitHub comments across Coinbase, x402, LlamaIndex, cognitia.cloud

### Changed
- GitHub topics expanded to 20 (added: mcp-server, mcp, agentic-commerce, erc-8183, ai-payments)
- README updated with SDK install commands, demo, ElizaOS plugin, architecture docs
- CONTRIBUTING.md clone URL fixed

## [1.1.0] - 2026-06-23

### Added
- **scope-dispute policy template** — 5 rules for agent mandate violations
  - `mandate-exceeded-full-refund`: Unauthorized action, no prior consent
  - `mandate-exceeded-partial`: Unauthorized but prior consent exists
  - `budget-exceeded`: Spend over authorized limit with overage calculation
  - `within-mandate-no-violation`: Action was within scope
  - `ambiguous-mandate`: Undefined scope → escalate to human review
- **Dockerfile** for one-command self-hosting (`docker-compose up`)
- **AGENTS.md** for AI agent discovery and integration
- **llms.txt** for machine-readable project description
- **scope_dispute_demo.py** — 3 real-world scenarios using Python SDK
- **GitHub Discussions** — community entry point with welcome announcement
- **FUNDING.yml** — GitHub sponsor button
- **CHANGELOG.md** — this file
- **Market validation research** — 5 authoritative sources confirming product-market fit

### Changed
- Bug-bounty policy: metadata override for `bug_reproducible` / `bug_severity`
- README updated: 7 policy templates, 39 rules, scope-dispute in policy table
- GitHub repo: 20 topics for discoverability, homepage set to live API docs
- Description updated to reflect ERC-8183 alignment

### Fixed
- Bug-bounty template always returning `valid-bug-full-payout` — metadata fields were ignored (#8711fbf)

## [1.0.0] - 2026-06-22

### Added
- **Core API** — FastAPI with 6 endpoints for dispute submission and verdict retrieval
- **6 policy templates, 34 rules:**
  - `freelance-delivery` (5 rules): non-delivery, late delivery, partial delivery
  - `milestone-payment` (6 rules): unpaid milestones, overdue, partial payments
  - `bug-bounty` (5 rules): reproducibility, severity, disclosure compliance
  - `sla-monitoring` (6 rules): uptime, latency, degraded service
  - `api-quality` (6 rules): schema mismatch, wrong types, stale data, missing fields
  - `physical-commerce` (6 rules): wrong item, damage, non-delivery, returns
- **Policy Engine** — deterministic rule matching with evidence scoring and fact extraction
- **3 SDKs** (all zero-dependency):
  - Python: `agentcourt_python_sdk.py`
  - JavaScript: `agentcourt.js`
  - TypeScript: `agentcourt.d.ts`
- **x402 middleware** — $0.05/dispute pricing, OpenAPI payment annotations, `.well-known/x402` manifest
- **ADRP adapter** — Implements Layers 1-3 of IETF draft-stone-adrp-00
- **Postman collection** for API testing
- **MCP server config** for Claude Desktop, Cursor, Claude Code
- **docker-compose.yml** with healthcheck
- **GitHub community files:** CONTRIBUTING.md, issue templates (bug report, feature request, policy template), PR template
- **Test suite** — 39 tests covering policy engine, ADRP adapter, x402 middleware
- **Production deployment** on Railway with 50+ verdicts resolved

### Standards
- ERC-8183: AgentCourt fulfills the "Evaluator" role
- ADRP: Layers 1-3 of IETF draft-stone-adrp-00
- x402: USDC on Base, x402scan indexed (16 endpoints)
