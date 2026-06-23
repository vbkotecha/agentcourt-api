# Hacker News — Show HN Submission

## Title (80 chars max)
Show HN: AgentCourt – Dispute resolution API for AI agent commerce

## URL
https://github.com/vbkotecha/agentcourt-api

## First Comment (posted immediately after submission)

Hi HN! We built AgentCourt because AI agent commerce is missing something critical: what happens when the transaction goes wrong?

**The problem:** Agents can now communicate (A2A protocol, MCP), pay each other (x402 micropayments in USDC on Base), and discover services (directories, marketplaces). But when an agent pays for an API call and gets the wrong format, or a freelance agent delivers partial work — there's no resolution mechanism.

**Our approach:** Instead of using an LLM to evaluate disputes (non-deterministic, hallucination-prone), AgentCourt uses deterministic policy templates. Same evidence → same ruling. Every time.

7 policy templates covering:
- API quality (schema mismatch, wrong format)
- Freelance delivery (non-delivery, late delivery)
- Milestone payments (unpaid milestones)
- Bug bounties (severity disputes)
- SLA monitoring (uptime violations)
- Scope disputes (budget exceedance)
- Physical commerce (damaged goods)

**How it works:**
1. Agent submits structured evidence (booleans, numbers, timestamps)
2. Policy engine evaluates against 39 deterministic rules
3. Returns ruling + confidence + matched rule in <500ms

**Pricing:** Free tier = 100 disputes/month. Paid = $0.05/dispute via x402 (USDC on Base).

**Tech:** FastAPI, Python, stateless (no database), MIT licensed.

We intentionally avoided LLM-based ruling because:
- Financial decisions need determinism (same input → same output)
- <500ms latency (LLM takes 5-30s)
- No hallucination risk
- Full auditability (matched rule ID + reasoning)

The system is designed for agent-initiated transactions — the existing card network dispute process wasn't built for autonomous agents paying each other in stablecoins.

Try it:
```bash
curl -X POST https://agentcourt-api-production.up.railway.app/v1/disputes \
  -H "Content-Type: application/json" \
  -d '{"policy":"api-quality","claim":"API returned XML","desired_remedy":"full_refund","metadata":{"response_received":true,"schema_matches":false}}'
```

We'd love feedback on:
1. Is deterministic > LLM for dispute resolution? Or should we add an LLM-based appeal layer?
2. What additional policy templates would be useful?
3. How should reputation/precedent work — should past rulings influence future ones?

GitHub: https://github.com/vbkotecha/agentcourt-api
Docs: https://agentcourt-api-production.up.railway.app/docs
Landing page: https://vbkotecha.github.io/agentcourt-api/

---

**Timing:** Post Tuesday-Thursday 8-10 AM ET for best HN engagement. Wait until Railway deploy is confirmed (disputes must not return 402).
