"""
Tests for ADRP Adapter — verify AgentCourt rulings convert to valid ADRP RulingBundles.
"""

import sys
sys.path.insert(0, "/root/.letta/agentcourt")

from src.engine.adrp_adapter import (
    get_adrp_verdict,
    get_adrp_claim_code,
    ruling_to_adrp_bundle,
    verify_ruling_bundle,
    to_escrow_directive,
    canonical_json,
    sha256_hex,
)

# ─── Test Data ───────────────────────────────────────────────────────────────

CONDUIT_PROOF_HASH = "a" * 64
DISPUTE_CHAIN_TIP = "b" * 64

SAMPLE_RULINGS = {
    "full_refund": {
        "remedy": "full_refund",
        "matched_rule_id": "non-delivery",
        "policy_name": "freelance-delivery",
        "confidence": "medium",
        "reasoning": "Respondent failed to deliver. Contract existed, deadline passed, no delivery evidence.",
    },
    "full_payout": {
        "remedy": "full_payout",
        "matched_rule_id": "milestone-completed-unpaid",
        "policy_name": "milestone-payment",
        "confidence": "high",
        "reasoning": "Milestone completed and accepted but payment never made.",
    },
    "partial": {
        "remedy": "partial_refund",
        "matched_rule_id": "partial-delivery",
        "policy_name": "freelance-delivery",
        "confidence": "medium",
        "reasoning": "Only 2 of 5 deliverables were submitted.",
        "split_ratio": {"to_buyer": 0.6, "to_seller": 0.4},
    },
    "escalate": {
        "remedy": "escalate",
        "matched_rule_id": "default-no-match",
        "policy_name": "freelance-delivery",
        "confidence": "low",
        "reasoning": "Insufficient evidence to match any rule.",
    },
}


def test_remedy_to_verdict_mapping():
    """All AgentCourt remedies map to correct ADRP verdicts."""
    assert get_adrp_verdict("full_refund") == "refund"
    assert get_adrp_verdict("full_payout") == "release"
    assert get_adrp_verdict("partial_refund") == "partial"
    assert get_adrp_verdict("escalate") is None
    assert get_adrp_verdict("none") is None
    print("✅ test_remedy_to_verdict_mapping")


def test_claim_code_mapping():
    """AgentCourt rules map to valid ADRP claim codes."""
    assert get_adrp_claim_code("freelance-delivery", "non-delivery") == "quality_mismatch"
    assert get_adrp_claim_code("sla-monitoring", "latency-breach") == "timing_breach"
    assert get_adrp_claim_code("bug-bounty", "non-reproducible-bug") == "quality_mismatch"
    assert get_adrp_claim_code("freelance-delivery", "disputed-acceptance") == "spec_ambiguity"
    print("✅ test_claim_code_mapping")


def test_full_refund_to_adrp():
    """Full refund ruling converts to ADRP RulingBundle with verdict=refund."""
    bundle = ruling_to_adrp_bundle(
        ruling=SAMPLE_RULINGS["full_refund"],
        conduit_proof_hash=CONDUIT_PROOF_HASH,
        dispute_chain_tip=DISPUTE_CHAIN_TIP,
    )
    assert bundle["type"] == "RulingBundle"
    assert bundle["verdict"] == "refund"
    assert bundle["supersedes"] == CONDUIT_PROOF_HASH
    assert bundle["prev_hash"] == DISPUTE_CHAIN_TIP
    assert bundle["arbitrator_did"] == "did:web:agentcourt.ai"
    assert len(bundle["rationale_hash"]) == 64
    print("✅ test_full_refund_to_adrp")


def test_full_payout_to_adrp():
    """Full payout ruling converts to ADRP RulingBundle with verdict=release."""
    bundle = ruling_to_adrp_bundle(
        ruling=SAMPLE_RULINGS["full_payout"],
        conduit_proof_hash=CONDUIT_PROOF_HASH,
        dispute_chain_tip=DISPUTE_CHAIN_TIP,
    )
    assert bundle["verdict"] == "release"
    assert "partial_split" not in bundle
    print("✅ test_full_payout_to_adrp")


def test_partial_to_adrp():
    """Partial refund ruling converts to ADRP RulingBundle with verdict=partial."""
    bundle = ruling_to_adrp_bundle(
        ruling=SAMPLE_RULINGS["partial"],
        conduit_proof_hash=CONDUIT_PROOF_HASH,
        dispute_chain_tip=DISPUTE_CHAIN_TIP,
    )
    assert bundle["verdict"] == "partial"
    assert bundle["partial_split"]["to_buyer"] == 0.6
    assert bundle["partial_split"]["to_seller"] == 0.4
    assert abs(bundle["partial_split"]["to_buyer"] + bundle["partial_split"]["to_seller"] - 1.0) < 0.001
    print("✅ test_partial_to_adrp")


def test_escalate_raises_error():
    """Escalated disputes cannot produce ADRP RulingBundles."""
    try:
        ruling_to_adrp_bundle(
            ruling=SAMPLE_RULINGS["escalate"],
            conduit_proof_hash=CONDUIT_PROOF_HASH,
            dispute_chain_tip=DISPUTE_CHAIN_TIP,
        )
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "escalation" in str(e).lower()
    print("✅ test_escalate_raises_error")


def test_verify_ruling_bundle_valid():
    """Valid RulingBundle passes verification."""
    bundle = ruling_to_adrp_bundle(
        ruling=SAMPLE_RULINGS["full_refund"],
        conduit_proof_hash=CONDUIT_PROOF_HASH,
        dispute_chain_tip=DISPUTE_CHAIN_TIP,
    )
    valid, msg = verify_ruling_bundle(bundle, CONDUIT_PROOF_HASH, DISPUTE_CHAIN_TIP)
    assert valid, f"Should be valid: {msg}"
    print("✅ test_verify_ruling_bundle_valid")


def test_verify_ruling_bundle_wrong_hash():
    """RulingBundle with wrong proof hash fails verification."""
    bundle = ruling_to_adrp_bundle(
        ruling=SAMPLE_RULINGS["full_refund"],
        conduit_proof_hash=CONDUIT_PROOF_HASH,
        dispute_chain_tip=DISPUTE_CHAIN_TIP,
    )
    valid, msg = verify_ruling_bundle(bundle, "w" * 64, DISPUTE_CHAIN_TIP)
    assert not valid
    assert "mismatch" in msg.lower()
    print("✅ test_verify_ruling_bundle_wrong_hash")


def test_escrow_directive_release():
    """EscrowDirective correctly derived for release verdict."""
    bundle = ruling_to_adrp_bundle(
        ruling=SAMPLE_RULINGS["full_payout"],
        conduit_proof_hash=CONDUIT_PROOF_HASH,
        dispute_chain_tip=DISPUTE_CHAIN_TIP,
    )
    directive = to_escrow_directive(bundle, "pm_123")
    assert directive["action"] == "release"
    assert directive["payment_mandate_ref"] == "pm_123"
    assert directive["split"] is None
    assert len(directive["ruling_ref"]) == 64
    print("✅ test_escrow_directive_release")


def test_escrow_directive_partial():
    """EscrowDirective correctly derived for partial verdict."""
    bundle = ruling_to_adrp_bundle(
        ruling=SAMPLE_RULINGS["partial"],
        conduit_proof_hash=CONDUIT_PROOF_HASH,
        dispute_chain_tip=DISPUTE_CHAIN_TIP,
    )
    directive = to_escrow_directive(bundle, "pm_456")
    assert directive["action"] == "partial"
    assert directive["split"]["to_buyer"] == 0.6
    assert directive["split"]["to_seller"] == 0.4
    print("✅ test_escrow_directive_partial")


def test_canonical_json():
    """Canonical JSON produces deterministic output."""
    obj = {"b": 1, "a": 2}
    result = canonical_json(obj)
    assert result == b'{"a":2,"b":1}'  # sorted keys, compact
    print("✅ test_canonical_json")


# ─── Run All Tests ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    test_remedy_to_verdict_mapping()
    test_claim_code_mapping()
    test_full_refund_to_adrp()
    test_full_payout_to_adrp()
    test_partial_to_adrp()
    test_escalate_raises_error()
    test_verify_ruling_bundle_valid()
    test_verify_ruling_bundle_wrong_hash()
    test_escrow_directive_release()
    test_escrow_directive_partial()
    test_canonical_json()
    print("\n" + "=" * 40)
    print("ADRP Adapter: 11/11 tests passed ✅")
