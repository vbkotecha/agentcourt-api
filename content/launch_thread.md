# AgentCourt Launch Thread — X/Twitter

Post from @AgentCourtHQ when account is created.
Include screenshot of verdict dashboard or API response.

---

1/ We just shipped AgentCourt — the dispute resolution layer for agent commerce.

Visa, Mastercard, and Google built the payment rails for AI agents.
Nobody built what happens when transactions go wrong.

We did. Here's what it does. 🧵

2/ The problem:

When an AI agent buys something and it goes wrong — late delivery, partial work, SLA breach, disputed bug bounty — who resolves it?

Card networks aren't built for agent disputes. There's no framework.

Until now.

3/ AgentCourt is a policy-driven dispute resolution API.

Submit evidence. Apply rules. Get a ruling.

Same evidence always produces the same ruling. Deterministic, not probabilistic.

4/ Four policy templates, 21 rules, all live:

📦 Freelance delivery (6 rules)
💰 Milestone payment (5 rules)  
🐛 Bug bounty (5 rules)
📊 SLA monitoring (5 rules)

Each tested with real evidence scenarios. 17/17 passing.

5/ How it works:

1. Both agents submit evidence (contracts, logs, commits, receipts)
2. Engine extracts facts using NLP + evidence scoring
3. Rules evaluate against facts
4. Output: matched rule + confidence + remedy + reasoning

Average time: <500ms

6/ Try it right now:

Live demos: agentcourt-api-production.up.railway.app/demos
API docs: agentcourt-api-production.up.railway.app/api-docs
Swagger UI: agentcourt-api-production.up.railway.app/swagger
Verdict dashboard: agentcourt-api-production.up.railway.app/verdicts

7/ For developers:

• Python SDK (pip install agentcourt)
• JavaScript/TypeScript SDK (npm i @agentcourt/sdk)
• MCP server for Claude integration
• OpenAPI 3.0.3 spec at /openapi.yaml
• Postman collection included
• MIT licensed

8/ We're looking for 5 design partners.

If you're building:
• An agent marketplace
• An escrow service
• A bounty platform
• An SLA monitoring tool

You need dispute resolution. Let's talk.

DM us or email support@agentcourt.to

9/ The agent economy needs three layers:

Transport (A2A, MCP) ✅ Built
Payment (x402, AP2, Visa IC) ✅ Built
Dispute resolution ✅ AgentCourt

The stack is complete.

Build with us: agentcourt-api-production.up.railway.app

---

# Notes for posting:
- Space out tweets 30-60 seconds apart
- Pin tweet 1 after posting
- Quote-tweet tweet 1 from @vbkotecha with commentary
- Include a screenshot or GIF of the demo page in tweet 1 or 6
