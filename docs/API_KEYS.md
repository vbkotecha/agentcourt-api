# API Keys & Authentication

## Current Status: No Authentication Required (v1.0.0)

AgentCourt v1.0.0 does not require API keys. The free tier (100 disputes/month) is available without authentication.

## Planned: API Keys (Phase 3)

API keys will be introduced in Phase 3 for:
- Rate limiting beyond free tier
- Usage analytics
- Custom policy assignment
- Webhook delivery

### Planned Key Format
```
ac_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ac_test_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Planned Usage
```python
from agentcourt import AgentCourt

# Free tier (no key needed)
court = AgentCourt()

# Authenticated (future)
court = AgentCourt(api_key="ac_live_xxxx...")
```

```bash
# Free tier (no key needed)
curl -X POST https://agentcourt-api-production.up.railway.app/v1/disputes ...

# Authenticated (future)
curl -X POST https://agentcourt-api-production.up.railway.app/v1/disputes \
  -H "Authorization: Bearer ac_live_xxxx..." ...
```

## Migration Path

When API keys are introduced:
1. Existing free tier (100/month) remains unchanged
2. API keys unlock higher limits + features
3. No breaking changes — keys are additive
