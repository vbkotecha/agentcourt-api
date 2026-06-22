"""
AgentCourt Policy Engine — Test Suite

Tests all 4 policy templates (20 rules total) against the live API.
Run: python3 tests/test_policy_engine.py
"""
import json
import urllib.request
import sys
from datetime import datetime

API = "https://agentcourt-api-production.up.railway.app/v1/disputes"
LOCAL_API = "http://localhost:8000/v1/disputes"

passed = 0
failed = 0
errors = []


def submit(name, case, expected_rule, expected_confidence=None, expected_remedy=None):
    """Submit a test case and verify the ruling."""
    global passed, failed
    payload = json.dumps(case).encode()
    req = urllib.request.Request(API, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        result = json.loads(resp.read())
    except Exception as e:
        failed += 1
        errors.append(f"FAIL [{name}]: API error: {e}")
        return

    rule = result.get("matched_rule_id", "?")
    conf = result.get("confidence", "?")
    remedy = result.get("remedy", "?")

    ok = rule == expected_rule
    if expected_confidence:
        ok = ok and conf == expected_confidence
    if expected_remedy:
        ok = ok and remedy == expected_remedy

    if ok:
        passed += 1
        print(f"  PASS [{name}] → {rule} / {conf} / {remedy}")
    else:
        failed += 1
        detail = f"got {rule}/{conf}/{remedy}, expected {expected_rule}"
        if expected_confidence:
            detail += f"/{expected_confidence}"
        if expected_remedy:
            detail += f"/{expected_remedy}"
        errors.append(f"FAIL [{name}]: {detail}")
        print(f"  FAIL [{name}] → {rule} / {conf} / {remedy} (expected {expected_rule})")


# ═══════════════════════════════════════════════════════════════
# FREELANCE DELIVERY TESTS
# ═══════════════════════════════════════════════════════════════
print("\n=== FREELANCE DELIVERY (5 tests) ===")

# 1. Clear non-delivery → high confidence, full refund
submit("non-delivery-clear", {
    "claimant": "buyer", "respondent": "seller",
    "contract": {"parties": ["buyer", "seller"], "obligations": ["Deliver logo design by June 20"],
                 "deadlines": ["2026-06-20"], "deliverables": ["3 logo concepts"], "payment_terms": "10 USDC on delivery"},
    "claim": "Deliverable was never received.", "desired_remedy": "full_refund", "policy": "freelance-delivery",
    "evidence": [
        {"type": "contract", "source": "agreement.json", "timestamp": "2026-06-15", "claimed_fact": "Seller must deliver 3 logo concepts by June 20"},
        {"type": "payment_proof", "source": "x402_receipt", "timestamp": "2026-06-15", "claimed_fact": "Buyer paid 10 USDC upfront"},
        {"type": "log", "source": "design_tool", "timestamp": "2026-06-22", "claimed_fact": "No design files exported or delivered"}
    ]
}, "non-delivery")

# 2. Late delivery, eventually accepted
submit("late-delivery-accepted", {
    "claimant": "buyer", "respondent": "seller",
    "contract": {"parties": ["buyer", "seller"], "obligations": ["Deliver code by June 10"],
                 "deadlines": ["2026-06-10"], "deliverables": ["Python module"], "payment_terms": "20 USDC"},
    "claim": "Delivery was 5 days late but I accepted the work.", "desired_remedy": "partial_refund", "policy": "freelance-delivery",
    "evidence": [
        {"type": "contract", "source": "agreement.json", "timestamp": "2026-06-01", "claimed_fact": "Delivery due June 10"},
        {"type": "commit", "source": "github", "timestamp": "2026-06-15", "claimed_fact": "Code delivered on June 15"},
        {"type": "message", "source": "email", "timestamp": "2026-06-16", "claimed_fact": "Buyer accepted the late delivery"}
    ]
}, "late-delivery-accepted")

# 3. Delivery on time, payment confirmed → positive match (no breach)
submit("on-time-delivery-no-breach", {
    "claimant": "buyer", "respondent": "seller",
    "contract": {"parties": ["buyer", "seller"], "obligations": ["Deliver design by June 10"],
                 "deadlines": ["2026-06-10"], "deliverables": ["UI mockup"], "payment_terms": "15 USDC"},
    "claim": "No issues with delivery.", "desired_remedy": "none", "policy": "freelance-delivery",
    "evidence": [
        {"type": "contract", "source": "agreement.json", "timestamp": "2026-06-01", "claimed_fact": "Deliver UI mockup by June 10"},
        {"type": "file", "source": "figma", "timestamp": "2026-06-09", "claimed_fact": "UI mockup delivered on June 9"},
        {"type": "message", "source": "slack", "timestamp": "2026-06-10", "claimed_fact": "Buyer confirmed acceptance and paid 15 USDC"}
    ]
}, "delivery-on-time-accepted")  # Positive rule — no breach

# 4. Partial delivery
submit("partial-delivery", {
    "claimant": "buyer", "respondent": "seller",
    "contract": {"parties": ["buyer", "seller"], "obligations": ["Deliver 5 landing page designs"],
                 "deadlines": ["2026-06-20"], "deliverables": ["5 designs"], "payment_terms": "50 USDC"},
    "claim": "Only 2 of 5 designs were delivered.", "desired_remedy": "partial_refund", "policy": "freelance-delivery",
    "evidence": [
        {"type": "contract", "source": "agreement.json", "timestamp": "2026-06-10", "claimed_fact": "Deliver 5 landing page designs by June 20"},
        {"type": "file", "source": "designs", "timestamp": "2026-06-19", "claimed_fact": "Only 2 of 5 designs delivered"},
        {"type": "message", "source": "slack", "timestamp": "2026-06-20", "claimed_fact": "Seller acknowledged partial delivery of 2 out of 5"}
    ]
}, "partial-delivery")

# 5. Disputed acceptance (conflicting evidence)
submit("disputed-acceptance", {
    "claimant": "buyer", "respondent": "seller",
    "contract": {"parties": ["buyer", "seller"], "obligations": ["Deliver mobile app"],
                 "deadlines": ["2026-06-15"], "deliverables": ["Working iOS app"], "payment_terms": "100 USDC"},
    "claim": "The app was never accepted but seller claims it was.", "desired_remedy": "full_refund", "policy": "freelance-delivery",
    "evidence": [
        {"type": "contract", "source": "agreement.json", "timestamp": "2026-06-01", "claimed_fact": "Deliver working iOS app by June 15"},
        {"type": "commit", "source": "github", "timestamp": "2026-06-14", "claimed_fact": "App source code pushed to repository"},
        {"type": "message", "source": "slack", "timestamp": "2026-06-15", "claimed_fact": "Seller claims buyer accepted the delivery"},
        {"type": "message", "source": "email", "timestamp": "2026-06-16", "claimed_fact": "Buyer disputes acceptance citing multiple bugs and crashes"}
    ]
}, "disputed-acceptance")


# ═══════════════════════════════════════════════════════════════
# MILESTONE PAYMENT TESTS
# ═══════════════════════════════════════════════════════════════
print("\n=== MILESTONE PAYMENT (4 tests) ===")

# 6. Milestone completed, unpaid
submit("milestone-completed-unpaid", {
    "claimant": "developer", "respondent": "client",
    "contract": {"parties": ["developer", "client"], "obligations": ["Complete API integration milestone"],
                 "deadlines": ["2026-06-18"], "deliverables": ["Working API"], "payment_terms": "25 USDC within 7 days of completion"},
    "claim": "Milestone completed but payment never received.", "desired_remedy": "payment", "policy": "milestone-payment",
    "evidence": [
        {"type": "contract", "source": "milestone_agreement.json", "timestamp": "2026-06-10", "claimed_fact": "25 USDC due on milestone completion within 7 days"},
        {"type": "commit", "source": "github", "timestamp": "2026-06-17", "claimed_fact": "API endpoint implemented and deployed"},
        {"type": "message", "source": "slack", "timestamp": "2026-06-18", "claimed_fact": "Buyer acknowledged milestone completion"},
        {"type": "log", "source": "payment_ledger", "timestamp": "2026-06-22", "claimed_fact": "No payment received 4 days after completion"}
    ]
}, "milestone-completed-unpaid", None, "full_payment_plus_penalty")

# 7. Milestone completed and paid → positive match
submit("milestone-completed-paid", {
    "claimant": "developer", "respondent": "client",
    "contract": {"parties": ["developer", "client"], "obligations": ["Complete design milestone"],
                 "deadlines": ["2026-06-10"], "deliverables": ["Design mockups"], "payment_terms": "30 USDC on completion"},
    "claim": "Payment was received.", "desired_remedy": "none", "policy": "milestone-payment",
    "evidence": [
        {"type": "contract", "source": "agreement.json", "timestamp": "2026-06-01", "claimed_fact": "30 USDC on design milestone completion"},
        {"type": "file", "source": "figma", "timestamp": "2026-06-09", "claimed_fact": "Design mockups delivered and accepted"},
        {"type": "receipt", "source": "blockchain", "timestamp": "2026-06-10", "claimed_fact": "30 USDC payment received via x402"}
    ]
}, "milestone-completed-paid")

# 8. Milestone incomplete, payment demanded
submit("milestone-incomplete", {
    "claimant": "developer", "respondent": "client",
    "contract": {"parties": ["developer", "client"], "obligations": ["Complete full backend by June 15"],
                 "deadlines": ["2026-06-15"], "deliverables": ["Backend API"], "payment_terms": "50 USDC"},
    "claim": "Client refuses to pay for incomplete milestone.", "desired_remedy": "payment", "policy": "milestone-payment",
    "evidence": [
        {"type": "contract", "source": "agreement.json", "timestamp": "2026-06-01", "claimed_fact": "50 USDC on backend completion by June 15"},
        {"type": "log", "source": "github", "timestamp": "2026-06-14", "claimed_fact": "Backend only 40% complete, major features missing"},
        {"type": "message", "source": "slack", "timestamp": "2026-06-15", "claimed_fact": "Client rejected incomplete deliverable"}
    ]
}, "milestone-incomplete-payment-demanded")

# 9. Milestone partially complete
submit("milestone-partial", {
    "claimant": "developer", "respondent": "client",
    "contract": {"parties": ["developer", "client"], "obligations": ["Complete 10 features"],
                 "deadlines": ["2026-06-20"], "deliverables": ["10 features"], "payment_terms": "100 USDC"},
    "claim": "7 of 10 features completed.", "desired_remedy": "payment", "policy": "milestone-payment",
    "evidence": [
        {"type": "contract", "source": "agreement.json", "timestamp": "2026-06-01", "claimed_fact": "100 USDC for 10 features"},
        {"type": "commit", "source": "github", "timestamp": "2026-06-19", "claimed_fact": "7 of 10 features implemented and tested"},
        {"type": "log", "source": "test_results", "timestamp": "2026-06-19", "claimed_fact": "70% of features passing tests"}
    ]
}, "milestone-partially-complete")


# ═══════════════════════════════════════════════════════════════
# BUG BOUNTY TESTS
# ═══════════════════════════════════════════════════════════════
print("\n=== BUG BOUNTY (4 tests) ===")

# 10. Valid critical bug, reproducible
submit("valid-critical-bug", {
    "claimant": "researcher", "respondent": "vendor",
    "contract": {"parties": ["researcher", "vendor"], "obligations": ["Pay for reproducible critical bugs"],
                 "deliverables": ["Bug report"], "payment_terms": "50 USDC for critical severity"},
    "claim": "Critical bug rejected but it's reproducible.", "desired_remedy": "payment", "policy": "bug-bounty",
    "evidence": [
        {"type": "contract", "source": "bounty_program.json", "timestamp": "2026-06-01", "claimed_fact": "50 USDC for critical bugs"},
        {"type": "file", "source": "bug_report.md", "timestamp": "2026-06-19", "claimed_fact": "Detailed reproduction steps for critical vulnerability"},
        {"type": "log", "source": "test_env", "timestamp": "2026-06-20", "claimed_fact": "Bug reproduced in 3 independent runs confirming critical severity"},
        {"type": "message", "source": "email", "timestamp": "2026-06-21", "claimed_fact": "Vendor claimed non-reproducible without testing"}
    ]
}, "valid-bug-full-payout")

# 11. Non-reproducible bug
submit("non-reproducible-bug", {
    "claimant": "researcher", "respondent": "vendor",
    "contract": {"parties": ["researcher", "vendor"], "obligations": ["Pay for reproducible bugs"],
                 "deliverables": ["Bug report"], "payment_terms": "30 USDC for verified bugs"},
    "claim": "Vendor refuses to pay for my bug report.", "desired_remedy": "payment", "policy": "bug-bounty",
    "evidence": [
        {"type": "contract", "source": "bounty.json", "timestamp": "2026-06-01", "claimed_fact": "30 USDC for verified reproducible bugs"},
        {"type": "file", "source": "report.md", "timestamp": "2026-06-15", "claimed_fact": "Bug report submitted with vague steps"},
        {"type": "log", "source": "vendor_test", "timestamp": "2026-06-18", "claimed_fact": "Bug not reproducible in 5 attempts"},
        {"type": "log", "source": "independent_test", "timestamp": "2026-06-19", "claimed_fact": "Could not reproduce bug in clean environment"}
    ]
}, "non-reproducible-bug")

# 12. Valid bug, lower severity than claimed
submit("partial-severity-bug", {
    "claimant": "researcher", "respondent": "vendor",
    "contract": {"parties": ["researcher", "vendor"], "obligations": ["Pay based on severity"],
                 "deliverables": ["Bug report"], "payment_terms": "50 USDC critical, 25 USDC high, 10 USDC medium"},
    "claim": "Bug marked as medium but it's critical.", "desired_remedy": "payment", "policy": "bug-bounty",
    "evidence": [
        {"type": "contract", "source": "bounty.json", "timestamp": "2026-06-01", "claimed_fact": "50 USDC for critical, 25 for high"},
        {"type": "file", "source": "report.md", "timestamp": "2026-06-15", "claimed_fact": "Bug report claims critical severity"},
        {"type": "log", "source": "assessment", "timestamp": "2026-06-17", "claimed_fact": "Independent assessment confirms bug is reproducible but rated medium severity"},
        {"type": "log", "source": "test", "timestamp": "2026-06-17", "claimed_fact": "Bug reproduced once but requires highly specific conditions"}
    ]
}, "valid-bug-partial-severity")

# 13. Disclosure violation
submit("disclosure-violation", {
    "claimant": "researcher", "respondent": "vendor",
    "contract": {"parties": ["researcher", "vendor"], "obligations": ["Follow responsible disclosure policy"],
                 "deliverables": ["Bug report"], "payment_terms": "50 USDC for critical with responsible disclosure"},
    "claim": "Vendor denied payout claiming I violated disclosure.", "desired_remedy": "payment", "policy": "bug-bounty",
    "evidence": [
        {"type": "contract", "source": "bounty.json", "timestamp": "2026-06-01", "claimed_fact": "Requires responsible disclosure before public reporting"},
        {"type": "file", "source": "blog.md", "timestamp": "2026-06-15", "claimed_fact": "Bug details published publicly before vendor notification"},
        {"type": "message", "source": "twitter", "timestamp": "2026-06-15", "claimed_fact": "Researcher tweeted exploit details publicly"},
        {"type": "log", "source": "timestamp", "timestamp": "2026-06-16", "claimed_fact": "Vendor notified 24 hours after public disclosure"}
    ]
}, "disclosure-violation")


# ═══════════════════════════════════════════════════════════════
# SLA MONITORING TESTS
# ═══════════════════════════════════════════════════════════════
print("\n=== SLA MONITORING (4 tests) ===")

# 14. Uptime violation (clear breach)
submit("uptime-violation", {
    "claimant": "consumer", "respondent": "provider",
    "contract": {"parties": ["consumer", "provider"], "obligations": ["Maintain 99.9% uptime SLA", "Max latency 200ms"],
                 "payment_terms": "500 USDC/month with SLA credits"},
    "claim": "Uptime fell below 99.9% SLA.", "desired_remedy": "service_credit", "policy": "sla-monitoring",
    "evidence": [
        {"type": "contract", "source": "agreement.json", "timestamp": "2026-06-01", "claimed_fact": "Provider agrees to 99.9% uptime SLA"},
        {"type": "log", "source": "uptime_monitor", "timestamp": "2026-06-22", "claimed_fact": "Measured actual uptime of 98.2% during June monitoring period"},
        {"type": "log", "source": "incident_log", "timestamp": "2026-06-15", "claimed_fact": "Three outages totaling 4 hours of downtime"}
    ]
}, "uptime-violation", None, "service_credit")

# 15. Latency breach
submit("latency-breach", {
    "claimant": "consumer", "respondent": "provider",
    "contract": {"parties": ["consumer", "provider"], "obligations": ["Max response time 100ms"],
                 "payment_terms": "200 USDC/month"},
    "claim": "Response times consistently exceeded 100ms.", "desired_remedy": "service_credit", "policy": "sla-monitoring",
    "evidence": [
        {"type": "contract", "source": "agreement.json", "timestamp": "2026-06-01", "claimed_fact": "Maximum response time 100ms guaranteed"},
        {"type": "log", "source": "latency_monitor", "timestamp": "2026-06-20", "claimed_fact": "Average response latency of 250ms during monitoring period"},
        {"type": "log", "source": "p95_log", "timestamp": "2026-06-20", "claimed_fact": "P95 latency of 400ms significantly exceeds 100ms threshold"}
    ]
}, "latency-breach")

# 16. Incidents within SLA (no breach)
submit("incidents-within-sla", {
    "claimant": "consumer", "respondent": "provider",
    "contract": {"parties": ["consumer", "provider"], "obligations": ["Maintain 99.9% uptime"],
                 "payment_terms": "300 USDC/month"},
    "claim": "Brief outage should trigger credit.", "desired_remedy": "service_credit", "policy": "sla-monitoring",
    "evidence": [
        {"type": "contract", "source": "agreement.json", "timestamp": "2026-06-01", "claimed_fact": "99.9% uptime SLA"},
        {"type": "log", "source": "monitor", "timestamp": "2026-06-22", "claimed_fact": "Measured actual uptime of 99.95% for June"},
        {"type": "log", "source": "incident", "timestamp": "2026-06-15", "claimed_fact": "Brief 2-minute outage occurred but uptime remained above SLA"}
    ]
}, "incidents-within-sla")

# 17. Insufficient monitoring data → default-no-match (low confidence)
submit("insufficient-monitoring", {
    "claimant": "consumer", "respondent": "provider",
    "contract": {"parties": ["consumer", "provider"], "obligations": ["Maintain 99.5% uptime"],
                 "payment_terms": "100 USDC/month"},
    "claim": "Service felt slow.", "desired_remedy": "service_credit", "policy": "sla-monitoring",
    "evidence": [
        {"type": "contract", "source": "agreement.json", "timestamp": "2026-06-01", "claimed_fact": "99.5% uptime SLA"},
        {"type": "message", "source": "email", "timestamp": "2026-06-20", "claimed_fact": "Consumer subjectively reports service felt slow"}
    ]
}, "default-no-match")  # No log/monitoring evidence → falls through to default


# ═══════════════════════════════════════════════════════════════
# RESULTS
# ═══════════════════════════════════════════════════════════════
print(f"\n{'='*50}")
print(f"RESULTS: {passed} passed, {failed} failed, {passed+failed} total")
print(f"{'='*50}")

if errors:
    print("\nFailures:")
    for e in errors:
        print(f"  {e}")
    sys.exit(1)
else:
    print("\nAll tests passed! ✅")
    sys.exit(0)
