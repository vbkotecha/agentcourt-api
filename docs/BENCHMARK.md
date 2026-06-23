# AgentCourt Performance Benchmarks

**Last measured:** June 23, 2026  
**Environment:** Railway production (free tier)  
**Location:** US-East

## API Latency

| Endpoint | Method | Avg Latency | Samples |
|----------|--------|-------------|---------|
| `/health` | GET | **40ms** | 3 |
| `/v1/policies` | GET | **104ms** | 3 |
| `/v1/cases` | GET | **56ms** | 3 |
| `/v1/verdicts` | GET | **46ms** | 3 |
| `/v1/disputes` | POST | **<500ms** (target) | — |

All GET endpoints respond in under 105ms. Well within our <500ms target.

## Scale Metrics

| Metric | Value |
|--------|-------|
| Policy Templates | 7 |
| Total Rules | 39 |
| API Version | 1.0.0 |
| State | Stateless (no DB) |
| Cold Start | ~2s (Railway free tier) |
| Warm Response | <100ms (most endpoints) |

## Why So Fast?

AgentCourt achieves sub-100ms latency because:

1. **No database calls** — Each request is evaluated independently
2. **No LLM inference** — Rules are JSON evaluation, not neural networks
3. **FastAPI + Uvicorn** — Async Python framework, minimal overhead
4. **In-memory rule evaluation** — Policy templates loaded at startup

For comparison, LLM-based dispute resolution takes 5-30 seconds per dispute.

## Benchmarking Yourself

```bash
# Install hey (HTTP load tester)
go install github.com/rakyll/hey@latest

# Benchmark the health endpoint
hey -n 1000 -c 10 https://agentcourt-api-production.up.railway.app/health

# Benchmark the policies endpoint  
hey -n 1000 -c 10 https://agentcourt-api-production.up.railway.app/v1/policies
```

---

*These benchmarks are from Railway's free tier. Production deployments with dedicated resources will be faster.*
