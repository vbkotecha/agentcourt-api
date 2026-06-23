# Security Policy

## Supported Versions

| Version | Supported |
| ------- | --------- |
| 1.0.x   | ✅        |

## Reporting a Vulnerability

AgentCourt is a stateless API that evaluates structured metadata against deterministic rules. The API does not store personal data or process financial transactions directly (x402 payments are handled by the payment layer, not AgentCourt).

If you discover a security vulnerability:

1. **Do NOT open a public issue**
2. Email: `vbkotecha@gmail.com` with subject `[SECURITY] AgentCourt`
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

You will receive a response within **48 hours**.

## Security Design Principles

### Stateless Evaluation
AgentCourt does not persist dispute data between requests. Each dispute is evaluated independently using deterministic rules. No session state, no database, no user data storage.

### No Financial Custody
AgentCourt does not hold, transfer, or escrow funds. x402 payments are processed by the payment middleware layer. AgentCourt only evaluates evidence and returns rulings.

### Deterministic Rules
All rulings are produced by JSON rule evaluation — not LLM inference. This eliminates:
- Prompt injection attacks
- Hallucination-based incorrect rulings
- Non-deterministic behavior

### Input Validation
All API inputs are validated against Pydantic schemas before rule evaluation. Invalid inputs are rejected with 422 Unprocessable Entity.

## Scope

**In scope:**
- AgentCourt API endpoints (`/v1/disputes`, `/v1/policies`, `/health`)
- Policy rule evaluation logic
- Input validation and sanitization

**Out of scope:**
- x402 payment infrastructure (handled by payment layer)
- Self-hosted deployments configured by users
- Third-party SDKs (Python, JavaScript) — these are thin clients

## Disclosure Policy

- We follow responsible disclosure
- Security fixes are prioritized and patched immediately
- Credit is given to reporters (unless anonymity is requested)

---

*AgentCourt is open source under the MIT license. Security is a community responsibility.*
