# x402 Micro-Grant Application: AgentCourt

**To:** Coinbase x402 Team (@murrlincoln)
**Project:** AgentCourt — The Evaluator Layer for Agent Commerce
**Grant Amount Requested:** $3,000

---

## What AgentCourt Does

AgentCourt is a **policy-driven dispute resolution API** for x402 agent commerce. When an agent pays for a service via x402 and receives something wrong (bad API response, non-delivery, SLA breach), AgentCourt evaluates the evidence and produces a deterministic ruling in under 500ms.

**Live API:** https://agentcourt-api-production.up.railway.app/docs
**Open Source:** https://github.com/vbkotecha/agentcourt-api
**x402scan Indexed:** 16 endpoints discovered

## How It Unlocks x402 Demand

Agent commerce's #1 problem isn't payments — it's **trust**. Agents can pay via x402, but they can't verify they'll get what they paid for. Without dispute resolution:

- Marketplaces like AgentCash (921K+ paid calls/month) have no recourse when APIs return bad data
- Agents are hesitant to transact with unknown counterparties
- There's no consequence for providing poor service

AgentCourt fixes this. Every x402 transaction becomes protected:

```
Agent pays via x402 → Bad response → AgentCourt dispute → Ruling → Remedy
```

This **unlocks new demand** because agents can transact with confidence, knowing disputes are resolvable.

## Live on Mainnet

AgentCourt is **live and processing real disputes**:

- **14 verdicts resolved** on production
- **6 policy templates** covering 5 dispute domains:
  - Freelance delivery, milestone payment, bug bounty
  - SLA monitoring, API quality, physical commerce
- **x402 middleware** with $0.05/dispute pricing (USDC on Base)
- **OpenAPI payment annotations** for automatic AgentCash discovery
- **39/39 tests passing** (engine + ADRP adapter + x402 middleware)
- **Indexed on x402scan** — 16 resources discoverable

## Technical Architecture

- **Policy-first**: Deterministic rule sets, not subjective LLM judgment
- **Evidence-native**: Structured evidence with provenance, scored by type reliability
- **Non-custodial**: Never holds funds. Produces rulings only.
- **ADRP-compatible**: Implements Layers 1-3 of IETF draft-stone-adrp-00
- **ERC-8183 aligned**: AgentCourt IS the "Evaluator" role defined in the spec

## Demo

Run the AgentCash integration demo to see a complete x402 dispute lifecycle:

```bash
python3 examples/agentcash_integration_demo.py
```

Output shows: agent pays 0.028 USDC → API returns wrong type → dispute filed → ruling: `schema-mismatch, full_refund` → resolution in <500ms.

## SDKs Available

- **Python**: `sdk/agentcourt_python_sdk.py` (zero-dependency, typed dataclasses)
- **JavaScript**: `sdk/agentcourt.js` (ESM + CommonJS dual export)
- **TypeScript**: `sdk/agentcourt.d.ts` (full type declarations)
- **Postman**: `postman_collection.json` (9 ready-to-run requests)
- **MCP**: Config for Claude Desktop, Cursor, Claude Code

## Use of Funds

1. **Base Builder Code registration** — attribute all x402 dispute traffic
2. **npm/PyPI package publishing** — `pip install agentcourt` / `npm install @agentcourt/sdk`
3. **Additional policy templates** — DeFi liquidation disputes, NFT authenticity, data provenance
4. **Reputation & precedent system** — rulings create case law, trust scores emerge from patterns

## Contact

- **X:** @vbkotecha
- **Telegram:** @vbkotecha
- **GitHub:** github.com/vbkotecha/agentcourt-api

---

*AgentCourt is MIT licensed, open source, and live in production. We're building the trust layer that makes x402 agent commerce viable at scale.*
