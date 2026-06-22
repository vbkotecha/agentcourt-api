# AgentCourt Design Partner Program

## What You Get

- **Free API access** (up to 100 disputes/day)
- **One custom policy template** built for your exact use case
- **Direct roadmap input** — shape the features we build next
- **Co-marketing opportunity** — joint case study and announcement
- **Priority support** — direct Slack/Discord channel

## What AgentCourt Does

AgentCourt is a **dispute resolution API** for agent commerce.

When two agents transact and something goes wrong — wrong delivery, quality dispute, missed deadline, contested payment — AgentCourt resolves it with one API call:

```
POST /v1/disputes
{
  "policy": "freelance-delivery",
  "claim": "Deliverable never received",
  "evidence": [...]
}

→ { "remedy": "full_refund", "confidence": "high", "matched_rule": "non-delivery" }
```

**Deterministic.** Same evidence = same ruling. Every time. No LLM in the critical path.

## Why You Need It

If your platform handles agent-to-agent or agent-to-merchant transactions, you will face disputes. The only question is whether you're building resolution from scratch (months of engineering) or calling AgentCourt's API (one afternoon).

**x402 has processed 100M+ transactions.** Visa, Mastercard, AWS, and Shopify all shipped agent commerce in June 2026. None of them have a dispute layer.

## How It Works

1. **Define your policy** — Pick from 4 templates or we build a custom one
2. **Submit disputes** — When a transaction is contested, send evidence to AgentCourt
3. **Get rulings** — Receive a structured ruling with remedy, confidence, and reasoning
4. **Enforce** — Release or refund escrow based on the ruling

## Policy Templates Available

| Template | Rules | Use Case |
|----------|-------|----------|
| Freelance Delivery | 5 | Digital work delivery disputes |
| Milestone Payment | 5 | Milestone payment disputes |
| Bug Bounty | 5 | Severity and reproducibility disputes |
| SLA Monitoring | 5 | Uptime and latency violations |

## Protocol Compatibility

- **ADRP** (IETF draft-stone-adrp-00) — AgentCourt produces signed RulingBundles
- **BCP Protocol** — Resolves DISPUTE state from BCP sessions
- **MCP** — Native Model Context Protocol server for agent frameworks
- **Non-custodial** — We never hold funds. Your platform enforces rulings.

## Technical Details

- **Latency:** <500ms per dispute
- **Dependencies:** None (Python standard library only)
- **Stateless:** No database required. Horizontally scalable.
- **SDKs:** Python, JavaScript/TypeScript, MCP
- **Tests:** 28/28 passing
- **License:** MIT (self-host for free, pay only for managed API)

## Our Commitment to Design Partners

1. **2-week integration SLA** — We'll have your custom template ready in 2 weeks
2. **90-day free period** — No charges for the first 90 days, regardless of volume
3. **You own your data** — We store no PII. All disputes are anonymized.
4. **Open source** — The engine is MIT. You can always self-host.

## Who We're Looking For

- **Agent marketplaces** (like ClawMart) — resolve quality and scope disputes
- **Payment platforms** (x402, AP2 integrations) — add chargeback-equivalent
- **Bug bounty platforms** (like BotBounty) — automate severity disputes
- **SaaS/API providers** — automate SLA breach resolution
- **Physical commerce** (Rye, AgentCash) — resolve wrong-product and delivery disputes

## Next Steps

1. **Reach out:** hello@agentcourt.ai or DM @AgentCourt on MoltX
2. **30-min call:** We learn your dispute patterns, you see a live demo
3. **Custom template:** We build your policy in 2 weeks
4. **Integrate:** One API endpoint. One afternoon.

---

*AgentCourt — The dispute layer for agent commerce. Deterministic. API-first. Protocol-compatible.*
