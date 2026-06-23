# Rate Limiting

## Free Tier (No Auth)
| Resource | Limit | Window |
|----------|-------|--------|
| Disputes | 100 | Per month |
| GET requests | 60 | Per minute |
| POST requests | 20 | Per minute |

## Rate Limit Headers (Planned)
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 97
X-RateLimit-Reset: 1719504000
```

## HTTP 429 Response
When rate limited, the API returns `429 Too Many Requests`:

```json
{
  "error": "RateLimitExceeded",
  "message": "Free tier limit reached: 100 disputes/month",
  "retry_after_seconds": 259200,
  "upgrade_url": "https://github.com/vbkotecha/agentcourt-api#pricing"
}
```

**Retry strategy:** Use exponential backoff (see [Error Handling Guide](ERROR_HANDLING.md)).
