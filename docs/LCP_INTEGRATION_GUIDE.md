# AgentCourt × Legal Context Protocol (LCP) Integration Guide

## Overview

AgentCourt is the first LCP Level 4 (Integrated) dispute resolution engine. Any service that implements the Legal Context Protocol can use AgentCourt to resolve disputes automatically.

## Quick Start

### 1. Check a Domain's LCP Status

```bash
curl https://api.agentcourt.to/v1/lcp/check/api.example.com
```

```python
from lcp_client import AgentCourtLCP

client = AgentCourtLCP()
info = client.check_domain("api.example.com")
print(info.summary())
```

### 2. Verify Terms Hash

```bash
curl https://api.agentcourt.to/v1/lcp/verify/api.example.com
```

### 3. File an LCP-Compliant Dispute

```bash
curl -X POST https://api.agentcourt.to/v1/lcp/disputes \
  -H "Content-Type: application/json" \
  -d '{
    "service_domain": "api.example.com",
    "claimant": "buyer-agent",
    "respondent": "api.example.com",
    "claim": "API credits not delivered after payment",
    "desired_remedy": "Full refund of $50 USDC",
    "evidence": [
      {
        "type": "payment",
        "source": "Coinbase Commerce",
        "timestamp": "2026-06-30T00:00:00Z",
        "claimed_fact": "Payment of $50 USDC sent on Base",
        "reliability": "high"
      }
    ]
  }'
```

```python
from lcp_client import AgentCourtLCP, Evidence

client = AgentCourtLCP()
ruling = client.dispute(
    service_domain="api.example.com",
    claimant="buyer-agent",
    respondent="api.example.com",
    claim="API credits not delivered after payment",
    desired_remedy="Full refund of $50 USDC",
    evidence=[
        Evidence(
            type="payment",
            source="Coinbase Commerce",
            timestamp="2026-06-30T00:00:00Z",
            claimed_fact="Payment of $50 USDC sent on Base",
            reliability="high"
        )
    ]
)
print(ruling)
```

### 4. Using AgentCourt with MCP

Add AgentCourt's MCP server to your agent's MCP configuration:

```json
{
  "mcpServers": {
    "agentcourt-lcp": {
      "command": "python3",
      "args": ["mcp-server/lcp_mcp_server.py"]
    }
  }
}
```

Available MCP tools:
- `check_lcp_domain` — Check if a domain implements LCP
- `verify_lcp_terms` — Verify a domain's terms hash
- `file_lcp_dispute` — File an LCP-compliant dispute
- `list_dispute_policies` — List available dispute policies
- `get_agentcourt_lcp` — Get AgentCourt's own LCP discovery document

## Pointing Your LCP to AgentCourt

To use AgentCourt as your dispute resolution provider in your own LCP discovery document:

```json
{
  "terms": "https://yourservice.com/terms.md",
  "disputeResolution": {
    "method": "AgentCourt Policy-Driven Resolution",
    "jurisdiction": "San Francisco, CA, USA",
    "contact": "disputes@agentcourt.to",
    "source": "https://api.agentcourt.to/dispute-resolution-rules.md",
    "catalog": "https://api.agentcourt.to/.well-known/dispute-services.json"
  },
  "api": "https://api.agentcourt.to/v1/lcp/disputes"
}
```

## How It Works

```
Agent Transaction
    ↓
Payment via x402/MPP/AP2
    ↓
LCP Discovery — Agent fetches /.well-known/legal-context.json
    ↓
Terms Verified — SHA-256 hash matches
    ↓
Transaction Completes (or doesn't)
    ↓
Dispute Filed — POST /v1/lcp/disputes
    ↓
AgentCourt Engine Evaluates Evidence Against Policy Rules
    ↓
Deterministic Ruling (< 500ms)
    ↓
Remedy Recommendation + Precedent Recorded
```

## Policy Templates

| Policy | Rules | Use Case |
|---|---|---|
| freelance-delivery | 7 | Freelance contract disputes |
| milestone-payment | 6 | Milestone payment release |
| bug-bounty | 8 | Bug severity classification |
| sla-monitoring | 10 | SLA violation disputes |
| physical-commerce | varies | Physical product disputes |
| api-quality | varies | API quality issues |
| scope-dispute | varies | Agent mandate violations |

## Pricing

- **Free tier**: 100 disputes/month
- **Paid**: $0.05 USDC per dispute (via x402 on Base Mainnet)
