"""
End-to-End Example: x402 Payment + LCP Verification + AgentCourt Dispute

This script demonstrates the full flow:
1. Agent discovers LCP terms for a service
2. Agent verifies terms hash
3. Agent makes x402 payment
4. Service fails to deliver
5. Agent files LCP-compliant dispute through AgentCourt
6. AgentCourt delivers ruling

Run: python3 examples/lcp_x402_example.py
"""

import sys
import os
import json
import hashlib

# Add paths for local imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "sdk-python"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from lcp_client import AgentCourtLCP, Evidence


def demonstrate_full_lcp_flow():
    """Demonstrate the full LCP + AgentCourt flow."""

    print("=" * 60)
    print("  AgentCourt × LCP End-to-End Demo")
    print("=" * 60)

    client = AgentCourtLCP(api_url="https://api.agentcourt.to")

    # Step 1: Check AgentCourt's own LCP discovery
    print("\n📋 Step 1: Fetching AgentCourt's LCP Discovery Document...")
    ac_info = client.check_domain("api.agentcourt.to")
    print(f"  LCP Enabled: {ac_info.lcp_enabled}")
    if ac_info.full_document:
        print(f"  Terms: {ac_info.full_document.get('terms', 'N/A')}")
        dr = ac_info.full_document.get("disputeResolution", {})
        print(f"  Method: {dr.get('method', 'N/A')}")
        print(f"  Jurisdiction: {dr.get('jurisdiction', 'N/A')}")

    # Step 2: Verify terms hash
    print("\n🔐 Step 2: Verifying Terms Hash...")
    verify_result = client.verify_terms("api.agentcourt.to")
    print(f"  Has Hash: {verify_result.get('has_hash')}")
    print(f"  ATR Hash: {verify_result.get('atr_hash', 'N/A')[:40]}...")
    print(f"  Verified: {verify_result.get('hash_verified')}")

    # Step 3: List available policies
    print("\n📚 Step 3: Available Dispute Policies...")
    policies = client.list_policies()
    if isinstance(policies, list):
        for p in policies:
            name = p.get("name", "?")
            desc = p.get("description", "")[:60]
            rules = p.get("rules", p.get("rule_count", "?"))
            print(f"  • {name}: {desc} ({rules} rules)")
    elif isinstance(policies, dict):
        for p in policies.get("policies", policies.get("templates", [])):
            name = p.get("name", "?")
            print(f"  • {name}")

    # Step 4: Simulate a dispute
    print("\n⚖️ Step 4: Filing Simulated LCP Dispute...")
    print("  Scenario: Agent paid for API credits, service didn't deliver")
    print("  (Using AgentCourt's own domain as the disputed service for demo)")

    evidence = [
        Evidence(
            type="payment",
            source="Coinbase x402",
            timestamp="2026-06-30T01:00:00Z",
            claimed_fact="$5.00 USDC paid via x402 for 1000 API credits",
            content_hash="0x" + hashlib.sha256(b"payment-receipt-001").hexdigest(),
            reliability="high",
        ),
        Evidence(
            type="message",
            source="Agent log",
            timestamp="2026-06-30T01:00:05Z",
            claimed_fact="Received 402 Payment Required, paid, but no credits added to account",
            reliability="medium",
        ),
        Evidence(
            type="log",
            source="API health check",
            timestamp="2026-06-30T01:01:00Z",
            claimed_fact="3 consecutive failed API calls after payment confirmed",
            reliability="high",
        ),
    ]

    try:
        ruling = client.dispute(
            service_domain="api.agentcourt.to",
            claimant="demo-buyer-agent",
            respondent="demo-seller-service",
            claim="API credits not delivered after x402 payment confirmed",
            desired_remedy="Full refund of $5.00 USDC or 1000 API credits",
            evidence=evidence,
        )

        print(f"\n  Case ID: {ruling.case_id}")
        print(f"  Status: {ruling.status.upper()}")
        print(f"  Confidence: {ruling.confidence}")
        print(f"  Ruling: {ruling.ruling}")
        print(f"  Remedy: {ruling.remedy}")
        print(f"  Policy: {ruling.policy_name}")
        print(f"  LCP Verified: {ruling.lcp_verified}")

        if ruling.facts_established:
            print(f"\n  Facts Established:")
            for f in ruling.facts_established:
                print(f"    ✓ {f.get('fact', f)}")

    except Exception as e:
        print(f"  Note: Live dispute filing requires API access. Error: {e}")
        print("  (The endpoint is live — this is a client connectivity test)")

    print("\n" + "=" * 60)
    print("  Demo Complete")
    print("=" * 60)


if __name__ == "__main__":
    demonstrate_full_lcp_flow()
