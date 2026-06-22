"""
AgentCourt ADRP Adapter — Converts AgentCourt rulings to ADRP RulingBundle format.

Implements compatibility with IETF draft-stone-adrp-00 (Agent Dispute Resolution Protocol).
Converts AgentCourt's policy engine output into the signed RulingBundle artifact
that ADRP's verify_resolution function consumes.

Usage:
    from src.engine.adrp_adapter import ruling_to_adrp_bundle
    
    agentcourt_ruling = evaluate_dispute(dispute, evidence, "freelance-delivery")
    adrp_bundle = ruling_to_adrp_bundle(
        ruling=agentcourt_ruling,
        conduit_proof_hash="abc123...",  # H_c from ADRP DisputeBundle
        dispute_chain_tip="def456...",   # H_d from ADRP DisputeBundle
        arbitrator_did="did:web:agentcourt.ai",
        signing_key=ed25519_private_key,  # optional for unsigned draft
    )

Dependencies: Only standard library for hashing. Ed25519 signing requires `cryptography` package.
"""

import hashlib
import json
from datetime import datetime, timezone
from typing import Optional


# ─── Remedy → Verdict Mapping ────────────────────────────────────────────────

REMEDY_TO_VERDICT = {
    # AgentCourt remedy → ADRP verdict
    "full_refund": "refund",
    "full_payout": "release",
    "payout": "release",
    "payment": "release",
    "full_payment": "release",
    "partial_refund": "partial",
    "partial_payout": "partial",
    "service_credit": "partial",
    "escalate": None,  # Cannot produce ADRP ruling for escalated disputes
    "none": None,
    "no_match": None,
}

# ─── Claim Code Mapping ──────────────────────────────────────────────────────

AGENTCOURT_TO_ADRP_CLAIM = {
    "freelance-delivery": {
        "non-delivery": "quality_mismatch",
        "late-delivery-accepted": "timing_breach",
        "late-delivery-rejected": "timing_breach",
        "partial-delivery": "quality_mismatch",
        "disputed-acceptance": "spec_ambiguity",
        "rejected-quality": "quality_mismatch",
        "default-no-match": "spec_ambiguity",
    },
    "milestone-payment": {
        "milestone-completed-unpaid": "quality_mismatch",
        "milestone-incomplete-payment-justified": "quality_mismatch",
        "milestone-overdue-disputed": "timing_breach",
        "default-no-match": "spec_ambiguity",
    },
    "bug-bounty": {
        "valid-bug-full-payout": "quality_mismatch",
        "non-reproducible-bug": "quality_mismatch",
        "severity-below-threshold": "quality_mismatch",
        "non-compliant-disclosure": "quality_mismatch",
        "default-no-match": "spec_ambiguity",
    },
    "sla-monitoring": {
        "uptime-violation": "timing_breach",
        "latency-breach": "timing_breach",
        "partial-degradation": "quality_mismatch",
        "incidents-within-sla": "quality_mismatch",
        "insufficient-monitoring": "spec_ambiguity",
    },
}


def get_adrp_claim_code(policy_name: str, rule_id: str) -> str:
    """Map an AgentCourt rule to an ADRP claim code."""
    policy_map = AGENTCOURT_TO_ADRP_CLAIM.get(policy_name, {})
    return policy_map.get(rule_id, "spec_ambiguity")


def get_adrp_verdict(remedy: str) -> Optional[str]:
    """Map an AgentCourt remedy to an ADRP verdict."""
    return REMEDY_TO_VERDICT.get(remedy)


# ─── Canonical JSON (JCS-compatible) ─────────────────────────────────────────

def canonical_json(obj: dict) -> bytes:
    """
    Produce canonical JSON for signing.
    Implements a simplified JCS (JSON Canonicalization Scheme, RFC 8785).
    """
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    """SHA-256 hex digest."""
    return hashlib.sha256(data).hexdigest()


# ─── RulingBundle Builder ────────────────────────────────────────────────────

def ruling_to_adrp_bundle(
    ruling: dict,
    conduit_proof_hash: str,
    dispute_chain_tip: str,
    arbitrator_did: str = "did:web:agentcourt.ai",
    arbitrator_vc_hash: Optional[str] = None,
    signing_key: Optional[bytes] = None,
) -> dict:
    """
    Convert an AgentCourt ruling to an ADRP RulingBundle.
    
    Args:
        ruling: AgentCourt evaluate_dispute() output
        conduit_proof_hash: H_c — tip hash of the Conduit ProofBundle
        dispute_chain_tip: H_d — tip hash of the DisputeBundle chain
        arbitrator_did: AgentCourt's DID
        arbitrator_vc_hash: Hash of AgentCourt's Verifiable Credential
        signing_key: Ed25519 private key bytes (optional — produces unsigned draft if absent)
    
    Returns:
        ADRP RulingBundle dict per draft-stone-adrp-00 Section 7.2
    
    Raises:
        ValueError: If ruling cannot be mapped to an ADRP verdict (e.g., escalate)
    """
    remedy = ruling.get("remedy", "none")
    verdict = get_adrp_verdict(remedy)
    
    if verdict is None:
        raise ValueError(
            f"AgentCourt remedy '{remedy}' cannot be mapped to an ADRP verdict. "
            f"Disputes requiring escalation cannot produce ADRP RulingBundles."
        )
    
    # Build rationale hash from AgentCourt reasoning
    rationale = ruling.get("reasoning", "") + "\n\nMatched rule: " + str(ruling.get("matched_rule_id"))
    rationale_hash = sha256_hex(rationale.encode("utf-8"))
    
    # Determine partial split if applicable
    partial_split = None
    if verdict == "partial":
        # Extract split ratio from AgentCourt remedy if available
        # Default: 50/50 for generic partial rulings
        partial_split = ruling.get("split_ratio", {"to_buyer": 0.5, "to_seller": 0.5})
        # Validate split sums to 1.0
        total = partial_split.get("to_buyer", 0) + partial_split.get("to_seller", 0)
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"Partial split must sum to 1.0, got {total}")
    
    signing_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Build the RulingBundle (without signature first)
    bundle = {
        "type": "RulingBundle",
        "supersedes": conduit_proof_hash,
        "dispute_chain_tip": dispute_chain_tip,
        "verdict": verdict,
        "rationale_hash": rationale_hash,
        "arbitrator_did": arbitrator_did,
        "arbitrator_vc_hash": arbitrator_vc_hash or "",
        "signing_time": signing_time,
        "prev_hash": dispute_chain_tip,
    }
    
    if partial_split:
        bundle["partial_split"] = partial_split
    
    # Sign if key provided
    if signing_key is not None:
        sig = _sign_ed25519(bundle, signing_key)
        bundle["sig"] = sig
    else:
        # Unsigned draft — for testing/development
        bundle["sig"] = ""
        bundle["_unsigned"] = True
    
    return bundle


def _sign_ed25519(obj: dict, private_key: bytes) -> str:
    """Sign a canonical JSON object with Ed25519. Returns base64 signature."""
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        from cryptography.hazmat.primitives import serialization
        import base64
        
        key = Ed25519PrivateKey.from_private_bytes(private_key)
        message = canonical_json(obj)
        signature = key.sign(message)
        return base64.b64encode(signature).decode("ascii")
    except ImportError:
        return ""  # cryptography package not available


# ─── Verification (mirrors ADRP verify_resolution) ───────────────────────────

def verify_ruling_bundle(
    bundle: dict,
    expected_proof_hash: str,
    expected_chain_tip: str,
) -> tuple[bool, str]:
    """
    Verify an ADRP RulingBundle produced by AgentCourt.
    
    Implements the relevant checks from ADRP Section 16.1 verify_resolution.
    
    Returns:
        (valid, message)
    """
    # 1. Type check
    if bundle.get("type") != "RulingBundle":
        return False, "Not a RulingBundle"
    
    # 2. Anchor checks
    if bundle.get("supersedes") != expected_proof_hash:
        return False, f"Proof hash mismatch: {bundle.get('supersedes')} != {expected_proof_hash}"
    
    if bundle.get("prev_hash") != expected_chain_tip:
        return False, f"Chain tip mismatch: {bundle.get('prev_hash')} != {expected_chain_tip}"
    
    # 3. Verdict well-formed
    verdict = bundle.get("verdict")
    if verdict not in ("release", "refund", "partial"):
        return False, f"Invalid verdict: {verdict}"
    
    # 4. Partial split validation
    if verdict == "partial":
        split = bundle.get("partial_split", {})
        buyer = split.get("to_buyer", 0)
        seller = split.get("to_seller", 0)
        if abs(buyer + seller - 1.0) > 0.001:
            return False, f"Partial split sums to {buyer + seller}, not 1.0"
    
    # 5. Required fields present
    for field in ("rationale_hash", "arbitrator_did", "signing_time"):
        if not bundle.get(field):
            return False, f"Missing required field: {field}"
    
    return True, "Valid"


# ─── EscrowDirective ─────────────────────────────────────────────────────────

def to_escrow_directive(bundle: dict, payment_mandate_ref: str) -> dict:
    """
    Derive an ADRP EscrowDirective from a RulingBundle.
    
    Per ADRP Section 16.1, verify_resolution produces an EscrowDirective
    consumed by the AP2 Payment Mandate executor or VCAP escrow rail.
    """
    verdict = bundle.get("verdict", "release")
    
    return {
        "payment_mandate_ref": payment_mandate_ref,
        "action": verdict,
        "split": bundle.get("partial_split", {"to_buyer": 1.0, "to_seller": 0.0}) if verdict == "partial" else None,
        "ruling_ref": sha256_hex(canonical_json(bundle)),
    }
