# AgentCourt — Frequently Asked Questions

## General

### What is AgentCourt?
AgentCourt is a policy-driven dispute resolution API for agent commerce. When two AI agents transact and something goes wrong — late delivery, partial work, SLA breach, contested bug bounty — AgentCourt evaluates the evidence and produces a deterministic ruling.

### How is this different from traditional dispute resolution (Stripe, PayPal)?
Traditional dispute resolution is designed for human-initiated transactions with credit cards. Agent transactions happen at machine speed, involve non-traditional deliverables (code, data, API access), and need instant resolution. AgentCourt is purpose-built for this.

### Do agents need to be "legal persons" to use AgentCourt?
No. AgentCourt adjudicates based on policy rules and evidence, not legal frameworks. The ruling is a structured output (remedy + reasoning) that platforms can enforce programmatically.

## Technical

### Is AgentCourt deterministic?
Yes. The same evidence, submitted against the same policy template, will always produce the same ruling. We use pattern-based fact extraction and boolean rule evaluation — no LLM in the critical path.

### Why no LLM for dispute evaluation?
Three reasons:
1. **Determinism** — LLMs can produce different outputs for identical inputs
2. **Auditability** — Our engine shows exactly which evidence contributed which weight
3. **Cost/latency** — Our engine runs in <500ms at $0 marginal cost

### What evidence types are supported?
Contracts, payment proofs, invoices, receipts, git commits, server logs, files, messages, screenshots, testimonials, and claims. Each type has a default weight (contract=1.0, screenshot=0.5, claim=0.1).

### How are disputed facts handled?
When evidence from both parties conflicts, the fact is resolved in favor of the higher-weighted evidence. The dispute is transparent in the ruling output — you can see both claims and why one prevailed.

### Does AgentCourt hold funds in escrow?
No. AgentCourt is a ruling engine, not a financial intermediary. Platforms enforce rulings through their own escrow, reputation, or access control mechanisms.

### Can I create custom policy templates?
Yes. Policy templates are JSON files. Define evidence weights, fact extraction patterns, and boolean rules. See CONTRIBUTING.md for details.

### What's the API response time?
Average ruling generation: <500ms. The engine is stateless with no database dependencies.

## Integration

### How do I integrate AgentCourt with my marketplace?
Three options:
1. **REST API** — POST to /v1/disputes with evidence, get ruling
2. **Python/JS SDK** — Zero-dependency client libraries
3. **MCP Server** — For agent frameworks that support Model Context Protocol

### Does AgentCourt work with x402 / ERC-8183 / AP2?
Yes. AgentCourt is protocol-agnostic. It evaluates disputes regardless of how the payment was made. The ruling output includes a structured remedy that any payment protocol can execute.

### Can I self-host?
Yes. AgentCourt is MIT licensed. Clone the repo, run `python -m uvicorn src.main:app`, and you have your own dispute resolution engine.

### Is there a free tier?
The API is currently free during the design partner program (up to 100 disputes/day). Self-hosting is always free.

## Security & Privacy

### Does AgentCourt store my dispute data?
No. The engine is stateless. Dispute data is processed in-memory and returned in the response. We don't store evidence, contracts, or rulings (the calling platform tracks case history).

### Can evidence be verified?
Yes. Evidence can include a `content_hash` field. When present, the engine adds a +0.10 weight bonus, recognizing that hashable evidence is more trustworthy.

### What about biased policies?
All policy templates are open source and inspectable. Anyone can audit the rules before submitting a dispute. Custom templates let platforms define their own fairness criteria.
