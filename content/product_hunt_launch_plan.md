# AgentCourt — Product Hunt Launch Plan

## Pre-Launch Checklist

### Assets Needed
- [ ] Logo (256x256)
- [ ] Gallery images (3-5, showing the API docs, demo, code examples)
- [ ] Tagline (60 chars max)
- [ ] Description (260 chars for summary)
- [ ] Maker comment draft (first comment on launch day)

### Suggested Tagline (60 chars)
"Dispute resolution for AI agent commerce. $0.05/ruling."

### Suggested Summary
"Policy-driven API that resolves disputes between AI agents in under 500ms. 7 templates, 39 rules, x402-native. When agents transact and things go wrong."

### Categories
- Developer Tools
- API
- Artificial Intelligence

### Gallery Slides
1. **Hero**: AgentCourt logo + "Dispute Resolution for Agent Commerce" + key stats
2. **Problem**: Agent pays for API → gets wrong response → who resolves it?
3. **Solution**: Submit evidence → deterministic ruling in <500ms
4. **Integration**: 5 paths (Python, JS, MCP, ElizaOS, REST)
5. **Comparison**: Deterministic rules vs LLM-as-judge

### Maker Comment Draft
"Hey Product Hunt! 👋 

We built AgentCourt because the agent commerce stack was missing something critical: what happens when the transaction goes wrong?

Agents can now communicate (A2A, MCP), pay each other (x402), and discover services (CDP Bazaar). But when an agent pays for an API call and gets XML instead of JSON — or pays for a service that never responds — there's no resolution mechanism.

AgentCourt fills that gap with deterministic policy templates. Same evidence → same ruling, every time. No LLM hallucination in the ruling path.

Try it: `curl -X POST https://agentcourt-api-production.up.railway.app/v1/disputes -H 'Content-Type: application/json' -d '{"policy":"api-quality","claim":"API returned XML","desired_remedy":"full_refund","metadata":{"response_received":true,"schema_matches":false}}'`

Free tier: 100 disputes/month. Happy to answer questions!"

## Launch Day Strategy

### Timing
- Launch at 12:01 AM PT on a Tuesday or Wednesday
- First 4 hours are critical for ranking

### Distribution
- Post on X/Twitter
- Share in Discord/Slack communities (AI agents, web3, developer tools)
- Email to anyone who starred/watched the repo
- Post on Hacker News (after PH launch stabilizes)

### After Launch
- Respond to every comment within 30 minutes
- Share milestone updates ("Top 5 in Developer Tools!")
- Thank early supporters publicly
