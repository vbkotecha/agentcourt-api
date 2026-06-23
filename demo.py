#!/usr/bin/env python3
"""
AgentCourt Quick Demo — No installation required.

Run: python3 demo.py

This script demonstrates AgentCourt's dispute resolution capabilities
by filing 3 sample disputes across different policy templates.
"""

import json
import urllib.request

BASE_URL = "https://agentcourt-api-production.up.railway.app"


def api_get(path):
    resp = urllib.request.urlopen(f"{BASE_URL}{path}", timeout=10)
    return json.loads(resp.read())


def api_post(path, data):
    body = json.dumps(data).encode()
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        if e.code == 402:
            return {"error": "Payment required — free tier limit reached or x402 payment needed"}
        return {"error": f"HTTP {e.code}"}


def main():
    print("=" * 60)
    print("  AgentCourt Quick Demo")
    print("  Policy-driven dispute resolution for agent commerce")
    print("=" * 60)

    # 1. Health check
    print("\n1. API Health Check")
    print("-" * 40)
    health = api_get("/health")
    print(f"   Status: {health.get('status', '?')}")
    print(f"   Version: {health.get('version', '?')}")
    print(f"   Policies: {len(health.get('policies', []))}")

    # 2. List policies
    print("\n2. Available Policy Templates")
    print("-" * 40)
    policies = api_get("/v1/policies")
    for p in policies:
        name = p.get("name", "?")
        rules = p.get("rule_count", "?")
        desc = p.get("description", "")[:50]
        print(f"   {name:20s} ({rules} rules) — {desc}")

    # 3. File sample disputes
    print("\n3. Sample Disputes")
    print("-" * 40)

    samples = [
        {
            "label": "API Quality: Schema Mismatch",
            "data": {
                "claimant": "demo-agent",
                "respondent": "stock-api",
                "contract": {"parties": ["demo-agent", "stock-api"], "obligations": ["Return JSON response"]},
                "claim": "API returned XML instead of JSON",
                "desired_remedy": "full_refund",
                "evidence": [{"type": "log", "source": "demo", "timestamp": "2026-01-01T00:00:00Z", "claimed_fact": "Content-Type was text/xml"}],
                "policy": "api-quality",
                "metadata": {"response_received": True, "schema_matches": False}
            }
        },
        {
            "label": "Freelance: Non-Delivery",
            "data": {
                "claimant": "demo-client",
                "respondent": "demo-freelancer",
                "contract": {"parties": ["demo-client", "demo-freelancer"], "obligations": ["Deliver web scraper"]},
                "claim": "Work was never delivered",
                "desired_remedy": "full_refund",
                "evidence": [{"type": "log", "source": "demo", "timestamp": "2026-01-01T00:00:00Z", "claimed_fact": "No deliverable submitted"}],
                "policy": "freelance-delivery",
                "metadata": {"delivered": False, "meets_spec": False, "response_received": False}
            }
        },
        {
            "label": "SLA: Uptime Breach",
            "data": {
                "claimant": "demo-subscriber",
                "respondent": "demo-provider",
                "contract": {"parties": ["demo-subscriber", "demo-provider"], "obligations": ["99.9% uptime"]},
                "claim": "Service down for 4 hours",
                "desired_remedy": "partial_refund",
                "evidence": [{"type": "log", "source": "demo", "timestamp": "2026-01-01T00:00:00Z", "claimed_fact": "Service unavailable"}],
                "policy": "sla-monitoring",
                "metadata": {"uptime_percentage": 83.3, "sla_threshold": 99.9}
            }
        }
    ]

    for sample in samples:
        print(f"\n   Filing: {sample['label']}")
        result = api_post("/v1/disputes", sample["data"])
        if "error" in result:
            print(f"   Result: {result['error']}")
            print("   (Free tier limit may have been reached)")
            break
        ruling = result.get("ruling", "?")
        confidence = result.get("confidence", "?")
        case_id = result.get("case_id", "?")
        reasoning = result.get("reasoning", "?")[:60]
        print(f"   Ruling: {ruling}")
        print(f"   Confidence: {confidence}")
        print(f"   Case ID: {case_id}")
        print(f"   Reasoning: {reasoning}")

    print("\n" + "=" * 60)
    print("  Demo complete!")
    print(f"  API: {BASE_URL}/docs")
    print(f"  GitHub: https://github.com/vbkotecha/agentcourt-api")
    print("=" * 60)


if __name__ == "__main__":
    import urllib.error
    main()
