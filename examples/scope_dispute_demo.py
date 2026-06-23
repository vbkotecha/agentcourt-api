#!/usr/bin/env python3
"""
AgentCourt Scope Dispute Demo

Demonstrates the most important new dispute type in agent commerce:
when an AI agent exceeds its authorized mandate.

This example shows how to handle the exact scenario FraudBeat described
in May 2026: "agent exceeded mandate" disputes that traditional
chargeback systems can't categorize.
"""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "sdk"))
from agentcourt_python_sdk import AgentCourt

court = AgentCourt(
    base_url=os.getenv("AGENTCOURT_URL", "https://agentcourt-api-production.up.railway.app")
)

# ─────────────────────────────────────────────────────────────────
# Scenario 1: Agent bought a premium subscription when authorized for basic only
# ─────────────────────────────────────────────────────────────────
print("=" * 60)
print("SCENARIO 1: Agent exceeded mandate (unauthorized purchase)")
print("=" * 60)

ruling = court.dispute(
    policy="scope-dispute",
    claim="Agent purchased premium subscription when authorized for basic only",
    claimant="consumer",
    respondent="ai_assistant",
    desired_remedy="full_refund",
    contract={
        "parties": ["consumer", "ai_assistant"],
        "obligations": ["Agent must stay within authorized purchase scope"],
        "deadlines": ["2026-06-30"],
    },
    metadata={
        "mandate_violated": True,
        "unauthorized_action": True,
        "no_prior_consent": True,
        "unauthorized_action_detail": "purchased premium subscription at $99/month instead of basic at $9/month",
    },
    evidence=[
        {
            "type": "mandate_document",
            "source": "agent_config.json",
            "timestamp": "2026-06-01",
            "claimed_fact": "Agent authorized to purchase basic plan only, maximum $9/month",
        },
        {
            "type": "authorization_log",
            "source": "payment_audit.log",
            "timestamp": "2026-06-22",
            "claimed_fact": "Agent purchased premium subscription at $99/month without additional authorization",
        },
    ],
)

print(f"\nRule: {ruling.matched_rule}")
print(f"Remedy: {ruling.remedy}")
print(f"Confidence: {ruling.confidence}")
print(f"\nReasoning: {ruling.reasoning[:200]}...")

# ─────────────────────────────────────────────────────────────────
# Scenario 2: Agent went over budget
# ─────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("SCENARIO 2: Agent exceeded budget limit")
print("=" * 60)

ruling2 = court.dispute(
    policy="scope-dispute",
    claim="Agent spent $120 when budget was $50",
    claimant="consumer",
    respondent="ai_assistant",
    desired_remedy="partial_refund",
    contract={
        "parties": ["consumer", "ai_assistant"],
        "obligations": ["Agent must not exceed budget limits"],
    },
    metadata={
        "budget_limit": 50,
        "actual_spend": 120,
        "budget_exceeded": True,
    },
    evidence=[
        {
            "type": "mandate_document",
            "source": "agent_config.json",
            "timestamp": "2026-06-01",
            "claimed_fact": "Budget limit set to $50 per day",
        },
        {
            "type": "audit_trail",
            "source": "payments.log",
            "timestamp": "2026-06-22",
            "claimed_fact": "Agent spent $120 across 3 API calls, exceeding the $50 daily budget",
        },
    ],
)

print(f"\nRule: {ruling2.matched_rule}")
print(f"Remedy: {ruling2.remedy}")
print(f"Confidence: {ruling2.confidence}")
print(f"\nBudget overage: ${ruling2.facts.get('budget_overage', '?')}")

# ─────────────────────────────────────────────────────────────────
# Scenario 3: Agent acted within scope (no violation)
# ─────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("SCENARIO 3: Agent acted within mandate (no violation)")
print("=" * 60)

ruling3 = court.dispute(
    policy="scope-dispute",
    claim="Consumer claims agent was unauthorized (but it wasn't)",
    claimant="consumer",
    respondent="ai_assistant",
    desired_remedy="full_refund",
    contract={
        "parties": ["consumer", "ai_assistant"],
        "obligations": ["Agent operates within configured scope"],
    },
    metadata={
        "mandate_violated": False,
        "mandate_scope": "purchase API credits up to $50 per day",
    },
    evidence=[
        {
            "type": "mandate_document",
            "source": "config.json",
            "timestamp": "2026-06-01",
            "claimed_fact": "Agent authorized to purchase API credits up to $50/day",
        },
        {
            "type": "audit_trail",
            "source": "audit.log",
            "timestamp": "2026-06-22",
            "claimed_fact": "Agent purchased $30 in API credits, well within scope",
        },
    ],
)

print(f"\nRule: {ruling3.matched_rule}")
print(f"Remedy: {ruling3.remedy}")
print(f"Confidence: {ruling3.confidence}")
print(f"\n→ Consumer's dispute rejected. Agent was within mandate.")

print("\n" + "=" * 60)
print("Demo complete. All scenarios evaluated successfully.")
print("=" * 60)
