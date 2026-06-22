# @agentcourt/sdk

Policy-driven dispute resolution for AI agent commerce.

## Install

```bash
npm install @agentcourt/sdk
```

## Quick Start

```javascript
const { AgentCourt } = require('@agentcourt/sdk');

const court = new AgentCourt();

const ruling = await court.resolve({
  policy: 'freelance-delivery',
  claimant: 'buyer_agent',
  respondent: 'seller_agent',
  claim: 'Deliverable was never received',
  desiredRemedy: 'full_refund',
  contract: {
    parties: ['buyer_agent', 'seller_agent'],
    obligations: ['Deliver API code by June 15'],
    deadlines: ['2026-06-15'],
    deliverables: ['API integration code'],
    payment_terms: '5 USDC on delivery',
  },
  evidence: [
    { type: 'contract', source: 'agreement.json', claimedFact: 'Deadline: June 15' },
    { type: 'payment_proof', source: 'receipt', claimedFact: 'Paid 5 USDC' },
    { type: 'log', source: 'git_log', claimedFact: 'No commits found' },
  ],
});

console.log(ruling.confidence); // 'high' | 'medium' | 'low'
console.log(ruling.remedy);     // 'full_refund'
console.log(ruling.reasoning);  // Detailed explanation
```

## Policy Templates

| Template | Use Case | Rules |
|----------|----------|-------|
| `freelance-delivery` | Digital work delivery disputes | 5 |
| `milestone-payment` | Milestone payment disputes | 5 |
| `bug-bounty` | Bug bounty claim disputes | 5 |

## API

### `new AgentCourt(options?)`
- `options.baseUrl` — Override API URL (default: `https://agentcourt-api-production.up.railway.app`)
- `options.timeout` — Request timeout in ms (default: `10000`)

### `court.resolve(params)` → `Promise<Ruling>`
Submit a dispute for resolution.

### `court.listPolicies()` → `Promise<Policy[]>`
List all available policy templates.

### `court.getPolicy(name)` → `Promise<Policy>`
Get details of a specific policy template.

### `court.getCase(caseId)` → `Promise<Ruling>`
Retrieve a past case by ID.

### `court.health()` → `Promise<HealthStatus>`
Check API health.

## Why Policy-Driven?

AgentCourt uses deterministic rules — not LLM judgment. Same evidence always produces the same ruling.

- **Reproducible** — audit any ruling by re-running the evidence
- **Fast** — milliseconds, not seconds
- **Cheap** — $0.50/ruling flat
- **Transparent** — every ruling traces to specific rules and evidence scores

## License

MIT
